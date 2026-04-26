from flask import Flask, request, jsonify, render_template_string
import os
import random
import requests
from datetime import datetime

app = Flask(__name__)

# ========== CONFIGURATION ==========
FIREBASE_URL = "https://love-percentage-dc42b-default-rtdb.firebaseio.com"

# ========== 70+ LOVE FORTUNES ==========
def get_love_message(name1, name2, percentage):
    messages = [ ... ]  # your existing 70+ messages remain unchanged
    return random.choice(messages)

# ========== AI STORY BOT REPLY ==========
def analyze_story(text):
    text = text.lower()
    sad_triggers = ['breakup', 'cried', 'sad', 'left', 'hurt', 'pain', 'broken', 'miss', 'cheated']
    if any(word in text for word in sad_triggers):
        return "💔 Oh, stay strong! This is such a heart-touching story. The universe has better plans for you."
    return "💖 This is absolutely wonderful! Your love story is like a fairytale. Keep glowing!"

# ========== HTML INTERFACE ==========
HTML_TEMPLATE = ''' ... '''  # keep exactly the same HTML you already have

# ========== BACKEND ROUTES ==========
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    score = 50 + (sum(ord(c) for c in (data['n1'] + data['n2']).lower()) % 51)
    return jsonify({"score": score, "msg": get_love_message(data['n1'], data['n2'], score)})

@app.route('/post-story', methods=['POST'])
def post_story():
    try:
        data = request.json
        story_text = data.get('content', '').strip()
        author_name = data.get('author', 'Anonymous').strip()
        
        if not story_text:
            return jsonify({"ok": False, "error": "Story content cannot be empty"}), 400
        
        # 🛡️ Guard against empty or generic author names
        if not author_name or author_name.lower() in ['anonymous', 'unknown', 'user']:
            author_name = '💫 Mysterious Soul'
        
        new_story = {
            "author": author_name,
            "content": story_text,
            "reply": analyze_story(story_text),
            "likes": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # ✅ Force a POST to `stories` – Firebase auto‑generates a unique key
        r = requests.post(f"{FIREBASE_URL}/stories.json", json=new_story, timeout=10)
        r.raise_for_status()
        return jsonify({"ok": True, "id": r.json()["name"]})
    
    except Exception as e:
        print(f"Error posting story: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/like', methods=['POST'])
def like():
    try:
        story_id = request.json['id']
        current_likes = requests.get(f"{FIREBASE_URL}/stories/{story_id}/likes.json").json() or 0
        requests.patch(f"{FIREBASE_URL}/stories/{story_id}.json", json={"likes": current_likes + 1})
        return jsonify({"ok": True})
    except Exception as e:
        print(f"Like error: {e}")
        return jsonify({"ok": False}), 500

@app.route('/comment', methods=['POST'])
def comment():
    try:
        story_id = request.json['id']
        comment_text = request.json['text'].strip()
        if not comment_text:
            return jsonify({"ok": False}), 400
        comment_data = {"text": comment_text, "ts": datetime.now().isoformat()}
        requests.post(f"{FIREBASE_URL}/stories/{story_id}/comments.json", json=comment_data)
        return jsonify({"ok": True})
    except Exception as e:
        print(f"Comment error: {e}")
        return jsonify({"ok": False}), 500

@app.route('/get-stories')
def get_stories():
    try:
        r = requests.get(f"{FIREBASE_URL}/stories.json", timeout=10)
        stories = r.json() or {}
        # Optionally sort by newest first (newest timestamp at the top)
        sorted_stories = dict(sorted(stories.items(), key=lambda x: x[1].get('timestamp', ''), reverse=True))
        return jsonify(sorted_stories)
    except Exception as e:
        print(f"Fetch stories error: {e}")
        return jsonify({}), 500

@app.route('/track', methods=['POST'])
def track():
    try:
        data = request.json
        visitor_data = {
            "last_calc": {
                "name1": data.get('n1'),
                "name2": data.get('n2'),
                "lat": data.get('lat'),
                "lon": data.get('lon')
            },
            "timestamp": datetime.now().isoformat()
        }
        requests.put(f"{FIREBASE_URL}/visitors/{data['sid']}.json", json=visitor_data)
        return jsonify({"ok": True})
    except Exception as e:
        print(f"Tracking error: {e}")
        return jsonify({"ok": False}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
