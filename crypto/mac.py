import hashlib


BLOCK_SIZE = 32  # bytes (256-bit blocks matching SHA-256 output)


def _xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def _pad(data):
    data = data.encode('utf-8') if isinstance(data, str) else data
    remainder = len(data) % BLOCK_SIZE
    if remainder != 0:
        data += b'\x00' * (BLOCK_SIZE - remainder)
    return data


def generate_mac(data, key):
    data_bytes = _pad(data)
    key_bytes = hashlib.sha256(key.encode('utf-8')).digest()

    state = b'\x00' * BLOCK_SIZE
    for i in range(0, len(data_bytes), BLOCK_SIZE):
        block = data_bytes[i:i + BLOCK_SIZE]
        xored = _xor_bytes(state, block)
        state = hashlib.sha256(key_bytes + xored).digest()

    return state.hex()


def verify_mac(data, key, tag):
    return generate_mac(data, key) == tag
