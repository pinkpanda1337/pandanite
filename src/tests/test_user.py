from pandanite.core.user import User
from pandanite.core.block import Block
from pandanite.core.helpers import PDN


def test_check_signature():
    b = Block()
    miner = User()
    receiver = User()
    t = miner.send(receiver, PDN(30.0))
    assert t.signature_valid()
