from flask import Blueprint, request, jsonify, session, current_app
from ldap3 import Server, Connection, ALL, SUBTREE
from datetime import datetime, timedelta
from app.models import db, User, LoginAttempt

auth_bp = Blueprint('auth', __name__)

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 10

def ldap_authenticate(username, password):
    """Try to bind to AD with the given username/password. Returns True/False."""
    ldap_host = current_app.config['LDAP_HOST']
    ldap_port = current_app.config['LDAP_PORT']
    use_ssl = current_app.config['LDAP_USE_SSL']

    server = Server(ldap_host, port=ldap_port, use_ssl=use_ssl, get_info=ALL)
    user_dn = f"{username}@ctf.local"

    try:
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        conn.unbind()
        return True
    except Exception as e:
        current_app.logger.warning(f"LDAP bind failed for {username}: {e}")
        return False

def is_locked_out(username):
    """Check if this username has too many recent failed attempts."""
    cutoff = datetime.utcnow() - timedelta(minutes=LOCKOUT_MINUTES)
    recent_failures = LoginAttempt.query.filter(
        LoginAttempt.username == username,
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= cutoff
    ).count()
    return recent_failures >= MAX_ATTEMPTS

def record_attempt(username, success):
    attempt = LoginAttempt(username=username, success=success)
    db.session.add(attempt)
    db.session.commit()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    if is_locked_out(username):
        return jsonify({
            'error': f'account temporarily locked due to repeated failed attempts. Try again in {LOCKOUT_MINUTES} minutes.'
        }), 429

    if ldap_authenticate(username, password):
        record_attempt(username, success=True)

        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, display_name=username)
            db.session.add(user)
            db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username

        return jsonify({
            'message': 'login successful',
            'username': user.username
        }), 200
    else:
        record_attempt(username, success=False)
        return jsonify({'error': 'invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'logged out'}), 200

@auth_bp.route('/whoami', methods=['GET'])
def whoami():
    if 'username' in session:
        return jsonify({'username': session['username']}), 200
    return jsonify({'error': 'not logged in'}), 401
