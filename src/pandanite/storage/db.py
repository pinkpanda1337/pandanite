# from typing import List
# from pandanite.core.transaction import Transaction
# from pandanite.core.crypto import SHA256Hash, PublicWalletAddress
# from pandanite.core.common import TransactionAmount
# from pandanite.core.block import Block, BlockHeader

# class PandaniteDB:
#     def __init__(self):
#         pass

#     def pop_block(self):
#         pass

#     def get_num_blocks(self) -> int:
#         pass

#     def find_block_for_transaction(self, t: Transaction) -> int:
#         pass

#     def find_block_for_transaction_id(self, txid: SHA256Hash) -> int:
#         pass

#     def get_wallet_value(self, addr: PublicWalletAddress) -> TransactionAmount:
#         pass

#     def get_transactions_for_wallet(self, addr: PublicWalletAddress) -> List[Transaction]:
#         pass

#     def get_last_hash(self) -> SHA256Hash:
#         return self._last_hash

#     def get_block(self, block_id: int) -> Block:
#         if (block_id <= 0 or block_id > self._num_blocks):
#             raise "Invalid block"
#         return self.db.get_block(block_id)

#     def get_total_work(self) -> int:
#         pass

#     def get_difficulty(self) -> int:
#         return self._difficulty

#     def get_block_count(self) -> int:
#         return self._num_blocks

#     def get_block_header(self, block_id: int) -> BlockHeader:
#         pass