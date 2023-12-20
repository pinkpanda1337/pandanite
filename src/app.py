import random
import string
from flask import Flask, request
from pandanite.core.blockchain import BlockChain
from pandanite.storage.db import PandaniteDB

app = Flask(__name__)

name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
db = PandaniteDB()
blockchain = BlockChain(db)
if db.get_num_blocks() == 0:
    blockchain.load_genesis()


@app.route("/")
def main():
    return "<h1>Pandanite Python Node</h1>"

@app.route("/name")
def name():
    return name


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
    args = request.args
    
    block_id = args.get('block_id', default=None, type=int)
    format = args.get('format', default='json', type=str)
    include_transactions = args.get('include_transactions', default=False, type=bool)
    
    if not block_id:
        return "No block id specified"
    
    block = db.get_block(block_id)
    
    if format == 'json':
        return block.to_json()
    elif format == 'avro':
        return block.to_avro(include_transactions=include_transactions)
    else:
        return "Unsupported format requested"
    


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
