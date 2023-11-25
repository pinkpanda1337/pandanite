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


# TEST(check_transaction_struct_serialization) {

#     User miner;
#     User receiver;

#     Transaction t = miner.mine();
#     Transaction t2 = miner.send(receiver, PDN(30.0));

#     ASSERT_TRUE(t2.signatureValid());

#     // test the send transaction
#     uint64_t ts = t2.getTimestamp();
#     TransactionInfo serialized = t2.serialize();
#     Transaction deserialized = Transaction(serialized);

#     ASSERT_TRUE(deserialized.signatureValid());
#     ASSERT_TRUE(t2 == deserialized);
#     ASSERT_EQUAL(ts, deserialized.getTimestamp());

#     // test mining transaction
#     serialized = t.serialize();
#     deserialized = Transaction(serialized);
#     ts = t.getTimestamp();
#     ASSERT_TRUE(t.hashContents() == deserialized.hashContents());
#     ASSERT_TRUE(t == deserialized);
#     ASSERT_EQUAL(ts, deserialized.getTimestamp());
# }

# TEST(check_transaction_copy) {

#     User miner;
#     User receiver;

#     Transaction t = miner.mine();
#     Transaction t2 = miner.send(receiver, PDN(30.0));

#     Transaction a = t;
#     Transaction b = t2;
#     ASSERT_TRUE(a==t);
#     ASSERT_TRUE(b==t2);
# }


# TEST(check_transaction_network_serialization) {
#     User miner;
#     User receiver;

#     Transaction a = miner.mine();
#     Transaction b = miner.send(receiver, PDN(30.0));

#     TransactionInfo t1 = a.serialize();
#     TransactionInfo t2 = b.serialize();

#     char buf1[TRANSACTIONINFO_BUFFER_SIZE];
#     char buf2[TRANSACTIONINFO_BUFFER_SIZE];

#     transactionInfoToBuffer(t1, buf1);
#     transactionInfoToBuffer(t2, buf2);

#     Transaction a2 = Transaction(transactionInfoFromBuffer(buf1));
#     Transaction b2 = Transaction(transactionInfoFromBuffer(buf2));

#     ASSERT_TRUE(a == a2);
#     ASSERT_TRUE(b == b2);
# }
