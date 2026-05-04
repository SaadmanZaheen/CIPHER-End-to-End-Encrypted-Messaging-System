import sqlite3
import os
import json
import secrets
from crypto.rsa import generate_keypair, encrypt, decrypt
from crypto.mac import generate_mac, verify_mac

DB_PATH = 'app.db'
SERVER_KEYS_PATH = 'server_keys.json'


# ── Server key bootstrap ──────────────────────────────────────────────────────

def _init_server_keys():
    if not os.path.exists(SERVER_KEYS_PATH):
        pub, priv = generate_keypair(bits=256)
        data = {
            'rsa_pub':  [pub[0],  pub[1]],
            'rsa_priv': [priv[0], priv[1]],
            'mac_key':  secrets.token_hex(32)
        }
        with open(SERVER_KEYS_PATH, 'w') as f:
            json.dump(data, f)


def _load_server_keys():
    with open(SERVER_KEYS_PATH, 'r') as f:
        return json.load(f)


def get_server_rsa_pub():
    d = _load_server_keys()
    return (d['rsa_pub'][0], d['rsa_pub'][1])


def get_server_rsa_priv():
    d = _load_server_keys()
    return (d['rsa_priv'][0], d['rsa_priv'][1])


def get_mac_key():
    return _load_server_keys()['mac_key']


# ── Field-level encrypt/decrypt using server RSA key ─────────────────────────

def field_encrypt(plaintext):
    return encrypt(str(plaintext), get_server_rsa_pub())


def field_decrypt(ciphertext):
    return decrypt(ciphertext, get_server_rsa_priv())


# ── Key serialization helpers ─────────────────────────────────────────────────

def serialize_rsa_pub(pub):
    return f"{pub[0]}|{pub[1]}"


def deserialize_rsa_pub(s):
    n, e = s.split('|')
    return (int(n), int(e))


def serialize_ecc_pub(pub):
    return f"{pub[0]}|{pub[1]}"


def deserialize_ecc_pub(s):
    x, y = s.split('|')
    return (int(x), int(y))


def encrypt_private_key(key_int):
    return encrypt(str(key_int), get_server_rsa_pub())


def decrypt_private_key(enc_str):
    return int(decrypt(enc_str, get_server_rsa_priv()))


def encrypt_rsa_priv(priv):
    # priv = (n, d) — encrypt d; n is public
    return encrypt(f"{priv[0]}|{priv[1]}", get_server_rsa_pub())


def decrypt_rsa_priv(enc_str):
    raw = decrypt(enc_str, get_server_rsa_priv())
    n, d = raw.split('|')
    return (int(n), int(d))


# ── DB connection ─────────────────────────────────────────────────────────────

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Table creation ────────────────────────────────────────────────────────────

def init_db():
    _init_server_keys()
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        username_enc    TEXT    NOT NULL UNIQUE,
        email_enc       TEXT    NOT NULL,
        contact_enc     TEXT    NOT NULL,
        password_hash   TEXT    NOT NULL,
        salt            TEXT    NOT NULL,
        role            TEXT    NOT NULL DEFAULT 'user',
        rsa_pub         TEXT    NOT NULL,
        rsa_priv_enc    TEXT    NOT NULL,
        ecc_pub         TEXT    NOT NULL,
        ecc_priv_enc    TEXT    NOT NULL,
        otp_secret      TEXT,
        mac_tag         TEXT    NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL,
        title_enc   TEXT    NOT NULL,
        content_enc TEXT    NOT NULL,
        ecc_sig     TEXT    NOT NULL DEFAULT '',
        created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        mac_tag     TEXT    NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    # Migration: add ecc_sig to existing DBs that predate this column
    try:
        c.execute("ALTER TABLE posts ADD COLUMN ecc_sig TEXT NOT NULL DEFAULT ''")
        conn.commit()
    except Exception:
        pass  # column already exists

    c.execute('''CREATE TABLE IF NOT EXISTS keys (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        key_version  INTEGER NOT NULL DEFAULT 1,
        rsa_pub      TEXT    NOT NULL,
        rsa_priv_enc TEXT    NOT NULL,
        ecc_pub      TEXT    NOT NULL,
        ecc_priv_enc TEXT    NOT NULL,
        created_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS friendships (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        requester_id INTEGER NOT NULL,
        recipient_id INTEGER NOT NULL,
        status       TEXT    NOT NULL DEFAULT 'pending',
        created_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (requester_id) REFERENCES users(id),
        FOREIGN KEY (recipient_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id         INTEGER NOT NULL,
        recipient_id      INTEGER NOT NULL,
        content_enc_recv  TEXT    NOT NULL,
        content_enc_send  TEXT    NOT NULL,
        mac_tag           TEXT    NOT NULL,
        is_read           INTEGER NOT NULL DEFAULT 0,
        created_at        TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id)    REFERENCES users(id),
        FOREIGN KEY (recipient_id) REFERENCES users(id)
    )''')
    try:
        c.execute("ALTER TABLE messages ADD COLUMN is_read INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    except Exception:
        pass  # column already exists

    conn.commit()
    conn.close()


# ── User operations ───────────────────────────────────────────────────────────

def insert_user(username, email, contact, password_hash, salt,
                rsa_pub, rsa_priv, ecc_pub, ecc_priv, role='user'):
    username_enc  = field_encrypt(username)
    email_enc     = field_encrypt(email)
    contact_enc   = field_encrypt(contact)
    rsa_pub_str   = serialize_rsa_pub(rsa_pub)
    rsa_priv_enc  = encrypt_rsa_priv(rsa_priv)
    ecc_pub_str   = serialize_ecc_pub(ecc_pub)
    ecc_priv_enc  = encrypt_private_key(ecc_priv)

    mac_data = f"{username_enc}|{email_enc}|{contact_enc}|{role}"
    mac_tag  = generate_mac(mac_data, get_mac_key())

    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO users
        (username_enc, email_enc, contact_enc, password_hash, salt, role,
         rsa_pub, rsa_priv_enc, ecc_pub, ecc_priv_enc, mac_tag)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
        (username_enc, email_enc, contact_enc, password_hash, salt, role,
         rsa_pub_str, rsa_priv_enc, ecc_pub_str, ecc_priv_enc, mac_tag))
    user_id = c.lastrowid

    # archive initial keypair in keys table
    c.execute('''INSERT INTO keys
        (user_id, key_version, rsa_pub, rsa_priv_enc, ecc_pub, ecc_priv_enc)
        VALUES (?,?,?,?,?,?)''',
        (user_id, 1, rsa_pub_str, rsa_priv_enc, ecc_pub_str, ecc_priv_enc))

    conn.commit()
    conn.close()
    return user_id


def get_user_by_username(username):
    username_enc = field_encrypt(username)
    conn = get_connection()
    row = conn.execute(
        'SELECT * FROM users WHERE username_enc = ?', (username_enc,)
    ).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return row


def get_all_users():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return rows


def update_user_otp(user_id, otp_secret):
    conn = get_connection()
    conn.execute('UPDATE users SET otp_secret = ? WHERE id = ?', (otp_secret, user_id))
    conn.commit()
    conn.close()


def update_user_profile(user_id, email, contact):
    email_enc   = field_encrypt(email)
    contact_enc = field_encrypt(contact)

    row = get_user_by_id(user_id)
    mac_data = f"{row['username_enc']}|{email_enc}|{contact_enc}|{row['role']}"
    mac_tag  = generate_mac(mac_data, get_mac_key())

    conn = get_connection()
    conn.execute(
        'UPDATE users SET email_enc=?, contact_enc=?, mac_tag=? WHERE id=?',
        (email_enc, contact_enc, mac_tag, user_id)
    )
    conn.commit()
    conn.close()


def rotate_user_keys(user_id, new_rsa_pub, new_rsa_priv, new_ecc_pub, new_ecc_priv):
    conn = get_connection()
    version = conn.execute(
        'SELECT MAX(key_version) FROM keys WHERE user_id=?', (user_id,)
    ).fetchone()[0] or 0

    rsa_pub_str  = serialize_rsa_pub(new_rsa_pub)
    rsa_priv_enc = encrypt_rsa_priv(new_rsa_priv)
    ecc_pub_str  = serialize_ecc_pub(new_ecc_pub)
    ecc_priv_enc = encrypt_private_key(new_ecc_priv)

    conn.execute('''INSERT INTO keys
        (user_id, key_version, rsa_pub, rsa_priv_enc, ecc_pub, ecc_priv_enc)
        VALUES (?,?,?,?,?,?)''',
        (user_id, version + 1, rsa_pub_str, rsa_priv_enc, ecc_pub_str, ecc_priv_enc))

    conn.execute('''UPDATE users SET
        rsa_pub=?, rsa_priv_enc=?, ecc_pub=?, ecc_priv_enc=? WHERE id=?''',
        (rsa_pub_str, rsa_priv_enc, ecc_pub_str, ecc_priv_enc, user_id))

    conn.commit()
    conn.close()


def verify_user_mac(row):
    mac_data = f"{row['username_enc']}|{row['email_enc']}|{row['contact_enc']}|{row['role']}"
    return verify_mac(mac_data, get_mac_key(), row['mac_tag'])


# ── Post operations ───────────────────────────────────────────────────────────

def insert_post(user_id, title_enc, content_enc, ecc_sig=''):
    mac_data = f"{user_id}|{title_enc}|{content_enc}"
    mac_tag  = generate_mac(mac_data, get_mac_key())

    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO posts (user_id, title_enc, content_enc, ecc_sig, mac_tag)
                 VALUES (?,?,?,?,?)''', (user_id, title_enc, content_enc, ecc_sig, mac_tag))
    post_id = c.lastrowid
    conn.commit()
    conn.close()
    return post_id


def get_posts_by_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM posts WHERE user_id=? ORDER BY created_at DESC', (user_id,)
    ).fetchall()
    conn.close()
    return rows


def get_post_by_id(post_id):
    conn = get_connection()
    row = conn.execute('SELECT * FROM posts WHERE id=?', (post_id,)).fetchone()
    conn.close()
    return row


def update_post(post_id, title_enc, content_enc, ecc_sig=''):
    row = get_post_by_id(post_id)
    mac_data = f"{row['user_id']}|{title_enc}|{content_enc}"
    mac_tag  = generate_mac(mac_data, get_mac_key())

    conn = get_connection()
    conn.execute(
        'UPDATE posts SET title_enc=?, content_enc=?, ecc_sig=?, mac_tag=? WHERE id=?',
        (title_enc, content_enc, ecc_sig, mac_tag, post_id)
    )
    conn.commit()
    conn.close()


def delete_post(post_id):
    conn = get_connection()
    conn.execute('DELETE FROM posts WHERE id=?', (post_id,))
    conn.commit()
    conn.close()


def verify_post_mac(row):
    mac_data = f"{row['user_id']}|{row['title_enc']}|{row['content_enc']}"
    return verify_mac(mac_data, get_mac_key(), row['mac_tag'])


def get_all_posts():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return rows


def get_key_history(user_id):
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM keys WHERE user_id=? ORDER BY key_version ASC', (user_id,)
    ).fetchall()
    conn.close()
    return rows


def update_user_role(user_id, new_role):
    row = get_user_by_id(user_id)
    mac_data = f"{row['username_enc']}|{row['email_enc']}|{row['contact_enc']}|{new_role}"
    mac_tag  = generate_mac(mac_data, get_mac_key())

    conn = get_connection()
    conn.execute('UPDATE users SET role=?, mac_tag=? WHERE id=?', (new_role, mac_tag, user_id))
    conn.commit()
    conn.close()


# ── Friendship operations ─────────────────────────────────────────────────────

def send_friend_request(requester_id, recipient_id):
    conn = get_connection()
    conn.execute(
        'INSERT INTO friendships (requester_id, recipient_id, status) VALUES (?,?,?)',
        (requester_id, recipient_id, 'pending')
    )
    conn.commit()
    conn.close()


def get_friendship(user_a, user_b):
    conn = get_connection()
    row = conn.execute(
        '''SELECT * FROM friendships WHERE
           (requester_id=? AND recipient_id=?) OR (requester_id=? AND recipient_id=?)
           LIMIT 1''',
        (user_a, user_b, user_b, user_a)
    ).fetchone()
    conn.close()
    return row


def get_pending_requests(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM friendships WHERE recipient_id=? AND status='pending'",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows


def get_sent_requests(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM friendships WHERE requester_id=? AND status='pending'",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows


def update_friendship_status(request_id, status, recipient_id):
    conn = get_connection()
    conn.execute(
        'UPDATE friendships SET status=? WHERE id=? AND recipient_id=?',
        (status, request_id, recipient_id)
    )
    conn.commit()
    conn.close()


def get_friends(user_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM friendships
           WHERE (requester_id=? OR recipient_id=?) AND status='accepted'""",
        (user_id, user_id)
    ).fetchall()
    conn.close()
    return rows


def are_friends(user_a, user_b):
    conn = get_connection()
    row = conn.execute(
        """SELECT id FROM friendships WHERE
           ((requester_id=? AND recipient_id=?) OR (requester_id=? AND recipient_id=?))
           AND status='accepted' LIMIT 1""",
        (user_a, user_b, user_b, user_a)
    ).fetchone()
    conn.close()
    return row is not None


# ── Message operations ────────────────────────────────────────────────────────

def insert_message(sender_id, recipient_id, content_enc_recv, content_enc_send):
    mac_data = f"{sender_id}|{recipient_id}|{content_enc_recv}|{content_enc_send}"
    mac_tag  = generate_mac(mac_data, get_mac_key())

    conn = get_connection()
    conn.execute(
        '''INSERT INTO messages
           (sender_id, recipient_id, content_enc_recv, content_enc_send, mac_tag)
           VALUES (?,?,?,?,?)''',
        (sender_id, recipient_id, content_enc_recv, content_enc_send, mac_tag)
    )
    conn.commit()
    conn.close()


def get_conversation(user_a, user_b):
    conn = get_connection()
    rows = conn.execute(
        '''SELECT * FROM messages WHERE
           (sender_id=? AND recipient_id=?) OR (sender_id=? AND recipient_id=?)
           ORDER BY created_at ASC''',
        (user_a, user_b, user_b, user_a)
    ).fetchall()
    conn.close()
    return rows


def verify_message_mac(row):
    mac_data = (f"{row['sender_id']}|{row['recipient_id']}"
                f"|{row['content_enc_recv']}|{row['content_enc_send']}")
    return verify_mac(mac_data, get_mac_key(), row['mac_tag'])


def get_unread_messages_count(user_id):
    conn = get_connection()
    count = conn.execute(
        'SELECT COUNT(*) FROM messages WHERE recipient_id=? AND is_read=0', (user_id,)
    ).fetchone()[0]
    conn.close()
    return count


def get_unread_count_from(user_id, sender_id):
    conn = get_connection()
    count = conn.execute(
        'SELECT COUNT(*) FROM messages WHERE recipient_id=? AND sender_id=? AND is_read=0', (user_id, sender_id)
    ).fetchone()[0]
    conn.close()
    return count


def mark_messages_read(user_id, sender_id):
    conn = get_connection()
    conn.execute(
        'UPDATE messages SET is_read=1 WHERE recipient_id=? AND sender_id=?',
        (user_id, sender_id)
    )
    conn.commit()
    conn.close()
