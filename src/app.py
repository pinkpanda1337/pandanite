from flask import Flask
from pandanite.core.blockchain import BlockChain
from pandanite.storage.db import PandaniteDB

app = Flask(__name__)

db = PandaniteDB()
blockchain = BlockChain(db)
if db.get_num_blocks() == 0:
    blockchain.load_genesis()


@app.route("/")
def main():
    return "<h1>Pandanite Python Node</h1>"


def name():
    pass


@app.route("/info", methods=["GET"])
def info():
    """
    Returns information regarding the blockchain state
    """
    supply = blockchain.get_supply()
    return {
        "total_work": db.get_total_work(),
        "block_count": db.get_num_blocks(),
        "supply": supply,
        "network_hash_rate": 0,
    }


@app.route("/mine_status", methods=["GET"])
def mine_status():
    """
    Returns the mining status (result) of the specified block
    args:
        block_id: int - The ID of the block to fetch mine status for
    """
    pass


@app.route("/transactions", methods=["GET"])
def transactions():
    """
    Returns the transactions currently in the mempool
    args:
        format: string - Specifies format of returned data (either "avro" or "json")
    """
    pass


@app.route("/blocks", methods=["GET"])
def blocks():
    """
    Returns the data for the block
    args:
        block_id: int - The ID of the block to fetch
        include_transactions: boolean - Whether or not to include transactions in response
        format: string - Specifies format of returned data (either "avro" or "json")
    """
    pass


@app.route("/add_block", methods=["POST"])
def add_block():
    """
    Receives a new serialized block to add to the chain in binary Avro format
    """
    pass


@app.route("/add_transaction")
def add_transaction():
    """
    Receives a new transaction to add to the mempool in JSON format
    """
    pass


@app.route("/add_peer")
def add_peer():
    pass
