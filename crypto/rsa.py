import os
import hashlib
from math import gcd


# ── Primality test (Miller-Rabin, replaces sympy.isprime) ─────────────────────

def _is_prime(n, rounds=20):
    """Miller-Rabin probabilistic primality test."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^r * d where d is odd
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(rounds):
        # Pick a random witness in [2, n-2]
        a = int.from_bytes(os.urandom((n.bit_length() + 7) // 8), 'big') % (n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _generate_prime(bits):
    """Generate a random prime of the given bit length using os.urandom."""
    while True:
        candidate = int.from_bytes(os.urandom(bits // 8), 'big')
        candidate |= (1 << (bits - 1)) | 1  # force correct bit length and odd
        if _is_prime(candidate):
            return candidate


# ── Key generation ─────────────────────────────────────────────────────────────

def generate_keypair(bits=256):
    """Generate an RSA keypair. Returns ((n, e), (n, d))."""
    p = _generate_prime(bits)
    q = _generate_prime(bits)
    while q == p:
        q = _generate_prime(bits)

    n   = p * q
    phi = (p - 1) * (q - 1)

    e = 11
    while gcd(e, phi) != 1:
        e += 2

    # Python 3.8+ built-in modular inverse (replaces sympy.mod_inverse)
    d = pow(e, -1, phi)

    return (n, e), (n, d)


# ── Encryption / Decryption ────────────────────────────────────────────────────

def encrypt(plaintext, public_key):
    """Encrypt a plaintext string with an RSA public key. Returns a colon-separated hex string."""
    n, e = public_key
    chunk_size = (n.bit_length() // 8) - 1
    data   = plaintext.encode('utf-8')
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    encrypted = []
    for chunk in chunks:
        m = int(chunk.hex(), 16)
        c = pow(m, e, n)
        encrypted.append(hex(c)[2:])

    return ':'.join(encrypted)


def decrypt(ciphertext, private_key):
    """Decrypt a colon-separated hex ciphertext with an RSA private key."""
    n, d   = private_key
    result = b''

    for chunk in ciphertext.split(':'):
        c       = int(chunk, 16)
        m       = pow(c, d, n)
        hex_val = hex(m)[2:]
        if len(hex_val) % 2 != 0:
            hex_val = '0' + hex_val
        result += bytes.fromhex(hex_val)

    return result.decode('utf-8')


# ── Signing / Verification ─────────────────────────────────────────────────────

def sign(message, private_key):
    """Sign a message with an RSA private key. Returns a hex string."""
    n, d     = private_key
    hash_int = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)
    return hex(pow(hash_int, d, n))[2:]


def verify(message, signature, public_key):
    """Verify an RSA signature. Returns True if valid."""
    n, e      = public_key
    hash_int  = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)
    recovered = pow(int(signature, 16), e, n)
    return recovered == hash_int
