import copy
import avro.schema
import io
from avro.io import DatumWriter, DatumReader
import ed25519
import hashlib
from typing import Dict, List, Optional, Deque, cast
from collections import deque
from pandanite.core.crypto import (
    PublicWalletAddress,
    PublicKey,
    PrivateKey,
    SHA256Hash,
    NULL_SHA256_HASH,
    NULL_ADDRESS,
    TransactionSignature,
    sha_256_to_string,
    wallet_address_to_string,
    string_to_wallet_address,
    string_to_signature,
    string_to_public_key,
    public_key_to_string,
    signature_to_string,
    sign_with_private_key_bytes,
    check_signature_bytes,
    concat_hashes,
    wallet_address_from_public_key,
)
from pandanite.core.common import TransactionAmount


class Transaction:
    def __init__(
        self,
        to_wallet: PublicWalletAddress = NULL_ADDRESS,
        amount: Optional[TransactionAmount] = None,
        signing_key: Optional[PublicKey] = None,
        fee: TransactionAmount = 0,
        timestamp: int = 0,
    ):
        self.signature: Optional[TransactionSignature] = None
        self.signing_key: PublicKey = copy.deepcopy(signing_key)
        self.timestamp = timestamp
        self.to: PublicWalletAddress = copy.deepcopy(to_wallet)
        self.amount: TransactionAmount = amount if amount else 0
        self.fee: TransactionAmount = fee

        # This is just used for genesis block transactions which are missing signing key
        self._wallet: Optional[PublicWalletAddress] = None

    def set_wallet_override(self, override: PublicWalletAddress):
        self._wallet = override

    def from_json(self, data: Dict):
        self.timestamp = int(data["timestamp"])
        self.to = string_to_wallet_address(data["to"])
        self.fee = data["fee"]
        self.amount = data["amount"]
        if "signingKey" in data.keys():
            self.signature = string_to_signature(data["signature"])
            self.signing_key = string_to_public_key(data["signingKey"])

        if "from" in data.keys() and len(data["from"]) != 0:
            self.set_wallet_override(string_to_wallet_address(data["from"]))

    def get_id(self):
        return sha_256_to_string(self.hash_contents())

    def to_json(self) -> Dict:
        result = {}
        result["to"] = wallet_address_to_string(self.to)
        result["amount"] = self.amount
        result["timestamp"] = str(self.timestamp)
        result["fee"] = self.fee
        result["txid"] = sha_256_to_string(self.hash_contents())
        if not self.is_fee():
            result["signingKey"] = public_key_to_string(self.signing_key)
            result["signature"] = signature_to_string(self.signature)
        return result

    def to_avro_dict(self) -> Dict:
        result = {}
        result["to"] = bytes(self.to)
        result["amount"] = self.amount
        result["timestamp"] = self.timestamp
        result["fee"] = self.fee
        if not self.is_fee():
            result["signing_key"] = self.signing_key.to_bytes()
            result["signature"] = bytes(self.signature)
        return result

    def to_avro(self, include_transactions=False) -> bytes:
        schema = avro.schema.parse(open("schema.json", "rb").read())
        writer = DatumWriter(schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(self.to_avro_dict(), encoder)
        ret = bytes_writer.getvalue()
        bytes_writer.close()
        return ret

    def from_avro(self, data: bytes):
        schema = avro.schema.parse(open("schema.json", "rb").read())
        f = io.BytesIO(data)
        decoder = avro.io.BinaryDecoder(f)
        reader = DatumReader(schema)
        result = reader.read(decoder)
        self.from_avro_dict(result)

    def from_avro_dict(self, result: dict):
        self.timestamp = result["timestamp"]
        self.to = result["to"]
        self.fee = result["fee"]
        self.amount = result["amount"]
        if result.get("signing_key"):
            self.signature = result["signature"]
            self.signing_key = ed25519.keys.VerifyingKey(result["signing_key"])

    def copy(self) -> "Transaction":
        return copy.deepcopy(self)

    def set_transaction_fee(self, amount: TransactionAmount):
        self.fee = amount

    def get_transaction_fee(self) -> TransactionAmount:
        return self.fee

    def get_sender(self) -> PublicWalletAddress:
        return wallet_address_from_public_key(self.signing_key)

    def set_amount(self, amt: TransactionAmount):
        self.amount = amt

    def get_signing_key(self) -> PublicKey:
        return self.signing_key

    def get_amount(self) -> TransactionAmount:
        return self.amount

    def get_fee(self) -> TransactionAmount:
        return self.fee

    def get_recepient(self) -> PublicWalletAddress:
        return self.to

    def set_timestamp(self, t: int):
        self.timestamp = t

    def get_timestamp(self) -> int:
        return self.timestamp

    def get_hash(self) -> SHA256Hash:
        ctx = hashlib.sha256()
        ctx.update(self.hash_contents())
        if not self.is_fee():
            if not self.signature:
                raise Exception("Tried to get hash of unsigned transaction")
            ctx.update(self.signature)
        return bytearray(ctx.digest())

    def hash_contents(self) -> SHA256Hash:
        ctx = hashlib.sha256()
        fee = bytearray(self.fee.to_bytes(8))
        amount = bytearray(self.amount.to_bytes(8))
        timestamp = bytearray(self.timestamp.to_bytes(8))
        fee.reverse()
        amount.reverse()
        timestamp.reverse()

        ctx.update(self.to)
        if not self.is_fee():
            ctx.update(self._wallet or wallet_address_from_public_key(self.signing_key))
        ctx.update(fee)
        ctx.update(amount)
        ctx.update(timestamp)
        return bytearray(ctx.digest())

    def sign(self, private_key: PrivateKey):
        hash = self.hash_contents()
        signature = sign_with_private_key_bytes(bytes(hash), private_key)
        self.signature = signature

    def get_signature(self) -> TransactionSignature:
        if not self.signature:
            raise Exception("Tried to read signature of unsigned transaction")
        return self.signature

    def signature_valid(self) -> bool:
        if self.is_fee():
            return True
        if not self.signature:
            raise Exception("No signature for transaction")
        hash = self.hash_contents()
        return check_signature_bytes(bytes(hash), self.signature, self.signing_key)

    def is_fee(self) -> bool:
        return self.signing_key == None

    def __eq__(self, other):
        if isinstance(other, Transaction):
            ret = (
                self.signature == other.signature
                and self.timestamp == other.timestamp
                and self.to == other.to
                and self.signing_key == other.signing_key
                and self.amount == other.amount
                and self.fee == other.fee
                and self.is_fee() == other.is_fee()
            )
            return ret
        return False


# merkle proofs
class Node:
    def __init__(self, hash: SHA256Hash):
        self.hash = hash
        self.parent: Optional[Node] = None
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None


def get_merkle_hash(items: List[Transaction]) -> SHA256Hash:
    # NOTE: This is not actually building a Merkle Tree
    # it is copied over from and consistent with the original C++ code
    items.sort(key=lambda a: sha_256_to_string(a.get_hash()), reverse=True)
    q: Deque[Node] = deque()

    for item in items:
        h = item.get_hash()
        node = Node(h)
        q.append(node)

    if len(q) % 2 == 1:
        repeat = Node(q[-1].hash)
        q.append(repeat)

    while len(q) > 1:
        a: Node = q.popleft()
        b: Node = q.popleft()
        root = Node(NULL_SHA256_HASH)
        root.left = a
        root.right = b
        a.parent = root
        b.parent = root
        root.hash = concat_hashes(a.hash, b.hash)
        q.append(root)

    return q[0].hash
