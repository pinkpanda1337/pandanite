import json

from typing import Dict, cast
from pandanite.logging import logger
from pandanite.core.helpers import PDN, compute_difficulty
from pandanite.core.constants import (
    DIFFICULTY_LOOKBACK,
    DESIRED_BLOCK_TIME_SEC,
    MAX_TRANSACTIONS_PER_BLOCK,
)
from pandanite.core.common import TransactionAmount
from pandanite.core.crypto import PublicWalletAddress, sha_256_to_string, mine_hash
from pandanite.core.executor import ExecutionStatus
from pandanite.core.transaction import Transaction, get_merkle_hash
from pandanite.storage.db import PandaniteDB
from pandanite.core.block import Block
from pandanite.core.executor import execute_block


class BlockChain:
    def __init__(self, db: PandaniteDB):
        self.db = db

    def load_genesis(self):
        self.db.clear()
        with open("genesis.json", "r") as f:
            block = Block()
            block.from_json(json.loads(f.read()))
            return self.add_block(block)

    def get_current_mining_fee(self, block_id: int) -> int:
        logical_block = block_id + 125180 + 7750 + 18000
        amount = 50.0
        while logical_block >= 666666:
            amount *= 2.0 / 3.0
            logical_block -= 666666
        return PDN(amount)

    def get_supply(self) -> int:
        supply = 0.0
        amount_offset = 6647477.8490
        amount = 50.0
        blocks = self.db.get_num_blocks()
        while blocks >= 666666:
            supply += 666666 * amount
            amount *= 2.0 / 3.0
            blocks -= 666666
        supply += blocks * amount
        return int(supply + amount_offset)

    def verify_transaction(self, t: Transaction) -> ExecutionStatus:
        return ExecutionStatus.EXPIRED_TRANSACTION

    def get_header_chain_stats(self) -> Dict[str, int]:
        return {}

    def pop_block(self):
        self.db.pop_block()
        if self.db.get_num_blocks() > 1:
            self._update_difficulty()

    def add_block(self, block: Block, network_timestamp: int = 0) -> ExecutionStatus:
        if len(block.get_transactions()) > MAX_TRANSACTIONS_PER_BLOCK:
            return ExecutionStatus.INVALID_TRANSACTION_COUNT

        if block.get_id() != self.db.get_num_blocks() + 1:
            print(self.db.get_num_blocks())
            return ExecutionStatus.INVALID_BLOCK_ID

        # check difficulty + nonce
        if block.get_difficulty() != self.db.get_difficulty():
            if (
                block.get_id() >= 536100
                and block.get_id() <= 536200
                and block.get_difficulty() == 27
            ):
                logger.log(
                    0, "Skipping difficulty verification on known invalid difficulty"
                )
            else:
                return ExecutionStatus.INVALID_DIFFICULTY

        if not block.verify_nonce():
            return ExecutionStatus.INVALID_NONCE

        if block.get_last_block_hash() != self.db.get_last_hash():
            return ExecutionStatus.INVALID_LASTBLOCK_HASH

        if block.get_id() != 1:
            # block must be less than 2 hrs into future from network time
            max_time = network_timestamp + 120 * 60
            if block.get_timestamp() > max_time:
                return ExecutionStatus.BLOCK_TIMESTAMP_IN_FUTURE

            # block must be after the median timestamp of last 10 blocks
            if self.db.get_num_blocks() > 10:
                times: list[int] = []
                for i in range(0, 10):
                    b = self.db.get_block(self.db.get_num_blocks() - i)
                    times.append(b.get_timestamp())

                times = sorted(times)
                # compute median
                if len(times) % 2 == 0:
                    median_time = (
                        times[len(times) // 2] + times[len(times) // 2 - 1]
                    ) / 2
                else:
                    median_time = times[len(times) // 2]
                if block.get_timestamp() < median_time:
                    return ExecutionStatus.BLOCK_TIMESTAMP_TOO_OLD

        # compute merkle tree and verify root matches;
        merkle_root = get_merkle_hash(block.get_transactions())
        if block.get_merkle_root() != merkle_root:
            return ExecutionStatus.INVALID_MERKLE_ROOT

        withdrawal_wallets: list[PublicWalletAddress] = []
        for t in block.get_transactions():
            if not t.is_fee():
                withdrawal_wallets.append(t.get_sender())
        wallets = self.db.get_wallets(withdrawal_wallets)

        # TODO: Run executor, add block
        status, updated_wallets = execute_block(
            self.db, wallets, block, self.get_current_mining_fee(block.get_id())
        )

        if status != ExecutionStatus.SUCCESS:
            return status

        updated_wallets = cast(Dict[str, TransactionAmount], updated_wallets)

        with self.db.start_session() as session:
            with session.start_transaction():
                self.db.add_block(block)
                for wallet in updated_wallets.keys():
                    self.db.update_wallet(wallet, updated_wallets[wallet])
                for t in block.get_transactions():
                    tx_id = sha_256_to_string(t.get_hash())
                    self.db.add_wallet_transaction(t.get_recepient(), tx_id)
                    if not t.is_fee() and block.get_id() != 1:
                        self.db.add_wallet_transaction(t.get_sender(), tx_id)

        return ExecutionStatus.SUCCESS

    def _update_difficulty(self):
        if self.db.get_num_blocks() <= DIFFICULTY_LOOKBACK * 2:
            return
        if self.db.get_num_blocks() % DIFFICULTY_LOOKBACK != 0:
            return
        first_id = self.db.get_num_blocks() - DIFFICULTY_LOOKBACK
        last_id = self.db.get_num_blocks()
        first = self.db.get_block(first_id)
        last = self.db.get_block(last_id)
        elapsed = last.get_timestamp() - first.get_timestamp()
        numBlocksElapsed = last_id - first_id
        target = numBlocksElapsed * DESIRED_BLOCK_TIME_SEC
        difficulty = last.get_difficulty()
        self.db.set_difficulty(compute_difficulty(difficulty, elapsed, target))
