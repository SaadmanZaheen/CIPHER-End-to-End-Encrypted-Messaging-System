import secrets
import hashlib
import time
from flask import Blueprint, request, session, redirect, url_for, render_template, flash

from database import (
    insert_user, get_user_by_username, get_user_by_id,
    update_user_otp, update_user_profile,
    rotate_user_keys, get_key_history
)
from models.user import User
from crypto.rsa import generate_keypair as rsa_keygen, sign as rsa_sign, verify as rsa_verify
from crypto.ecc import generate_keypair as ecc_keygen
from crypto.hashing import hash_password, verify_password

auth_bp = Blueprint('auth', __name__)


# ── From-scratch HMAC-SHA1 (RFC 2104) ────────────────────────────────────────
# Replaces the stdlib `hmac` module — uses only the allowed `hashlib` package.

def _hmac_sha1(key_bytes: bytes, msg_bytes: bytes) -> bytes:
    block = 64                          # SHA-1 internal block size in bytes
    if len(key_bytes) > block:
        key_bytes = hashlib.sha1(key_bytes).digest()
    key_bytes = key_bytes.ljust(block, b'\x00')
    ipad = bytes(b ^ 0x36 for b in key_bytes)
    opad = bytes(b ^ 0x5C for b in key_bytes)
    inner = hashlib.sha1(ipad + msg_bytes).digest()
    return hashlib.sha1(opad + inner).digest()


# ── From-scratch Base32 encoder ───────────────────────────────────────────────
# Replaces `base64.b32encode` — used only for the TOTP URI display string.

_B32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
# pad_bytes is how many zero-bytes we appended to fill the 5-byte chunk.
# Each real-byte count maps to a specific number of '=' output chars:
#   5 bytes → 0 '=',  4 bytes → 1 '=',  3 bytes → 3 '=',  2 bytes → 4 '=',  1 byte → 6 '='
_B32_PAD = {0: 0, 1: 1, 2: 3, 3: 4, 4: 6}

def _b32encode(data: bytes) -> str:
    out = []
    for i in range(0, len(data), 5):
        chunk = data[i:i + 5]
        pad_bytes = 5 - len(chunk)
        n = int.from_bytes(chunk + b'\x00' * pad_bytes, 'big')
        chars = [_B32[(n >> (5 * j)) & 0x1F] for j in range(7, -1, -1)]
        eq = _B32_PAD[pad_bytes]
        out.extend(chars[:8 - eq])
        out.extend(['='] * eq)
    return ''.join(out)


# ── TOTP helpers (RFC 6238, 6 digits, 30-second window) ──────────────────────

def _hotp(secret_bytes, counter):
    msg = counter.to_bytes(8, 'big')         # big-endian 64-bit counter
    mac = _hmac_sha1(secret_bytes, msg)
    offset = mac[-1] & 0x0F
    code = int.from_bytes(mac[offset:offset + 4], 'big') & 0x7FFFFFFF
    return str(code % 1_000_000).zfill(6)


def _totp(secret_hex):
    secret_bytes = bytes.fromhex(secret_hex)
    counter = int(time.time()) // 30
    return _hotp(secret_bytes, counter)


def _verify_totp(secret_hex, token):
    secret_bytes = bytes.fromhex(secret_hex)
    counter = int(time.time()) // 30
    for delta in (-1, 0, 1):
        if _hotp(secret_bytes, counter + delta) == token.strip():
            return True
    return False


def _totp_uri(username, secret_hex):
    secret_b32 = _b32encode(bytes.fromhex(secret_hex))
    return f"otpauth://totp/CSE447:{username}?secret={secret_b32}&issuer=CSE447"


# ── Session token helpers ─────────────────────────────────────────────────────

def _issue_token(user):
    """RSA-sign a token and store it in the Flask session (Req 12)."""
    token = f"{user.id}:{secrets.token_hex(16)}"
    sig = rsa_sign(token, user.get_rsa_priv())
    session['token'] = token
    session['sig']   = sig
    session['uid']   = user.id


def _verify_session():
    """Return User if the session token signature is valid, else None."""
    token = session.get('token')
    sig   = session.get('sig')
    uid   = session.get('uid')
    if not (token and sig and uid):
        return None
    row = get_user_by_id(uid)
    if row is None:
        return None
    user = User(row)
    if not rsa_verify(token, sig, user.rsa_pub):
        return None
    return user


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = _verify_session()
        if user is None:
            flash('Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, user=user, **kwargs)
    return decorated


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = _verify_session()
        if user is None:
            return redirect(url_for('auth.login'))
        if not user.is_admin():
            flash('Admin only.', 'danger')
            return redirect(url_for('posts.feed'))
        return f(*args, user=user, **kwargs)
    return decorated


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username', '').strip()
    email    = request.form.get('email', '').strip()
    contact  = request.form.get('contact', '').strip()
    password = request.form.get('password', '')
    confirm  = request.form.get('confirm', '')

    if not all([username, email, contact, password]):
        flash('All fields are required.', 'danger')
        return render_template('register.html')

    if password != confirm:
        flash('Passwords do not match.', 'danger')
        return render_template('register.html')

    if get_user_by_username(username) is not None:
        flash('Username already taken.', 'danger')
        return render_template('register.html')

    pw_hash, salt = hash_password(password)
    rsa_pub, rsa_priv = rsa_keygen(bits=256)
    ecc_pub, ecc_priv = ecc_keygen()

    user_id = insert_user(
        username, email, contact, pw_hash, salt,
        rsa_pub, rsa_priv, ecc_pub, ecc_priv
    )

    # Generate OTP secret and store it
    otp_secret = secrets.token_hex(20)
    update_user_otp(user_id, otp_secret)

    session['pending_uid']    = user_id
    session['pending_action'] = 'setup_otp'
    return redirect(url_for('auth.setup_otp'))


@auth_bp.route('/setup-otp')
def setup_otp():
    uid = session.get('pending_uid')
    if session.get('pending_action') != 'setup_otp' or not uid:
        return redirect(url_for('auth.login'))
    row  = get_user_by_id(uid)
    user = User(row)
    uri  = _totp_uri(user.username, user.otp_secret)
    return render_template('setup_otp.html', otp_uri=uri, username=user.username,
                           otp_secret=user.otp_secret)


@auth_bp.route('/setup-otp/confirm', methods=['POST'])
def confirm_otp():
    uid = session.get('pending_uid')
    if session.get('pending_action') != 'setup_otp' or not uid:
        return redirect(url_for('auth.login'))
    token = request.form.get('token', '').strip()
    row   = get_user_by_id(uid)
    user  = User(row)
    if not _verify_totp(user.otp_secret, token):
        flash('Invalid OTP code. Try again.', 'danger')
        return redirect(url_for('auth.setup_otp'))
    session.pop('pending_uid', None)
    session.pop('pending_action', None)
    flash('2FA enabled. Please log in.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    row = get_user_by_username(username)
    if row is None:
        flash('Invalid credentials.', 'danger')
        return render_template('login.html')

    user = User(row)

    if not user.mac_valid:
        flash('Account integrity check failed.', 'danger')
        return render_template('login.html')

    if not verify_password(password, user.password_hash, user.salt):
        flash('Invalid credentials.', 'danger')
        return render_template('login.html')

    # If OTP is configured, require 2FA
    if user.otp_secret:
        session['pending_uid']    = user.id
        session['pending_action'] = 'verify_otp'
        return redirect(url_for('auth.verify_otp'))

    _issue_token(user)
    flash(f'Welcome, {user.username}!', 'success')
    return redirect(url_for('posts.feed'))


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    uid = session.get('pending_uid')
    if session.get('pending_action') != 'verify_otp' or not uid:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('verify_otp.html')

    token = request.form.get('token', '').strip()
    row   = get_user_by_id(uid)
    user  = User(row)

    if not _verify_totp(user.otp_secret, token):
        flash('Invalid OTP code.', 'danger')
        return render_template('verify_otp.html')

    session.pop('pending_uid', None)
    session.pop('pending_action', None)
    _issue_token(user)
    flash(f'Welcome, {user.username}!', 'success')
    return redirect(url_for('posts.feed'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile(user):
    if request.method == 'GET':
        return render_template('profile.html', user=user)

    email   = request.form.get('email', '').strip()
    contact = request.form.get('contact', '').strip()
    if not email or not contact:
        flash('Email and contact are required.', 'danger')
        return render_template('profile.html', user=user)

    update_user_profile(user.id, email, contact)
    flash('Profile updated.', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/keys/rotate', methods=['GET', 'POST'])
@login_required
def key_rotate(user):
    if request.method == 'GET':
        history = get_key_history(user.id)
        return render_template('key_rotate.html', user=user, history=history)

    # Generate fresh RSA + ECC keypairs
    new_rsa_pub, new_rsa_priv = rsa_keygen(bits=256)
    new_ecc_pub, new_ecc_priv = ecc_keygen()
    rotate_user_keys(user.id, new_rsa_pub, new_rsa_priv, new_ecc_pub, new_ecc_priv)

    # Re-issue session token with the new RSA private key
    row      = get_user_by_id(user.id)
    new_user = User(row)
    _issue_token(new_user)

    flash('Keypairs rotated successfully. New session token issued.', 'success')
    return redirect(url_for('auth.key_rotate'))


@auth_bp.route('/keys/history')
@login_required
def key_history(user):
    history = get_key_history(user.id)
    return render_template('key_history.html', user=user, history=history)
