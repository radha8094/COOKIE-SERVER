import requests
import time
import threading
import os
import datetime
import random
import hashlib
import re
from flask import Flask, render_template_string, request, jsonify

# --- SECURITY LOCK ---
AUTHOR_NAME = "MR. RAVI KUMAR PRAJAPAT"
AUTHOR_TAG = "RAVI KUMAR CONVO NONSTOP"

app = Flask(__name__)

bot_running = False
logs = []
total_sent = 0
total_failed = 0

def add_log(status, target, msg, color="#0f0"):
    global logs
    now = datetime.datetime.now().strftime("%I:%M:%S %p")
    border = "❉═══════RK-PRAJAPAT════════❉"
    formatted = f"<div style='color:{color}; font-weight:bold;'>{border}<br>STATUS :- {status}<br>TARGET :- {target}<br>MSG :- {msg}<br>TIME :- {now}<br>{border}</div><br>"
    logs.append(formatted)
    if len(logs) > 25: logs.pop(0)

def get_fb_dtsg(cookie):
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

def send_message(convo_id, hater_name, cookie, message):
    fb_dtsg, jazoest = get_fb_dtsg(cookie)
    if not fb_dtsg:
        return False, "Cookie Expired or Invalid"

    url = f"https://m.facebook.com/messages/send/?icm=1&tids=cid.c.{convo_id}"
    headers = {
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
        'referer': f'https://m.facebook.com/messages/read/?tid=cid.c.{convo_id}'
    }
    
    data = {
        'fb_dtsg': fb_dtsg,
        'jazoest': jazoest,
        'body': f"{hater_name} {message}",
        'tids': f'cid.c.{convo_id}',
        'www_dot_messenger_dot_com_messaging_send_message_sent': '1'
    }

    try:
        res = requests.post(url, data=data, headers=headers)
        if res.status_code == 200:
            return True, "Success"
        return False, "FB Refused"
    except:
        return False, "Network Error"

def bot_logic(convo_id, hater_name, cookies, messages, speed):
    global bot_running, total_sent, total_failed
    bot_running = True
    msg_list = messages.splitlines()
    cookie_list = cookies.splitlines()

    while bot_running:
        for i, msg in enumerate(msg_list):
            if not bot_running: break
            cookie = cookie_list[i % len(cookie_list)].strip()
            
            status, info = send_message(convo_id, hater_name, cookie, msg.strip())
            
            if status:
                total_sent += 1
                add_log("MESSAGE DELIVERED ✅", convo_id, f"{hater_name} {msg}", color="#0f0")
            else:
                total_failed += 1
                add_log(f"FAILED: {info} ❌", convo_id, "---", color="#f00")
            
            time.sleep(int(speed))

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FIXED COOKIE SERVER</title>
        <style>
            body { background: #ffb6c1; font-family: sans-serif; text-align: center; }
            .container { background: white; padding: 20px; border-radius: 20px; border: 3px solid #ff1493; width: 90%; max-width: 500px; display: inline-block; margin-top: 20px; }
            .box { background: #ff1493; color: white; padding: 10px; margin: 10px 0; border-radius: 10px; font-weight: bold; }
            input, textarea { width: 90%; padding: 10px; margin: 5px 0; border-radius: 10px; border: 1px solid #ccc; }
            #console { background: #000; color: #0f0; text-align: left; padding: 15px; height: 250px; overflow-y: auto; font-size: 11px; border-radius: 10px; }
            .btn { background: #ff1493; color: white; padding: 15px; border: none; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1 style="color: gold; text-shadow: 2px 2px black;">MR. RAVI KUMAR PRAJAPAT</h1>
        <div class="container">
            <div class="box">🆔 GROUP ID</div>
            <input type="text" id="convo_id" placeholder="Enter ID...">
            <div class="box">👤 HATER NAME</div>
            <input type="text" id="hater_name" placeholder="Name...">
            <div class="box">🍪 COOKIES</div>
            <textarea id="cookies" placeholder="Paste Cookies..." rows="3"></textarea>
            <div class="box">📤 UPLOAD MESSAGES</div>
            <input type="file" id="fileInput">
            <div class="box">⚡ SPEED</div>
            <input type="number" id="speed" value="60">
            <button class="btn" onclick="startBot()">🚀 START FIXED SERVER</button>
            <div id="console" style="margin-top:20px;">Logs will appear here...</div>
        </div>
        <script>
            let msgs = "";
            document.getElementById('fileInput').onchange = (e) => {
                let fr = new FileReader();
                fr.onload = () => msgs = fr.result;
                fr.readAsText(e.target.files[0]);
            };
            function startBot() {
                let data = {
                    convo_id: document.getElementById('convo_id').value,
                    hater_name: document.getElementById('hater_name').value,
                    cookies: document.getElementById('cookies').value,
                    messages: msgs,
                    speed: document.getElementById('speed').value
                };
                fetch('/start', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
            }
            setInterval(() => {
                fetch('/status').then(r => r.json()).then(d => {
                    document.getElementById('console').innerHTML = d.logs.join('');
                });
            }, 2000);
        </script>
    </body>
    </html>
    """)

@app.route('/status')
def status(): return jsonify(logs=logs)

@app.route('/start', methods=['POST'])
def start():
    data = request.json
    threading.Thread(target=bot_logic, args=(data['convo_id'], data['hater_name'], data['cookies'], data['messages'], data['speed'])).start()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

