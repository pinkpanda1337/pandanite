import copy
import avro.schema
import io
from avro.io import DatumWriter, DatumReader
from typing import List, Dict
from pandanite.core.crypto import (
    SHA256Hash,
    sha_256,
    string_to_sha_256,
    sha_256_to_string,
    verify_hash,
    NULL_SHA256_HASH,
)
from pandanite.core.constants import MIN_DIFFICULTY
from pandanite.core.helpers import get_current_time
from pandanite.core.transaction import Transaction


class Block:
    def __init__(self: "Block"):
        self.transactions: List[Transaction] = []
        self.id = 1
        self.timestamp = get_current_time()
        self.difficulty = MIN_DIFFICULTY
        self.merkle_root = NULL_SHA256_HASH
        self.last_block_hash = NULL_SHA256_HASH
        self.nonce = NULL_SHA256_HASH

    def from_json(self, block: Dict):
        self.nonce = string_to_sha_256(block["nonce"])
        self.merkle_root = string_to_sha_256(block["merkleRoot"])
        self.last_block_hash = string_to_sha_256(block["lastBlockHash"])
        self.id = block["id"]
        self.difficulty = block["difficulty"]
        self.timestamp = int(block["timestamp"])
        self.transactions = []
        for t in block["transactions"]:
            curr = Transaction()
            curr.from_json(t)
            self.transactions.append(curr)

    def to_json(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": str(self.timestamp),
            "difficulty": self.difficulty,
            "nonce": sha_256_to_string(self.nonce),
            "merkleRoot": sha_256_to_string(self.merkle_root),
            "lastBlockHash": sha_256_to_string(self.last_block_hash),
            "transactions": [t.to_json() for t in self.transactions],
        }
    
    def to_avro_dict(self, include_transactions=False) -> Dict:
        transactions = None
        if include_transactions:
            transactions = [tx.to_avro_dict() for tx in self.transactions]
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "nonce": bytes(self.nonce),
            "merkle_root": bytes(self.merkle_root),
            "last_block_hash": bytes(self.last_block_hash),
            "transactions": transactions
        }

    def to_avro(self, include_transactions=False) -> bytes:
        schema = avro.schema.parse(open("schema.json", "rb").read())
        writer = DatumWriter(schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(self.to_avro_dict(include_transactions=include_transactions), encoder)
        ret = bytes_writer.getvalue()
        bytes_writer.close()
        return ret
    
    def from_avro(self, data: bytes):
        schema = avro.schema.parse(open("schema.json", "rb").read())
        f = io.BytesIO(data)
        decoder = avro.io.BinaryDecoder(f)
        reader = DatumReader(schema)
        result = reader.read(decoder)
        self.nonce = result["nonce"]
        self.merkle_root = result["merkle_root"]
        self.last_block_hash = result["last_block_hash"]
        self.id = result["id"]
        self.difficulty = result["difficulty"]
        self.timestamp = result["timestamp"]
        self.transactions = []
        for t in result["transactions"]:
            curr = Transaction()
            curr.from_avro_dict(t)
            self.transactions.append(curr)

    def copy(self) -> "Block":
        return copy.deepcopy(self)

    def add_transaction(self, t: Transaction):
        self.transactions.append(t.copy())

    def set_nonce(self, s: SHA256Hash):
        self.nonce = s

    def set_merkle_root(self, s: SHA256Hash):
        self.merkle_root = s

    def set_timestamp(self, t: int):
        self.timestamp = t

    def set_id(self, id: int):
        self.id = id

    def set_difficulty(self, d: int):
        self.difficulty = d

    def get_hash(self) -> SHA256Hash:
        difficulty = bytearray(self.difficulty.to_bytes(4))
        timestamp = bytearray(self.timestamp.to_bytes(8))
        difficulty.reverse()
        timestamp.reverse()
        return sha_256(
            bytes(self.merkle_root + self.last_block_hash + difficulty + timestamp)
        )

    def get_nonce(self) -> SHA256Hash:
        return self.nonce

    def get_merkle_root(self) -> SHA256Hash:
        return self.merkle_root

    def get_last_block_hash(self) -> SHA256Hash:
        return self.last_block_hash

    def set_last_block_hash(self, hash: SHA256Hash):
        self.last_block_hash = hash

    def get_timestamp(self) -> int:
        return self.timestamp

    def get_difficulty(self) -> int:
        return self.difficulty

    def get_transactions(self) -> List[Transaction]:
        return self.transactions

    def get_id(self) -> int:
        return self.id

    def verify_nonce(self) -> bool:
        target = self.get_hash()
        return verify_hash(target, self.nonce, self.difficulty)

    def __eq__(self, other):
        if isinstance(other, Block):
            return (
                self.id == other.id
                and self.timestamp == other.timestamp
                and self.difficulty == other.difficulty
                and self.merkle_root == other.merkle_root
                and self.last_block_hash == other.last_block_hash
                and self.nonce == other.nonce
                and len(self.transactions) == len(other.transactions)
                and self.transactions == other.transactions
            )

        return False
