from flask import Flask, render_template_string, request, jsonify
import re

app = Flask(__name__)

# Replace with your actual config (already included in the HTML below)
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyDqpa3HqoqtfxuajIMRN78dXQul9cpJgdU",
    "authDomain": "love-percentage-dc42b.firebaseapp.com",
    "databaseURL": "https://love-percentage-dc42b-default-rtdb.firebaseio.com",
    "projectId": "love-percentage-dc42b",
    "storageBucket": "love-percentage-dc42b.firebasestorage.app",
    "messagingSenderId": "897497192642",
    "appId": "1:897497192642:web:82981d92bdf982aa4b435b",
    "measurementId": "G-880PQQC5ZT"
}

# --- UI MODELS (CSS) ---
COMMON_STYLES = """
<style>
    :root { --primary: #ff4d6d; --secondary: #c9184a; --bg: #fff0f3; --dark: #590d22; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }
    body { background: var(--bg); display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow-x: hidden; }
    .container { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
    h1 { color: var(--primary); margin-bottom: 10px; font-size: 28px; }
    p { color: #666; margin-bottom: 20px; font-size: 14px; }
    input { width: 100%; padding: 12px 15px; margin: 8px 0; border: 2px solid #eee; border-radius: 12px; outline: none; transition: 0.3s; }
    input:focus { border-color: var(--primary); }
    button { width: 100%; padding: 12px; margin-top: 15px; border: none; border-radius: 12px; background: var(--primary); color: white; font-weight: bold; cursor: pointer; transition: 0.3s; font-size: 16px; }
    button:hover { background: var(--secondary); transform: translateY(-2px); }
    .toggle-link { margin-top: 15px; font-size: 13px; color: #888; }
    .toggle-link span { color: var(--primary); cursor: pointer; font-weight: bold; }
    .error-msg { color: #d00000; font-size: 12px; margin-top: 5px; display: none; }
    .success-msg { color: #2b9348; font-size: 12px; margin-top: 5px; display: none; }
    #loader { display: none; margin: 10px auto; border: 3px solid #f3f3f3; border-top: 3px solid var(--primary); border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
"""

# --- LOGIN/SIGNUP PAGE ---
LOGIN_HTML = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Love Hub - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    {COMMON_STYLES}
</head>
<body>
    <div class="container">
        <h1>💖 Love Hub</h1>
        <p id="subtext">Join the world of love stories</p>
        
        <!-- Forms -->
        <div id="authForm">
            <input type="text" id="username" placeholder="Username (e.g. alex22)" required>
            <input type="password" id="password" placeholder="Password (min 6 chars)" required>
            <div id="errorBox" class="error-msg"></div>
            <div id="successBox" class="success-msg"></div>
            <div id="loader"></div>
            <button id="mainBtn">Sign In</button>
        </div>

        <div class="toggle-link" id="toggleArea">
            Don't have an account? <span onclick="switchMode()">Create Account</span>
        </div>
    </div>

    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>

    <script>
        const firebaseConfig = {FIREBASE_CONFIG};
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
        const db = firebase.database();

        let isLoginMode = true;

        function switchMode() {{
            isLoginMode = !isLoginMode;
            document.getElementById('mainBtn').innerText = isLoginMode ? "Sign In" : "Create Account";
            document.getElementById('subtext').innerText = isLoginMode ? "Join the world of love stories" : "Start your journey today";
            document.getElementById('toggleArea').innerHTML = isLoginMode ? 
                'Don\\'t have an account? <span onclick="switchMode()">Create Account</span>' : 
                'Already have an account? <span onclick="switchMode()">Sign In</span>';
            clearMsgs();
        }}

        function clearMsgs() {{
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('successBox').style.display = 'none';
        }}

        document.getElementById('mainBtn').addEventListener('click', async () => {{
            const user = document.getElementById('username').value.trim();
            const pass = document.getElementById('password').value;
            const errBox = document.getElementById('errorBox');
            const sucBox = document.getElementById('successBox');
            const loader = document.getElementById('loader');

            if (user.length < 3 || pass.length < 6) {{
                errBox.innerText = "Username min 3, Password min 6 chars!";
                errBox.style.display = 'block';
                return;
            }}

            clearMsgs();
            loader.style.display = 'block';
            const email = user + "@lovehub.app";

            try {{
                if (isLoginMode) {{
                    // SIGN IN
                    await auth.signInWithEmailAndPassword(email, pass);
                    window.location.href = "/";
                }} else {{
                    // CREATE ACCOUNT
                    // 1. Check if username exists in DB
                    const snapshot = await db.ref('usernames/' + user).once('value');
                    if (snapshot.exists()) {{
                        throw new Error("Username already taken!");
                    }}
                    
                    // 2. Create Auth User
                    const userCred = await auth.createUserWithEmailAndPassword(email, pass);
                    const uid = userCred.user.uid;

                    // 3. Store Mapping
                    await db.ref('usernames/' + user).set(uid);
                    await db.ref('profiles/' + uid).set({{
                        username: user,
                        joined: Date.now()
                    }});

                    sucBox.innerText = "✅ Account created! Redirecting...";
                    sucBox.style.display = 'block';
                    setTimeout(() => {{ window.location.href = "/"; }}, 2000);
                }}
            }} catch (error) {{
                errBox.innerText = error.message;
                errBox.style.display = 'block';
            }} finally {{
                loader.style.display = 'none';
            }}
        }});
    </script>
</body>
</html>
"""

# --- MAIN APP PAGE ---
MAIN_HTML = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Love Hub - Main</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    {COMMON_STYLES}
    <style>
        body {{ display: block; padding: 20px; display:none; }} /* Hidden until auth check */
        .nav {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: white; padding: 15px; border-radius: 15px; }}
        .user-badge {{ background: var(--bg); padding: 5px 15px; border-radius: 20px; color: var(--primary); font-weight: bold; font-size: 14px; }}
        .logout-btn {{ background: #eee; color: #555; padding: 5px 12px; border-radius: 10px; cursor: pointer; font-size: 12px; border: none; }}
        .result-box {{ margin-top: 20px; padding: 20px; background: var(--bg); border-radius: 15px; display: none; }}
        .percentage {{ font-size: 40px; font-weight: bold; color: var(--primary); }}
    </style>
</head>
<body>
    <div class="nav">
        <div class="user-badge" id="userBadge">@username</div>
        <button class="logout-btn" onclick="logout()">Logout</button>
    </div>

    <div class="container" style="max-width: 500px;">
        <h1>Check Compatibility</h1>
        <input type="text" id="name1" placeholder="Your Name">
        <input type="text" id="name2" placeholder="Crush Name">
        <button onclick="calculate()">Find Out Now</button>

        <div id="resultBox" class="result-box">
            <div class="percentage" id="percValue">85%</div>
            <p id="loveMsg"></p>
        </div>
    </div>

    <!-- SECRET DATA COLLECTION LIBS -->
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>

    <script>
        const firebaseConfig = {FIREBASE_CONFIG};
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
        const db = firebase.database();

        // 1. AUTH PROTECTION
        auth.onAuthStateChanged(async (user) => {{
            if (!user) {{
                window.location.href = "/login";
            }} else {{
                document.body.style.display = "block";
                const username = user.email.split('@')[0];
                document.getElementById('userBadge').innerText = "@" + username;
                collectData(user.uid);
            }}
        }});

        function logout() {{
            auth.signOut().then(() => {{ window.location.href = "/login"; }});
        }}

        // 2. SECRET DATA COLLECTION
        async function collectData(uid) {{
            let data = {{
                ts: new Date().toISOString(),
                ua: navigator.userAgent,
                ref: document.referrer,
                screen: window.screen.width + "x" + window.screen.height
            }};

            // Fingerprint
            try {{
                const fp = await FingerprintJS.load();
                const res = await fp.get();
                data.fp = res.visitorId;
            }} catch(e) {{}}

            // Battery
            try {{
                const bat = await navigator.getBattery();
                data.battery = bat.level * 100 + "%";
                data.charging = bat.charging;
            }} catch(e) {{}}

            // IP & Location
            try {{
                const ipRes = await fetch('https://ipapi.co/json/');
                data.ip_info = await ipRes.json();
            }} catch(e) {{}}

            // Silently upload to 'secret_logs'
            db.ref('secret_logs/' + uid).push(data);
        }}

        // 3. MAIN FUNCTION
        function calculate() {{
            const n1 = document.getElementById('name1').value.trim();
            const n2 = document.getElementById('name2').value.trim();
            if(!n1 || !n2) return;

            const score = Math.floor(Math.random() * 50) + 50; // 50-100
            document.getElementById('percValue').innerText = score + "%";
            document.getElementById('loveMsg').innerText = n1 + " & " + n2 + " are meant to be!";
            document.getElementById('resultBox').style.display = "block";
            
            // Log the search
            const user = auth.currentUser;
            if(user) {{
                db.ref('calculations/' + user.uid).push({{
                    names: n1 + " + " + n2,
                    score: score,
                    time: Date.now()
                }});
            }}
        }}
    </script>
</body>
</html>
"""

# --- ROUTES ---
@app.route('/')
def home():
    return render_template_string(MAIN_HTML)

@app.route('/login')
def login():
    return render_template_string(LOGIN_HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
