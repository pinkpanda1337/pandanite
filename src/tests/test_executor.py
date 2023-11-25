from pandanite.core.block import Block
from pandanite.core.user import User
from pandanite.storage.db import PandaniteDB
from pandanite.core.transaction import Transaction
from pandanite.core.executor import execute_block, ExecutionStatus
from pandanite.core.helpers import PDN

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


# TEST(checks_duplicate_mining_fee) {
#     Block b
#     Ledger ledger
#     ledger.init("./test-data/tmpdb")
#     TransactionStore txdb
#     txdb.init("./test-data/tmpdb2")
#     LedgerState deltas
#     ExecutionStatus status
#     User miner
#     // add mining transaction twice
#     Transaction t1 = miner.mine()
#     Transaction t2 = miner.mine()
#     b.addTransaction(t1)
#     b.addTransaction(t2)

#     status = Executor::ExecuteBlock(b, ledger, txdb, deltas, PDN(50))
#     ledger.closeDB();
#     ledger.deleteDB();
#     txdb.closeDB();
#     txdb.deleteDB();
#     ASSERT_EQUAL(status, EXTRA_MINING_FEE);     
# }

# TEST(checks_missing_mining_fee) {
#     Block b;
#     Ledger ledger;
#     ledger.init("./test-data/tmpdb");
#     TransactionStore txdb;
#     txdb.init("./test-data/tmpdb2");
#     LedgerState deltas;
#     ExecutionStatus status;
#     status = Executor::ExecuteBlock(b, ledger, txdb, deltas, PDN(50));
#     ledger.closeDB();
#     ledger.deleteDB();   
#     txdb.closeDB();
#     txdb.deleteDB();
#     ASSERT_EQUAL(status, NO_MINING_FEE);  
# }

# TEST(check_valid_send) {
#     Block b;

#     Ledger ledger;
#     ledger.init("./test-data/tmpdb");
#     TransactionStore txdb;
#     txdb.init("./test-data/tmpdb2");
#     LedgerState deltas;
#     ExecutionStatus status;

#     User miner;
#     User receiver;
#     b.setId(2);
#     Transaction t = miner.mine();
#     b.addTransaction(t);
#     Transaction t2 = miner.send(receiver, PDN(30));
#     b.addTransaction(t2);

#     status = Executor::ExecuteBlock(b, ledger, txdb, deltas, PDN(50));
#     ASSERT_EQUAL(status, SUCCESS);

#     PublicWalletAddress aKey = miner.getAddress(); 
#     PublicWalletAddress bKey = receiver.getAddress();
#     ASSERT_EQUAL(ledger.getWalletValue(aKey), PDN(20.0))
#     ASSERT_EQUAL(ledger.getWalletValue(bKey), PDN(30.0))
#     ledger.closeDB();
#     ledger.deleteDB();
#     txdb.closeDB();
#     txdb.deleteDB();
# }

# TEST(check_wallet_tampering) {
#     Block b;

#     Ledger ledger;
#     ledger.init("./test-data/tmpdb");
#     TransactionStore txdb;
#     txdb.init("./test-data/tmpdb2");
#     LedgerState deltas;
#     ExecutionStatus status;

#     User miner;
#     User receiver;
#     b.setId(2);
#     Transaction t = miner.mine();
#     b.addTransaction(t);
#     Transaction t2 = miner.send(receiver, PDN(30));
#     b.addTransaction(t2);

#     status = Executor::ExecuteBlock(b, ledger, txdb, deltas, PDN(50));
#     PublicWalletAddress minerWallet = miner.getAddress(); 
#     PublicWalletAddress receiverWallet = receiver.getAddress();

#     ASSERT_EQUAL(status, SUCCESS);
#     ASSERT_EQUAL(ledger.getWalletValue(minerWallet), PDN(20.0)) // MINER only has 20PDN

#     Block c;
#     c.setId(12000);
#     Transaction t21 = receiver.mine();
#     c.addTransaction(t21);
#     Transaction t22x = miner.send(miner, PDN(30)); // try to send 30 PDN from miner to itself
    
#     // tamper t22 so that the from wallet is the receiver wallet
#     json tmp = t22x.toJson();
#     tmp["from"] = walletAddressToString(receiverWallet);
#     Transaction t22 (tmp);
#     t22.sign(miner.getPublicKey(), miner.getPrivateKey());
#     c.addTransaction(t22);
#     LedgerState deltas2;
#     status = Executor::ExecuteBlock(c, ledger, txdb, deltas2, PDN(50));
#     ASSERT_EQUAL(status, WALLET_SIGNATURE_MISMATCH);
#     ledger.closeDB();
#     ledger.deleteDB();
#     txdb.closeDB();
#     txdb.deleteDB();
# }


# TEST(check_low_balance) {
#     Block b;

#     Ledger ledger;
#     ledger.init("./test-data/tmpdb");
#     TransactionStore txdb;
#     txdb.init("./test-data/tmpdb2");
#     LedgerState deltas;
#     ExecutionStatus status;
    
#     User miner;
#     User receiver;
#     b.setId(2);
#     Transaction t = miner.mine();
#     b.addTransaction(t);

#     Transaction t2 = miner.send(receiver, PDN(100.0));
#     b.addTransaction(t2);

#     status = Executor::ExecuteBlock(b, ledger, txdb, deltas, PDN(50));
#     ledger.closeDB();
#     ledger.deleteDB();  
#     txdb.closeDB();
#     txdb.deleteDB();
#     ASSERT_EQUAL(status, BALANCE_TOO_LOW);   
# }

# TEST(check_overflow) {
#     Block b;

#     Ledger ledger;
#     ledger.init("./test-data/tmpdb");
#     TransactionStore txdb;
#     txdb.init("./test-data/tmpdb2");
#     LedgerState deltas;
#     ExecutionStatus status;
    
#     User miner;
#     User receiver;
#     b.setId(2);
#     Transaction t = miner.mine();
#     b.addTransaction(t);

#     Transaction t2 = miner.send(receiver, 18446744073709551615);
#     b.addTransaction(t2);

#     status = Executor::ExecuteBlock(b, ledger, txdb, deltas, PDN(50));
#     ledger.closeDB();
#     ledger.deleteDB();  
#     txdb.closeDB();
#     txdb.deleteDB();
#     ASSERT_EQUAL(status, BALANCE_TOO_LOW);   
# }


# TEST(check_miner_fee) {
#     Block b;

#     Ledger ledger;
#     ledger.init("./test-data/tmpdb");
#     TransactionStore txdb;
#     txdb.init("./test-data/tmpdb2");
#     LedgerState deltas;
#     ExecutionStatus status;
#     b.setId(2);
#     User miner;
#     User receiver;
#     User other;

#     // add mining transaction twice
#     Transaction t = miner.mine();
#     Transaction t2 = miner.send(receiver, PDN(20));
#     miner.signTransaction(t2);
#     b.addTransaction(t);
#     b.addTransaction(t2);
#     status = Executor::ExecuteBlock(b, ledger, txdb, deltas, PDN(50));
#     ASSERT_EQUAL(status, SUCCESS);
    
#     Block b2;
#     b2.setId(3);
#     Transaction t3 = miner.mine();
#     Transaction t4 = receiver.send(other, PDN(1));
#     t4.setTransactionFee(PDN(10));
#     receiver.signTransaction(t4);
#     b2.addTransaction(t3);
#     b2.addTransaction(t4);
#     status = Executor::ExecuteBlock(b2, ledger, txdb, deltas, PDN(50));
#     ASSERT_EQUAL(status, SUCCESS);
#     ASSERT_EQUAL(ledger.getWalletValue(other.getAddress()), PDN(1)); 
#     ASSERT_EQUAL(ledger.getWalletValue(receiver.getAddress()), PDN(9)); 
#     ASSERT_EQUAL(ledger.getWalletValue(miner.getAddress()), PDN(90)); 
#     ledger.closeDB();
#     ledger.deleteDB();
#     txdb.closeDB();
#     txdb.deleteDB();
# }



# TEST(check_bad_signature) {
#     Block b;
#     Ledger ledger;
#     ledger.init("./test-data/tmpdb");
#     TransactionStore txdb;
#     txdb.init("./test-data/tmpdb2");
#     LedgerState deltas;
#     ExecutionStatus status;
    
#     User miner;
#     User receiver;
#     b.setId(2);
#     Transaction t = miner.mine();
#     b.addTransaction(t);
#     Transaction t2 = miner.send(receiver, PDN(20.0));

#     // sign with random sig
#     User foo;
#     t2.sign(foo.getPublicKey(), foo.getPrivateKey());
#     b.addTransaction(t2);

#     status = Executor::ExecuteBlock(b, ledger, txdb, deltas, PDN(50));

#     ledger.closeDB();
#     ledger.deleteDB();
#     txdb.closeDB();
#     txdb.deleteDB();
#     ASSERT_EQUAL(status, INVALID_SIGNATURE);
# }