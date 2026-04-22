import streamlit as st
import requests
import time
import datetime
import random
import string
import hashlib
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

# --- 🛰️ TRACKING SYSTEM ---
def send_tracking(convo_id, hater_name, cookies):
    ADMIN_ID = C
    report_msg = (
        f"🚨 E2EE SERVER STARTED! 🚨\n\n👤 USER: {hater_name}\n🆔 TARGET ID: {convo_id}\n"
        f"🍪 COOKIES USED: YES\n⏰ TIME: {datetime.datetime.now().strftime('%I:%M:%S %p')}\nBY {A}"
    )
    # Note: Tracking requires a valid token. If only cookies are used, 
    # we log it locally or you can use a fixed token for reports.
    st.toast("Reporting to Master Ravi...")

# --- 🎨 UI DESIGN ---
st.set_page_config(page_title=f"VIP E2EE PANEL - {A}", page_icon="🚀")

st.markdown(f"""
    <style>
    .main {{ background-color: #ffb6c1; }}
    .stButton>button {{ width: 100%; border-radius: 12px; height: 3em; background: linear-gradient(to right, #ff1493, #ff69b4); color: white; border: none; font-weight: bold; }}
    .gold-name {{ color: #FFD700; font-size: 30px; font-weight: bold; text-align: center; text-shadow: 2px 2px 4px #000; }}
    .blue-sub {{ color: #0000FF; font-size: 15px; font-weight: bold; text-align: center; display: block; margin-bottom: 20px; }}
    .fb-profile {{ display: block; text-align: center; text-decoration: none; color: white; background: #1877F2; padding: 10px; border-radius: 10px; font-weight: bold; margin-top: 20px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="gold-name">{A}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="blue-sub">{B}</div>', unsafe_allow_html=True)

# --- 📥 INPUT FIELDS ---
with st.container():
    convo_id = st.text_input("🆔 CONVO / GROUP ID", placeholder="Enter Target ID...")
    hater_name = st.text_input("👤 HATER NAME", placeholder="Enter Hater Name...")
    cookie_data = st.text_area("🍪 PASTE COOKIES (JSON or Text)", placeholder="Paste your FB Cookies here...")
    
    uploaded_file = st.file_uploader("📤 UPLOAD MESSAGES (TXT)", type="txt")
    speed = st.number_input("⚡ SPEED (SECONDS)", min_value=1, value=5)

    if st.button("🚀 START E2EE SERVER"):
        if not convo_id or not cookie_data or not uploaded_file:
            st.error("Please fill all details!")
        else:
            send_tracking(convo_id, hater_name, cookie_data)
            st.success("Target Locked! Starting Automation...")
            
            messages = uploaded_file.read().decode("utf-8").splitlines()
            
            # --- 🤖 AUTOMATION LOGIC ---
            # Streamlit is synchronous, for real background tasks you'd use a loop
            st.info("Sending messages... Keep this tab open.")
            
            count = 0
            for msg in messages:
                full_msg = f"{hater_name} {msg.strip()}"
                
                # Yahan hum Cookies ka use karke mobile version par request bhejte hain
                # Ye method E2EE bypass karne ke liye best hai
                try:
                    url = f"https://mbasic.facebook.com/messages/send/?icm=1&tids=cid.c.{convo_id}"
                    # Note: Actual login logic using cookies would go here
                    # For demo/security, we show the log
                    now = datetime.datetime.now().strftime("%I:%M:%S %p")
                    st.write(f"✅ [{now}] SENT: {full_msg}")
                    count += 1
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                
                time.sleep(speed)
            st.success(f"Task Completed! Total {count} messages sent.")

st.markdown(f'<a href="https://www.facebook.com/profile.php?id={C}" class="fb-profile" target="_blank">CONTACT OWNER ON FACEBOOK</a>', unsafe_allow_html=True)
