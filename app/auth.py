from flask import Blueprint, request, jsonify, session, current_app
from ldap3 import Server, Connection, ALL, SUBTREE
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

def ldap_authenticate(username, password):
    """Try to bind to AD with the given username/password. Returns True/False."""
    ldap_host = current_app.config['LDAP_HOST']
    ldap_port = current_app.config['LDAP_PORT']
    use_ssl = current_app.config['LDAP_USE_SSL']

    server = Server(ldap_host, port=ldap_port, use_ssl=use_ssl, get_info=ALL)

    # AD accepts "user@domain" format for simple binds
    user_dn = f"{username}@ctf.local"

    try:
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        conn.unbind()
        return True
    except Exception as e:
        current_app.logger.warning(f"LDAP bind failed for {username}: {e}")
        return False

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    if ldap_authenticate(username, password):
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
