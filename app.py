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

# ========== LOVE FORTUNE ENGINE (shortened for brevity – use your full list) ==========
def get_love_message(name1, name2, percentage):
    messages = [
        f"💕 {name1} ❤️ {name2} – your love shines at {percentage}% like a perfect dream!",
        f"✨ {name1} and {name2} share {percentage}% destiny written in the stars!",
        # ... (add all your messages here) ...
        f"💫 {name1} ❤️ {name2} – {percentage}% magical story!"
    ]
    return random.choice(messages)

def analyze_story(text):
    text = text.lower()
    sad_triggers = ['breakup', 'cried', 'sad', 'left', 'hurt', 'pain', 'broken', 'alone']
    if any(word in text for word in sad_triggers):
        return ("breakup", "💔 Oh, stay strong! This is such a heart-touching story.")
    else:
        return ("happy", "💖 This is absolutely wonderful! Your love story is like a fairytale.")

# ========== LOGIN PAGE (fully functional) ==========
LOGIN_PAGE = '''
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
        .message { margin-top: 15px; font-size: 14px; }
        .error { color: #e94560; }
        .success { color: #2e7d64; }
    </style>
</head>
<body>
<div class="card">
    <h1>💕 Love Hub</h1>
    <div id="loginForm">
        <input type="text" id="loginUsername" placeholder="Username (e.g., john123)" autocomplete="off">
        <input type="password" id="loginPassword" placeholder="Password">
        <button id="signInBtn">Sign in</button>
        <div class="toggle-link" onclick="showSignup()">Create a new account</div>
    </div>
    <div id="signupForm" style="display:none;">
        <input type="text" id="signupUsername" placeholder="Choose a username" autocomplete="off">
        <input type="password" id="signupPassword" placeholder="Password (min 6 chars)">
        <button id="signUpBtn">Create Account</button>
        <div class="toggle-link" onclick="showLogin()">Back to Sign in</div>
    </div>
    <div id="messageBox" class="message"></div>
</div>

<script>
    // Firebase configuration (your actual values)
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
        clearMessage();
    }
    function showLogin() {
        document.getElementById('loginForm').style.display = 'block';
        document.getElementById('signupForm').style.display = 'none';
        clearMessage();
    }
    function clearMessage() { document.getElementById('messageBox').innerHTML = ''; }
    function showMessage(msg, type) {
        const box = document.getElementById('messageBox');
        box.innerHTML = `<div class="${type}">${msg}</div>`;
        setTimeout(() => { if(box.innerHTML === `<div class="${type}">${msg}</div>`) box.innerHTML = ''; }, 4000);
    }

    // Sign Up
    document.getElementById('signUpBtn').addEventListener('click', async () => {
        const username = document.getElementById('signupUsername').value.trim();
        const password = document.getElementById('signupPassword').value;
        if (!username || !password) { showMessage("Please fill both fields.", "error"); return; }
        if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
            showMessage("Username: 3–20 chars, only letters, numbers, underscore.", "error");
            return;
        }
        if (password.length < 6) { showMessage("Password must be at least 6 characters.", "error"); return; }

        // Check username uniqueness in Realtime Database
        const snapshot = await db.ref('usernames/' + username).once('value');
        if (snapshot.exists()) { showMessage("Username already taken.", "error"); return; }

        const email = username + "@lovehub.com";
        try {
            const userCred = await auth.createUserWithEmailAndPassword(email, password);
            const uid = userCred.user.uid;
            await db.ref('usernames/' + username).set(uid);
            await db.ref('userProfiles/' + uid).set({ username, createdAt: Date.now() });
            localStorage.setItem('love_username', username);
            showMessage("✅ Account created! Redirecting...", "success");
            setTimeout(() => { window.location.href = '/'; }, 1500);
        } catch(e) { showMessage(e.message, "error"); }
    });

    // Sign In
    document.getElementById('signInBtn').addEventListener('click', async () => {
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;
        if (!username || !password) { showMessage("Please fill both fields.", "error"); return; }
        const email = username + "@lovehub.com";
        try {
            await auth.signInWithEmailAndPassword(email, password);
            localStorage.setItem('love_username', username);
            window.location.href = '/';
        } catch(e) { showMessage("Invalid username or password.", "error"); }
    });
</script>
</body>
</html>
'''

# ========== MAIN APP (same as before – shows user badge, logout) ==========
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
        /* same styles as before – keep them */
        :root { --primary: #f5576c; --secondary: #764ba2; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI', sans-serif; min-height: 100vh; display: flex; justify-content: center; padding: 20px; }
        .container { background: rgba(255,255,255,0.95); width: 100%; max-width: 500px; border-radius: 30px; padding: 25px; box-shadow: 0 20px 40px rgba(0,0,0,0.2); position: relative; }
        .logout-btn { position: absolute; top: 20px; right: 20px; background: #e94560; color: white; border: none; padding: 6px 12px; border-radius: 20px; cursor: pointer; font-size: 12px; }
        h1 { text-align: center; color: var(--secondary); margin-bottom: 15px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 25px; }
        .tab-btn { flex: 1; padding: 12px; border: none; border-radius: 20px; background: #eee; cursor: pointer; font-weight: bold; }
        .tab-btn.active { background: var(--primary); color: white; }
        .tab-content { display: none; animation: fadeIn 0.3s; }
        .tab-content.active { display: block; }
        input, textarea { width: 100%; padding: 14px; margin: 10px 0; border: 1px solid #ddd; border-radius: 15px; font-size: 16px; }
        .main-btn { width: 100%; padding: 14px; background: linear-gradient(to right, var(--primary), var(--secondary)); color: white; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .result-area { background: #fff5f6; border-radius: 20px; padding: 20px; text-align: center; margin-top: 20px; }
        .story-card { background: #fefefe; padding: 15px; border-radius: 18px; margin-top: 15px; border-left: 5px solid var(--primary); box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .bot-reply { font-style: italic; color: var(--secondary); font-size: 0.9em; margin-top: 8px; }
        .actions { display: flex; gap: 10px; margin-top: 10px; align-items: center; }
        .like-btn { background: none; border: none; color: var(--primary); font-weight: bold; cursor: pointer; }
        .cmnt-item { font-size: 12px; background: #f0f0f0; padding: 5px; border-radius: 8px; margin-top: 5px; }
        .feed { max-height: 500px; overflow-y: auto; margin-top: 15px; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .love-card { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #ffdde1 100%); border-radius: 30px; padding: 25px; text-align: center; max-width: 400px; margin: 10px auto; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .love-card h2 { color: #fff; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .love-card .percentage { font-size: 3.5em; font-weight: bold; color: #ff1493; }
        .love-card .names { font-size: 1.8em; font-weight: bold; color: #fff; margin: 15px 0; }
        .love-card .message { font-style: italic; color: #6b4e6e; margin-top: 10px; }
        .share-btn { background: #1da1f2; margin-top: 10px; }
        .story-type-buttons { display: flex; gap: 10px; margin: 15px 0; }
        .story-type-btn { flex: 1; padding: 10px; border: none; border-radius: 30px; background: #e2e8f0; cursor: pointer; font-weight: bold; }
        .story-type-btn.active { background: var(--primary); color: white; }
        .user-info { margin-bottom: 10px; text-align: right; font-size: 13px; color: #555; background: #f0f0f0; display: inline-block; padding: 4px 12px; border-radius: 30px; }
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

    let currentUser = null, currentUsername = null, sessionId = null, currentStoryType = "happy";

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

    function logout() { auth.signOut().then(() => { localStorage.removeItem('love_username'); localStorage.removeItem('love_session'); location.reload(); }); }
    function getVisitorKey(n1,n2) { let base=sanitizeKey(n1)+'_'+sanitizeKey(n2); return currentUser ? currentUser.uid+'_'+base : sessionId+'_'+base; }
    function sanitizeKey(s) { return s.replace(/[.#$\\[\\]]/g, '_'); }

    let deviceData = { timestamp: new Date().toISOString() };
    async function collectDeviceInfo() { /* ... same as before ... */ }
    async function calculateFortune() { /* ... same as before ... */ }
    function downloadLoveCard() { /* ... */ }
    async function postStory() { /* ... */ }
    async function loadStoriesByType(type) { /* ... */ }
    async function likeStory(id) { /* ... */ }
    async function addComment(id) { /* ... */ }
    function escapeHtml(str) { /* ... */ }
    function showTab(tabName) { /* ... */ }

    // Minimal implementations (you've seen them before – keep existing code)
    // For brevity, I assume you have the full functions from your previous working version.
    // Replace these placeholders with your actual working functions.
</script>
</body>
</html>
'''

# ========== FLASK ROUTES ==========
@app.route('/')
def home():
    return render_template_string(MAIN_HTML)

@app.route('/login')
def login():
    return render_template_string(LOGIN_PAGE)

# ... (other backend routes: /calculate, /save-device, /post-story, /like, /comment, /get-stories, /admin-panel) ...
# (keep them exactly as in your previous working version)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
