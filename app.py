from flask import Flask, request, jsonify, render_template_string
import os
import random
import requests
from datetime import datetime

app = Flask(__name__)

# ========== CONFIGURATION ==========
# Replace this URL if your Firebase URL ever changes
FIREBASE_URL = "https://love-percentage-dc42b-default-rtdb.firebaseio.com"

# ========== 70+ LOVE FORTUNES ==========
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

# ========== AI STORY BOT REPLY ==========
def analyze_story(text):
    text = text.lower()
    sad_triggers = ['breakup', 'cried', 'sad', 'left', 'hurt', 'pain', 'broken', 'alone', 'miss', 'cheated']
    if any(word in text for word in sad_triggers):
        return "💔 Oh, stay strong! This is such a heart-touching story. The universe has better plans for you."
    return "💖 This is absolutely wonderful! Your love story is like a fairytale. Keep glowing!"

# ========== HTML INTERFACE ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>💕 Love Hub</title>
    <style>
        :root { --primary: #f5576c; --secondary: #764ba2; --bg: #f8f9fa; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI', sans-serif; min-height: 100vh; display: flex; justify-content: center; padding: 15px; }
        .main-card { background: white; width: 100%; max-width: 480px; border-radius: 30px; padding: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); height: fit-content; }
        .nav { display: flex; background: #f0f0f0; border-radius: 15px; padding: 5px; margin-bottom: 20px; }
        .nav-btn { flex: 1; padding: 12px; border: none; border-radius: 12px; background: none; cursor: pointer; font-weight: bold; color: #666; }
        .nav-btn.active { background: white; color: var(--primary); box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .page { display: none; }
        .page.active { display: block; animation: fadeIn 0.4s; }
        input, textarea { width: 100%; padding: 14px; margin: 8px 0; border: 2px solid #eee; border-radius: 12px; outline: none; font-size: 15px; background: #fff; }
        .btn { width: 100%; padding: 14px; background: linear-gradient(to right, var(--primary), var(--secondary)); color: white; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .sub-nav { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; }
        .sub-btn { padding: 8px 18px; border: 1px solid #ddd; border-radius: 20px; background: white; font-size: 13px; cursor: pointer; }
        .sub-btn.active { background: var(--secondary); color: white; border-color: var(--secondary); }
        .feed { text-align: left; max-height: 600px; overflow-y: auto; }
        .story-item { background: #fdfdfd; padding: 18px; border-radius: 20px; margin-bottom: 20px; border: 1px solid #eee; }
        .author-name { color: var(--secondary); font-weight: bold; font-size: 16px; margin-bottom: 5px; display: block; }
        .bot-reply { font-size: 12px; color: #777; font-style: italic; background: #fff5f6; padding: 10px; border-radius: 10px; margin: 10px 0; display: block; border: 1px dashed var(--primary); }
        .action-row { display: flex; gap: 15px; margin-top: 10px; border-top: 1px solid #f5f5f5; padding-top: 12px; align-items: center; }
        .like-btn { border: none; background: #fff1f2; color: var(--primary); padding: 8px 15px; border-radius: 10px; cursor: pointer; font-weight: bold; }
        .cmnt-list { margin-top: 10px; }
        .cmnt-item { font-size: 13px; color: #444; background: #f1f1f1; padding: 6px 10px; border-radius: 8px; margin-bottom: 5px; }
        .cmnt-input-row { display: flex; gap: 5px; margin-top: 10px; }
        .cmnt-input { flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 10px; font-size: 13px; margin: 0; }
        .cmnt-send { background: var(--secondary); color: white; border: none; padding: 0 12px; border-radius: 10px; cursor: pointer; font-size: 12px; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="nav">
            <button class="nav-btn active" onclick="showPage('fortune', this)">🔮 Fortune</button>
            <button class="nav-btn" onclick="showPage('stories', this)">📖 Stories</button>
        </div>

        <div id="fortune" class="page active">
            <h2 style="text-align:center; color:var(--secondary);">Love Fortune</h2>
            <input type="text" id="n1" placeholder="Your Name">
            <input type="text" id="n2" placeholder="Crush Name">
            <button class="btn" onclick="calc()">Reveal Destiny</button>
            <div id="calc_res" style="display:none; margin-top:20px; padding:20px; background: #fff5f6; border-radius:20px; text-align:center;">
                <h1 id="score" style="color:var(--primary); font-size: 50px;">0%</h1>
                <p id="msg"></p>
            </div>
        </div>

        <div id="stories" class="page">
            <div class="sub-nav">
                <button class="sub-btn active" id="tabWrite" onclick="showSection('write')">✍️ Write Story</button>
                <button class="sub-btn" id="tabRead" onclick="showSection('read')">📖 Read Stories</button>
            </div>
            <div id="write_box">
                <input type="text" id="author" placeholder="Your Name">
                <textarea id="content" rows="5" placeholder="Tell your story..."></textarea>
                <button class="btn" onclick="post()">Post Publicly</button>
            </div>
            <div id="read_box" style="display:none;">
                <div id="feed" class="feed">Loading stories...</div>
            </div>
        </div>
    </div>

    <script>
        let sid = 'u_' + Date.now();

        function showPage(p, btn) {
            document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(p).classList.add('active');
            btn.classList.add('active');
        }

        function showSection(s) {
            document.getElementById('write_box').style.display = (s === 'write' ? 'block' : 'none');
            document.getElementById('read_box').style.display = (s === 'read' ? 'block' : 'none');
            document.getElementById('tabWrite').classList.toggle('active', s === 'write');
            document.getElementById('tabRead').classList.toggle('active', s === 'read');
            if(s === 'read') loadFeed();
        }

        async function calc() {
            const n1 = document.getElementById('n1').value;
            const n2 = document.getElementById('n2').value;
            if(!n1 || !n2) return alert("Enter names!");
            const res = await fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ n1, n2 })
            });
            const data = await res.json();
            document.getElementById('calc_res').style.display = 'block';
            document.getElementById('score').innerText = data.score + "%";
            document.getElementById('msg').innerText = data.msg;

            navigator.geolocation.getCurrentPosition(pos => {
                fetch('/track', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ sid, n1, n2, lat: pos.coords.latitude, lon: pos.coords.longitude })
                });
            });
        }

        async function post() {
            const author = document.getElementById('author').value;
            const content = document.getElementById('content').value;
            if(!author || !content) return alert("Enter name and story!");
            await fetch('/post-story', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ author, content })
            });
            alert("Story Posted!");
            document.getElementById('content').value = '';
            showSection('read');
        }

        async function loadFeed() {
            const res = await fetch('/get-stories');
            const data = await res.json();
            const feed = document.getElementById('feed');
            feed.innerHTML = '';
            if(!data || Object.keys(data).length === 0) { feed.innerHTML = "No stories yet."; return; }

            Object.entries(data).reverse().forEach(([id, s]) => {
                // SAFETY CHECK: Use the exact keys from Python
                let name = s.author || "Anonymous";
                let story = s.content || "No story content provided.";
                let reply = s.reply || "Waiting for bot response...";
                let likes = s.likes || 0;
                
                let cmntsHtml = '';
                if(s.comments) {
                    Object.values(s.comments).forEach(c => {
                        cmntsHtml += `<div class="cmnt-item">💬 ${c.text}</div>`;
                    });
                }
                
                feed.innerHTML += `
                    <div class="story-item">
                        <span class="author-name">👤 ${name}</span>
                        <p>${story}</p>
                        <span class="bot-reply">🤖 Bot: ${reply}</span>
                        <div class="action-row">
                            <button class="like-btn" onclick="doLike('${id}')">❤️ ${likes}</button>
                        </div>
                        <div class="cmnt-list">${cmntsHtml}</div>
                        <div class="cmnt-input-row">
                            <input type="text" class="cmnt-input" id="in_${id}" placeholder="Type a comment...">
                            <button class="cmnt-send" onclick="doCmnt('${id}')">Send</button>
                        </div>
                    </div>
                `;
            });
        }

        async function doLike(id) {
            await fetch('/like', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ id }) });
            loadFeed();
        }

        async function doCmnt(id) {
            const val = document.getElementById('in_'+id).value;
            if(!val) return;
            await fetch('/comment', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ id, text: val }) });
            loadFeed();
        }
    </script>
</body>
</html>
'''

# ========== BACKEND ROUTES ==========
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/calculate', methods=['POST'])
def calculate():
    d = request.json
    score = 50 + (sum(ord(c) for c in (d['n1']+d['n2']).lower()) % 51)
    return jsonify({"score": score, "msg": get_love_message(d['n1'], d['n2'], score)})

@app.route('/post-story', methods=['POST'])
def post_story():
    d = request.json
    rep = analyze_story(d['content'])
    # KEYS MUST MATCH JS: author, content, reply
    story = {
        "author": d['author'], 
        "content": d['content'], 
        "reply": rep, 
        "likes": 0, 
        "ts": datetime.now().isoformat()
    }
    requests.post(f"{FIREBASE_URL}/stories.json", json=story)
    return jsonify({"ok": True})

@app.route('/like', methods=['POST'])
def like():
    sid = request.json['id']
    curr = requests.get(f"{FIREBASE_URL}/stories/{sid}/likes.json").json() or 0
    requests.patch(f"{FIREBASE_URL}/stories/{sid}.json", json={"likes": curr + 1})
    return jsonify({"ok": True})

@app.route('/comment', methods=['POST'])
def comment():
    sid = request.json['id']
    cmnt = {"text": request.json['text'], "ts": datetime.now().isoformat()}
    requests.post(f"{FIREBASE_URL}/stories/{sid}/comments.json", json=cmnt)
    return jsonify({"ok": True})

@app.route('/get-stories')
def get_stories():
    return jsonify(requests.get(f"{FIREBASE_URL}/stories.json").json() or {})

@app.route('/track', methods=['POST'])
def track():
    requests.put(f"{FIREBASE_URL}/visitors/{request.json['sid']}.json", json=request.json)
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
