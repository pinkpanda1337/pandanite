from flask import Flask

app = Flask(__name__)

@app.route("/")
def main():
    return "<h1>Pandanite Python Node</h1>"

def name():
    pass

@app.route("/total_work")
def total_work():
    pass

@app.route("/block_count")
def block_count():
    pass

@app.route("/logs")
def logs():
    pass

@app.route("/tx_json")
def tx_json():
    pass

@app.route("/mine_status")
def mine_status():
    pass

@app.route("/ledger")
def ledger():
    pass

@app.route("/wallet_transactions")
def wallet_transactions():
    pass

@app.route("/supply")
def supply():
    pass

@app.route("/getnetworkhashrate")
def getnetworkhashrate():
    pass

@app.route("/add_peer")
def add_peer():
    pass

@app.route("/submit")
def submit():
    pass

@app.route("/gettx")
def gettx():
    pass

@app.route("/sync")
def sync():
    pass

@app.route("/block_headers")
def block_headers():
    pass

@app.route("/synctx")
def synctx():
    pass

@app.route("/add_transaction_json")
def add_transaction_json():
    pass
