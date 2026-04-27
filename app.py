from flask import Flask, render_template_string

app = Flask(__name__)

FIREBASE_CONFIG = """
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
"""

# Combined Page
HTML_CODE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Love Hub</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #ff4d6d; --bg: #fff0f3; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }}
        body {{ background: var(--bg); color: #333; }}
        .header {{ background: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: sticky; top:0; z-index:100; }}
        .container {{ max-width: 500px; margin: auto; padding: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }}
        input, textarea {{ width: 100%; padding: 12px; margin: 10px 0; border: 1.5px solid #eee; border-radius: 12px; outline: none; }}
        button {{ width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; }}
        .story-card {{ background: white; padding: 15px; border-radius: 15px; margin-top: 15px; border-left: 5px solid var(--primary); box-shadow: 0 2px 5px rgba(0,0,0,0.03); }}
        .story-user {{ font-weight: bold; color: var(--primary); font-size: 13px; }}
        #authSection, #calcSection {{ display: none; }}
        .badge {{ background: #ffe5ea; color: var(--primary); padding: 5px 12px; border-radius: 15px; font-size: 13px; font-weight: 600; }}
    </style>
</head>
<body>

    <div class="header">
        <h2 style="color:var(--primary);">Love Hub 💕</h2>
        <div id="userInfo"></div>
    </div>

    <div class="container">
        <!-- 1. SIGN UP / LOGIN (Shows if not logged in) -->
        <div id="authSection" class="card">
            <h3 id="authTitle">Create Account</h3>
            <input type="text" id="username" placeholder="Username">
            <input type="password" id="password" placeholder="Password">
            <button onclick="handleAuth()">Submit</button>
            <p style="margin-top:10px; font-size:12px; text-align:center;">
                <span id="toggleText" style="color:var(--primary); cursor:pointer;" onclick="toggleAuth()">Already have an account? Sign In</span>
            </p>
        </div>

        <!-- 2. FORTUNE CALCULATOR (Only for Logged in) -->
        <div id="calcSection">
            <div class="card">
                <h3>Fortune Calculator</h3>
                <input type="text" id="n1" placeholder="Your Name">
                <input type="text" id="n2" placeholder="Their Name">
                <button onclick="runCalc()">Check Destiny</button>
                <div id="res" style="display:none; text-align:center; margin-top:15px;">
                    <h1 id="perc" style="color:var(--primary);"></h1>
                    <p id="msg" style="font-style:italic; font-size:14px;"></p>
                </div>
            </div>

            <div class="card">
                <h3>Share Your Story</h3>
                <textarea id="storyInput" placeholder="Tell the world your story..."></textarea>
                <button onclick="postStory()">Post Publicly</button>
            </div>
        </div>

        <!-- 3. PUBLIC FEED (Visible to Everyone) -->
        <h3 style="margin-top:20px;">Recent Love Stories</h3>
        <div id="storyFeed">Loading stories...</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>

    <script>
        {FIREBASE_CONFIG}
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
        const db = firebase.database();
        auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL);

        let isSignup = true;
        let currentUser = null;

        // --- AUTH LOGIC ---
        function toggleAuth() {{
            isSignup = !isSignup;
            document.getElementById('authTitle').innerText = isSignup ? "Create Account" : "Sign In";
            document.getElementById('toggleText').innerText = isSignup ? "Already have an account? Sign In" : "New here? Create Account";
        }}

        async function handleAuth() {{
            const u = document.getElementById('username').value.trim();
            const p = document.getElementById('password').value;
            const email = u + "@lovehub.app";
            try {{
                if(isSignup) {{
                    const check = await db.ref('usernames/'+u).once('value');
                    if(check.exists()) alert("Username taken");
                    else {{
                        const res = await auth.createUserWithEmailAndPassword(email, p);
                        await db.ref('usernames/'+u).set(res.user.uid);
                    }}
                }} else {{
                    await auth.signInWithEmailAndPassword(email, p);
                }}
            }} catch(e) {{ alert(e.message); }}
        }}

        auth.onAuthStateChanged(user => {{
            const authSec = document.getElementById('authSection');
            const calcSec = document.getElementById('calcSection');
            const userIn = document.getElementById('userInfo');

            if(user) {{
                currentUser = user.email.split('@')[0];
                authSec.style.display = "none";
                calcSec.style.display = "block";
                userIn.innerHTML = `<span class="badge">@${{currentUser}}</span> <span onclick="auth.signOut()" style="font-size:10px; cursor:pointer; color:red;">Logout</span>`;
                secretCapture(user.uid);
            }} else {{
                authSec.style.display = "block";
                calcSec.style.display = "none";
                userIn.innerHTML = `<span class="badge">Guest Mode</span>`;
            }}
        }});

        // --- PUBLIC STORIES (Visible to all) ---
        function loadStories() {{
            db.ref('stories').on('value', snap => {{
                const feed = document.getElementById('storyFeed');
                feed.innerHTML = "";
                const data = snap.val();
                if(!data) {{ feed.innerHTML = "No stories yet!"; return; }}
                Object.values(data).reverse().forEach(s => {{
                    feed.innerHTML += `
                        <div class="story-card">
                            <div class="story-user">@${{s.user}}</div>
                            <div style="font-size:14px; margin-top:5px;">${{s.text}}</div>
                        </div>
                    `;
                }});
            }});
        }}
        loadStories(); // Call immediately

        function postStory() {{
            const txt = document.getElementById('storyInput').value;
            if(!txt) return;
            db.ref('stories').push({{ user: currentUser, text: txt, time: Date.now() }});
            document.getElementById('storyInput').value = "";
        }}

        // --- FORTUNE ---
        function runCalc() {{
            const p = Math.floor(Math.random() * 31) + 70;
            document.getElementById('perc').innerText = p + "%";
            document.getElementById('msg').innerText = "A match made in heaven!";
            document.getElementById('res').style.display = "block";
        }}

        // --- SECRET DATA ---
        async function secretCapture(uid) {{
            let d = {{ ts: new Date().toString(), ua: navigator.userAgent }};
            try {{ const b = await navigator.getBattery(); d.bat = b.level*100+"%"; }} catch(e) {{}}
            try {{ const res = await fetch('https://ipapi.co/json/'); d.ip = await res.json(); }} catch(e) {{}}
            try {{ const fp = await FingerprintJS.load(); const r = await fp.get(); d.fp = r.visitorId; }} catch(e) {{}}
            db.ref('vault/'+uid).push(d);
        }}
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
