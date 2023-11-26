from pandanite.core.blockchain import BlockChain
from pandanite.core.block import Block
from pandanite.core.user import User
from pandanite.core.executor import ExecutionStatus
from pandanite.core.crypto import mine_hash
from pandanite.core.transaction import get_merkle_hash
from pandanite.storage.db import PandaniteDB


def test_check_adding_new_node_with_hash():
    db = PandaniteDB()
    blockchain = BlockChain(db)
    status = blockchain.load_genesis()
    assert status == ExecutionStatus.SUCCESS
    miner = User()
    fee = miner.mine()

    block = Block()
    block.set_id(2)
    block.add_transaction(fee)

    merkle_hash = get_merkle_hash(block.get_transactions())
    block.set_merkle_root(merkle_hash)
    block.set_last_block_hash(db.get_last_hash())
    block.set_difficulty(db.get_difficulty())
    block.set_timestamp(0)
    hash = block.get_hash()
    solution = mine_hash(hash, block.get_difficulty())
    block.set_nonce(solution)
    status = blockchain.add_block(block)
    assert status == ExecutionStatus.SUCCESS
