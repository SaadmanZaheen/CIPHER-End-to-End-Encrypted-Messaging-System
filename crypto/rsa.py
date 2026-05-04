import random
import hashlib
import sympy
from math import gcd


def _generate_prime(bits):
    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << (bits - 1)) | 1
        if sympy.isprime(candidate):
            return candidate


def generate_keypair(bits=256):
    p = _generate_prime(bits)
    q = _generate_prime(bits)
    while q == p:
        q = _generate_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 11
    while gcd(e, phi) != 1:
        e += 2

    d = sympy.mod_inverse(e, phi)

    return (n, e), (n, d)


def encrypt(plaintext, public_key):
    n, e = public_key
    chunk_size = (n.bit_length() // 8) - 1
    data = plaintext.encode('utf-8')
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    encrypted = []
    for chunk in chunks:
        m = int(chunk.hex(), 16)
        c = pow(m, e, n)
        encrypted.append(hex(c)[2:])

    return ':'.join(encrypted)


def decrypt(ciphertext, private_key):
    n, d = private_key
    result = b''

    for chunk in ciphertext.split(':'):
        c = int(chunk, 16)
        m = pow(c, d, n)
        hex_val = hex(m)[2:]
        if len(hex_val) % 2 != 0:
            hex_val = '0' + hex_val
        result += bytes.fromhex(hex_val)

    return result.decode('utf-8')


def sign(message, private_key):
    n, d = private_key
    hash_int = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)
    signature = pow(hash_int, d, n)
    return hex(signature)[2:]


def verify(message, signature, public_key):
    n, e = public_key
    hash_int = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)
    recovered = pow(int(signature, 16), e, n)
    return recovered == hash_int
