import requests
import time
import threading
import datetime
import re
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Global variables for tracking
bot_running = False
logs = []

def add_log(status, target, msg, color="#0f0"):
    global logs
    now = datetime.datetime.now().strftime("%I:%M:%S %p")
    border = "❉═══════RK-PRAJAPAT════════❉"
    formatted = (
        f"<div style='color:{color}; font-weight:bold; margin-bottom:10px;'>"
        f"{border}<br>"
        f"STATUS :- {status}<br>"
        f"TARGET ID :- {target}<br>"
        f"MSG :- {msg}<br>"
        f"TIME :- {now}<br>"
        f"{border}</div>"
    )
    logs.append(formatted)
    if len(logs) > 25:
        logs.pop(0)

def get_fb_tokens(cookie):
    try:
        headers = {
            'cookie': cookie,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        res = requests.get('https://m.facebook.com/', headers=headers).text
        fb_dtsg = re.search(r'name="fb_dtsg" value="(.*?)"', res).group(1)
        jazoest = re.search(r'name="jazoest" value="(.*?)"', res).group(1)
        return fb_dtsg, jazoest
    except:
        return None, None

def bot_logic(convo_id, hater_name, cookies, messages, speed):
    global bot_running
    bot_running = True
    msg_list = messages.splitlines()
    cookie_list = cookies.splitlines()

    while bot_running:
        for i, msg in enumerate(msg_list):
            if not bot_running:
                add_log("STOPPED 🛑", convo_id, "Server manually stopped", color="#ff0")
                return
            
            current_cookie = cookie_list[i % len(cookie_list)].strip()
            fb_dtsg, jazoest = get_fb_tokens(current_cookie)
            
            if not fb_dtsg:
                add_log("FAILED: Cookie Invalid ❌", convo_id, "---", color="#f00")
                continue

            url = f"https://m.facebook.com/messages/send/?icm=1&tids=cid.c.{convo_id}"
            headers = {
                'cookie': current_cookie,
                'user-agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
                'referer': f'https://m.facebook.com/messages/read/?tid=cid.c.{convo_id}'
            }
            payload = {
                'fb_dtsg': fb_dtsg,
                'jazoest': jazoest,
                'body': f"{hater_name} {msg.strip()}",
                'tids': f'cid.c.{convo_id}',
                'www_dot_messenger_dot_com_messaging_send_message_sent': '1'
            }

            try:
                response = requests.post(url, data=payload, headers=headers)
                if response.status_code == 200:
                    add_log("SUCCESS ✅", convo_id, f"{hater_name} {msg}", color="#0f0")
                else:
                    add_log("FAILED: FB Blocked ❌", convo_id, "---", color="#f00")
            except:
                add_log("ERROR: Network Issue ❌", convo_id, "---", color="#f00")
            
            time.sleep(int(speed))

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MR. RAVI KUMAR PRAJAPAT</title>
        <style>
            body { background-color: #ffb6c1; font-family: sans-serif; text-align: center; margin: 0; padding: 10px; }
            .gold-title { color: gold; font-size: 28px; font-weight: bold; text-shadow: 2px 2px #000; margin-bottom: 20px; }
            .main-box { background: #fff; border: 3px solid #ff1493; border-radius: 20px; padding: 20px; display: inline-block; width: 95%; max-width: 500px; }
            .label-box { background: #ff1493; color: white; padding: 8px; margin: 10px 0; border-radius: 10px; font-weight: bold; font-size: 14px; }
            input, textarea { width: 92%; padding: 10px; margin-bottom: 10px; border-radius: 10px; border: 1px solid #ddd; }
            .btn-start { background: #ff1493; color: white; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 16px; margin-top: 10px; }
            .btn-stop { background: #000; color: #fff; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 16px; margin-top: 10px; }
            #logs-container { background: #000; color: #0f0; text-align: left; padding: 15px; height: 300px; overflow-y: auto; font-size: 11px; margin-top: 20px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="gold-title">MR. RAVI KUMAR PRAJAPAT</div>
        <div class="main-box">
            <input type="text" id="cid" placeholder="Group ID">
            <input type="text" id="hname" placeholder="Hater Name">
            <textarea id="cookies" rows="4" placeholder="Paste Cookies"></textarea>
            <textarea id="msgs" rows="4" placeholder="Paste Messages"></textarea>
            <input type="number" id="speed" value="60">
            
            <button class="btn-start" onclick="startBot()">🚀 START SERVER</button>
            <button class="btn-stop" onclick="stopBot()">🛑 STOP SERVER</button>
            
            <div id="logs-container">Waiting...</div>
        </div>

        <script>
            function startBot() {
                const payload = {
                    cid: document.getElementById('cid').value,
                    hname: document.getElementById('hname').value,
                    cookies: document.getElementById('cookies').value,
                    messages: document.getElementById('msgs').value,
                    speed: document.getElementById('speed').value
                };
                fetch('/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            }

            function stopBot() {
                fetch('/stop', { method: 'POST' }).then(() => alert("Stopping Server..."));
            }

            setInterval(() => {
                fetch('/status').then(res => res.json()).then(data => {
                    document.getElementById('logs-container').innerHTML = data.logs.join('');
                });
            }, 2000);
        </script>
    </body>
    </html>
    ''')

@app.route('/status')
def status():
    return jsonify(logs=logs)

@app.route('/start', methods=['POST'])
def start():
    global bot_running
    if bot_running: return jsonify({"status": "Already running"})
    data = request.json
    thread = threading.Thread(target=bot_logic, args=(data['cid'], data['hname'], data['cookies'], data['messages'], data['speed']))
    thread.daemon = True
    thread.start()
    return jsonify({"status": "Started"})

@app.route('/stop', methods=['POST'])
def stop():
    global bot_running
    bot_running = False
    return jsonify({"status": "Stopped"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
