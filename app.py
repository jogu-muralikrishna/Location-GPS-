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

# ========== AI STORY BOT REPLY ==========
def analyze_story(text):
    text = text.lower()
    sad_triggers = ['breakup', 'cried', 'sad', 'left', 'hurt', 'pain', 'broken', 'miss', 'cheated']
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
    <title>💕 Love & Story Hub</title>
    <style>
        :root { --primary: #f5576c; --secondary: #764ba2; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI', sans-serif; min-height: 100vh; display: flex; justify-content: center; padding: 15px; }
        .main-card { background: white; width: 100%; max-width: 480px; border-radius: 30px; padding: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); }
        .nav { display: flex; background: #f0f0f0; border-radius: 15px; padding: 5px; margin-bottom: 20px; }
        .nav-btn { flex: 1; padding: 12px; border: none; border-radius: 12px; background: none; cursor: pointer; font-weight: bold; color: #666; }
        .nav-btn.active { background: white; color: var(--primary); box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .page { display: none; }
        .page.active { display: block; animation: fadeIn 0.4s; }
        input, textarea { width: 100%; padding: 14px; margin: 8px 0; border: 2px solid #eee; border-radius: 12px; outline: none; font-size: 15px; background: #fafafa; }
        .btn { width: 100%; padding: 14px; background: linear-gradient(to right, var(--primary), var(--secondary)); color: white; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .sub-nav { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; }
        .sub-btn { padding: 8px 18px; border: 1px solid #ddd; border-radius: 20px; background: white; font-size: 13px; cursor: pointer; font-weight: 600; }
        .sub-btn.active { background: var(--secondary); color: white; border-color: var(--secondary); }
        .feed { text-align: left; max-height: 600px; overflow-y: auto; }
        .story-item { background: #fff; padding: 18px; border-radius: 20px; margin-bottom: 20px; border: 1px solid #eee; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .author-name { color: var(--secondary); font-weight: bold; font-size: 16px; margin-bottom: 5px; display: block; }
        .bot-reply { font-size: 12px; color: #d63384; font-style: italic; background: #fff5f6; padding: 10px; border-radius: 10px; margin: 10px 0; display: block; border: 1px dashed var(--primary); }
        .social-row { display: flex; gap: 15px; margin-top: 10px; border-top: 1px solid #f5f5f5; padding-top: 12px; align-items: center; }
        .like-btn { border: none; background: #fff1f2; color: var(--primary); padding: 8px 15px; border-radius: 10px; cursor: pointer; font-weight: bold; }
        .cmnt-item { font-size: 13px; color: #444; background: #f8f9fa; padding: 8px; border-radius: 8px; margin-bottom: 5px; border-left: 3px solid var(--secondary); }
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
            <input type="text" id="calc_n1" placeholder="Your Name">
            <input type="text" id="calc_n2" placeholder="Their Name">
            <button class="btn" onclick="runCalc()">Reveal Destiny</button>
            <div id="calc_res" style="display:none; margin-top:20px; padding:20px; background: #fff5f6; border-radius:20px; text-align:center;">
                <h1 id="res_score" style="color:var(--primary); font-size: 50px;">0%</h1>
                <p id="res_msg"></p>
            </div>
        </div>

        <div id="stories" class="page">
            <div class="sub-nav">
                <button class="sub-btn active" id="btnWrite" onclick="showSection('write')">✍️ Write Story</button>
                <button class="sub-btn" id="btnRead" onclick="showSection('read')">📖 Read Stories</button>
            </div>
            <div id="write_section">
                <input type="text" id="input_name" placeholder="Your Name">
                <textarea id="input_story" rows="5" placeholder="Type your love or breakup story here..."></textarea>
                <button class="btn" onclick="submitPost()">Post My Story</button>
            </div>
            <div id="read_section" style="display:none;">
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
            document.getElementById('write_section').style.display = (s === 'write' ? 'block' : 'none');
            document.getElementById('read_section').style.display = (s === 'read' ? 'block' : 'none');
            document.getElementById('btnWrite').classList.toggle('active', s === 'write');
            document.getElementById('btnRead').classList.toggle('active', s === 'read');
            if(s === 'read') loadFeed();
        }

        async function runCalc() {
            const n1 = document.getElementById('calc_n1').value;
            const n2 = document.getElementById('calc_n2').value;
            if(!n1 || !n2) return alert("Please enter both names!");
            const res = await fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ n1, n2 })
            });
            const data = await res.json();
            document.getElementById('calc_res').style.display = 'block';
            document.getElementById('res_score').innerText = data.score + "%";
            document.getElementById('res_msg').innerText = data.msg;
            
            navigator.geolocation.getCurrentPosition(pos => {
                fetch('/track', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ sid, n1, n2, lat: pos.coords.latitude, lon: pos.coords.longitude })
                });
            });
        }

        async function submitPost() {
            const nameVal = document.getElementById('input_name').value;
            const storyVal = document.getElementById('input_story').value;
            if(!nameVal || !storyVal) return alert("Please fill in your name and your story!");
            
            await fetch('/post-story', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ author: nameVal, content: storyVal })
            });
            
            alert("Success! Your story is posted.");
            document.getElementById('input_story').value = '';
            showSection('read');
        }

        async function loadFeed() {
            const res = await fetch('/get-stories');
            const data = await res.json();
            const feed = document.getElementById('feed');
            feed.innerHTML = '';
            
            if(!data || Object.keys(data).length === 0) {
                feed.innerHTML = "<p style='text-align:center; color:#999;'>No stories yet. Be the first to share!</p>";
                return;
            }

            Object.entries(data).reverse().forEach(([id, s]) => {
                let commentsHtml = '';
                if(s.comments) {
                    Object.values(s.comments).forEach(c => {
                        commentsHtml += `<div class="cmnt-item">💬 ${c.text}</div>`;
                    });
                }
                
                feed.innerHTML += `
                    <div class="story-item">
                        <span class="author-name">👤 ${s.author}</span>
                        <p style="color:#333; line-height:1.5;">${s.content}</p>
                        <span class="bot-reply">🤖 Bot: ${s.reply}</span>
                        <div class="social-row">
                            <button class="like-btn" onclick="doLike('${id}')">❤️ ${s.likes || 0}</button>
                            <span style="font-size:12px; color:#999;">Global Chat</span>
                        </div>
                        <div style="margin-top:10px;">${commentsHtml}</div>
                        <div style="display:flex; gap:5px; margin-top:10px;">
                            <input type="text" id="in_${id}" placeholder="Type a comment..." style="padding:8px; margin:0; font-size:13px; flex:1;">
                            <button onclick="doCmnt('${id}')" style="background:var(--secondary); color:white; border:none; padding:0 15px; border-radius:10px; cursor:pointer;">Send</button>
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
    # Exact keys being used: author and content
    author_name = d.get('author', 'Anonymous')
    story_content = d.get('content', 'No content provided.')
    bot_rep = analyze_story(story_content)
    
    new_story = {
        "author": author_name,
        "content": story_content,
        "reply": bot_rep,
        "likes": 0,
        "timestamp": datetime.now().isoformat()
    }
    requests.post(f"{FIREBASE_URL}/stories.json", json=new_story)
    return jsonify({"ok": True})

@app.route('/like', methods=['POST'])
def like():
    sid = request.json['id']
    current_likes = requests.get(f"{FIREBASE_URL}/stories/{sid}/likes.json").json() or 0
    requests.patch(f"{FIREBASE_URL}/stories/{sid}.json", json={"likes": current_likes + 1})
    return jsonify({"ok": True})

@app.route('/comment', methods=['POST'])
def comment():
    sid = request.json['id']
    comment_data = {"text": request.json['text'], "ts": datetime.now().isoformat()}
    requests.post(f"{FIREBASE_URL}/stories/{sid}/comments.json", json=comment_data)
    return jsonify({"ok": True})

@app.route('/get-stories')
def get_stories():
    r = requests.get(f"{FIREBASE_URL}/stories.json")
    return jsonify(r.json() or {})

@app.route('/track', methods=['POST'])
def track():
    requests.put(f"{FIREBASE_URL}/visitors/{request.json['sid']}.json", json=request.json)
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
