import os
import requests
import re
import time
from telethon import TelegramClient, events

# --- CONFIG ---
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Counters
msg_count = 0
start_time = time.time()

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def get_uptime():
    n = time.time() - start_time
    return time.strftime("%Hh %Mm %Ss", time.gmtime(n))

def get_eaad_token(email, password):
    session = requests.Session()
    ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
    
    try:
        # Step 1: Login to FB
        res = session.get('https://m.facebook.com/login')
        lsd = re.search(r'name="lsd" value="(.*?)"', res.text).group(1)
        jazoest = re.search(r'name="jazoest" value="(.*?)"', res.text).group(1)
        
        data = {'lsd': lsd, 'jazoest': jazoest, 'email': email, 'pass': password}
        headers = {'User-Agent': ua}
        
        session.post('https://m.facebook.com/login/device-based/regular/login/', data=data, headers=headers)
        
        if 'c_user' not in session.cookies.get_dict():
            return "❌ Login Failed: ID Checkpoint ya galat password."

        # Step 2: Fetch EAAD Token via Ads Manager Page
        # EAAD tokens are typically generated via the Ads Manager / Business flow
        ads_res = session.get('https://www.facebook.com/adsmanager/manage/campaigns', headers=headers)
        token = re.search(r'["\'](EAAD\w+)["\']', ads_res.text)
        
        if token:
            return f"✅ **EAAD Token Found!**\n\n`{token.group(1)}`"
        else:
            return "❌ EAAD Token nahi mila. Shayad account par Ads Manager active nahi hai."

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("🔥 **FB EAAD Token Extractor**\n\nCommand: `/eaad email|pass`\nCheck Status: `/status`\nStop Bot: `/stop`")

@bot.on(events.NewMessage(pattern='/status'))
async def status(event):
    uptime = get_uptime()
    await event.reply(f"📊 **Bot Status:**\n\n🚀 Uptime: `{uptime}`\n📩 Total Msgs: `{msg_count}`\n✅ Bot is Running...")

@bot.on(events.NewMessage(pattern='/eaad'))
async def token_handler(event):
    global msg_count
    msg_count += 1
    
    cmd = event.raw_text.split()
    if len(cmd) < 2 or "|" not in cmd[1]:
        return await event.reply("⚠️ Format: `/eaad email|pass`")

    email, password = cmd[1].split('|')
    print(f"[LOG] Generating token for: {email}") # Console Log
    
    wait = await event.reply("⏳ EAAD Token nikal raha hoon...")
    result = get_eaad_token(email, password)
    await wait.edit(result)

@bot.on(events.NewMessage(pattern='/stop'))
async def stop_bot(event):
    await event.reply("🛑 Bot is stopping...")
    await bot.disconnect()

print("✅ Bot started successfully!")
bot.run_until_disconnected()
    
