from pandanite.core.blockchain import BlockChain
from pandanite.core.block import Block
from pandanite.core.user import User
from pandanite.core.executor import ExecutionStatus
from pandanite.core.crypto import mine_hash, wallet_address_to_string
from pandanite.core.transaction import get_merkle_hash
from pandanite.storage.db import PandaniteDB
from pandanite.core.helpers import PDN


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


# // TEST(check_adding_wrong_lastblock_hash_fails) {
# //     HostManager h;
# //     BlockChain* blockchain = new BlockChain(h, ledger, blocks, txdb);
# //     User miner;
# //     User other;
# //     // have miner mine the next block
# //     Transaction fee = miner.mine();
# //     vector<Transaction> transactions;
# //     Block newBlock;
# //     newBlock.setId(2);
# //     newBlock.addTransaction(fee);
# //     addMerkleHashToBlock(newBlock);
# //     newBlock.setLastBlockHash(NULL_SHA256_HASH);
# //     SHA256Hash hash = newBlock.getHash();
# //     SHA256Hash solution = mineHash(hash, newBlock.getDifficulty());
# //     newBlock.setNonce(solution);
# //     ExecutionStatus status = blockchain->addBlock(newBlock);
# //     ASSERT_EQUAL(status, INVALID_LASTBLOCK_HASH);
# //     blockchain->deleteDB();
# //     delete blockchain;
# // }

# // TEST(check_adding_two_nodes_updates_ledger) {
# //     HostManager h;
# //     BlockChain* blockchain = new BlockChain(h, ledger, blocks, txdb);
# //     User miner;

# //     // have miner mine the next block
# //     for (int i =2; i <4; i++) {
# //         Transaction fee = miner.mine();
# //         Block newBlock;
# //         newBlock.setId(i);
# //         newBlock.addTransaction(fee);
# //         addMerkleHashToBlock(newBlock);
# //         newBlock.setLastBlockHash(blockchain->getLastHash());
# //         SHA256Hash hash = newBlock.getHash();
# //         SHA256Hash solution = mineHash(hash, newBlock.getDifficulty());
# //         newBlock.setNonce(solution);
# //         ExecutionStatus status = blockchain->addBlock(newBlock);
# //         ASSERT_EQUAL(status, SUCCESS);
# //     }
# //     Ledger& ledger = blockchain->getLedger();
# //     double total = ledger.getWalletValue(miner.getAddress());
# //     ASSERT_EQUAL(total, PDN(100.0));
# //     blockchain->deleteDB();
# //     delete blockchain;
# // }

# // TEST(check_sending_transaction_updates_ledger) {
# //     HostManager h;
# //     BlockChain* blockchain = new BlockChain(h, ledger, blocks, txdb);
# //     User miner;
# //     User other;

# //     // have miner mine the next block
# //     for (int i =2; i <4; i++) {
# //         Transaction fee = miner.mine();
# //         Block newBlock;
# //         newBlock.setId(i);
# //         newBlock.addTransaction(fee);
# //         if (i==3) {
# //             Transaction t = miner.send(other, PDN(20.0));
# //             newBlock.addTransaction(t);
# //         }
# //         addMerkleHashToBlock(newBlock);
# //         newBlock.setLastBlockHash(blockchain->getLastHash());
# //         SHA256Hash hash = newBlock.getHash();
# //         SHA256Hash solution = mineHash(hash, newBlock.getDifficulty());
# //         newBlock.setNonce(solution);
# //         ExecutionStatus status = blockchain->addBlock(newBlock);
# //         ASSERT_EQUAL(status, SUCCESS);
# //     }
# //     Ledger& ledger = blockchain->getLedger();
# //     double minerTotal = ledger.getWalletValue(miner.getAddress());
# //     double otherTotal = ledger.getWalletValue(other.getAddress());
# //     Bigint totalWork = blockchain->getTotalWork();
# //     Bigint base = 2;
# //     Bigint work = base.pow(MIN_DIFFICULTY);
# //     Bigint num = 3;
# //     Bigint total = num * work;
# //     ASSERT_EQUAL(totalWork, total);
# //     ASSERT_EQUAL(minerTotal, PDN(80.0));
# //     ASSERT_EQUAL(otherTotal, PDN(20.0));
# //     blockchain->deleteDB();
# //     delete blockchain;
# // }


# // TEST(check_duplicate_tx_fails) {
# //     HostManager h;
# //     BlockChain* blockchain = new BlockChain(h, ledger, blocks, txdb);
# //     User miner;
# //     User other;

# //     Transaction t = miner.send(other, PDN(20.0));
# //     // have miner mine the next block
# //     for (int i =2; i <=4; i++) {
# //         Transaction fee = miner.mine();
# //         Block newBlock;
# //         newBlock.setId(i);
# //         newBlock.addTransaction(fee);

# //         if (i==3 || i==4) {
# //             newBlock.addTransaction(t);
# //         }
# //         addMerkleHashToBlock(newBlock);
# //         newBlock.setLastBlockHash(blockchain->getLastHash());
# //         SHA256Hash hash = newBlock.getHash();
# //         SHA256Hash solution = mineHash(hash, newBlock.getDifficulty());
# //         newBlock.setNonce(solution);
# //         ExecutionStatus status = blockchain->addBlock(newBlock);
# //         if (i==4) {
# //             ASSERT_EQUAL(status, EXPIRED_TRANSACTION);
# //         }else {
# //             ASSERT_EQUAL(status, SUCCESS);
# //         }
# //     }
# //     blockchain->deleteDB();
# //     delete blockchain;
# // }
