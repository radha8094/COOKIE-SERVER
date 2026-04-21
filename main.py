import requests
import time
import threading
import datetime
import re
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global variables for tracking
logs = []
bot_running = True
total_sent = 0

def add_log(category, message, status="info"):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "time": now,
        "category": category,
        "message": message,
        "status": status
    }
    logs.append(log_entry)
    if len(logs) > 50: logs.pop(0)

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

def send_logic(target_id, hater_name, cookies, messages, delay):
    global total_sent, bot_running
    msg_list = messages.splitlines()
    cookie_list = cookies.splitlines()
    
    while bot_running:
        for i, msg in enumerate(msg_list):
            if not bot_running: break
            current_cookie = cookie_list[i % len(cookie_list)].strip()
            fb_dtsg, jazoest = get_fb_tokens(current_cookie)
            
            if not fb_dtsg:
                add_log("System", "Invalid Cookie detected", "error")
                continue

            url = f"https://m.facebook.com/messages/send/?icm=1&tids=cid.c.{target_id}"
            headers = {'cookie': current_cookie, 'user-agent': 'Mozilla/5.0 (Linux; Android 11)'}
            payload = {
                'fb_dtsg': fb_dtsg,
                'jazoest': jazoest,
                'body': f"{hater_name} {msg.strip()}",
                'tids': f'cid.c.{target_id}',
                'www_dot_messenger_dot_com_messaging_send_message_sent': '1'
            }

            try:
                response = requests.post(url, data=payload, headers=headers)
                if response.status_code == 200:
                    total_sent += 1
                    add_log("Messaging", f"Sent: {msg[:15]}...", "success")
                else:
                    add_log("Messaging", "Failed to send", "error")
            except:
                add_log("Messaging", "Network Error", "error")
            
            time.sleep(int(delay))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    return jsonify({
        "success": True,
        "activeSessions": 1 if bot_running else 0,
        "totalMessages": total_sent,
        "availableSlots": 5
    })

@app.route('/api/messages/single', methods=['POST'])
def single_message():
    data = request.json
    thread = threading.Thread(target=send_logic, args=(
        data['targetId'], data['haterName'], data['cookie'], data['messageFile'], data['delay']
    ))
    thread.daemon = True
    thread.start()
    return jsonify({"success": True, "message": "Single Messaging Started"})

@app.route('/api/messages/multi', methods=['POST'])
def multi_message():
    data = request.json
    thread = threading.Thread(target=send_logic, args=(
        data['targetId'], data['haterName'], data['cookies'], data['messageFile'], data['delay']
    ))
    thread.daemon = True
    thread.start()
    return jsonify({"success": True, "message": "Multi Messaging Started"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

