import hashlib
import secrets


def hash_password(password):
    salt = secrets.token_hex(32)
    pw_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return pw_hash, salt


def verify_password(password, stored_hash, salt):
    pw_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return pw_hash == stored_hash
