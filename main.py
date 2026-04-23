import random
import string
import json
import time
import requests
import uuid
import base64
import io
import struct
import sys
import os
from flask import Flask, render_template_string, request, jsonify, session
import threading

# Crypto libraries check
try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
except ImportError:
    print("Error: 'pycryptodome' module not found.")
    print("Run: pip install pycryptodome")
    sys.exit()

# ===========================================
# ORIGINAL CLASSES (UNCHANGED)
# ===========================================

class FacebookPasswordEncryptor:
    @staticmethod
    def get_public_key():
        try:
            url = 'https://b-graph.facebook.com/pwd_key_fetch'
            params = {
                'version': '2',
                'flow': 'CONTROLLER_INITIALIZATION',
                'method': 'GET',
                'fb_api_req_friendly_name': 'pwdKeyFetch',
                'fb_api_caller_class': 'com.facebook.auth.login.AuthOperations',
                'access_token': '438142079694454|fc0a7caa49b192f64f6f5a6d9643bb28'
            }
            response = requests.post(url, params=params).json()
            return response.get('public_key'), str(response.get('key_id', '25'))
        except Exception as e:
            raise Exception(f"Public key fetch error: {e}")

    @staticmethod
    def encrypt(password, public_key=None, key_id="25"):
        if public_key is None:
            public_key, key_id = FacebookPasswordEncryptor.get_public_key()

        try:
            rand_key = get_random_bytes(32)
            iv = get_random_bytes(12)
            
            pubkey = RSA.import_key(public_key)
            cipher_rsa = PKCS1_v1_5.new(pubkey)
            encrypted_rand_key = cipher_rsa.encrypt(rand_key)
            
            cipher_aes = AES.new(rand_key, AES.MODE_GCM, nonce=iv)
            current_time = int(time.time())
            cipher_aes.update(str(current_time).encode("utf-8"))
            encrypted_passwd, auth_tag = cipher_aes.encrypt_and_digest(password.encode("utf-8"))
            
            buf = io.BytesIO()
            buf.write(bytes([1, int(key_id)]))
            buf.write(iv)
            buf.write(struct.pack("<h", len(encrypted_rand_key)))
            buf.write(encrypted_rand_key)
            buf.write(auth_tag)
            buf.write(encrypted_passwd)
            
            encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"#PWD_FB4A:2:{current_time}:{encoded}"
        except Exception as e:
            raise Exception(f"Encryption error: {e}")


class FacebookAppTokens:
    APPS = {
        'FB_ANDROID': {'name': 'Facebook For Android', 'app_id': '350685531728'},
        'MESSENGER_ANDROID': {'name': 'Facebook Messenger For Android', 'app_id': '256002347743983'},
        'FB_LITE': {'name': 'Facebook For Lite', 'app_id': '275254692598279'},
        'MESSENGER_LITE': {'name': 'Facebook Messenger For Lite', 'app_id': '200424423651082'},
        'ADS_MANAGER_ANDROID': {'name': 'Ads Manager App For Android', 'app_id': '438142079694454'},
        'PAGES_MANAGER_ANDROID': {'name': 'Pages Manager For Android', 'app_id': '121876164619130'}
    }
    
    @staticmethod
    def get_app_id(app_key):
        app = FacebookAppTokens.APPS.get(app_key)
        return app['app_id'] if app else None
    
    @staticmethod
    def get_all_app_keys():
        return list(FacebookAppTokens.APPS.keys())
    
    @staticmethod
    def extract_token_prefix(token):
        for i, char in enumerate(token):
            if char.islower():
                return token[:i]
        return token


class FacebookLogin:
    API_URL = "https://b-graph.facebook.com/auth/login"
    ACCESS_TOKEN = "350685531728|62f8ce9f74b12f84c123cc23437a4a32"
    API_KEY = "882a8490361da98702bf97a021ddc14d"
    SIG = "214049b9f17c38bd767de53752b53946"
    
    BASE_HEADERS = {
        "content-type": "application/x-www-form-urlencoded",
        "x-fb-net-hni": "45201",
        "zero-rated": "0",
        "x-fb-sim-hni": "45201",
        "x-fb-connection-quality": "EXCELLENT",
        "x-fb-friendly-name": "authenticate",
        "x-fb-connection-bandwidth": "78032897",
        "x-tigon-is-retry": "False",
        "authorization": "OAuth null",
        "x-fb-connection-type": "WIFI",
        "x-fb-device-group": "3342",
        "priority": "u=3,i",
        "x-fb-http-engine": "Liger",
        "x-fb-client-ip": "True",
        "x-fb-server-cluster": "True"
    }
    
    def __init__(self, uid_phone_mail, password, machine_id=None, convert_token_to=None, convert_all_tokens=False):
        self.uid_phone_mail = uid_phone_mail
        
        if password.startswith("#PWD_FB4A"):
            self.password = password
        else:
            self.password = FacebookPasswordEncryptor.encrypt(password)
        
        if convert_all_tokens:
            self.convert_token_to = FacebookAppTokens.get_all_app_keys()
        elif convert_token_to:
            self.convert_token_to = convert_token_to if isinstance(convert_token_to, list) else [convert_token_to]
        else:
            self.convert_token_to = []
        
        self.session = requests.Session()
        
        self.device_id = str(uuid.uuid4())
        self.adid = str(uuid.uuid4())
        self.secure_family_device_id = str(uuid.uuid4())
        self.machine_id = machine_id if machine_id else self._generate_machine_id()
        self.jazoest = ''.join(random.choices(string.digits, k=5))
        self.sim_serial = ''.join(random.choices(string.digits, k=20))
        
        self.headers = self._build_headers()
        self.data = self._build_data()
    
    @staticmethod
    def _generate_machine_id():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=24))
    
    def _build_headers(self):
        headers = self.BASE_HEADERS.copy()
        headers.update({
            "x-fb-request-analytics-tags": '{"network_tags":{"product":"350685531728","retry_attempt":"0"},"application_tags":"unknown"}',
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; 23113RKC6C Build/PQ3A.190705.08211809) [FBAN/FB4A;FBAV/417.0.0.33.65;FBPN/com.facebook.katana;FBLC/vi_VN;FBBV/480086274;FBCR/MobiFone;FBMF/Redmi;FBBD/Redmi;FBDV/23113RKC6C;FBSV/9;FBCA/x86:armeabi-v7a;FBDM/{density=1.5,width=1280,height=720};FB_FW/1;FBRV/0;]"
        })
        return headers
    
    def _build_data(self):
        base_data = {
            "format": "json",
            "email": self.uid_phone_mail,
            "password": self.password,
            "credentials_type": "password",
            "generate_session_cookies": "1",
            "locale": "vi_VN",
            "client_country_code": "VN",
            "api_key": self.API_KEY,
            "access_token": self.ACCESS_TOKEN
        }
        
        base_data.update({
            "adid": self.adid,
            "device_id": self.device_id,
            "generate_analytics_claim": "1",
            "community_id": "",
            "linked_guest_account_userid": "",
            "cpl": "true",
            "try_num": "1",
            "family_device_id": self.device_id,
            "secure_family_device_id": self.secure_family_device_id,
            "sim_serials": f'["{self.sim_serial}"]',
            "openid_flow": "android_login",
            "openid_provider": "google",
            "openid_tokens": "[]",
            "account_switcher_uids": f'["{self.uid_phone_mail}"]',
            "fb4a_shared_phone_cpl_experiment": "fb4a_shared_phone_nonce_cpl_at_risk_v3",
            "fb4a_shared_phone_cpl_group": "enable_v3_at_risk",
            "enroll_misauth": "false",
            "error_detail_type": "button_with_disabled",
            "source": "login",
            "machine_id": self.machine_id,
            "jazoest": self.jazoest,
            "meta_inf_fbmeta": "V2_UNTAGGED",
            "advertiser_id": self.adid,
            "encrypted_msisdn": "",
            "currently_logged_in_userid": "0",
            "fb_api_req_friendly_name": "authenticate",
            "fb_api_caller_class": "Fb4aAuthHandler",
            "sig": self.SIG
        })
        
        return base_data
    
    def _convert_token(self, access_token, target_app):
        try:
            app_id = FacebookAppTokens.get_app_id(target_app)
            if not app_id:
                return None
            
            response = requests.post(
                'https://api.facebook.com/method/auth.getSessionforApp',
                data={
                    'access_token': access_token,
                    'format': 'json',
                    'new_app_id': app_id,
                    'generate_session_cookies': '1'
                }
            )
            
            result = response.json()
            
            if 'access_token' in result:
                token = result['access_token']
                prefix = FacebookAppTokens.extract_token_prefix(token)
                
                cookies_dict = {}
                cookies_string = ""
                
                if 'session_cookies' in result:
                    for cookie in result['session_cookies']:
                        cookies_dict[cookie['name']] = cookie['value']
                        cookies_string += f"{cookie['name']}={cookie['value']}; "
                
                return {
                    'token_prefix': prefix,
                    'access_token': token,
                    'cookies': {
                        'dict': cookies_dict,
                        'string': cookies_string.rstrip('; ')
                    }
                }
            return None     
        except:
            return None
    
    def _parse_success_response(self, response_json):
        original_token = response_json.get('access_token')
        original_prefix = FacebookAppTokens.extract_token_prefix(original_token)
        
        result = {
            'success': True,
            'original_token': {
                'token_prefix': original_prefix,
                'access_token': original_token
            },
            'cookies': {}
        }
        
        if 'session_cookies' in response_json:
            cookies_dict = {}
            cookies_string = ""
            for cookie in response_json['session_cookies']:
                cookies_dict[cookie['name']] = cookie['value']
                cookies_string += f"{cookie['name']}={cookie['value']}; "
            result['cookies'] = {
                'dict': cookies_dict,
                'string': cookies_string.rstrip('; ')
            }
        
        if self.convert_token_to:
            result['converted_tokens'] = {}
            for target_app in self.convert_token_to:
                converted = self._convert_token(original_token, target_app)
                if converted:
                    result['converted_tokens'][target_app] = converted
        
        return result
    
    def _handle_2fa_manual(self, error_data):
        return {
            'requires_2fa': True,
            'login_first_factor': error_data['login_first_factor'],
            'uid': error_data['uid']
        }
    
    def login(self):
        try:
            response = self.session.post(self.API_URL, headers=self.headers, data=self.data)
            response_json = response.json()
            
            if 'access_token' in response_json:
                return self._parse_success_response(response_json)
            
            if 'error' in response_json:
                error_data = response_json.get('error', {}).get('error_data', {})
                
                if 'login_first_factor' in error_data and 'uid' in error_data:
                    return self._handle_2fa_manual(error_data)
                
                return {
                    'success': False,
                    'error': response_json['error'].get('message', 'Unknown error'),
                    'error_user_msg': response_json['error'].get('error_user_msg')
                }
            
            return {'success': False, 'error': 'Unknown response format'}
            
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid JSON response'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# ===========================================
# FLASK APPLICATION
# ===========================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'facebook_login_tool_secret_key_2024')
login_sessions = {}

# HTML Template with CSS and JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>𝕱𝖆𝖈𝖊𝖇𝖔𝖔𝖐 𝕷𝖔𝖌𝖎𝖓 𝕿𝖔𝖔𝖑</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        :root {
            --primary-gradient: linear-gradient(135deg, #1877f2 0%, #00a8ff 100%);
            --dark-bg: #0f1419;
            --card-bg: rgba(255, 255, 255, 0.05);
            --glass-bg: rgba(255, 255, 255, 0.08);
            --text-primary: #ffffff;
            --text-secondary: #b0b3b8;
            --accent: #00a8ff;
        }
        body {
            background-color: #05080a;
            min-height: 100vh;
            color: var(--text-primary);
            overflow-x: hidden;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            min-height: 100vh;
            align-items: center;
        }
        @media (max-width: 768px) { .container { grid-template-columns: 1fr; } }
        
        /* Owner Profile Section */
        .owner-profile {
            margin-bottom: 25px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            border: 1px solid rgba(0, 168, 255, 0.2);
            display: inline-block;
            width: 100%;
        }
        .owner-img {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: 3px solid var(--accent);
            box-shadow: 0 0 20px rgba(0, 168, 255, 0.5);
            margin-bottom: 15px;
            object-fit: cover;
        }
        .owner-link {
            color: var(--accent);
            text-decoration: none;
            font-weight: bold;
            font-size: 1.2rem;
            display: block;
            transition: 0.3s;
        }
        .owner-link:hover { text-shadow: 0 0 10px var(--accent); transform: scale(1.05); }

        .hero-section {
            text-align: center;
            padding: 40px;
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent), #ffffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .features { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 30px; }
        .feature { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); }
        .feature i { font-size: 1.5rem; color: var(--accent); margin-bottom: 5px; }
        
        .login-form { background: var(--card-bg); backdrop-filter: blur(20px); padding: 40px; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1); }
        .form-group { position: relative; margin-bottom: 25px; }
        .form-group input { width: 100%; padding: 15px; background: rgba(255, 255, 255, 0.07); border: 2px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; }
        .btn { width: 100%; padding: 16px; background: var(--primary-gradient); color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; transition: 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0, 168, 255, 0.3); }
        
        .results-section { display: none; margin-top: 25px; padding: 15px; border-radius: 16px; background: rgba(0, 168, 255, 0.1); border: 1px solid var(--accent); }
        .token-box { background: rgba(0,0,0,0.4); padding: 10px; border-radius: 8px; margin: 10px 0; word-break: break-all; font-family: monospace; font-size: 0.85rem; }
        .alert { padding: 10px; border-radius: 8px; margin-bottom: 15px; display: none; text-align: center; }
        .alert-error { background: #ff475722; color: #ff4757; border: 1px solid #ff475755; }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero-section">
            <div class="owner-profile">
                <img src="https://i.postimg.cc/4xqSYF3V/IMG-20260306-225423.png" alt="Ravi Prajapat" class="owner-img">
                <a href="https://www.facebook.com/Prajapat.9649" target="_blank" class="owner-link">
                    MR. RAVI KUMAR PRAJAPAT
                </a>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 5px;">👑 Tool Owner & Developer 👑</p>
            </div>

            <h1 class="title">𝗥𝗞-𝗣𝗥𝗔𝗝𝗔𝗣𝗔𝗧-𝗧𝗢𝗞𝗘𝗡-𝗧𝗢𝗢𝗟</h1>
            <p class="subtitle">Premium Facebook Authentication Tool with Full App Support</p>
            
            <div class="features">
                <div class="feature"><i class="fas fa-shield-alt"></i><h3>Encrypted</h3></div>
                <div class="feature"><i class="fas fa-sync-alt"></i><h3>Convert</h3></div>
                <div class="feature"><i class="fas fa-mobile-alt"></i><h3>2FA</h3></div>
                <div class="feature"><i class="fas fa-bolt"></i><h3>Fast</h3></div>
            </div>
        </div>

        <div class="login-form">
            <div class="alert alert-error" id="alert"></div>
            <form id="loginForm">
                <div class="form-group">
                    <input type="text" id="email" placeholder="Email / Phone Number" required>
                </div>
                <div class="form-group">
                    <input type="password" id="password" placeholder="Password" required>
                </div>
                <button type="submit" class="btn" id="loginBtn">Login to Facebook</button>
            </form>

            <div class="results-section" id="results">
                <h3 style="color: var(--accent);"><i class="fas fa-check-circle"></i> Success</h3>
                <div class="token-box" id="tokenDisplay"></div>
                <div class="token-box" id="cookieDisplay"></div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = document.getElementById('loginBtn');
            btn.disabled = true;
            btn.innerHTML = 'Logging in...';

            fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: document.getElementById('email').value,
                    password: document.getElementById('password').value
                })
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    document.getElementById('results').style.display = 'block';
                    document.getElementById('tokenDisplay').textContent = data.original_token.access_token;
                    document.getElementById('cookieDisplay').textContent = data.cookies.string;
                } else {
                    const al = document.getElementById('alert');
                    al.textContent = data.error;
                    al.style.display = 'block';
                }
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = 'Login to Facebook';
            });
        });
    </script>
</body>
</html>
'''

# ===========================================
# FLASK ROUTES
# ===========================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        fb_login = FacebookLogin(uid_phone_mail=data.get('email'), password=data.get('password'), convert_all_tokens=True)
        result = fb_login.login()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
