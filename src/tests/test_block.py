from pandanite.core.block import Block
from pandanite.core.user import User


def test_block_json_serialization():
    a = Block()
    miner = User()
    receiver = User()
    t = miner.mine()
    a.add_transaction(t)
    # send tiny shares to receiver:
    for _ in range(0, 5):
        a.add_transaction(miner.send(receiver, 1))
    b = Block()
    b.from_json(a.to_json())
    assert a == b

def test_block_avro_serialization():
    a = Block()
    miner = User()
    receiver = User()
    t = miner.mine()
    a.add_transaction(t)
    # send tiny shares to receiver:
    for _ in range(0, 5):
        a.add_transaction(miner.send(receiver, 1))
    b = Block()
    b.from_avro(a.to_avro(include_transactions=True))
    print(a.to_json())
    print(b.to_json())
    assert a == b