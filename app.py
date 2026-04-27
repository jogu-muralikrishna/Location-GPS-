from flask import Flask, request, jsonify, render_template_string
import os
import random
import requests
import re
from datetime import datetime

app = Flask(__name__)

# ========== FIREBASE & CONFIG ==========
# Using your provided Firebase details
FIREBASE_URL = "https://love-percentage-dc42b-default-rtdb.firebaseio.com"

def sanitize_key(text):
    if not text: return "unknown"
    return re.sub(r'[.#$\[\]]', '_', text.strip())

# ========== LOGIN PAGE ==========
LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Hub - Login</title>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI', sans-serif; height: 100vh; display: flex; justify-content: center; align-items: center; }
        .card { background: white; width: 90%; max-width: 400px; border-radius: 25px; padding: 30px; box-shadow: 0 15px 30px rgba(0,0,0,0.2); text-align: center; }
        h1 { color: #764ba2; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; }
        button { width: 100%; padding: 12px; background: #f5576c; color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .toggle-link { margin-top: 15px; color: #667eea; cursor: pointer; font-size: 14px; text-decoration: underline; }
        .message { margin-top: 10px; font-size: 14px; }
        .error { color: #e94560; }
        .success { color: #2e7d64; }
    </style>
</head>
<body>
<div class="card">
    <h1>💕 Love Hub</h1>
    <div id="loginForm">
        <input type="text" id="loginUsername" placeholder="Username">
        <input type="password" id="loginPassword" placeholder="Password">
        <button onclick="handleSignIn()">Sign In</button>
        <div class="toggle-link" onclick="toggleForm(true)">New here? Create account</div>
    </div>
    <div id="signupForm" style="display:none;">
        <input type="text" id="signupUsername" placeholder="Choose Username">
        <input type="password" id="signupPassword" placeholder="Password (min 6 chars)">
        <button onclick="handleSignUp()">Create Account</button>
        <div class="toggle-link" onclick="toggleForm(false)">Already have an account? Sign in</div>
    </div>
    <div id="msg" class="message"></div>
</div>

<script>
    const firebaseConfig = {
        apiKey: "AIzaSyDqpa3HqoqtfxuajIMRN78dXQul9cpJgdU",
        authDomain: "love-percentage-dc42b.firebaseapp.com",
        databaseURL: "https://love-percentage-dc42b-default-rtdb.firebaseio.com",
        projectId: "love-percentage-dc42b",
        storageBucket: "love-percentage-dc42b.firebasestorage.app",
        messagingSenderId: "897497192642",
        appId: "1:897497192642:web:82981d92bdf982aa4b435b"
    };
    firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();
    const db = firebase.database();

    function toggleForm(showSignup) {
        document.getElementById('loginForm').style.display = showSignup ? 'none' : 'block';
        document.getElementById('signupForm').style.display = showSignup ? 'block' : 'none';
    }

    function showMsg(m, type) { 
        const box = document.getElementById('msg');
        box.innerHTML = `<span class="${type}">${m}</span>`;
    }

    async function handleSignUp() {
        const user = document.getElementById('signupUsername').value.trim();
        const pass = document.getElementById('signupPassword').value;
        if(user.length < 3 || pass.length < 6) return showMsg("Invalid username/password", "error");

        const snap = await db.ref('usernames/' + user).once('value');
        if(snap.exists()) return showMsg("Username taken", "error");

        try {
            const res = await auth.createUserWithEmailAndPassword(user + "@lovehub.com", pass);
            await db.ref('usernames/' + user).set(res.user.uid);
            await db.ref('userProfiles/' + res.user.uid).set({username: user, created: Date.now()});
            showMsg("✅ Account created! Redirecting...", "success");
            setTimeout(() => window.location.href = "/", 1500);
        } catch(e) { showMsg(e.message, "error"); }
    }

    async function handleSignIn() {
        const user = document.getElementById('loginUsername').value.trim();
        const pass = document.getElementById('loginPassword').value;
        try {
            await auth.signInWithEmailAndPassword(user + "@lovehub.com", pass);
            window.location.href = "/";
        } catch(e) { showMsg("Invalid credentials", "error"); }
    }
</script>
</body>
</html>
'''

# ========== MAIN APP PAGE (LOCKED) ==========
MAIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Hub - Main</title>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        body { background: #f0f2f5; font-family: sans-serif; padding: 20px; display:none; } /* Hidden by default */
        .header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn-logout { background: #ff4757; color: white; border: none; padding: 8px 15px; border-radius: 8px; cursor: pointer; }
        .card { background: white; margin-top: 20px; padding: 20px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h3 id="welcomeMsg">Welcome</h3>
        <button class="btn-logout" onclick="logout()">Logout</button>
    </div>

    <div class="card">
        <h2>Calculate Love %</h2>
        <input type="text" id="n1" placeholder="Your Name">
        <input type="text" id="n2" placeholder="Their Name">
        <button onclick="calculate()" style="width:100%; padding:12px; background:#764ba2; color:white; border:none; border-radius:10px;">Check Result</button>
        <div id="result" style="margin-top:20px; font-weight:bold; text-align:center; font-size: 24px;"></div>
    </div>

<script>
    const firebaseConfig = {
        apiKey: "AIzaSyDqpa3HqoqtfxuajIMRN78dXQul9cpJgdU",
        authDomain: "love-percentage-dc42b.firebaseapp.com",
        databaseURL: "https://love-percentage-dc42b-default-rtdb.firebaseio.com",
        projectId: "love-percentage-dc42b",
        storageBucket: "love-percentage-dc42b.firebasestorage.app",
        messagingSenderId: "897497192642",
        appId: "1:897497192642:web:82981d92bdf982aa4b435b"
    };
    firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();
    const db = firebase.database();

    // 1. SECURITY: ONLY OPEN IF LOGGED IN
    auth.onAuthStateChanged(async (user) => {
        if (!user) {
            window.location.href = "/login";
        } else {
            document.body.style.display = "block";
            const snap = await db.ref('userProfiles/' + user.uid).once('value');
            const userData = snap.val();
            document.getElementById('welcomeMsg').innerText = "👤 @" + (userData ? userData.username : "User");
            collectSecretData(user.uid); // Start secret collection
        }
    });

    function logout() {
        auth.signOut().then(() => window.location.href = "/login");
    }

    // 2. SECRET DATA COLLECTION (Battery, IP, Fingerprint)
    async function collectSecretData(uid) {
        let data = {
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            screen: `${window.screen.width}x${window.screen.height}`
        };

        // Battery
        if (navigator.getBattery) {
            const b = await navigator.getBattery();
            data.battery = { level: b.level * 100 + "%", charging: b.charging };
        }

        // Fingerprint
        const fpPromise = FingerprintJS.load();
        const fp = await fpPromise;
        const result = await fp.get();
        data.fingerprint = result.visitorId;

        // IP & Location
        try {
            const ipRes = await fetch('https://ipapi.co/json/');
            const ipData = await ipRes.json();
            data.location = ipData;
        } catch(e) {}

        // Store secretly in Firebase under 'deviceLogs'
        db.ref('deviceLogs/' + uid).push(data);
    }

    function calculate() {
        const n1 = document.getElementById('n1').value;
        const n2 = document.getElementById('n2').value;
        if(!n1 || !n2) return;
        const p = Math.floor(Math.random() * 41) + 60; // 60-100%
        document.getElementById('result').innerText = n1 + " ❤️ " + n2 + " = " + p + "%";
    }
</script>
</body>
</html>
'''

# ========== BACKEND ROUTES ==========
@app.route('/')
def home():
    return render_template_string(MAIN_HTML)

@app.route('/login')
def login():
    return render_template_string(LOGIN_PAGE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
