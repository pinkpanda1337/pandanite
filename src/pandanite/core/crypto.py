import random
import hashlib
import ed25519

from typing import TypeAlias, Tuple, Union
from Crypto.Hash import RIPEMD160
from pandanite.core.common import WorkAmount

SHA256Hash: TypeAlias = bytearray
RIPEMDHash: TypeAlias = bytearray
PublicWalletAddress: TypeAlias = bytearray
PublicKey: TypeAlias = ed25519.keys.VerifyingKey
PrivateKey: TypeAlias = ed25519.keys.SigningKey
TransactionSignature: TypeAlias = bytes

NULL_SHA256_HASH = SHA256Hash(32)
NULL_KEY = SHA256Hash(32)
NULL_ADDRESS = PublicWalletAddress(25)


def sha_256(buf: Union[bytes, bytearray]) -> SHA256Hash:
    return bytearray(hashlib.sha256(buf).digest())


def ripemd(buf: Union[bytes, bytearray]) -> RIPEMDHash:
    hash_obj = RIPEMD160.new()
    hash_obj.update(buf)
    return bytearray(hash_obj.digest())


def string_to_sha_256(hex: str):
    return hex_decode(hex)


def sha_256_to_string(hash: SHA256Hash) -> str:
    return hex_encode(hash)


def hex_decode(hex: str) -> bytearray:
    return bytearray.fromhex(hex)


def hex_encode(buf: Union[bytes, bytearray]) -> str:
    return buf.hex()


def concat_hashes(a: SHA256Hash, b: SHA256Hash) -> SHA256Hash:
    return sha_256(a + b)


def check_leading_zero_bits(hash: SHA256Hash, N: int) -> bool:
    for i in range(N):
        byte_index = i // 8
        bit_index = i % 8
        if hash[byte_index] & (1 << (7 - bit_index)):
            return False
        if byte_index == len(hash) - 1 and i < N - 1:
            return False
    return True


def add_work(previous_work: WorkAmount, challenge_size: int) -> WorkAmount:
    return previous_work + 2**challenge_size


def remove_work(previous_work: WorkAmount, challenge_size: int) -> WorkAmount:
    return previous_work - 2**challenge_size


# keys
def wallet_address_from_public_key(input_key: PublicKey) -> PublicWalletAddress:
    # Based on: https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses
    hash = sha_256(input_key.to_bytes())
    hash2 = ripemd(hash)
    hash3 = sha_256(hash2)
    hash4 = sha_256(hash3)
    address: PublicWalletAddress = NULL_ADDRESS
    address[0] = 0
    for i in range(0, 20):
        address[i] = hash2[i]
    address[21] = hash4[0]
    address[22] = hash4[1]
    address[23] = hash4[2]
    address[24] = hash4[3]
    return address


def verify_hash(target: SHA256Hash, nonce: SHA256Hash, difficulty: int):
    concat = concat_hashes(target, nonce)
    return check_leading_zero_bits(concat, difficulty)


def generate_key_pair() -> Tuple[PublicKey, PrivateKey]:
    private_key = ed25519.SigningKey(random.randint(0, 2**256).to_bytes(32))
    public_key = private_key.get_verifying_key()
    return (public_key, private_key)


def wallet_address_to_string(public_wallet_address: PublicWalletAddress) -> str:
    return hex_encode(public_wallet_address)


def string_to_wallet_address(s: str) -> PublicWalletAddress:
    if len(s) != 50:
        raise Exception("Invalid address string")
    return hex_decode(s)


def public_key_to_string(public_key: PublicKey) -> str:
    return public_key.to_bytes().hex()


def string_to_public_key(s: str) -> PublicKey:
    if len(s) != 64:
        raise Exception("Invalid public key string")
    return ed25519.keys.VerifyingKey(s, encoding="base16")


def private_key_to_string(private_key: PrivateKey) -> str:
    return private_key.to_bytes().hex()


def string_to_private_key(s: str) -> PrivateKey:
    if len(s) != 128:
        raise Exception("Invalid private key string")
    return ed25519.keys.SigningKey(s, encoding="base16")


# signatures
def signature_to_string(t: TransactionSignature) -> str:
    return hex_encode(t)


def string_to_signature(t: str) -> TransactionSignature:
    return hex_decode(t)


def sign_with_private_key(content: str, priv_key: PrivateKey) -> TransactionSignature:
    return sign_with_private_key_bytes(content.encode("utf-8"), priv_key)


def sign_with_private_key_bytes(
    bytes: Union[bytes, bytearray], priv_key: PrivateKey
) -> TransactionSignature:
    return priv_key.sign(bytes)


def check_signature(
    content: str, signature: TransactionSignature, verifying_key: PublicKey
) -> bool:
    return check_signature_bytes(content.encode("utf-8"), signature, verifying_key)


def check_signature_bytes(
    bytes: bytes,
    signature: TransactionSignature,
    verifying_key: PublicKey,
) -> bool:
    try:
        verifying_key.verify(signature, bytes)
        return True
    except:
        return False


# miner


def mine_hash(target: SHA256Hash, challenge_size: int):
    while True:
        solution = SHA256Hash(random.randint(0, 2**256).to_bytes(32))
        full_hash = concat_hashes(target, solution)
        found = check_leading_zero_bits(full_hash, challenge_size)
        if found:
            break
    return solution
