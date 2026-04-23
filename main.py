import os
import requests
import re
import time
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread

# --- RENDER PORT FIX (Isse error nahi aayega) ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIG ---
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Counters
msg_count = 0
start_time = time.time()

def get_uptime():
    n = time.time() - start_time
    return time.strftime("%Hh %Mm %Ss", time.gmtime(n))

# Bot Setup
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def get_eaad_token(email, password):
    session = requests.Session()
    ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
    try:
        res = session.get('https://m.facebook.com/login')
        lsd = re.search(r'name="lsd" value="(.*?)"', res.text).group(1)
        jazoest = re.search(r'name="jazoest" value="(.*?)"', res.text).group(1)
        data = {'lsd': lsd, 'jazoest': jazoest, 'email': email, 'pass': password}
        headers = {'User-Agent': ua}
        session.post('https://m.facebook.com/login/device-based/regular/login/', data=data, headers=headers)
        
        if 'c_user' not in session.cookies.get_dict():
            return "❌ Login Failed: Checkpoint ya Wrong Pass."

        ads_res = session.get('https://www.facebook.com/adsmanager/manage/campaigns', headers=headers)
        token = re.search(r'["\'](EAAD\w+)["\']', ads_res.text)
        
        if token:
            return f"✅ **EAAD Token Found!**\n\n`{token.group(1)}`"
        else:
            return "❌ EAAD Token nahi mila. Ads Manager active nahi hai."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("🔥 **FB EAAD Token Extractor**\n\nCommand: `/eaad email|pass`\nStatus: `/status`")

@bot.on(events.NewMessage(pattern='/status'))
async def status(event):
    uptime = get_uptime()
    await event.reply(f"📊 **Bot Status:**\n\n🚀 Uptime: `{uptime}`\n📩 Total Msgs: `{msg_count}`")

@bot.on(events.NewMessage(pattern='/eaad'))
async def token_handler(event):
    global msg_count
    msg_count += 1
    cmd = event.raw_text.split()
    if len(cmd) < 2 or "|" not in cmd[1]:
        return await event.reply("⚠️ Format: `/eaad email|pass`")
    email, password = cmd[1].split('|')
    wait = await event.reply("⏳ EAAD Token nikal raha hoon...")
    result = get_eaad_token(email, password)
    await wait.edit(result)

if __name__ == "__main__":
    # Start Flask server in background
    t = Thread(target=run)
    t.start()
    print("✅ Port listener started. Bot is starting...")
    bot.run_until_disconnected()

