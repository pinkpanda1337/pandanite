import requests
from pandanite.core.block import Block
from pandanite.core.transaction import Transaction

def get_total_work(host_url: str) -> int:
    # Function logic here
    pass

def get_current_block_count(host_url: str) -> int:
    return int(requests.get(host_url + '/block_count'))

def get_name(host_url: str) -> str:
    return requests.get(host_url + '/name')

# def get_block_data(host_url: str, idx: int) -> Block:
#     # Function logic here
#     pass

# def get_mining_problem(host_url: str) -> :
#     # Function logic here
#     pass

# def send_transaction(host_url: str, t: Transaction) -> :
#     # Function logic here
#     pass

# def send_transactions(host_url: str, transaction_list: List[Transaction]) -> json:
#     # Function logic here
#     pass

# def verify_transaction(host_url: str, t: Transaction) -> json:
#     # Function logic here
#     pass

# def ping_peer(host_url: str, peer_url: str, time: int, version: str, network_name: str) -> json:
#     # Function logic here
#     pass

# def submit_block(host_url: str, b: Block) -> json:
#     # Function logic here
#     pass

# def read_raw_blocks(host_url: str, start_id: int, end_id: int) -> list[Block]:
#     # Function logic here
#     pass

# def read_raw_transactions(host_url: str) -> list[Transaction]:
#     # Function logic here
#     pass

# def read_raw_headers(host_url: str, start_id: int, end_id: int) -> list[BlockHeader]:
#     # Function logic here
#     pass