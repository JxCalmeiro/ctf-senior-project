from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'vuln.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, is_admin INTEGER)')
    c.execute("INSERT INTO users (username, password, is_admin) VALUES ('guest', 'guestpass', 0)")
    c.execute("INSERT INTO users (username, password, is_admin) VALUES ('admin', 'S3cur3AdminPass!9284', 1)")
    conn.commit()
    conn.close()

LOGIN_PAGE = """
<!DOCTYPE html>
<html><head><title>Portal Login</title>
<style>
body { font-family: sans-serif; background: #0d1117; color: #c9d1d9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
.box { background: #161b22; padding: 40px; border-radius: 8px; border: 1px solid #30363d; }
input { display: block; margin: 10px 0; padding: 8px; width: 200px; background: #0d1117; border: 1px solid #30363d; color: #fff; }
button { padding: 8px 20px; background: #238636; color: white; border: none; border-radius: 4px; cursor: pointer; }
.result { margin-top: 20px; padding: 10px; border-radius: 4px; }
.success { background: #1a4d2e; }
.fail { background: #4d1a1a; }
</style></head>
<body>
<div class="box">
  <h2>Internal Portal Login</h2>
  <form method="POST">
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <button type="submit">Login</button>
  </form>
  {% if result %}
  <div class="result {{ 'success' if success else 'fail' }}">{{ result }}</div>
  {% endif %}
</div>
</body></html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    result = None
    success = False
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Intentionally vulnerable - direct string formatting, no parameterization
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            c.execute(query)
            row = c.fetchone()
            if row:
                if row[3] == 1:
                    result = f"Welcome admin! Flag: CTF{{sq1i_bypasses_auth_logic}}"
                    success = True
                else:
                    result = f"Welcome, {row[1]}. (Not an admin.)"
                    success = True
            else:
                result = "Invalid credentials."
        except Exception as e:
            result = f"Database error: {str(e)}"
        conn.close()

    return render_template_string(LOGIN_PAGE, result=result, success=success)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)

