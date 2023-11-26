from enum import Enum
from typing import Dict, Optional, Set, Tuple
from pandanite.core.common import TransactionAmount
from pandanite.core.crypto import (
    PublicWalletAddress,
    sha_256_to_string,
    wallet_address_from_public_key,
    wallet_address_to_string,
)
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


def execute_block(
    db: PandaniteDB,
    wallets: Dict[str, TransactionAmount],
    block: Block,
    block_mining_fee: TransactionAmount,
) -> Tuple[ExecutionStatus, Optional[Dict[str, TransactionAmount]]]:
    # try executing each transaction
    miner: Optional[PublicWalletAddress] = None
    mining_fee: TransactionAmount = 0
    transaction_hashes: Set[str] = set()

    for t in block.get_transactions():
        tx_id = sha_256_to_string(t.get_hash())
        if t.is_fee():
            if miner != None:
                return ExecutionStatus.EXTRA_MINING_FEE, None
            else:
                miner = t.get_recepient()
                mining_fee = t.get_amount()
        elif tx_id in transaction_hashes or db.find_block_for_transaction(t) > 0:
            return ExecutionStatus.EXPIRED_TRANSACTION, None

        transaction_hashes.add(tx_id)

    if not miner:
        return ExecutionStatus.NO_MINING_FEE, None

    miner_address = wallet_address_to_string(miner)

    if mining_fee != block_mining_fee:
        return ExecutionStatus.INCORRECT_MINING_FEE, None

    for t in block.get_transactions():
        if not t.is_fee() and not t.signature_valid() and block.get_id() != 1:
            return ExecutionStatus.INVALID_SIGNATURE, None

        recepient_address = wallet_address_to_string(t.get_recepient())

        if block.get_id() == 1:
            if recepient_address in wallets.keys():
                wallets[recepient_address] += t.get_amount()
            else:
                wallets[recepient_address] = t.get_amount()
        else:
            if t.is_fee():
                amount = t.get_amount()
                if amount == block_mining_fee:
                    if recepient_address in wallets.keys():
                        wallets[recepient_address] += amount
                    else:
                        wallets[recepient_address] = amount
                else:
                    return ExecutionStatus.INCORRECT_MINING_FEE, None
            else:
                sender_address = wallet_address_to_string(t.get_sender())

                # from account must exist
                if not sender_address in wallets.keys():
                    return ExecutionStatus.SENDER_DOES_NOT_EXIST, None
                amount = t.get_amount()
                fees = t.get_fee()
                available = wallets[sender_address]

                if available < (amount + fees):
                    return ExecutionStatus.BALANCE_TOO_LOW, None

                wallets[sender_address] -= amount + fees

                # deposit funds
                if recepient_address in wallets.keys():
                    wallets[recepient_address] += amount
                else:
                    wallets[recepient_address] = amount

                # deposit fees to miner
                if miner_address in wallets.keys():
                    wallets[miner_address] += fees
                else:
                    wallets[miner_address] = fees

    return ExecutionStatus.SUCCESS, wallets
