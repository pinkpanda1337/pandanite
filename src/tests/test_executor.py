from pandanite.core.block import Block
from pandanite.core.user import User
from pandanite.storage.db import PandaniteDB
from pandanite.core.transaction import Transaction
from pandanite.core.executor import execute_block, ExecutionStatus
from pandanite.core.helpers import PDN
from pandanite.core.crypto import wallet_address_to_string, public_key_to_string


def test_checks_invalid_mining_fee():
    b = Block()
    miner = User()

    # add incorrect mining fee to block
    t = miner.mine()
    t.set_amount(PDN(100.0))
    b.add_transaction(t)

    db = PandaniteDB()
    wallets = {}
    status, wallets = execute_block(db, wallets, b, PDN(50.0))
    assert status == ExecutionStatus.INCORRECT_MINING_FEE


def test_checks_duplicate_mining_fee():
    b = Block()
    miner = User()
    # add mining transaction twice
    t1 = miner.mine()
    t2 = miner.mine()
    b.add_transaction(t1)
    b.add_transaction(t2)

    db = PandaniteDB()
    wallets = {}
    status, _ = execute_block(db, wallets, b, PDN(50.0))
    assert status == ExecutionStatus.EXTRA_MINING_FEE


def test_checks_missing_mining_fee():
    b = Block()
    db = PandaniteDB()
    wallets = {}
    status, _ = execute_block(db, wallets, b, PDN(50.0))
    assert status == ExecutionStatus.NO_MINING_FEE


def test_check_valid_send():
    b = Block()
    miner = User()
    receiver = User()
    b.set_id(2)
    t = miner.mine()
    b.add_transaction(t)
    t2 = miner.send(receiver, PDN(30.0))
    b.add_transaction(t2)

    db = PandaniteDB()
    wallets = {}
    status, out = execute_block(db, wallets, b, PDN(50.0))
    assert status == ExecutionStatus.SUCCESS

    a_key = wallet_address_to_string(miner.get_address())
    b_key = wallet_address_to_string(receiver.get_address())
    assert out.get(a_key) == PDN(20.0)
    assert out.get(b_key) == PDN(30.0)


def test_check_sender_tampering():
    b = Block()
    miner = User()
    receiver = User()
    b.set_id(2)
    t = miner.mine()
    b.add_transaction(t)
    t2 = miner.send(receiver, PDN(30))
    b.add_transaction(t2)

    db = PandaniteDB()
    wallets = {}
    status, out = execute_block(db, wallets, b, PDN(50.0))
    assert status == ExecutionStatus.SUCCESS

    a_key = wallet_address_to_string(miner.get_address())
    b_key = wallet_address_to_string(receiver.get_address())
    assert out.get(a_key) == PDN(20.0)

    c = Block()
    c.set_id(12000)
    t21 = receiver.mine()
    c.add_transaction(t21)
    t22x = miner.send(miner, PDN(30))

    # tamper t22 so that the from wallet is the receiver wallet
    tmp = t22x.to_json()
    tmp["signingKey"] = public_key_to_string(receiver.get_public_key())
    t22 = Transaction()
    t22.from_json(tmp)
    t22.sign(miner.get_private_key())
    c.add_transaction(t22)
    db = PandaniteDB()
    wallets = {}
    status, out = execute_block(db, wallets, c, PDN(50.0))
    assert status == ExecutionStatus.INVALID_SIGNATURE


def test_check_low_balance():
    b = Block()
    miner = User()
    receiver = User()
    b.set_id(2)
    t = miner.mine()
    b.add_transaction(t)

    t2 = miner.send(receiver, PDN(100.0))
    b.add_transaction(t2)
    db = PandaniteDB()
    wallets = {}
    status, out = execute_block(db, wallets, b, PDN(50.0))
    assert status == ExecutionStatus.BALANCE_TOO_LOW


def test_check_overflow():
    b = Block()
    miner = User()
    receiver = User()
    b.set_id(2)
    t = miner.mine()
    b.add_transaction(t)

    t2 = miner.send(receiver, 18446744073709551615)
    b.add_transaction(t2)
    db = PandaniteDB()
    wallets = {}
    status, out = execute_block(db, wallets, b, PDN(50.0))
    assert status == ExecutionStatus.BALANCE_TOO_LOW


def test_check_miner_fee():
    b = Block()
    miner = User()
    receiver = User()
    other = User()
    b.set_id(2)

    t = miner.mine()
    t2 = miner.send(receiver, PDN(20))
    b.add_transaction(t)
    b.add_transaction(t2)

    db = PandaniteDB()
    wallets = {}
    status, out = execute_block(db, wallets, b, PDN(50.0))
    assert status == ExecutionStatus.SUCCESS

    b2 = Block()
    b2.set_id(3)
    t3 = miner.mine()
    t4 = receiver.send(other, PDN(1), PDN(10))
    b2.add_transaction(t3)
    b2.add_transaction(t4)
    status, out = execute_block(db, wallets, b2, PDN(50.0))
    assert status == ExecutionStatus.SUCCESS
    assert out.get(wallet_address_to_string(other.get_address()), PDN(1))
    assert out.get(wallet_address_to_string(receiver.get_address()), PDN(9))
    assert out.get(wallet_address_to_string(miner.get_address()), PDN(90))


def test_check_bad_signature():
    b = Block()
    miner = User()
    receiver = User()
    b.set_id(2)
    t = miner.mine()
    b.add_transaction(t)
    t2 = miner.send(receiver, PDN(20.0))

    # sign with random sig
    foo = User()
    t2.sign(foo.get_private_key())
    b.add_transaction(t2)

    db = PandaniteDB()
    wallets = {}
    status, out = execute_block(db, wallets, b, PDN(50.0))

    assert status == ExecutionStatus.INVALID_SIGNATURE
