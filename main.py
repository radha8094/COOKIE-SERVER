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

try:
    import pytz
    KOLKATA = pytz.timezone('Asia/Kolkata')
except ImportError:
    KOLKATA = None

app = Flask(__name__)

# Global Variables
bot_running = False
logs = []
render_start_time = datetime.datetime.now()
total_sent = 0
total_failed = 0
active_users = 0
current_stop_token = ""

def verify_lock():
    check = hashlib.sha256((AUTHOR_NAME + AUTHOR_TAG).encode()).hexdigest()
    return check == SECURITY_KEY

def get_now_time():
    if KOLKATA:
        return datetime.datetime.now(KOLKATA).strftime("%I:%M:%S %p")
    return datetime.datetime.now().strftime("%I:%M:%S %p")

def add_log(status_msg, target_id, actual_msg, color="#0f0"):
    global logs
    now = get_now_time()
    border = "❉═══════RK-PRAJAPAT════════❉"
    formatted_log = (
        f"<div style='color:{color}; margin-bottom:10px; font-weight:bold;'>"
        f"{border}<br>"
        f"COOKIE USER :- {status_msg}<br>"
        f"TARGET ID :- {target_id}<br>"
        f"MSG :- {actual_msg}<br>"
        f"TIME :- {now}<br>"
        f"{border}</div>"
    )
    logs.append(formatted_log)
    if len(logs) > 30: logs.pop(0)

# HTML Dashboard (Same Pink & Gold Theme)
HTML_DASHBOARD = f"""
<!DOCTYPE html>
<html>
<head>
    <title>COOKIE VIP PANEL - {AUTHOR_NAME}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ background-color: #ffb6c1; color: #000; font-family: 'Poppins', sans-serif; text-align: center; margin: 0; padding: 10px; }}
        .gold-name {{ color: #FFD700; font-size: 26px; font-weight: bold; text-shadow: 2px 2px 4px #000; margin-top: 10px; }}
        .blue-sub {{ color: #0000FF; font-size: 13px; font-weight: bold; display: block; }}
        .uptime-live {{ color: #ffffff; background: #000; display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 12px; margin: 15px 0; font-weight: bold; border: 1px solid #ff1493; }}
        .container {{ background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 25px; border: 3px solid #ff1493; display: inline-block; width: 95%; max-width: 600px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .box {{ padding: 12px; margin: 10px 0; border-radius: 12px; font-weight: bold; border: 2px solid #fff; }}
        .blue-box {{ background: #00bfff; color: #fff; }}
        .purple-box {{ background: #9370db; color: #fff; }}
        .pink-box {{ background: #ff69b4; color: #fff; }}
        .orange-box {{ background: #ffa500; color: #fff; }}
        .green-box {{ background: #32cd32; color: #fff; }}
        input, textarea {{ width: 92%; padding: 12px; margin: 5px 0; border-radius: 10px; border: 1px solid #ccc; }}
        .btn-start {{ background: linear-gradient(to right, #ff1493, #ff69b4); color: #fff; padding: 15px; border: none; cursor: pointer; font-weight: bold; width: 95%; border-radius: 12px; font-size: 18px; margin-top: 15px; }}
        .btn-stop {{ background: #000; color: #fff; padding: 15px; border: none; cursor: pointer; font-weight: bold; width: 95%; border-radius: 12px; margin-top: 15px; }}
        .status-box {{ background: #fff; border: 3px solid #ff1493; padding: 15px; margin-top: 20px; border-radius: 15px; text-align: left; }}
        .status-item {{ font-size: 14px; margin: 5px 0; display: flex; justify-content: space-between; border-bottom: 1px dashed #ffb6c1; padding-bottom: 3px; }}
        #console {{ background: #1a1a1a; color: #0f0; text-align: left; padding: 15px; height: 250px; overflow-y: auto; border: 2px solid #ff1493; font-family: monospace; font-size: 11px; margin-top: 20px; border-radius: 12px; }}
    </style>
</head>
<body>
    <div class="gold-name">{AUTHOR_NAME}</div>
    <div class="blue-sub">{AUTHOR_TAG}</div>
    <div class="uptime-live" id="render_uptime">Cookie Server Live: Loading...</div>

    <div class="container">
        <div id="tokenBox" style="background:#ffff00; padding:10px; margin:10px; display:none; border-radius:10px; font-weight:bold; border: 2px solid #000;">
            🔑 STOP TOKEN: <span id="generatedToken">---</span>
        </div>

        <form id="botForm">
            <div class="box blue-box">🆔 TARGET CONVO ID</div>
            <input type="text" id="convo_id" placeholder="Enter Target ID..." required>
            
            <div class="box purple-box">👤 HATER NAME</div>
            <input type="text" id="hater_name" placeholder="Enter Name..." required>
            
            <div class="box pink-box">🍪 PASTE COOKIES (ONE PER LINE)</div>
            <textarea id="cookies" placeholder="Paste Your Cookies Here..." rows="3" required></textarea>
            
            <div class="box orange-box">📤 UPLOAD MESSAGES (FILE.TXT)</div>
            <input type="file" id="fileInput" accept=".txt">
            
            <div class="box green-box">⚡ SPEED (SECONDS)</div>
            <input type="number" id="speed" placeholder="Speed" required>
            
            <button type="button" class="btn-start" onclick="startBot()">🚀 START COOKIE SERVER</button>
            <button type="button" class="btn-stop" onclick="stopBot()">🛑 STOP SERVER</button>
            <input type="text" id="stop_token_input" placeholder="Paste Stop Token to Stop" style="margin-top:10px;">
        </form>

        <div class="status-box">
            <div class="status-item"><span>🚀 Active Users:</span> <span id="active_users">1</span></div>
            <div class="status-item"><span>✅ Sent:</span> <span id="sent" style="color:green;">0</span></div>
            <div class="status-item"><span>❌ Failed:</span> <span id="failed" style="color:red;">0</span></div>
        </div>

        <div id="console">⌨️ Cookie Logs Ready...</div>
    </div>

    <script>
        let uploadedMessages = "";
        document.getElementById('fileInput').addEventListener('change', function(e) {{
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {{ uploadedMessages = e.target.result; alert("✅ Messages Loaded!"); }};
            reader.readAsText(file);
        }});

        function startBot() {{
            const data = {{
                convo_id: document.getElementById('convo_id').value,
                hater_name: document.getElementById('hater_name').value,
                cookies: document.getElementById('cookies').value,
                messages: uploadedMessages,
                speed: document.getElementById('speed').value
            }};
            fetch('/start', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(data) }})
            .then(res => res.json()).then(resData => {{
                if(resData.error) {{ alert(resData.error); return; }}
                document.getElementById('tokenBox').style.display = 'block';
                document.getElementById('generatedToken').innerText = resData.token;
            }});
        }}

        function stopBot() {{
            const code = document.getElementById('stop_token_input').value;
            fetch('/stop', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{code: code}}) }})
            .then(res => res.json()).then(data => alert(data.message));
        }}

        function updateUI() {{
            fetch('/status').then(res => res.json()).then(data => {{
                document.getElementById('render_uptime').innerText = "Cookie Server Live: " + data.render_uptime;
                document.getElementById('sent').innerText = data.sent;
                document.getElementById('failed').innerText = data.failed;
                document.getElementById('active_users').innerText = data.users;
                document.getElementById('console').innerHTML = data.logs.join('');
                const consoleDiv = document.getElementById('console');
                consoleDiv.scrollTop = consoleDiv.scrollHeight;
            }});
        }}
        setInterval(updateUI, 2000);
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
            full_msg = f"{hater_name} {msg.strip()}"
            
            # Simple Cookie Header Setup
            headers = {
                'Cookie': cookie,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            try:
                # FB Cookie based message sending logic
                # Note: Exact endpoint depends on FB version (mbasic/touch)
                url = f"https://mbasic.facebook.com/messages/send/?icm=1&tids=cid.c.{convo_id}"
                # For this demo, using a standard request pattern
                res = requests.post(url, data={'body': full_msg}, headers=headers)
                
                if res.status_code == 200:
                    total_sent += 1
                    add_log("SUCCESS", convo_id, full_msg, color="#0f0")
                else:
                    total_failed += 1
                    add_log("FAIL", convo_id, "Cookie Dead", color="#f00")
            except:
                total_failed += 1
            time.sleep(int(speed))

@app.route('/')
def index():
    global active_users
    active_users += 1
    if not verify_lock(): return "<h1>FILE TAMPERED!</h1>"
    return render_template_string(HTML_DASHBOARD)

@app.route('/status')
def get_status():
    r_td = datetime.datetime.now() - render_start_time
    return jsonify(render_uptime=str(r_td).split('.')[0], sent=total_sent, failed=total_failed, users=active_users, logs=logs)

@app.route('/start', methods=['POST'])
def start():
    global bot_running, current_stop_token
    current_stop_token = "RAVI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    data = request.json
    cookie_list = data.get('cookies').splitlines()
    threading.Thread(target=message_sender, args=(data.get('convo_id'), data.get('hater_name'), cookie_list, data.get('messages'), data['speed'])).start()
    return jsonify(token=current_stop_token)

@app.route('/stop', methods=['POST'])
def stop():
    global bot_running
    if request.json.get('code') == current_stop_token:
        bot_running = False
        return jsonify(message="🛑 Cookie Server Stopped!")
    return jsonify(message="❌ Invalid Token!")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
