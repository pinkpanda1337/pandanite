import json
from pandanite.core.helpers import PDN
from pandanite.core.user import User
from pandanite.core.transaction import Transaction


def check_transaction_json_serialization():
    miner = User()
    receiver = User()

    t = miner.mine()
    t2 = miner.send(receiver, PDN(30.0))

    assert t2.signature_valid()

    # test the send transaction
    ts = t2.get_timestamp()
    serialized = json.dumps(t2.to_json())
    parsed = json.loads(serialized)
    deserialized = Transaction()
    deserialized.from_json(parsed)

    assert deserialized.signature_valid()
    assert t2 == deserialized
    assert t2.hash_contents() == deserialized.hash_contents()
    assert ts == deserialized.get_timestamp()

    # test mining transaction
    serialized = json.dumps(t.to_json())

    parsed = json.loads(serialized)
    deserialized = Transaction()
    deserialized.from_json(parsed)
    ts = t.get_timestamp()
    assert t.hash_contents() == deserialized.hash_contents()
    assert t == deserialized
    assert ts, deserialized.get_timestamp()
