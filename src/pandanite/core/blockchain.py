# from typing import Dict
# from pandanite.logging import logger
# from pandanite.core.helpers import PDN, compute_difficulty
# from pandanite.core.constants import (
#     DIFFICULTY_LOOKBACK,
#     DESIRED_BLOCK_TIME_SEC,
#     PUFFERFISH_START_BLOCK,
#     MIN_DIFFICULTY,
#     MAX_TRANSACTIONS_PER_BLOCK,
# )
# from pandanite.core.executor import ExecutionStatus
# from pandanite.core.crypto import get_merkle_hash
# from pandanite.core.transaction import Transaction
# from pandanite.storage.db import PandaniteDB
# from pandanite.core.block import Block


# class BlockChain:
#     def __init__(self):
#         self.db = PandaniteDB()

#     def get_current_mining_fee(self, block_id: int) -> int:
#         logical_block = block_id + 125180 + 7750 + 18000
#         amount = 50.0
#         while logical_block >= 666666:
#             amount *= 2.0 / 3.0
#             logical_block -= 666666
#         return PDN(amount)

#     def get_supply(self) -> float:
#         supply = 0
#         amount_offset = 6647477.8490
#         amount = 50.0
#         blocks = self.db.get_num_blocks()
#         while blocks >= 666666:
#             supply += 666666 * amount
#             amount *= 2.0 / 3.0
#             blocks -= 666666
#         supply += blocks * amount
#         return supply + amount_offset

#     def verify_transaction(self, t: Transaction) -> ExecutionStatus:
#         pass

#     def get_header_chain_stats(self) -> Dict[str, int]:
#         pass

#     def pop_block(self):
#         self.db.pop_block()
#         if self.db.get_block_count() > 1:
#             self._update_difficulty()

#     def add_block(self, block: Block, network_timestamp: int) -> ExecutionStatus:
#         if len(block.get_transactions()) > MAX_TRANSACTIONS_PER_BLOCK:
#             return ExecutionStatus.INVALID_TRANSACTION_COUNT

#         if block.get_id() != self.db.get_block_count() + 1:
#             return ExecutionStatus.INVALID_BLOCK_ID

#         # check difficulty + nonce
#         if block.get_difficulty() != self.difficulty:
#             if (
#                 block.getId() >= 536100
#                 and block.get_id() <= 536200
#                 and block.get_difficulty() == 27
#             ):
#                 logger.log(
#                     "Skipping difficulty verification on known invalid difficulty"
#                 )
#             else:
#                 return ExecutionStatus.INVALID_DIFFICULTY

#         if not block.verify_nonce():
#             return ExecutionStatus.INVALID_NONCE

#         if block.get_last_block_hash() != self.db.get_last_hash():
#             return ExecutionStatus.INVALID_LASTBLOCK_HASH

#         if block.get_id() != 1:
#             # block must be less than 2 hrs into future from network time
#             max_time = network_timestamp + 120 * 60
#             if block.get_timestamp() > max_time:
#                 return ExecutionStatus.BLOCK_TIMESTAMP_IN_FUTURE

#             # block must be after the median timestamp of last 10 blocks
#             if self.db.get_num_blocks() > 10:
#                 times = []
#                 for i in range(0, 10):
#                     b = self.db.get_block(self.db.get_num_blocks() - i)
#                     times.push_back(b.get_timestamp())

#                 times = sorted(times)
#                 # compute median
#                 if len(times) % 2 == 0:
#                     median_time = (
#                         times[len(times) // 2] + times[len(times) // 2 - 1]
#                     ) / 2
#                 else:
#                     median_time = times[len(times) // 2]
#                 if block.get_timestamp() < median_time:
#                     return ExecutionStatus.BLOCK_TIMESTAMP_TOO_OLD

#         # compute merkle tree and verify root matches;
#         merkle_root = get_merkle_hash(block.get_transactions())
#         if block.get_merkle_root() != merkle_root():
#             return ExecutionStatus.INVALID_MERKLE_ROOT

#         # LedgerState deltasFromBlock;
#         # ExecutionStatus status = Executor::ExecuteBlock(block, this->ledger, this->txdb, deltasFromBlock, this->getCurrentMiningFee(block.getId()));

#         # if (status != SUCCESS) {
#         #     Executor::Rollback(this->ledger, deltasFromBlock);
#         # } else {
#         #     if (this->memPool != nullptr) {
#         #         this->memPool->finishBlock(block);
#         #     }
#         #     // add all transactions to txdb:
#         #     for(auto t : block.getTransactions()) {
#         #         this->txdb.insertTransaction(t, block.getId());
#         #     }
#         #     this->blockStore->setBlock(block);
#         #     this->numBlocks++;
#         #     this->totalWork = addWork(this->totalWork, block.getDifficulty());
#         #     this->blockStore->setTotalWork(this->totalWork);
#         #     this->blockStore->setBlockCount(this->numBlocks);
#         #     this->lastHash = block.getHash();
#         #     this->updateDifficulty();
#         #     Logger::logStatus("Added block " + to_string(block.getId()));
#         #     Logger::logStatus("difficulty= " + to_string(block.getDifficulty()));
#         # }
#         # return status;

#     def _update_difficulty(self):
#         if self.db.get_num_blocks() <= DIFFICULTY_LOOKBACK * 2:
#             return
#         if self.db.get_num_blocks() % DIFFICULTY_LOOKBACK != 0:
#             return
#         first_id = self.db.get_num_blocks() - DIFFICULTY_LOOKBACK
#         last_id = self.db.get_num_blocks()
#         first = self.db.get_block(first_id)
#         last = self.db.get_block(last_id)
#         elapsed = last.get_timestamp() - first.get_timestamp()
#         numBlocksElapsed = last_id - first_id
#         target = numBlocksElapsed * DESIRED_BLOCK_TIME_SEC
#         difficulty = last.get_difficulty()
#         self.difficulty = compute_difficulty(difficulty, elapsed, target)
#         if (
#             self.db.get_num_blocks() >= PUFFERFISH_START_BLOCK
#             and self.db.get_num_blocks()
#             < (PUFFERFISH_START_BLOCK + DIFFICULTY_LOOKBACK * 2)
#         ):
#             self.difficulty = MIN_DIFFICULTY
