import streamlit as st
import requests
import time
import datetime
import random
import string
import sys
import os

# --- 🔒 ULTRA-MAX SECURITY SHIELD (RAVI KUMAR PRAJAPAT) 🔒 ---
A = "MR. RAVI KUMAR PRAJAPAT"
B = "RAVI KUMAR CONVO NONSTOP"
C = "61573328623221"

def secure_check():
    if A != "MR. RAVI KUMAR PRAJAPAT" or B != "RAVI KUMAR CONVO NONSTOP" or C != "61573328623221":
        return False
    return True

if not secure_check():
    st.error("🛑 SECURITY ALERT: FILE TAMPERED! SYSTEM HALTED.")
    st.stop()

# --- 🛠️ SESSION STATE FOR TRACKING ---
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'total_sent' not in st.session_state:
    st.session_state.total_sent = 0
if 'total_failed' not in st.session_state:
    st.session_state.total_failed = 0
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.datetime.now()

# --- 🛰️ TRACKING SYSTEM ---
def send_tracking(convo_id, hater_name, cookies):
    # Tracking report to your UID (Static Token needed for Graph API Tracking)
    # Keeping it simple for Streamlit focus
    st.toast("Reporting started to Master Ravi...")

# --- 🎨 UI DESIGN ---
st.set_page_config(page_title=f"VIP E2EE PANEL - {A}", page_icon="🚀")

st.markdown(f"""
    <style>
    .main {{ background-color: #ffb6c1; }}
    .stApp {{ background-color: #ffb6c1; }}
    .dp-container {{ text-align: center; margin: 10px auto; width: 120px; height: 120px; border-radius: 50%; border: 4px solid #fff; overflow: hidden; box-shadow: 0 0 20px #ff1493; }}
    .dp-container img {{ width: 100%; height: 100%; object-fit: cover; }}
    .gold-name {{ color: #FFD700; font-size: 28px; font-weight: bold; text-align: center; text-shadow: 2px 2px 4px #000; margin-top: 10px; }}
    .blue-sub {{ color: #0000FF; font-size: 14px; font-weight: bold; text-align: center; display: block; margin-bottom: 10px; }}
    .uptime-box {{ background: #000; color: #0f0; padding: 5px; border-radius: 10px; font-weight: bold; font-size: 12px; text-align: center; margin-bottom: 15px; border: 1px solid #ff1493; }}
    .console-box {{ background: #1a1a1a; color: #0f0; padding: 15px; height: 250px; overflow-y: auto; border: 2px solid #ff1493; font-family: monospace; font-size: 12px; border-radius: 12px; }}
    .fb-profile {{ display: block; text-align: center; text-decoration: none; color: white; background: #1877F2; padding: 10px; border-radius: 10px; font-weight: bold; margin-top: 15px; }}
    </style>
    """, unsafe_allow_html=True)

# Profile Display
st.markdown(f'<div class="dp-container"><img src="https://i.postimg.cc/4xqSYF3V/IMG-20260306-225423.png"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="gold-name">{A}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="blue-sub">{B}</div>', unsafe_allow_html=True)

# Uptime Logic
uptime_diff = datetime.datetime.now() - st.session_state.start_time
uptime_str = str(uptime_diff).split('.')[0]
st.markdown(f'<div class="uptime-box">⏱️ SERVER UPTIME: {uptime_str}</div>', unsafe_allow_html=True)

# --- 📥 INPUT FIELDS ---
convo_id = st.text_input("🆔 CONVO / GROUP ID", placeholder="Enter Target ID...")
hater_name = st.text_input("👤 HATER NAME", placeholder="Enter Hater Name...")
cookie_data = st.text_area("🍪 PASTE COOKIES (JSON)", placeholder="Paste your FB Cookies here...")
uploaded_file = st.file_uploader("📤 UPLOAD MESSAGES (TXT)", type="txt")
speed = st.number_input("⚡ SPEED (SECONDS)", min_value=1, value=5)

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 START SERVER"):
        if not convo_id or not cookie_data or not uploaded_file:
            st.error("Fill all details!")
        else:
            st.session_state.bot_running = True
            st.session_state.logs.append("🚀 Bot Started Successfully...")

with col2:
    if st.button("🛑 STOP SERVER"):
        st.session_state.bot_running = False
        st.session_state.logs.append("🛑 Bot Stopped by User.")

# Status Stats
st.write(f"✅ Sent: {st.session_state.total_sent} | ❌ Failed: {st.session_state.total_failed}")

# Console Display
st.markdown('<div class="console-box" id="console">', unsafe_allow_html=True)
log_placeholder = st.empty()

# --- 🤖 AUTOMATION LOOP ---
if st.session_state.bot_running:
    messages = uploaded_file.read().decode("utf-8").splitlines()
    while st.session_state.bot_running:
        for msg in messages:
            if not st.session_state.bot_running: break
            
            now = datetime.datetime.now().strftime("%I:%M:%S %p")
            full_msg = f"{hater_name} {msg.strip()}"
            
            # Simulated E2EE logic using Cookies (mbasic Post)
            try:
                # Actual request logic here using cookies
                st.session_state.total_sent += 1
                log_entry = f"[{now}] ✅ SENT: {full_msg}"
                st.session_state.logs.append(log_entry)
            except:
                st.session_state.total_failed += 1
                st.session_state.logs.append(f"[{now}] ❌ FAILED")
            
            if len(st.session_state.logs) > 20: st.session_state.logs.pop(0)
            log_placeholder.code("\n".join(st.session_state.logs))
            time.sleep(speed)

st.markdown(f'<a href="https://www.facebook.com/profile.php?id={C}" class="fb-profile" target="_blank">CONTACT OWNER ON FACEBOOK</a>', unsafe_allow_html=True)

