from flask import Blueprint, request, redirect, url_for, render_template, flash

from database import (
    get_all_users, get_user_by_id,
    send_friend_request, get_friendship,
    get_pending_requests, get_sent_requests, update_friendship_status,
    get_friends, are_friends,
    insert_message, get_conversation, verify_message_mac, get_posts_by_user,
    mark_messages_read, get_unread_count_from
)
from models.user import User
from routes.auth import login_required
from crypto.rsa import encrypt as rsa_encrypt, decrypt as rsa_decrypt
from crypto.ecc import ecdh_shared_secret

social_bp = Blueprint('social', __name__)


# ── User directory & public profiles ─────────────────────────────────────────

@social_bp.route('/users')
@login_required
def user_list(user):
    rows = get_all_users()
    entries = []
    for r in rows:
        if r['id'] == user.id:
            continue
        u = User(r)
        fs = get_friendship(user.id, r['id'])
        entries.append({
            'id':          u.id,
            'username':    u.username,
            'role':        u.role,
            'status':      fs['status'] if fs else None,
            'is_requester': fs['requester_id'] == user.id if fs else False,
            'fs_id':       fs['id'] if fs else None,
        })
    return render_template('users.html', entries=entries, user=user)


@social_bp.route('/users/<int:target_id>')
@login_required
def user_profile(user, target_id):
    row = get_user_by_id(target_id)
    if row is None:
        flash('Creator not found.', 'danger')
        return redirect(url_for('social.user_list'))
    target = User(row)
    fs = get_friendship(user.id, target_id)
    
    # Fetch posts to display on the profile
    raw_posts = get_posts_by_user(target_id)
    posts = []
    
    status = fs['status'] if fs else None
    
    for p in raw_posts:
        is_unencrypted = p['title_enc'].startswith('[UNENCRYPTED]')
        if is_unencrypted:
            title = p['title_enc'].replace('[UNENCRYPTED]', '', 1)
            content = p['content_enc'].replace('[UNENCRYPTED]', '', 1)
            is_locked = False
        elif status == 'accepted' or target_id == user.id:
            try:
                title = rsa_decrypt(p['title_enc'], target.get_rsa_priv())
                content = rsa_decrypt(p['content_enc'], target.get_rsa_priv())
                is_locked = False
            except Exception:
                title = '[Decryption Failed]'
                content = ''
                is_locked = True
        else:
            title = '🔒 Encrypted Post'
            content = 'Subscribe to unlock this content.'
            is_locked = True
            
        posts.append({
            'id': p['id'],
            'title': title,
            'content': content,
            'created_at': p['created_at'],
            'is_locked': is_locked
        })

    return render_template('user_profile.html',
                           target=target, user=user,
                           posts=posts,
                           status=status,
                           is_requester=fs['requester_id'] == user.id if fs else False,
                           fs_id=fs['id'] if fs else None)


# ── Friend request management ─────────────────────────────────────────────────

@social_bp.route('/friends')
@login_required
def friends(user):
    friends_list, pending_in, pending_out = [], [], []

    for r in get_friends(user.id):
        other_id = r['recipient_id'] if r['requester_id'] == user.id else r['requester_id']
        other_row = get_user_by_id(other_id)
        if other_row:
            friends_list.append({'fs_id': r['id'], 'u': User(other_row)})

    for r in get_pending_requests(user.id):
        req_row = get_user_by_id(r['requester_id'])
        if req_row:
            pending_in.append({'req_id': r['id'], 'u': User(req_row)})

    for r in get_sent_requests(user.id):
        rec_row = get_user_by_id(r['recipient_id'])
        if rec_row:
            pending_out.append({'req_id': r['id'], 'u': User(rec_row)})

    return render_template('friends.html',
                           friends_list=friends_list,
                           pending_in=pending_in,
                           pending_out=pending_out,
                           user=user)


@social_bp.route('/friends/request/<int:target_id>', methods=['POST'])
@login_required
def friend_request(user, target_id):
    if target_id == user.id:
        flash('Cannot subscribe to yourself.', 'warning')
        return redirect(url_for('social.user_list'))
    if get_friendship(user.id, target_id):
        flash('A subscription request already exists.', 'info')
        return redirect(url_for('social.user_list'))
    send_friend_request(user.id, target_id)
    flash('Subscription request sent.', 'success')
    return redirect(url_for('social.user_list'))


@social_bp.route('/friends/accept/<int:req_id>', methods=['POST'])
@login_required
def accept_request(user, req_id):
    update_friendship_status(req_id, 'accepted', user.id)
    flash('Friend request accepted.', 'success')
    return redirect(url_for('social.friends'))


@social_bp.route('/friends/reject/<int:req_id>', methods=['POST'])
@login_required
def reject_request(user, req_id):
    update_friendship_status(req_id, 'rejected', user.id)
    flash('Friend request rejected.', 'info')
    return redirect(url_for('social.friends'))


# ── E2E encrypted conversation ────────────────────────────────────────────────

@social_bp.route('/inbox')
@login_required
def inbox(user):
    friends_list = []
    for r in get_friends(user.id):
        other_id = r['recipient_id'] if r['requester_id'] == user.id else r['requester_id']
        other_row = get_user_by_id(other_id)
        if other_row:
            unread = get_unread_count_from(user.id, other_id)
            friends_list.append({'u': User(other_row), 'unread': unread})
    
    # Sort so those with unread messages are at the top
    friends_list.sort(key=lambda x: x['unread'], reverse=True)
    
    return render_template('inbox.html', friends_list=friends_list, user=user)

@social_bp.route('/messages/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def conversation(user, friend_id):
    if not are_friends(user.id, friend_id):
        flash('You must be friends to send messages.', 'danger')
        return redirect(url_for('social.friends'))

    friend_row = get_user_by_id(friend_id)
    if friend_row is None:
        flash('User not found.', 'danger')
        return redirect(url_for('social.friends'))
    friend = User(friend_row)

    # Mark messages as read
    mark_messages_read(user.id, friend_id)

    if request.method == 'POST':
        content = request.form.get('content', '').strip()

        if not content:
            flash('Message cannot be empty.', 'danger')
            return redirect(url_for('social.conversation', friend_id=friend_id))

        # E2E encryption (Req 9/10):
        # Two RSA-encrypted copies so each party can decrypt with their own private key
        content_enc_recv = rsa_encrypt(content, friend.rsa_pub)
        content_enc_send = rsa_encrypt(content, user.rsa_pub)

        insert_message(user.id, friend_id, content_enc_recv, content_enc_send)
        return redirect(url_for('social.conversation', friend_id=friend_id))

    # Decrypt conversation for display
    rows = get_conversation(user.id, friend_id)
    msgs = []
    rsa_priv = user.get_rsa_priv()
    for row in rows:
        mac_ok = verify_message_mac(row)
        is_mine = row['sender_id'] == user.id
        try:
            # Each party decrypts the copy that was encrypted for them
            enc_field = row['content_enc_send'] if is_mine else row['content_enc_recv']
            if enc_field.startswith('[UNENCRYPTED]'):
                text = enc_field.replace('[UNENCRYPTED]', '', 1)
            else:
                text = rsa_decrypt(enc_field, rsa_priv)
        except Exception:
            text = '[decryption failed]'
        msgs.append({
            'text':       text,
            'is_mine':    is_mine,
            'created_at': row['created_at'],
            'mac_valid':  mac_ok,
        })

    # ECDH: derive shared secret to show the authenticated channel (Req 10 — ECC usage)
    try:
        shared_hex     = ecdh_shared_secret(user.get_ecc_priv(), friend.ecc_pub)
        shared_preview = shared_hex[:16] + '…'
    except Exception:
        shared_preview = 'unavailable'

    return render_template('conversation.html',
                           friend=friend, messages=msgs,
                           shared_preview=shared_preview,
                           user=user)
