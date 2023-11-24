from typing import Dict, List, Optional, Deque
from collections import deque
import copy
import ed25519
from pandanite.core.crypto import (
    PublicWalletAddress,
    PublicKey,
    PrivateKey,
    SHA256Hash,
    NULL_SHA256_HASH,
    NULL_ADDRESS,
    TransactionSignature,
    sha_256,
    sha_256_to_string,
    wallet_address_to_string,
    string_to_wallet_address,
    string_to_signature,
    string_to_public_key,
    public_key_to_string,
    signature_to_string,
    sign_with_private_key_bytes,
    check_signature_bytes,
    concat_hashes
)
from pandanite.core.common import TransactionAmount


class TransactionInfo:
    def __init__(
        self,
        signature: bytes,
        signing_key: bytes,
        timestamp: int,
        to: PublicWalletAddress,
        from_address: PublicWalletAddress,
        amount: TransactionAmount,
        fee: TransactionAmount,
        is_transaction_fee: bool,
    ):
        self.signature = signature  # This should be a 64-byte array
        self.signing_key = signing_key  # This should be a 32-byte array
        self.timestamp = timestamp
        self.to = to
        self.from_address = from_address
        self.amount = amount
        self.fee = fee
        self.is_transaction_fee = is_transaction_fee


TRANSACTIONINFO_BUFFER_SIZE = 149


# def transaction_info_from_buffer(buffer: bytearray) -> TransactionInfo:
#     pass


# def transaction_info_to_buffer(t: TransactionInfo, buffer: bytearray):
#     pass


class Transaction:
    def __init__(
        self,
        to_wallet: PublicWalletAddress = NULL_ADDRESS,
        amount: Optional[TransactionAmount] = None,
        from_wallet: Optional[PublicWalletAddress] = None,
        signing_key: Optional[PublicKey] = None,
        fee: TransactionAmount = 0,
        timestamp: int = 0,
    ):
        self.signature: Optional[TransactionSignature] = None
        self.signing_key: PublicKey = signing_key
        self.timestamp = timestamp
        self.to: PublicWalletAddress = to_wallet
        self.from_: Optional[PublicWalletAddress] = from_wallet
        self.amount: TransactionAmount = amount if amount else 0
        self.fee: TransactionAmount = fee
        self.is_transaction_fee: bool = from_wallet == None


    # def from_transaction_info(self, t: TransactionInfo):
    #     self.signature = t.signature
    #     self.signing_key = ed25519.keys.SigningKey(t.signing_key)
    #     self.timestamp = t.timestamp
    #     self.to = t.to
    #     self.from_ = t.from_address
    #     self.amount = t.amount
    #     self.fee = t.fee
    #     self.is_transaction_fee = t.is_transaction_fee

    def from_json(self, data: Dict):
        self.timestamp = int(data["timestamp"])
        self.to = string_to_wallet_address(data["to"])
        self.fee = data["fee"]
        if data["from"] == "":
            self.amount = data["amount"]
            self.is_transaction_fee = True
        else:
            self.from_ = string_to_wallet_address(data["from"])
            self.signature = string_to_signature(data["signature"])
            self.amount = data["amount"]
            self.is_transaction_fee = False
            self.signing_key = string_to_public_key(data["signingKey"])

    # def serialize(self) -> TransactionInfo:
    #     return TransactionInfo(
    #         self.signature,
    #         self.signing_key.to_bytes(),
    #         self.timestamp,
    #         self.to,
    #         self.from_,
    #         self.amount,
    #         self.fee,
    #         self.is_transaction_fee,
    #     )

    def to_json(self):
        result = {}
        result["to"] = wallet_address_to_string(self.to)
        result["amount"] = self.amount
        result["timestamp"] = str(self.timestamp)
        result["fee"] = self.fee
        if not self.is_transaction_fee:
            result["txid"] = sha_256_to_string(self.hash_contents())
            result["from"] = wallet_address_to_string(self.from_)
            result["signingKey"] = public_key_to_string(self.signing_key)
            result["signature"] = signature_to_string(self.signature)
        else:
            result["txid"] = sha_256_to_string(self.hash_contents())
            result["from"] = ""
        return result

    def copy(self) -> 'Transaction':
        return copy.deepcopy(self)

    def sign(self, pub_key: PublicKey, signing_key: PrivateKey):
        hash = self.hash_contents()
        signature = sign_with_private_key_bytes(hash, signing_key)
        self.signature = signature

    def set_transaction_fee(self, amount: TransactionAmount):
        self.fee = amount

    def get_transaction_fee(self) -> TransactionAmount:
        return self.fee

    def set_amount(self, amt: TransactionAmount):
        self.amount = amt

    def get_signing_key(self) -> PublicKey:
        return self.signing_key

    def from_wallet(self) -> PublicWalletAddress:
        if not self.from_:
            raise Exception('Read from wallet when no from wallet exists')
        return self.from_

    def to_wallet(self) -> PublicWalletAddress:
        return self.to

    def get_amount(self) -> TransactionAmount:
        return self.amount

    def get_fee(self) -> TransactionAmount:
        return self.fee

    def set_timestamp(self, t: int):
        self.timestamp = t

    def get_timestamp(self) -> int:
        return self.timestamp

    def get_hash(self) -> SHA256Hash:
        hash = self.hash_contents()
        if not self.is_transaction_fee:
            if not self.signature:
                raise Exception('Tried to get hash of unsigned transaction')
            hash += self.signature
        return sha_256(hash)

    def hash_contents(self) -> SHA256Hash:
        buf = bytearray()
        buf += self.to
        if not self.is_transaction_fee:
            if not self.from_:
                raise Exception('Missing sender')
            buf += self.from_
        buf += (
            self.fee.to_bytes(8) + self.amount.to_bytes(8) + self.timestamp.to_bytes(8)
        )
        return sha_256(buf)

    def get_signature(self) -> TransactionSignature:
        if not self.signature:
            raise Exception('Tried to read signature of unsigned transaction')
        return self.signature

    def signature_valid(self) -> bool:
        if not self.signature:
            return False
        if self.is_transaction_fee:
            return True
        hash = self.hash_contents()
        return check_signature_bytes(hash, self.signature, self.signing_key)

    def is_fee(self) -> bool:
        return self.is_transaction_fee

    def __eq__(self, other):
        if isinstance(other, Transaction):
            return (
                self.signature == other.signature
                and self.timestamp == other.timestamp
                and self.to == other.to
                and self.from_ == other.from_
                and self.amount == other.amount
                and self.fee == other.fee
                and self.is_transaction_fee == other.is_transaction_fee
            )
        return False

# merkle proofs
class Node:
    def __init__(self, hash):
        self.hash = hash
        self.parent: Optional[Node] = None
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

def get_merkle_hash(items: List[Transaction]) -> SHA256Hash:
    fringe_nodes: Dict[bytearray, Node] = {}
    items.sort(key=lambda a: sha_256_to_string(a.get_hash()), reverse=True)
    
    q: Deque[Node] = deque()

    for item in items:
        h = item.get_hash()
        fringe_nodes[h] = Node(h)
        q.append(fringe_nodes[h])

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