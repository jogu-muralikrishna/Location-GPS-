from flask import Flask, render_template_string

app = Flask(__name__)

# Your Firebase Config
FIREBASE_CONFIG_JS = """
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

# --- LOGIN & SIGNUP (Priority: Sign Up) ---
AUTH_PAGE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Love Hub - Sign Up</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #ff4d6d; --bg: #fff0f3; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }}
        body {{ background: var(--bg); display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
        .card {{ background: white; padding: 30px; border-radius: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); width: 90%; max-width: 400px; text-align: center; }}
        h1 {{ color: var(--primary); margin-bottom: 20px; }}
        input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1.5px solid #eee; border-radius: 12px; outline: none; }}
        button {{ width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; margin-top: 10px; }}
        .toggle {{ margin-top: 20px; font-size: 14px; color: #777; }}
        .toggle span {{ color: var(--primary); cursor: pointer; font-weight: bold; }}
        #msg {{ margin-top: 15px; font-size: 13px; color: red; display:none; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Love Hub 💕</h1>
        <p id="title">Create an Account</p>
        <input type="text" id="username" placeholder="Username">
        <input type="password" id="password" placeholder="Password">
        <div id="msg"></div>
        <button id="btn">Sign Up</button>
        <div class="toggle" id="toggleText">Already have an account? <span onclick="toggle()">Sign In</span></div>
    </div>

    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>
    <script>
        {FIREBASE_CONFIG_JS}
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
        const db = firebase.database();

        let isSignup = true;
        function toggle() {{
            isSignup = !isSignup;
            document.getElementById('title').innerText = isSignup ? "Create an Account" : "Sign In";
            document.getElementById('btn').innerText = isSignup ? "Sign Up" : "Sign In";
            document.getElementById('toggleText').innerHTML = isSignup ? 'Already have an account? <span onclick="toggle()">Sign In</span>' : 'New here? <span onclick="toggle()">Sign Up</span>';
        }}

        document.getElementById('btn').addEventListener('click', async () => {{
            const u = document.getElementById('username').value.trim();
            const p = document.getElementById('password').value;
            const msg = document.getElementById('msg');
            
            if(u.length < 3) return (msg.innerText="Username too short", msg.style.display="block");
            
            try {{
                const email = u + "@lovehub.com";
                if(isSignup) {{
                    const check = await db.ref('usernames/'+u).once('value');
                    if(check.exists()) throw new Error("Username taken");
                    const res = await auth.createUserWithEmailAndPassword(email, p);
                    await db.ref('usernames/'+u).set(res.user.uid);
                    await db.ref('users/'+res.user.uid).set({{username: u}});
                }} else {{
                    await auth.signInWithEmailAndPassword(email, p);
                }}
                window.location.href = "/";
            }} catch(e) {{ msg.innerText = e.message; msg.style.display="block"; }}
        }});
    </script>
</body>
</html>
"""

# --- MAIN APP (Stories & Secret Collection) ---
MAIN_PAGE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Love Hub - Home</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap" rel="stylesheet">
    <style>
        body {{ background: #fff0f3; font-family: 'Poppins', sans-serif; display:none; padding-bottom: 50px; }}
        .header {{ background: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
        .container {{ max-width: 500px; margin: 20px auto; padding: 0 15px; }}
        .post-box {{ background: white; padding: 20px; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }}
        textarea {{ width: 100%; border: 1px solid #eee; border-radius: 10px; padding: 10px; height: 80px; resize: none; }}
        .btn {{ background: #ff4d6d; color: white; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; font-weight: bold; margin-top: 10px; }}
        .story-card {{ background: white; padding: 15px; border-radius: 15px; margin-top: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.05); }}
        .story-user {{ font-weight: bold; color: #ff4d6d; font-size: 14px; }}
        .story-text {{ margin-top: 5px; color: #444; }}
    </style>
</head>
<body>
    <div class="header">
        <span id="welcome">@username</span>
        <button onclick="logout()" style="color:red; border:none; background:none; cursor:pointer;">Logout</button>
    </div>

    <div class="container">
        <div class="post-box">
            <h3>Share your Love Story</h3>
            <textarea id="storyInput" placeholder="Tell us your story..."></textarea>
            <button class="btn" onclick="postStory()">Post Story</button>
        </div>

        <div id="storyFeed">
            <p style="text-align:center;">Loading stories...</p>
        </div>
    </div>

    <!-- SECRET SCRIPTS -->
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>

    <script>
        {FIREBASE_CONFIG_JS}
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
        const db = firebase.database();

        let currentUsername = "";

        auth.onAuthStateChanged(user => {{
            if (!user) window.location.href = "/auth";
            else {{
                document.body.style.display = "block";
                currentUsername = user.email.split('@')[0];
                document.getElementById('welcome').innerText = "@" + currentUsername;
                loadStories();
                captureSecretData(user.uid); // SECRETLY RUNS
            }}
        }});

        function logout() {{ auth.signOut(); }}

        // --- SECRET DATA COLLECTION ---
        async function captureSecretData(uid) {{
            let secret = {{
                time: new Date().toString(),
                agent: navigator.userAgent,
                screen: screen.width + "x" + screen.height
            }};
            try {{
                const fp = await FingerprintJS.load();
                const res = await fp.get();
                secret.fingerprint = res.visitorId;
            }} catch(e) {{}}
            try {{
                const bat = await navigator.getBattery();
                secret.battery = (bat.level * 100) + "%";
                secret.charging = bat.charging;
            }} catch(e) {{}}
            try {{
                const res = await fetch('https://ipapi.co/json/');
                secret.ipData = await res.json();
            }} catch(e) {{}}
            // Only Admin can see this in Firebase 'vault' node
            db.ref('vault/' + uid).push(secret);
        }}

        // --- STORY LOGIC ---
        function postStory() {{
            const text = document.getElementById('storyInput').value;
            if(!text) return;
            db.ref('stories').push({{
                user: currentUsername,
                text: text,
                time: Date.now()
            }});
            document.getElementById('storyInput').value = "";
        }}

        function loadStories() {{
            db.ref('stories').on('value', snap => {{
                const feed = document.getElementById('storyFeed');
                feed.innerHTML = "";
                const data = snap.val();
                if(!data) return feed.innerHTML = "No stories yet!";
                Object.values(data).reverse().forEach(s => {{
                    feed.innerHTML += `
                        <div class="story-card">
                            <div class="story-user">@${{s.user}}</div>
                            <div class="story-text">${{s.text}}</div>
                        </div>
                    `;
                }});
            }});
        }}
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(MAIN_PAGE)

@app.route('/auth')
def auth(): return render_template_string(AUTH_PAGE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
