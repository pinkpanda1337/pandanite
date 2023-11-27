from pandanite.core.blockchain import BlockChain
from pandanite.core.block import Block
from pandanite.core.user import User
from pandanite.core.executor import ExecutionStatus
from pandanite.core.crypto import mine_hash, wallet_address_to_string
from pandanite.core.transaction import get_merkle_hash
from pandanite.storage.db import PandaniteDB
from pandanite.core.helpers import PDN
from pandanite.core.crypto import NULL_SHA256_HASH

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


def test_check_popping_block():
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
    # check the wallet value
    miner_address = wallet_address_to_string(miner.get_address())
    wallets = db.get_wallets([miner.get_address()])
    assert wallets[miner_address] == PDN(50.0)
    blockchain.pop_block()
    wallets = db.get_wallets([miner.get_address()])
    assert wallets[miner_address] == PDN(0.0)


def test_check_adding_wrong_lastblock_hash_fails():
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
    block.set_last_block_hash(NULL_SHA256_HASH)
    block.set_difficulty(db.get_difficulty())
    block.set_timestamp(0)
    hash = block.get_hash()
    solution = mine_hash(hash, block.get_difficulty())
    block.set_nonce(solution)
    status = blockchain.add_block(block)
    assert status == ExecutionStatus.INVALID_LASTBLOCK_HASH

def test_check_adding_two_nodes_updates_ledger():
    db = PandaniteDB()
    blockchain = BlockChain(db)
    status = blockchain.load_genesis()
    assert status == ExecutionStatus.SUCCESS
    miner = User()
    for i in range(2, 4):
        fee = miner.mine()
        new_block = Block()
        new_block.set_id(i)
        new_block.add_transaction(fee)
        merkle_hash = get_merkle_hash(new_block.get_transactions())
        new_block.set_merkle_root(merkle_hash)
        new_block.set_last_block_hash(db.get_last_hash())
        new_block.set_difficulty(db.get_difficulty())
        new_block.set_timestamp(0)
        hash = new_block.get_hash()
        solution = mine_hash(hash, db.get_difficulty())
        new_block.set_nonce(solution)
        status = blockchain.add_block(new_block)
        assert status == ExecutionStatus.SUCCESS
    # check the wallet value
    miner_address = wallet_address_to_string(miner.get_address())
    wallets = db.get_wallets([miner.get_address()])
    assert wallets[miner_address] == PDN(100.0)

def test_check_sending_transaction_updates_ledger():
    db = PandaniteDB()
    blockchain = BlockChain(db)
    status = blockchain.load_genesis()
    assert status == ExecutionStatus.SUCCESS
    miner = User()
    other = User()
    for i in range(2, 4):
        fee = miner.mine()
        new_block = Block()
        new_block.set_id(i)
        new_block.add_transaction(fee)
        if (i==3):
            t = miner.send(other, PDN(20.0))
            new_block.add_transaction(t)
        merkle_hash = get_merkle_hash(new_block.get_transactions())
        new_block.set_merkle_root(merkle_hash)
        new_block.set_last_block_hash(db.get_last_hash())
        new_block.set_difficulty(db.get_difficulty())
        new_block.set_timestamp(0)
        hash = new_block.get_hash()
        solution = mine_hash(hash, db.get_difficulty())
        new_block.set_nonce(solution)
        status = blockchain.add_block(new_block)
        assert status == ExecutionStatus.SUCCESS
    miner_addr = wallet_address_to_string(miner.get_address())
    other_addr = wallet_address_to_string(other.get_address())
    wallets = db.get_wallets([miner.get_address(), other.get_address()])
    total_work = db.get_total_work()
    expected_work = 3 * (2**16)
    assert total_work == expected_work
    assert wallets[miner_addr] == PDN(80.0)
    assert wallets[other_addr] == PDN(20.0)


def test_check_duplicate_tx_fails():
    db = PandaniteDB()
    blockchain = BlockChain(db)
    status = blockchain.load_genesis()
    assert status == ExecutionStatus.SUCCESS
    miner = User()
    other = User()
    tx = miner.send(other, PDN(20.0))
    for i in range(2, 5):
        fee = miner.mine()
        new_block = Block()
        new_block.set_id(i)
        new_block.add_transaction(fee)
        if (i==3 or i == 4):
            new_block.add_transaction(tx)
        merkle_hash = get_merkle_hash(new_block.get_transactions())
        new_block.set_merkle_root(merkle_hash)
        new_block.set_last_block_hash(db.get_last_hash())
        new_block.set_difficulty(db.get_difficulty())
        new_block.set_timestamp(0)
        hash = new_block.get_hash()
        solution = mine_hash(hash, db.get_difficulty())
        new_block.set_nonce(solution)
        status = blockchain.add_block(new_block)
        if i == 4:
            assert status == ExecutionStatus.EXPIRED_TRANSACTION
        else:
            assert status == ExecutionStatus.SUCCESS
