import json
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
    print(a.to_json())
    print(b.to_json())
    assert a == b

# TEST(check_block_struct_serialization) {
#     Block a
#     User miner;
#     User receiver;
#     Transaction t = miner.mine();
#     a.addTransaction(t);
#     // send tiny shares to receiver:
#     for(int i = 0; i < 5; i++) {
#         a.addTransaction(miner.send(receiver, 1));
#     }
#     BlockHeader d = a.serialize();
#     Block b(d, a.getTransactions());
#     ASSERT_TRUE(a==b);
# }

# TEST(check_block_network_serialization) {
#     Block a;
#     User miner;
#     User receiver;
#     Transaction t = miner.mine();
#     a.addTransaction(t);
#     // send tiny shares to receiver:
#     for(int i = 0; i < 5; i++) {
#         a.addTransaction(miner.send(receiver, 1));
#     }
#     BlockHeader d = a.serialize();
    
#     char buf[BLOCKHEADER_BUFFER_SIZE];
#     blockHeaderToBuffer(d, buf);

#     BlockHeader c = blockHeaderFromBuffer(buf);
#     vector<Transaction> tx = a.getTransactions();

#     Block check = Block(c, tx);

#     ASSERT_TRUE(check == a);

# }


# def test_block_hash_consistency():
#     A = "{\"difficulty\":25,\"id\":4780,\"lastBlockHash\":\"408B78E303A2130FCB5903887467286CE7D320D1080CBE8D3DE8198053B43AD6\",\"merkleRoot\":\"6B6431D62D1095CBB4D20F10168C1B39754D34997C528C3CE92AE68BB0BDE2CB\",\"nonce\":\"4566676B61BAB77BF15A658D6974592194EA453E7EBA975E74B2AD81056B094A\",\"timestamp\":\"1637858747\",\"transactions\":[{\"amount\":500000,\"fee\":0,\"from\":\"\",\"id\":4780,\"nonce\":\"92zgZDU7\",\"timestamp\":\"1637858747\",\"to\":\"00B28B48A25AFFBF80122963F2CB7957571AE2612B0126BF0D\"}]}";
#     B = "{\"difficulty\":25,\"id\":4780,\"lastBlockHash\":\"408B78E303A2130FCB5903887467286CE7D320D1080CBE8D3DE8198053B43AD6\",\"merkleRoot\":\"EB334D4DA3054E7463210F90EC2D3A0B33105F69AC099BADB863DEC97C7A347F\",\"nonce\":\"236278BC9D738823F361906FBD398DBEB7E8EB1C1E18FAD4099477BD3FBDBD62\",\"timestamp\":\"1637858713\",\"transactions\":[{\"amount\":500000,\"fee\":0,\"from\":\"\",\"id\":4780,\"nonce\":\"I2iyrN6f\",\"timestamp\":\"1637858713\",\"to\":\"00D1B6AF7C92153D2B3BD643B53FF4311746FCF889BE8F9078\"}]}";
#     a = Block()
#     b = Block()
#     a.load_json(json.loads(A));
#     b.load_json(json.loads(B));
#     assert a.get_hash() != b.get_hash();
