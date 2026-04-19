import requests
import time
import threading
import os
import datetime
import random
import string
import hashlib
from flask import Flask, render_template_string, request, jsonify

# --- SECURITY LOCK ---
AUTHOR_NAME = "MR. RAVI KUMAR PRAJAPAT"
AUTHOR_TAG = "RAVI KUMAR CONVO NONSTOP"
SECURITY_KEY = hashlib.sha256((AUTHOR_NAME + AUTHOR_TAG).encode()).hexdigest()

app = Flask(__name__)

# Global Variables
bot_running = False
logs = []
render_start_time = datetime.datetime.now()
total_sent = 0
total_failed = 0

def add_log(status_msg, target_id, actual_msg, color="#0f0"):
    global logs
    now = datetime.datetime.now().strftime("%I:%M:%S %p")
    border = "❉═══════RK-PRAJAPAT════════❉"
    formatted_log = (
        f"<div style='color:{color}; margin-bottom:10px; font-weight:bold;'>"
        f"{border}<br>"
        f"STATUS :- {status_msg}<br>"
        f"TARGET ID :- {target_id}<br>"
        f"MSG :- {actual_msg}<br>"
        f"TIME :- {now}<br>"
        f"{border}</div>"
    )
    logs.append(formatted_log)
    if len(logs) > 30: logs.pop(0)

# Dashboard UI (Same Stylish Look)
HTML_DASHBOARD = f"""
<!DOCTYPE html>
<html>
<head>
    <title>VIP COOKIE FIX - {AUTHOR_NAME}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ background-color: #ffb6c1; color: #000; font-family: sans-serif; text-align: center; padding: 10px; }}
        .gold-name {{ color: #FFD700; font-size: 24px; font-weight: bold; text-shadow: 2px 2px #000; }}
        .container {{ background: white; padding: 20px; border-radius: 20px; border: 3px solid #ff1493; display: inline-block; width: 95%; max-width: 500px; }}
        .box {{ background: #ff1493; color: white; padding: 10px; margin: 10px 0; border-radius: 10px; font-weight: bold; }}
        input, textarea {{ width: 90%; padding: 10px; margin: 5px 0; border-radius: 10px; border: 1px solid #ccc; }}
        #console {{ background: #000; color: #0f0; text-align: left; padding: 15px; height: 250px; overflow-y: auto; font-size: 11px; margin-top: 20px; border-radius: 10px; }}
        .btn {{ background: #ff1493; color: white; padding: 15px; border: none; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="gold-name">{AUTHOR_NAME}</div>
    <div class="container">
        <form id="botForm">
            <div class="box">🆔 GROUP ID</div>
            <input type="text" id="convo_id" placeholder="Enter ID (e.g. 8953...)" required>
            <div class="box">👤 HATER NAME</div>
            <input type="text" id="hater_name" placeholder="Name..." required>
            <div class="box">🍪 COOKIES</div>
            <textarea id="cookies" placeholder="Paste Cookies..." rows="3" required></textarea>
            <div class="box">📤 UPLOAD FILE.TXT</div>
            <input type="file" id="fileInput" accept=".txt">
            <div class="box">⚡ SPEED (SECONDS)</div>
            <input type="number" id="speed" value="60" required>
            <button type="button" class="btn" onclick="startBot()">🚀 START FIXED SERVER</button>
        </form>
        <div id="console">Ready...</div>
    </div>

    <script>
        let uploadedMessages = "";
        document.getElementById('fileInput').addEventListener('change', function(e) {{
            const reader = new FileReader();
            reader.onload = function(e) {{ uploadedMessages = e.target.result; }};
            reader.readAsText(e.target.files[0]);
        }});

        function startBot() {{
            const data = {{
                convo_id: document.getElementById('convo_id').value,
                hater_name: document.getElementById('hater_name').value,
                cookies: document.getElementById('cookies').value,
                messages: uploadedMessages,
                speed: document.getElementById('speed').value
            }};
            fetch('/start', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(data) }});
        }}

        setInterval(() => {{
            fetch('/status').then(res => res.json()).then(data => {{
                document.getElementById('console').innerHTML = data.logs.join('');
            }});
        }}, 2000);
    </script>
</body>
</html>
"""

def message_sender(convo_id, hater_name, cookies, messages, speed):
    global bot_running, total_sent, total_failed
    bot_running = True
    msg_list = messages.splitlines()
    num_cookies = len(cookies)
    
    while bot_running:
        for i, msg in enumerate(msg_list):
            if not bot_running: break
            cookie = cookies[i % num_cookies].strip()
            # Prefixing 't_' for Group Conversations
            target = f"t_{convo_id}" if not convo_id.startswith('t_') else convo_id
            full_msg = f"{hater_name} {msg.strip()}"
            
            # Using API Style Headers
            headers = {
                'authority': 'm.facebook.com',
                'accept': '*/*',
                'cookie': cookie,
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
            }
            
            try:
                # Updated Endpoint for better delivery
                url = f"https://m.facebook.com/messages/send/?icm=1&tids=cid.c.{convo_id}"
                # Adding FB dtsg token would be better, but we'll try with Direct Body first
                payload = {
                    'body': full_msg,
                    'tids': f'cid.c.{convo_id}',
                    'www_dot_messenger_dot_com_messaging_send_message_sent': '1'
                }
                res = requests.post(url, data=payload, headers=headers)
                
                # Check if message actually landed
                if res.status_code == 200 and "error" not in res.text.lower():
                    total_sent += 1
                    add_log("MESSAGE DELIVERED ✅", convo_id, full_msg, color="#0f0")
                else:
                    total_failed += 1
                    add_log("FB BLOCKED DELIVERY ❌", convo_id, "Check Cookie/Speed", color="#f00")
            except:
                total_failed += 1
            time.sleep(int(speed))

@app.route('/')
def index(): return render_template_string(HTML_DASHBOARD)

@app.route('/status')
def get_status(): return jsonify(logs=logs)

@app.route('/start', methods=['POST'])
def start():
    data = request.json
    cookies = data.get('cookies').splitlines()
    threading.Thread(target=message_sender, args=(data.get('convo_id'), data.get('hater_name'), cookies, data.get('messages'), data['speed'])).start()
    return jsonify(status="Started")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

