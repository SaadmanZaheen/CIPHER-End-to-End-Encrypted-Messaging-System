from flask import Blueprint, request, session, redirect, url_for, render_template, flash

from database import (
    insert_post, get_posts_by_user, get_post_by_id,
    update_post, delete_post, get_all_posts, get_user_by_id, get_all_users,
    verify_post_mac, update_user_role, are_friends
)
from models.user import User
from routes.auth import login_required, admin_required
from crypto.ecc import ecdh_shared_secret, ecdsa_sign, ecdsa_verify
from crypto.rsa import encrypt as rsa_encrypt, decrypt as rsa_decrypt

posts_bp = Blueprint('posts', __name__)


def _post_decrypt(ciphertext, rsa_priv):
    if ciphertext.startswith('[UNENCRYPTED]'):
        return ciphertext.replace('[UNENCRYPTED]', '', 1)
    return rsa_decrypt(ciphertext, rsa_priv)


# ── Routes ────────────────────────────────────────────────────────────────────

@posts_bp.route('/feed')
@login_required
def feed(user):
    """Show all posts visible to the current user, decrypted with their RSA key."""
    rows = get_all_posts()
    posts = []
    for row in rows:
        if not verify_post_mac(row):
            continue  # skip tampered posts silently
        author_row = get_user_by_id(row['user_id'])
        if author_row is None:
            continue
        author = User(author_row)

        ecc_valid = ecdsa_verify(
            row['title_enc'] + row['content_enc'],
            row['ecc_sig'],
            author.ecc_pub
        ) if row['ecc_sig'] else None

        is_owner = (row['user_id'] == user.id)
        is_subscribed = are_friends(user.id, author.id)
        is_unencrypted = row['title_enc'].startswith('[UNENCRYPTED]')
        
        if is_unencrypted:
            title     = row['title_enc'].replace('[UNENCRYPTED]', '', 1)
            content   = row['content_enc'].replace('[UNENCRYPTED]', '', 1)
            is_locked = False
        elif is_owner or is_subscribed:
            try:
                title   = _post_decrypt(row['title_enc'],   author.get_rsa_priv())
                content = _post_decrypt(row['content_enc'], author.get_rsa_priv())
                is_locked = False
            except Exception:
                title   = '[Decryption Failed]'
                content = ''
                is_locked = True
        else:
            title   = '🔒 Encrypted Post'
            content = 'Add to unlock this content.'
            is_locked = True

        posts.append({
            'id':         row['id'],
            'author':     author.username,
            'author_id':  author.id,
            'title':      title,
            'content':    content,
            'created_at': row['created_at'],
            'is_owner':   is_owner,
            'mac_valid':  True,
            'ecc_valid':  ecc_valid,
            'is_locked':  is_locked
        })
    return render_template('feed.html', posts=posts, user=user)


@posts_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post(user):
    if request.method == 'GET':
        return render_template('new_post.html', user=user)

    title   = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    encrypt_post = request.form.get('encrypt_post') == '1'
    if not title or not content:
        flash('Title and content are required.', 'danger')
        return render_template('new_post.html', user=user)

    if encrypt_post:
        title_enc   = rsa_encrypt(title,   user.rsa_pub)
        content_enc = rsa_encrypt(content, user.rsa_pub)
        ecc_sig = ecdsa_sign(title_enc + content_enc, user.get_ecc_priv())
    else:
        title_enc   = f"[UNENCRYPTED]{title}"
        content_enc = f"[UNENCRYPTED]{content}"
        ecc_sig     = ''

    post_id = insert_post(user.id, title_enc, content_enc, ecc_sig)
    flash('Post created.', 'success')
    return redirect(url_for('posts.feed'))


@posts_bp.route('/post/<int:post_id>')
@login_required
def view_post(user, post_id):
    row = get_post_by_id(post_id)
    if row is None:
        flash('Post not found.', 'danger')
        return redirect(url_for('posts.feed'))

    mac_valid = verify_post_mac(row)
    author_row = get_user_by_id(row['user_id'])
    author = User(author_row)

    ecc_valid = ecdsa_verify(
        row['title_enc'] + row['content_enc'],
        row['ecc_sig'],
        author.ecc_pub
    ) if row['ecc_sig'] else None

    is_unencrypted = row['title_enc'].startswith('[UNENCRYPTED]')
    if is_unencrypted:
        title   = row['title_enc'].replace('[UNENCRYPTED]', '', 1)
        content = row['content_enc'].replace('[UNENCRYPTED]', '', 1)
    elif row['user_id'] == user.id:
        try:
            title   = _post_decrypt(row['title_enc'],   user.get_rsa_priv())
            content = _post_decrypt(row['content_enc'], user.get_rsa_priv())
        except Exception:
            title = content = '[decryption failed]'
    else:
        title   = '[encrypted — private post]'
        content = '[Only the author can decrypt this post.]'

    return render_template('view_post.html', post={
        'id': row['id'], 'title': title, 'content': content,
        'author': author.username, 'created_at': row['created_at'],
        'is_owner': row['user_id'] == user.id,
        'mac_valid': mac_valid, 'ecc_valid': ecc_valid,
    }, user=user)


@posts_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(user, post_id):
    row = get_post_by_id(post_id)
    if row is None or row['user_id'] != user.id:
        flash('Not found or access denied.', 'danger')
        return redirect(url_for('posts.feed'))

    if request.method == 'GET':
        try:
            title   = _post_decrypt(row['title_enc'],   user.get_rsa_priv())
            content = _post_decrypt(row['content_enc'], user.get_rsa_priv())
        except Exception:
            title = content = ''
        return render_template('edit_post.html', post_id=post_id,
                               title=title, content=content, user=user)

    title   = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    encrypt_post = request.form.get('encrypt_post') == '1'

    if not title or not content:
        flash('Title and content are required.', 'danger')
        return redirect(url_for('posts.edit_post', post_id=post_id))

    if encrypt_post:
        title_enc   = rsa_encrypt(title, user.rsa_pub)
        content_enc = rsa_encrypt(content, user.rsa_pub)
        ecc_sig     = ecdsa_sign(title_enc + content_enc, user.get_ecc_priv())
    else:
        title_enc   = f"[UNENCRYPTED]{title}"
        content_enc = f"[UNENCRYPTED]{content}"
        ecc_sig     = ''
    update_post(post_id, title_enc, content_enc, ecc_sig)
    flash('Post updated.', 'success')
    return redirect(url_for('posts.view_post', post_id=post_id))


@posts_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post_route(user, post_id):
    row = get_post_by_id(post_id)
    if row is None or row['user_id'] != user.id:
        flash('Not found or access denied.', 'danger')
        return redirect(url_for('posts.feed'))
    delete_post(post_id)
    flash('Post deleted.', 'success')
    return redirect(url_for('posts.my_posts'))


@posts_bp.route('/my-posts')
@login_required
def my_posts(user):
    rows = get_posts_by_user(user.id)
    posts = []
    rsa_priv = user.get_rsa_priv()
    for row in rows:
        mac_valid = verify_post_mac(row)
        try:
            title   = _post_decrypt(row['title_enc'],   rsa_priv)
            content = _post_decrypt(row['content_enc'], rsa_priv)
        except Exception:
            title = '[error]'; content = ''
        posts.append({
            'id': row['id'], 'title': title, 'content': content,
            'created_at': row['created_at'], 'mac_valid': mac_valid
        })
    return render_template('my_posts.html', posts=posts, user=user)


# ── Admin views ───────────────────────────────────────────────────────────────

@posts_bp.route('/admin/users')
@admin_required
def admin_users(user):
    rows  = get_all_users()
    users = [User(r) for r in rows]
    return render_template('admin_users.html', users=users, current_user=user)


@posts_bp.route('/admin/users/<int:target_id>/promote', methods=['POST'])
@admin_required
def promote_user(user, target_id):
    row = get_user_by_id(target_id)
    if row is None:
        flash('User not found.', 'danger')
        return redirect(url_for('posts.admin_users'))
    target = User(row)
    if target.is_admin():
        flash(f'{target.username} is already an admin.', 'warning')
        return redirect(url_for('posts.admin_users'))
    update_user_role(target_id, 'admin')
    flash(f'{target.username} promoted to admin.', 'success')
    return redirect(url_for('posts.admin_users'))


@posts_bp.route('/admin/users/<int:target_id>/demote', methods=['POST'])
@admin_required
def demote_user(user, target_id):
    if target_id == user.id:
        flash('You cannot demote yourself.', 'danger')
        return redirect(url_for('posts.admin_users'))
    row = get_user_by_id(target_id)
    if row is None:
        flash('User not found.', 'danger')
        return redirect(url_for('posts.admin_users'))
    target = User(row)
    update_user_role(target_id, 'user')
    flash(f'{target.username} demoted to user.', 'success')
    return redirect(url_for('posts.admin_users'))


@posts_bp.route('/admin/posts')
@admin_required
def admin_posts(user):
    rows  = get_all_posts()
    posts = []
    for row in rows:
        mac_valid  = verify_post_mac(row)
        author_row = get_user_by_id(row['user_id'])
        author     = User(author_row) if author_row else None
        posts.append({
            'id':         row['id'],
            'author':     author.username if author else '?',
            'created_at': row['created_at'],
            'mac_valid':  mac_valid,
        })
    return render_template('admin_posts.html', posts=posts, current_user=user)
