from pandanite.core.crypto import (
    generate_key_pair,
    string_to_public_key,
    public_key_to_string,
    sign_with_private_key,
    string_to_signature,
    signature_to_string,
    check_signature,
    add_work,
    sha_256,
    sha_256_to_string,
    string_to_sha_256,
    mine_hash,
    concat_hashes,
)


def test_key_string_conversion():
    pub, priv = generate_key_pair()
    converted = string_to_public_key(public_key_to_string(pub))
    assert pub == converted


def test_signature_string_conversion():
    pub, priv = generate_key_pair()
    t = sign_with_private_key("FOOBAR", priv)
    converted = string_to_signature(signature_to_string(t))
    assert converted == t


def test_signature_verifications():
    pub, priv = generate_key_pair()
    t = sign_with_private_key("FOOBAR", priv)
    status = check_signature("FOOBAR", t, pub)
    assert status == True

    _, priv2 = generate_key_pair()
    t = sign_with_private_key("FOOBAR", priv2)
    status = check_signature("FOOBAR", t, pub)
    assert status == False


def test_total_work():
    work = 0
    work = add_work(work, 16)
    work = add_work(work, 16)
    work = add_work(work, 16)
    base = 2
    mult = 3
    expected = mult * base**16
    assert work == expected
    assert work == 196608

    work = add_work(work, 32)
    work = add_work(work, 28)
    work = add_work(work, 74)
    work = add_work(work, 174)
    b = 0
    b += expected
    base = 2
    b += base**32
    base = 2
    b += base**28
    base = 2
    b += base**74
    base = 2
    b += base**174

    assert b == work
    assert str(work) == "23945242826029513411849172299242470459974281928572928"


def test_sha256_to_string():
    h = sha_256("FOOBAR".encode("utf-8"))
    assert h == string_to_sha_256(sha_256_to_string(h))


def test_mine_hash():
    hash = sha_256("Hello World".encode("utf-8"))
    answer = mine_hash(hash, 6)
    new_hash = concat_hashes(hash, answer)
    assert new_hash[0] < 63
