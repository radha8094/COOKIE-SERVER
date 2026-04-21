import os
import time
import threading
import requests
import re
from flask import Flask, render_template, request, jsonify

# Template folder ko explicitly define kiya hai
app = Flask(__name__, template_folder='templates')

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
            
            if not fb_dtsg: continue

            # Target ID handling (t_ prefix for groups)
            convo_id = f"t_{target_id}" if not target_id.startswith('t_') else target_id
            url = f"https://m.facebook.com/messages/send/?icm=1&tids=cid.c.{target_id}"
            
            payload = {
                'fb_dtsg': fb_dtsg,
                'jazoest': jazoest,
                'body': f"{hater_name} {msg.strip()}",
                'tids': f'cid.c.{target_id}',
                'www_dot_messenger_dot_com_messaging_send_message_sent': '1'
            }
            try:
                requests.post(url, data=payload, headers={'cookie': current_cookie})
                total_sent += 1
            except: pass
            time.sleep(int(delay))

@app.route('/')
def index():
    # Folder check logic
    if not os.path.exists('templates/index.html'):
        return "Error: 'templates/index.html' file nahi mili! Folder structure check karein."
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
    return jsonify({"success": True})

@app.route('/api/messages/multi', methods=['POST'])
def multi_message():
    data = request.json
    thread = threading.Thread(target=send_logic, args=(
        data['targetId'], data['haterName'], data['cookies'], data['messageFile'], data['delay']
    ))
    thread.daemon = True
    thread.start()
    return jsonify({"success": True})

if __name__ == "__main__":
    # Render dynamic port logic
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

