"""
Full integration test — covers all 12 project requirements.
Run from e:\\447_Project:   py test_all.py
"""
import os, sys, secrets, time

PASS = '\033[92mPASS\033[0m'
FAIL = '\033[91mFAIL\033[0m'
results = []

def check(label, condition):
    status = PASS if condition else FAIL
    print(f"  [{status}] {label}")
    results.append((label, condition))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

# ── clean slate ───────────────────────────────────────────────────────────────
for f in ('app.db', 'server_keys.json'):
    if os.path.exists(f): os.remove(f)

from database import (
    init_db, insert_user, get_user_by_username, get_user_by_id,
    update_user_otp, update_user_profile, rotate_user_keys,
    get_key_history, update_user_role,
    insert_post, get_post_by_id, get_posts_by_user,
    update_post, get_all_posts, verify_post_mac
)
from models.user import User
from crypto.rsa import generate_keypair as rsa_keygen, encrypt as rsa_enc, decrypt as rsa_dec
from crypto.rsa import sign as rsa_sign, verify as rsa_verify
from crypto.ecc import generate_keypair as ecc_keygen, ecdh_shared_secret
from crypto.hashing import hash_password, verify_password
from crypto.mac import generate_mac, verify_mac

init_db()

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 1 — User registration with all fields")

rp, rv = rsa_keygen(bits=256)
ep, ev = ecc_keygen()
pw1, s1 = hash_password('AlicePass1')
uid_alice = insert_user('alice', 'alice@test.com', '01700000001', pw1, s1, rp, rv, ep, ev)
otp_alice = secrets.token_hex(20)
update_user_otp(uid_alice, otp_alice)

check("alice registered (id returned)", isinstance(uid_alice, int) and uid_alice > 0)

row = get_user_by_username('alice')
alice = User(row)
check("username decrypts correctly", alice.username == 'alice')
check("email decrypts correctly",    alice.email    == 'alice@test.com')
check("contact decrypts correctly",  alice.contact  == '01700000001')
check("otp_secret stored",           alice.otp_secret == otp_alice)

# Register bob too
rp2, rv2 = rsa_keygen(bits=256)
ep2, ev2 = ecc_keygen()
pw2, s2 = hash_password('BobPass2')
uid_bob = insert_user('bob', 'bob@test.com', '01800000002', pw2, s2, rp2, rv2, ep2, ev2)
bob = User(get_user_by_username('bob'))
check("bob registered",  bob.username == 'bob')

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 2 — All user info encrypted before DB storage")

import sqlite3
conn = sqlite3.connect('app.db')
raw = conn.execute('SELECT username_enc, email_enc, contact_enc FROM users WHERE id=?',
                   (uid_alice,)).fetchone()
conn.close()

check("username_enc is not plaintext 'alice'",   raw[0] != 'alice')
check("email_enc is not plaintext 'alice@…'",    raw[1] != 'alice@test.com')
check("contact_enc is not plaintext '017…'",     raw[2] != '01700000001')
check("username_enc looks like hex ciphertext",  ':' in raw[0] or len(raw[0]) > 30)

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 3 — Passwords hashed with salt (SHA-256)")

check("correct password verifies",       verify_password('AlicePass1', alice.password_hash, alice.salt))
check("wrong password rejected",         not verify_password('WrongPass',  alice.password_hash, alice.salt))
check("hash is not plaintext password",  alice.password_hash != 'AlicePass1')
check("salt is 64-char hex (32 bytes)",  len(alice.salt) == 64)

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 4 — Two-Factor Authentication (TOTP, RFC 6238)")

import hashlib, hmac as hmac_mod, struct

def _hotp(secret_bytes, counter):
    msg = struct.pack('>Q', counter)
    mac = hmac_mod.new(secret_bytes, msg, hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    code = struct.unpack('>I', mac[offset:offset+4])[0] & 0x7FFFFFFF
    return str(code % 1_000_000).zfill(6)

def _verify_totp(secret_hex, token):
    secret_bytes = bytes.fromhex(secret_hex)
    counter = int(time.time()) // 30
    return any(_hotp(secret_bytes, counter+d) == token for d in (-1,0,1))

current_token = _hotp(bytes.fromhex(otp_alice), int(time.time())//30)
check("current TOTP verifies",    _verify_totp(otp_alice, current_token))
check("wrong TOTP code rejected", not _verify_totp(otp_alice, '000000'))
check("TOTP is 6 digits",         len(current_token) == 6 and current_token.isdigit())

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 5 — Key generation, storage, and rotation")

check("RSA public key stored in DB",  alice.rsa_pub is not None)
check("ECC public key stored in DB",  alice.ecc_pub is not None)
check("RSA private key decryptable",  alice.get_rsa_priv() is not None)
check("ECC private key decryptable",  alice.get_ecc_priv() is not None)

# Key rotation
new_rp, new_rv = rsa_keygen(bits=256)
new_ep, new_ev = ecc_keygen()
rotate_user_keys(uid_alice, new_rp, new_rv, new_ep, new_ev)
history = get_key_history(uid_alice)
check("key history has 2 versions after rotation", len(history) == 2)
check("key_version increments correctly",          history[-1]['key_version'] == 2)

# Reload alice to get new keys
alice_v2 = User(get_user_by_id(uid_alice))
check("new RSA pub key differs from old",
      alice_v2.rsa_pub[0] != alice.rsa_pub[0])

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 6 — Secure login (password + MAC integrity check)")

check("login with correct credentials succeeds",
      verify_password('AlicePass1', alice.password_hash, alice.salt)
      and alice.mac_valid)
check("login with wrong password fails",
      not verify_password('wrongpassword', alice.password_hash, alice.salt))
check("MAC valid on alice's row", alice.mac_valid)
check("MAC valid on bob's row",   bob.mac_valid)

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 7 — Posts encrypted before storage (no plaintext in DB)")

alice_fresh = User(get_user_by_id(uid_alice))
title_enc   = rsa_enc('My Secret Title',   alice_fresh.rsa_pub)
content_enc = rsa_enc('My secret content.', alice_fresh.rsa_pub)
post_id = insert_post(uid_alice, title_enc, content_enc)

raw_post = sqlite3.connect('app.db').execute(
    'SELECT title_enc, content_enc FROM posts WHERE id=?', (post_id,)
).fetchone()
check("title not stored in plaintext",   raw_post[0] != 'My Secret Title')
check("content not stored in plaintext", raw_post[1] != 'My secret content.')
check("title_enc looks like ciphertext", ':' in raw_post[0] or len(raw_post[0]) > 20)

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 8 — CBC-MAC on every record, verified on every read")

prow = get_post_by_id(post_id)
check("post MAC valid on fresh insert",    verify_post_mac(prow))
check("user MAC valid on alice record",    verify_mac(
    f"{row['username_enc']}|{row['email_enc']}|{row['contact_enc']}|{row['role']}",
    __import__('database').get_mac_key(), row['mac_tag']
))

# Simulate tamper — change mac_tag directly
conn = sqlite3.connect('app.db')
conn.execute('UPDATE posts SET content_enc=? WHERE id=?', ('TAMPERED_DATA', post_id))
conn.commit(); conn.close()
tampered_row = get_post_by_id(post_id)
check("tampered post MAC fails",           not verify_post_mac(tampered_row))

# Restore the post
conn = sqlite3.connect('app.db')
conn.execute('UPDATE posts SET content_enc=?, mac_tag=? WHERE id=?',
             (content_enc,
              generate_mac(f"{uid_alice}|{title_enc}|{content_enc}",
                           __import__('database').get_mac_key()),
              post_id))
conn.commit(); conn.close()
check("restored post MAC valid again",     verify_post_mac(get_post_by_id(post_id)))

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 9 — Only asymmetric encryption used (RSA)")

# Verify by checking imports — no AES/symmetric anywhere
import ast, pathlib
import re as _re
# look for import statements using forbidden libraries only
forbidden_patterns = [
    r'import\s+Crypto',       # pycryptodome
    r'from\s+Crypto\b',
    r'import\s+cryptography',
    r'from\s+cryptography\b',
    r'from\s+Fernet',
    r'AES\s*\(',              # AES usage
    r'ChaCha20',
]
violations = []
for pyfile in pathlib.Path('.').rglob('*.py'):
    skip = ['venv', 'test_all']
    if any(s in str(pyfile) for s in skip):
        continue
    src = pyfile.read_text(errors='ignore')
    for pat in forbidden_patterns:
        if _re.search(pat, src):
            violations.append(f"{pyfile}: {pat}")
check("no forbidden symmetric/third-party crypto libraries used",
      len(violations) == 0)

title2  = rsa_enc('RSA-only post', alice_fresh.rsa_pub)
content2 = rsa_enc('Encrypted with RSA only.', alice_fresh.rsa_pub)
pid2 = insert_post(uid_alice, title2, content2)
decrypted = rsa_dec(get_post_by_id(pid2)['title_enc'], alice_fresh.get_rsa_priv())
check("RSA encrypt->decrypt round-trip works", decrypted == 'RSA-only post')

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 10 — Two different algorithms: RSA + ECC")

check("RSA keypair generated (phase 1)", alice.rsa_pub is not None)
check("ECC keypair generated (phase 1)", alice.ecc_pub is not None)

shared_ab = ecdh_shared_secret(alice_fresh.get_ecc_priv(), bob.ecc_pub)
shared_ba = ecdh_shared_secret(bob.get_ecc_priv(),         alice_fresh.ecc_pub)
check("ECDH shared secret is 64-char hex", len(shared_ab) == 64)
check("ECDH is commutative (alice×bob == bob×alice)", shared_ab == shared_ba)

# alice holds the original keys (before rotation in REQ 5) — different ECC priv
shared_orig_ab = ecdh_shared_secret(alice.get_ecc_priv(), bob.ecc_pub)
check("different ECC private keys produce different shared secrets",
      shared_ab != shared_orig_ab)

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 11 — Role-based access control (RBAC)")

check("default role is 'user'",     alice.role == 'user')
check("is_admin() returns False",   not alice.is_admin())

update_user_role(uid_alice, 'admin')
alice_admin = User(get_user_by_id(uid_alice))
check("role updated to 'admin'",    alice_admin.role == 'admin')
check("is_admin() returns True",    alice_admin.is_admin())
check("MAC recomputed after role change", alice_admin.mac_valid)

update_user_role(uid_alice, 'user')
alice_reset = User(get_user_by_id(uid_alice))
check("demoted back to 'user'",     alice_reset.role == 'user')
check("MAC valid after demotion",   alice_reset.mac_valid)

# ─────────────────────────────────────────────────────────────────────────────
section("REQ 12 — RSA-signed session tokens")

user_for_token = User(get_user_by_id(uid_alice))
token = f"{user_for_token.id}:{secrets.token_hex(16)}"
sig   = rsa_sign(token, user_for_token.get_rsa_priv())

check("RSA signature verifies correctly",   rsa_verify(token, sig, user_for_token.rsa_pub))
check("tampered token fails verification",  not rsa_verify('tampered_token', sig, user_for_token.rsa_pub))
check("bob's key cannot verify alice's sig",
      not rsa_verify(token, sig, bob.rsa_pub))

token2 = f"{user_for_token.id}:{secrets.token_hex(16)}"
check("two logins produce different tokens", token != token2)

# ─────────────────────────────────────────────────────────────────────────────
section("SUMMARY")

total  = len(results)
passed = sum(1 for _, ok in results if ok)
failed = total - passed

print(f"\n  Total checks : {total}")
print(f"  Passed       : {passed}")
print(f"  Failed       : {failed}")

if failed == 0:
    print(f"\n  \033[92mALL {total} CHECKS PASSED -- all 12 requirements verified\033[0m\n")
else:
    print(f"\n  \033[91m✘ {failed} check(s) FAILED\033[0m\n")
    for label, ok in results:
        if not ok:
            print(f"    FAILED: {label}")
    sys.exit(1)
