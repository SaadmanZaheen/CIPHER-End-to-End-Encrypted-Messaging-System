import os
import secrets
from flask import Flask, session, render_template
from database import init_db, get_pending_requests, get_unread_messages_count
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.social import social_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(social_bp)


@app.context_processor
def inject_nav_counts():
    """Inject friend-request and unread-message counts into every template."""
    pending_count = 0
    unread_msgs   = 0
    uid = session.get('uid')
    if uid:
        pending_count = len(get_pending_requests(uid))
        unread_msgs   = get_unread_messages_count(uid)
    return dict(pending_count=pending_count, unread_msgs=unread_msgs)


@app.route('/')
def index():
    return render_template('landing.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
