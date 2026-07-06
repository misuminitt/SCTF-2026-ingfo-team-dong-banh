from flask import Flask, request, render_template, redirect, session, jsonify
import os
import secrets

app = Flask(__name__)
app.secret_key = os.urandom(32)

users = {}
reports = []

# Admin setup
admin_username = 'admin'
admin_password = secrets.token_hex(16)
admin_token = secrets.token_hex(16) # 32 chars long
users[admin_username] = {
    'password': admin_password,
    'url': 'http://example.com',
    'token': admin_token
}

FLAG = "SCTF26{REDACTED}"

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "frame-ancestors 'none'; form-action 'self'; connect-src 'self'; script-src 'self'; font-src 'self'; style-src 'self';"
    return response

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/urlstorage')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect('/urlstorage')
    return "Invalid credentials", 403

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password and username not in users:
        users[username] = {
            'password': password,
            'url': 'http://example.com',
            'token': secrets.token_hex(16) # 32 chars
        }
        session['username'] = username
        return redirect('/urlstorage')
    return "Registration failed", 400

@app.route('/urlstorage', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/urlstorage/<path:path>', methods=['GET', 'POST'])
def urlstorage(path):
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    
    if request.method == 'POST':
        url = request.form.get('url', '')
        users[username]['url'] = url
        return redirect('/urlstorage')
        
    user_url = users[username]['url']
    token = users[username]['token']
    return render_template('urlstorage.html', url=user_url, token=token)

@app.route('/flag', methods=['GET'])
def flag():
    # Vulnerability: XSS in token (limit 64 chars)
    token_input = request.args.get('token', '')
    if len(token_input) > 64:
        return "Token too long! Max 64 chars.", 400
        
    # Valid token is only the first 32 characters
    flag_token = token_input[:32]
    
    is_admin = (flag_token == admin_token)
        
    return render_template('flag.html', token=token_input, is_admin=is_admin, flag=FLAG)

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        url = request.form.get('url')
        if url and url.startswith('http'):
            reports.append(url)
            return "URL reported to admin! Admin will visit it shortly."
        return "Invalid URL."
    return render_template('report.html')

# API for the bot
@app.route('/api/get_reports')
def get_reports():
    global reports
    ret = reports.copy()
    reports = []
    return jsonify({'reports': ret, 'admin_username': admin_username, 'admin_password': admin_password})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
