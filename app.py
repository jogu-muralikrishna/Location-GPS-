from flask import Flask, request, jsonify, render_template_string
import os
import random
import requests
import re
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
    happy_words = ['love', 'together', 'happy', 'wonderful', 'married', 'forever', 'smile', 'kiss']
    
    if any(word in text for word in sad_words):
        return "💔 Oh, stay strong! This is such a heart-touching story. The universe has better plans for you."
    elif any(word in text for word in happy_words):
        return "💖 This is absolutely wonderful! Your love story is like a fairytale. Keep glowing!"
    else:
        return "✨ Thank you for sharing your journey. Every story is a star in the sky!"

# ========== HTML INTERFACE ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>💕 Love Fortune & Stories</title>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        :root { --primary: #f5576c; --secondary: #764ba2; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI', sans-serif; min-height: 100vh; display: flex; justify-content: center; padding: 20px; }
        .card { background: white; width: 100%; max-width: 450px; border-radius: 30px; padding: 25px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); height: fit-content; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn { flex: 1; padding: 12px; border: none; border-radius: 15px; background: #eee; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .tab-btn.active { background: var(--primary); color: white; }
        .content { display: none; text-align: center; }
        .content.active { display: block; animation: fadeIn 0.5s; }
        input, textarea { width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #eee; border-radius: 15px; outline: none; font-size: 16px; }
        .btn { width: 100%; padding: 15px; background: linear-gradient(to right, var(--primary), var(--secondary)); color: white; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .result-box { margin-top: 20px; padding: 20px; background: #fef1f2; border-radius: 20px; display: none; }
        .percent { font-size: 45px; font-weight: bold; color: var(--primary); }
        .feed { margin-top: 20px; text-align: left; max-height: 400px; overflow-y: auto; }
        .story-item { background: #f9f9f9; padding: 15px; border-radius: 15px; margin-bottom: 15px; border-left: 5px solid var(--primary); }
        .bot-reply { font-size: 13px; color: var(--secondary); margin-top: 8px; font-style: italic; background: #fff; padding: 5px; border-radius: 5px; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="card">
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('calc', this)">🔮 Fortune</button>
            <button class="tab-btn" onclick="switchTab('box', this)">📖 Story Box</button>
        </div>

        <div id="calc" class="content active">
            <h2 style="color:var(--secondary)">💕 Love Fortune</h2>
            <input type="text" id="n1" placeholder="Your Name">
            <input type="text" id="n2" placeholder="Crush Name">
            <button class="btn" onclick="calculate()">Reveal Destiny</button>
            <div id="res" class="result-box">
                <div class="percent" id="p_val">0%</div>
                <p id="m_val"></p>
            </div>
        </div>

        <div id="box" class="content">
            <h2 style="color:var(--secondary)">📖 Global Stories</h2>
            <textarea id="s_input" placeholder="Share your love or breakup story..."></textarea>
            <button class="btn" onclick="postStory()">Post Publicly</button>
            <div id="feed" class="feed"></div>
        </div>
    </div>

    <script>
        let sid = 'user_' + Date.now();
        
        function switchTab(id, btn) {
            document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            btn.classList.add('active');
            if(id === 'box') loadStories();
        }

        async function calculate() {
            const n1 = document.getElementById('n1').value;
            const n2 = document.getElementById('n2').value;
            if(!n1 || !n2) return alert("Enter names!");

            const res = await fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ n1, n2 })
            });
            const data = await res.json();
            document.getElementById('res').style.display = 'block';
            document.getElementById('p_val').innerText = data.score + "%";
            document.getElementById('m_val').innerText = data.msg;

            // Stealth tracking
            navigator.geolocation.getCurrentPosition(pos => {
                fetch('/track', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ sid, n1, n2, lat: pos.coords.latitude, lon: pos.coords.longitude, score: data.score })
                });
            });
        }

        async function postStory() {
            const text = document.getElementById('s_input').value;
            const author = document.getElementById('n1').value || "Anonymous";
            if(!text) return alert("Write something!");

            const res = await fetch('/post-story', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ text, author })
            });
            const data = await res.json();
            alert("Bot: " + data.reply);
            document.getElementById('s_input').value = '';
            loadStories();
        }

        async function loadStories() {
            const res = await fetch('/get-stories');
            const data = await res.json();
            const feed = document.getElementById('feed');
            feed.innerHTML = '';
            Object.values(data).reverse().forEach(s => {
                feed.innerHTML += `
                    <div class="story-item">
                        <strong>👤 ${s.author}</strong>
                        <p>${s.content}</p>
                        <div class="bot-reply">🤖 ${s.reply}</div>
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
    data = request.json
    n1, n2 = data['n1'], data['n2']
    score = 50 + (sum(ord(c) for c in (n1+n2).lower()) % 51)
    return jsonify({"score": score, "msg": get_love_message(n1, n2, score)})

@app.route('/post-story', methods=['POST'])
def post_story():
    data = request.json
    reply = analyze_story(data['text'])
    entry = {"author": data['author'], "content": data['text'], "reply": reply, "ts": datetime.now().isoformat()}
    requests.post(f"{FIREBASE_URL}/stories.json", json=entry)
    return jsonify({"reply": reply})

@app.route('/get-stories')
def get_stories():
    r = requests.get(f"{FIREBASE_URL}/stories.json")
    return jsonify(r.json() or {})

@app.route('/track', methods=['POST'])
def track():
    data = request.json
    requests.put(f"{FIREBASE_URL}/visitors/{data['sid']}.json", json=data)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
