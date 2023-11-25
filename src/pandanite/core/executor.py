from enum import Enum
from typing import Dict, Optional, Set, Tuple
from pandanite.core.common import TransactionAmount
from pandanite.core.crypto import PublicWalletAddress, SHA256Hash, wallet_address_from_public_key
from pandanite.core.block import Block
from pandanite.storage.db import PandaniteDB

class ExecutionStatus(Enum):
    SENDER_DOES_NOT_EXIST = "SENDER_DOES_NOT_EXIST"
    BALANCE_TOO_LOW = "BALANCE_TOO_LOW"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    INVALID_NONCE = "INVALID_NONCE"
    EXTRA_MINING_FEE = "EXTRA_MINING_FEE"
    INCORRECT_MINING_FEE = "INCORRECT_MINING_FEE"
    INVALID_BLOCK_ID = "INVALID_BLOCK_ID"
    NO_MINING_FEE = "NO_MINING_FEE"
    INVALID_DIFFICULTY = "INVALID_DIFFICULTY"
    INVALID_TRANSACTION_NONCE = "INVALID_TRANSACTION_NONCE"
    INVALID_TRANSACTION_TIMESTAMP = "INVALID_TRANSACTION_TIMESTAMP"
    BLOCK_TIMESTAMP_TOO_OLD = "BLOCK_TIMESTAMP_TOO_OLD"
    BLOCK_TIMESTAMP_IN_FUTURE = "BLOCK_TIMESTAMP_IN_FUTURE"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    QUEUE_FULL = "QUEUE_FULL"
    HEADER_HASH_INVALID = "HEADER_HASH_INVALID"
    EXPIRED_TRANSACTION = "EXPIRED_TRANSACTION"
    ALREADY_IN_QUEUE = "ALREADY_IN_QUEUE"
    BLOCK_ID_TOO_LARGE = "BLOCK_ID_TOO_LARGE"
    INVALID_MERKLE_ROOT = "INVALID_MERKLE_ROOT"
    INVALID_LASTBLOCK_HASH = "INVALID_LASTBLOCK_HASH"
    INVALID_TRANSACTION_COUNT = "INVALID_TRANSACTION_COUNT"
    TRANSACTION_FEE_TOO_LOW = "TRANSACTION_FEE_TOO_LOW"
    WALLET_SIGNATURE_MISMATCH = "WALLET_SIGNATURE_MISMATCH"
    IS_SYNCING = "IS_SYNCING"
    SUCCESS = "SUCCESS"

def execute_block(db: PandaniteDB, wallets: Dict[PublicWalletAddress, TransactionAmount], block: Block, block_mining_fee: TransactionAmount) -> Tuple[ExecutionStatus, Optional[Dict[PublicWalletAddress, TransactionAmount]]]:
    # try executing each transaction
    miner: Optional[PublicWalletAddress] = None
    mining_fee: TransactionAmount = 0
    transaction_hashes: Set[SHA256Hash] = set()

    for t in block.get_transactions():
        tx_id = t.get_hash()
        if t.is_fee():
            if miner != None:
                return ExecutionStatus.EXTRA_MINING_FEE, None
            else:
                miner = t.to_wallet()
                mining_fee = t.get_amount()
        elif (tx_id in transaction_hashes or db.find_block_for_transaction(t) > 0):
            return ExecutionStatus.EXPIRED_TRANSACTION, None
        
        if not t.is_fee() and block.get_id() > 1 and wallet_address_from_public_key(t.get_signing_key()) != t.from_wallet():
            return ExecutionStatus.WALLET_SIGNATURE_MISMATCH, None
        
        
    if not miner:
        return ExecutionStatus.NO_MINING_FEE, None

    if (mining_fee != block_mining_fee):
        return ExecutionStatus.INCORRECT_MINING_FEE, None

    for t in block.get_transactions():
        if (not t.is_fee() and not t.signature_valid() and block.get_id() != 1):
            return ExecutionStatus.INVALID_SIGNATURE, None

        if block.get_id() == 1:
            if t.get_recepient() in wallets.keys():
                wallets[t.get_recepient()] += t.get_amount()
        else:
            # from account must exist
            if not t.get_sender() in wallets.keys():
                return ExecutionStatus.SENDER_DOES_NOT_EXIST, None
            amount = t.get_amount()
            fees = t.get_fee()
            available = wallets[t.get_sender()]

            if available < (amount + fees):
                return ExecutionStatus.BALANCE_TOO_LOW, None
            
            wallets[t.get_sender()] -= amount + fees
            
            # deposit funds
            if t.get_recepient() in wallets.keys():
                wallets[t.get_recepient()] += amount
            else:
                wallets[t.get_recepient()] = amount

            # deposit fees to miner
            if miner in wallets.keys():
                wallets[miner] += fees
            else:
                wallets[miner] = fees

    return ExecutionStatus.SUCCESS, wallets
