from typing import List, Dict, Any
from pymongo import MongoClient
from pandanite.logging import logger
from pandanite.core.transaction import Transaction
from pandanite.core.crypto import (
    SHA256Hash,
    PublicWalletAddress,
    wallet_address_to_string,
)
from pandanite.core.common import TransactionAmount
from pandanite.core.block import Block

"""'
Mongo collection schemas
blocks: Results of block.to_json() are stored directly
transaction_to_block: { 'tx_id': string, 'block_id': int }
ledger: {'address': string, 'balance': int }
wallet_to_transaction: {'address': string, 'tx_ids': list[string]}
info: {'total_work': int}
"""


class PandaniteDB:
    def __init__(self, port: int = 27017, db: str = "pandanite-test"):
        self.client = MongoClient("localhost", port)
        self.db = self.client[db]
        self.transaction_to_block = self.db.transaction_to_block
        self.transaction_to_block.create_index("tx_id", unique=True)
        self.blocks = self.db.blocks
        self.blocks.create_index("id", unique=True)
        self.ledger = self.db.ledger
        self.ledger.create_index("address", unique=True)
        self.wallet_to_transaction = self.db.wallet_to_transaction
        self.wallet_to_transaction.create_index("address", unique=True)
        self.info = self.db.info

    def add_block(self, block: Block):
        self.blocks.replace_one({"id": block.get_id()}, block.to_json(), upsert=True)

    def start_session(self):
        return self.db.start_session()

    def get_wallets(
        self, wallets: list[PublicWalletAddress]
    ) -> Dict[str, TransactionAmount]:
        wallet_totals: Dict[str, TransactionAmount]
        for wallet in wallets:
            wallet_address = wallet_address_to_string(wallet)
            found_wallet = self.ledger.find_one({"wallet": wallet_address})
            if found_wallet:
                wallet_totals[wallet_address] = found_wallet["balance"]
        return wallet_totals

    def update_wallet(self, wallet: str, amount: TransactionAmount):
        updated_record = {
            "address": wallet,
            "balance": amount,
        }
        self.ledger.replace_one({"address": wallet}, updated_record, upsert=True)

    def add_wallet_transaction(self, wallet: PublicWalletAddress, tx_id: str):
        address = wallet_address_to_string(wallet)
        self.wallet_to_transaction.update_one(
            {"address": address}, {"$push": {"tx_ids": tx_id}}, upsert=True
        )

    def pop_block(self):
        # TODO remove actual block from mongo collection
        return None

    def get_num_blocks(self) -> int:
        return self.blocks.count()

    def find_block_for_transaction(self, t: Transaction) -> int:
        return 0

    def find_block_for_transaction_id(self, txid: SHA256Hash) -> int:
        return 0

    def get_wallet_value(self, addr: PublicWalletAddress) -> TransactionAmount:
        return 0

    def get_transactions_for_wallet(
        self, addr: PublicWalletAddress
    ) -> List[Transaction]:
        return []

    def get_last_hash(self) -> SHA256Hash:
        return self.get_block(self.get_num_blocks()).last_block_hash

    def get_block(self, block_id: int) -> Block:
        if block_id <= 0 or block_id > self.get_num_blocks():
            raise Exception("Invalid block")
        return self.blocks.find_one({"id": block_id})

    def get_total_work(self) -> int:
        return self.info.find_one()["total_work"]

    def get_difficulty(self) -> int:
        return self.get_block(self.get_num_blocks()).difficulty
