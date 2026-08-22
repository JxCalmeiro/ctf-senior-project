import hashlib
import hmac
import subprocess
import os
from flask import Flask, request, abort

app = Flask(__name__)

# Set this as an environment variable, not hardcoded
SECRET = os.environ.get('WEBHOOK_SECRET', '').encode()
REPO_PATH = '/home/serveradmin/ctf-app'
COMPOSE_FILE = f'{REPO_PATH}/docker-compose.yml'

def verify_signature(payload, signature):
    if not SECRET:
        return False
    mac = hmac.new(SECRET, msg=payload, digestmod=hashlib.sha256)
    expected = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected, signature or "")

@app.route('/webhook', methods=['POST'])
def webhook():
    sig = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, sig):
        abort(403)

    payload = request.json
    if payload.get('ref') == 'refs/heads/main':
        subprocess.run(['git', '-C', REPO_PATH, 'pull'], check=True)
        subprocess.run(
            ['docker', 'compose', '-f', COMPOSE_FILE, 'up', '-d', '--build'],
            check=True
        )
        return 'Deployed', 200

    return 'Ignored (not main branch)', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
