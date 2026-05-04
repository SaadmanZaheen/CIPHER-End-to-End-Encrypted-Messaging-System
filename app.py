import os
import secrets
from flask import Flask, redirect, url_for, session, render_template, send_from_directory
from database import init_db, get_pending_requests, get_unread_messages_count
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.social import social_bp

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # regenerated each restart; sessions cleared on restart

init_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(social_bp)

@app.context_processor
def inject_pending_requests():
    count = 0
    unread = 0
    uid = session.get('uid')
    if uid:
        reqs = get_pending_requests(uid)
        count = len(reqs)
        unread = get_unread_messages_count(uid)
    return dict(pending_count=count, unread_msgs=unread)

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/cipher')
def cipher():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'CIPHER.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
