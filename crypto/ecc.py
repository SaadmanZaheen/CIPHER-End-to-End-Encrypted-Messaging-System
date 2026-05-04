import random
import hashlib

# Curve: y^2 = x^3 + ax + b (mod p)
# Using a well-known 192-bit prime curve for real security
_P  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFF
_A  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFC
_B  = 0x64210519E59C80E70FA7E9AB72243049FEB8DEECC146B9B1
_GX = 0x188DA80EB03090F67CBF20EB43A18800F4FF0AFD82FF1012
_GY = 0x07192B95FFC8DA78631011ED6B24CDD573F977A11E794811
_N  = 0xFFFFFFFFFFFFFFFFFFFFFFFF99DEF836146BC9B1B4D22831
_G  = (_GX, _GY)


def _inverse_mod(k, p):
    return pow(k, -1, p)


def point_add(P, Q, a=_A, p=_P):
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if P == Q:
        num = (3 * pow(x1, 2) + a) % p
        den = _inverse_mod(2 * y1, p)
    else:
        num = (y2 - y1) % p
        den = _inverse_mod(x2 - x1, p)

    m = (num * den) % p
    x_r = (pow(m, 2) - x1 - x2) % p
    y_r = (m * (x1 - x_r) - y1) % p

    return (x_r, y_r)


def scalar_mult(k, P, a=_A, p=_P):
    R = None
    Q = P

    while k > 0:
        if k % 2 == 1:
            R = point_add(R, Q, a, p)
        Q = point_add(Q, Q, a, p)
        k //= 2

    return R


def generate_keypair():
    private_key = random.randint(2, _N - 1)
    public_key = scalar_mult(private_key, _G)
    return public_key, private_key


def ecdh_shared_secret(private_key, other_public_key):
    shared_point = scalar_mult(private_key, other_public_key)
    shared_bytes = shared_point[0].to_bytes(24, 'big')
    return hashlib.sha256(shared_bytes).hexdigest()


# ── ECDSA (sign / verify) — satisfies Req 10: ECC for a different purpose ─────

def ecdsa_sign(message, private_key):
    """Sign a message with an ECC private key (ECDSA, SHA-256 hash)."""
    z = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16) % _N
    while True:
        k = random.randint(1, _N - 1)
        R = scalar_mult(k, _G)
        if R is None:
            continue
        r = R[0] % _N
        if r == 0:
            continue
        k_inv = _inverse_mod(k, _N)
        s = (k_inv * (z + r * private_key)) % _N
        if s != 0:
            return f"{r}|{s}"


def ecdsa_verify(message, signature_str, public_key):
    """Verify an ECDSA signature string 'r|s' against a message and ECC public key."""
    try:
        r, s = (int(x) for x in signature_str.split('|'))
    except Exception:
        return False
    if not (1 <= r < _N and 1 <= s < _N):
        return False
    z = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16) % _N
    w = _inverse_mod(s, _N)
    u1 = (z * w) % _N
    u2 = (r * w) % _N
    P = point_add(scalar_mult(u1, _G), scalar_mult(u2, public_key))
    if P is None:
        return False
    return P[0] % _N == r
