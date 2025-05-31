import asyncio
import json
import logging
import base64
import urllib.request
import urllib.parse
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import webbrowser
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import pygame
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import math
import colorsys
from threading import Lock
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경 변수에서 Spotify 클라이언트 정보 로드
def load_env_file(env_path=".env"):
    """
    .env 파일에서 환경 변수를 로드합니다.
    """
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# .env 파일 로드
load_env_file()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("경고: Spotify 클라이언트 ID 또는 시크릿이 설정되지 않았습니다.")
    print(".env 파일을 확인하거나 환경 변수를 설정해주세요.")

SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"
SPOTIFY_SCOPE = "user-read-currently-playing user-read-playback-state"

# 글로벌 변수
access_token = None
refresh_token = None
token_expires_at = None
current_track_data = {}

class SpotifyAPI:
    """Spotify API 클라이언트"""
    
    def __init__(self):
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        
    def get_auth_url(self):
        """인증 URL 생성"""
        params = {
            'client_id': SPOTIFY_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'scope': SPOTIFY_SCOPE,
            'show_dialog': 'true'
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"https://accounts.spotify.com/authorize?{query_string}"
    
    def get_access_token(self, auth_code):
        """인증 코드로 액세스 토큰 획득"""
        global access_token, refresh_token, token_expires_at
        
        # Basic Auth 헤더 생성
        credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': SPOTIFY_REDIRECT_URI
        }
        
        try:
            data_encoded = urllib.parse.urlencode(data).encode()
            req = urllib.request.Request(self.auth_url, data=data_encoded, method='POST')
            req.add_header('Authorization', f'Basic {credentials_b64}')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode())
                    access_token = result['access_token']
                    refresh_token = result['refresh_token']
                    expires_in = result['expires_in']
                    token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    logger.info("✅ Spotify 액세스 토큰 획득 성공!")
                    return True
                else:
                    logger.error(f"❌ 토큰 획득 실패: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ 토큰 획득 오류: {e}")
            return False
    
    def refresh_access_token(self):
        """리프레시 토큰으로 액세스 토큰 갱신"""
        global access_token, token_expires_at
        
        if not refresh_token:
            return False
            
        credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        try:
            data_encoded = urllib.parse.urlencode(data).encode()
            req = urllib.request.Request(self.auth_url, data=data_encoded, method='POST')
            req.add_header('Authorization', f'Basic {credentials_b64}')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode())
                    access_token = result['access_token']
                    expires_in = result['expires_in']
                    token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    logger.info("🔄 Spotify 토큰 갱신 성공!")
                    return True
                else:
                    logger.error(f"❌ 토큰 갱신 실패: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ 토큰 갱신 오류: {e}")
            return False
    
    def get_current_track(self):
        """현재 재생 중인 트랙 정보 가져오기"""
        global current_track_data
        
        if not access_token:
            return None
            
        # 토큰 만료 확인
        if token_expires_at and datetime.now() >= token_expires_at:
            if not self.refresh_access_token():
                return None
        
        url = f"{self.base_url}/me/player/currently-playing"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'Bearer {access_token}')
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    
                    if data and 'item' in data:
                        track = data['item']
                        current_track_data = {
                            'is_playing': data.get('is_playing', False),
                            'progress_ms': data.get('progress_ms', 0),
                            'track_name': track.get('name', '알 수 없음'),
                            'artist_name': ', '.join([artist['name'] for artist in track.get('artists', [])]),
                            'album_name': track.get('album', {}).get('name', '알 수 없음'),
                            'album_image': track.get('album', {}).get('images', [{}])[0].get('url', ''),
                            'duration_ms': track.get('duration_ms', 0),
                            'external_url': track.get('external_urls', {}).get('spotify', ''),
                            'popularity': track.get('popularity', 0)
                        }
                        return current_track_data
                elif response.status == 204:
                    # 재생 중인 트랙 없음
                    current_track_data = {'is_playing': False, 'track_name': '재생 중인 음악 없음'}
                    return current_track_data
                else:
                    logger.warning(f"⚠️ API 응답 오류: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ 현재 트랙 조회 오류: {e}")
            return None

class PastelSpotifyHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """파스텔 스포티파이 오버레이 HTTP 핸들러"""
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                
                html = self.get_pastel_spotify_html()
                self.wfile.write(html.encode('utf-8'))
            elif parsed_path.path == '/callback':
                # Spotify 인증 콜백 처리
                query = parse_qs(parsed_path.query)
                auth_code = query.get('code', [None])[0]
                
                if auth_code:
                    spotify_api = SpotifyAPI()
                    if spotify_api.get_access_token(auth_code):
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        
                        success_html = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>🌸 Spotify 인증 완료 🌸</title>
                            <style>
                                body { 
                                    font-family: 'Comfortaa', Arial, sans-serif; 
                                    text-align: center; 
                                    padding: 50px; 
                                    background: linear-gradient(135deg, #FFB6C1, #DDA0DD); 
                                    color: white; 
                                    border-radius: 20px;
                                }
                                .success { font-size: 28px; margin: 20px 0; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }
                                .subtitle { font-size: 16px; opacity: 0.9; }
                            </style>
                        </head>
                        <body>
                            <div class="success">🌸✨ Spotify 인증 완료! ✨🌸</div>
                            <p class="subtitle">이제 이 창을 닫고 파스텔 오버레이를 확인하세요.</p>
                            <script>setTimeout(() => window.close(), 3000);</script>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode('utf-8'))
                    else:
                        self.send_response(400)
                        self.end_headers()
                else:
                    self.send_response(400)
                    self.end_headers()
            elif parsed_path.path == '/api/current-track':
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = json.dumps(current_track_data, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
            elif parsed_path.path == '/auth':
                # 인증 시작
                spotify_api = SpotifyAPI()
                auth_url = spotify_api.get_auth_url()
                webbrowser.open(auth_url)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                redirect_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>🌸 Spotify 인증 시작 🌸</title>
                    <style>
                        body { 
                            font-family: 'Comfortaa', Arial, sans-serif; 
                            text-align: center; 
                            padding: 50px; 
                            background: linear-gradient(135deg, #FFB6C1, #DDA0DD); 
                            color: white; 
                        }
                    </style>
                </head>
                <body>
                    <h2>🌸 Spotify 인증이 시작되었습니다 🌸</h2>
                    <p>브라우저에서 Spotify 인증을 완료해주세요.</p>
                </body>
                </html>
                """
                self.wfile.write(redirect_html.encode('utf-8'))
            else:
                self.send_error(404)
                
        except Exception as e:
            logger.error(f"HTTP 요청 처리 오류: {e}")
            try:
                self.send_response(500)
                self.end_headers()
            except:
                pass
    
    def get_pastel_spotify_html(self):
        """레트로 픽셀 파스텔 컨셉의 스포티파이 오버레이 HTML"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕹️ Retro Pixel Music Player 🕹️</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: transparent;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            position: relative;
            font-family: 'Press Start 2P', monospace;
        }

        /* CRT 스캔라인 효과 */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(255, 102, 204, 0.03) 2px,
                rgba(255, 102, 204, 0.03) 4px
            );
            pointer-events: none;
            z-index: 1000;
            animation: scanlines 0.1s linear infinite;
        }

        @keyframes scanlines {
            0% { transform: translateY(0); }
            100% { transform: translateY(4px); }
        }

        .pixel-music-player {
            position: fixed;
            top: 30px;
            right: 30px;
            width: 320px;
            background: linear-gradient(135deg, 
                rgba(0, 0, 0, 0.9) 0%,
                rgba(20, 20, 40, 0.95) 100%);
            border: 4px solid #66FFFF;
            box-shadow: 
                0 0 0 2px rgba(0, 0, 0, 0.8),
                inset 0 0 0 2px rgba(102, 255, 255, 0.3),
                0 8px 0 0 #0066CC,
                0 16px 32px rgba(0, 0, 0, 0.6),
                0 0 40px rgba(102, 255, 255, 0.4);
            image-rendering: pixelated;
            font-family: 'Press Start 2P', monospace;
            animation: pixelBoot 2s ease-out;
            z-index: 100;
        }

        @keyframes pixelBoot {
            0% {
                transform: scale(0.8) rotate(-2deg);
                opacity: 0;
                filter: blur(4px);
            }
            50% {
                transform: scale(1.1) rotate(1deg);
                opacity: 0.8;
                filter: blur(1px);
            }
            100% {
                transform: scale(1) rotate(0deg);
                opacity: 1;
                filter: blur(0px);
            }
        }

        .pixel-music-player.hidden {
            animation: pixelShutdown 1s ease-in forwards;
        }

        @keyframes pixelShutdown {
            0% {
                transform: scale(1);
                opacity: 1;
            }
            100% {
                transform: scale(0.1);
                opacity: 0;
            }
        }

        /* CRT 헤더 */
        .crt-header {
            background: linear-gradient(135deg, #FF66CC, #66FFFF);
            padding: 8px 12px;
            border-bottom: 2px solid #000;
            position: relative;
        }

        .crt-header::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(
                90deg,
                transparent,
                transparent 1px,
                rgba(0, 0, 0, 0.1) 1px,
                rgba(0, 0, 0, 0.1) 2px
            );
        }

        .pixel-title {
            color: #000;
            font-size: 10px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.5);
        }

        /* 앨범 아트 영역 */
        .album-section {
            padding: 16px;
            text-align: center;
            background: linear-gradient(45deg, 
                rgba(255, 102, 204, 0.1) 0%,
                rgba(102, 255, 255, 0.1) 100%);
        }

        .pixel-album-art {
            width: 120px;
            height: 120px;
            margin: 0 auto 12px;
            background: linear-gradient(45deg, #333, #666);
            border: 3px solid #66FFFF;
            box-shadow: 
                0 0 0 1px #000,
                inset 0 0 0 1px rgba(102, 255, 255, 0.3),
                0 4px 0 0 #0066CC,
                0 0 20px rgba(102, 255, 255, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: #66FFFF;
            text-shadow: 1px 1px 0 #000;
            image-rendering: pixelated;
            position: relative;
            overflow: hidden;
        }

        .pixel-album-art img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            image-rendering: pixelated;
        }

        .pixel-album-art.playing {
            animation: pixelPulse 2s ease-in-out infinite;
        }

        @keyframes pixelPulse {
            0%, 100% {
                box-shadow: 
                    0 0 0 1px #000,
                    inset 0 0 0 1px rgba(102, 255, 255, 0.3),
                    0 4px 0 0 #0066CC,
                    0 0 20px rgba(102, 255, 255, 0.4);
            }
            50% {
                box-shadow: 
                    0 0 0 1px #000,
                    inset 0 0 0 1px rgba(102, 255, 255, 0.5),
                    0 4px 0 0 #0066CC,
                    0 0 30px rgba(102, 255, 255, 0.8);
            }
        }

        /* 트랙 정보 */
        .pixel-track-info {
            color: #66FFFF;
            font-size: 8px;
            line-height: 12px;
            text-align: center;
            padding: 0 8px;
        }

        .pixel-track-name {
            color: #FF66CC;
            margin-bottom: 6px;
            text-shadow: 1px 1px 0 #000;
            animation: pixelGlow 3s ease-in-out infinite alternate;
        }

        .pixel-artist-name {
            color: #FFFF66;
            margin-bottom: 4px;
            text-shadow: 1px 1px 0 #000;
        }

        .pixel-album-name {
            color: #66FFFF;
            opacity: 0.8;
            text-shadow: 1px 1px 0 #000;
        }

        @keyframes pixelGlow {
            0% {
                text-shadow: 1px 1px 0 #000, 0 0 10px rgba(255, 102, 204, 0.6);
            }
            100% {
                text-shadow: 1px 1px 0 #000, 0 0 20px rgba(255, 102, 204, 1);
            }
        }

        /* 진행률 바 */
        .pixel-progress-section {
            padding: 12px 16px;
            background: rgba(0, 0, 0, 0.5);
            border-top: 2px solid #333;
        }

        .pixel-progress-bar {
            width: 100%;
            height: 8px;
            background: #333;
            border: 2px solid #66FFFF;
            position: relative;
            margin-bottom: 8px;
            box-shadow: inset 0 0 0 1px rgba(102, 255, 255, 0.3);
        }

        .pixel-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #FF66CC, #66FFFF, #FFFF66);
            background-size: 200% 100%;
            animation: pixelProgressGlow 3s ease-in-out infinite;
            transition: width 0.1s linear;
            box-shadow: 0 0 10px rgba(255, 102, 204, 0.6);
            image-rendering: pixelated;
        }

        @keyframes pixelProgressGlow {
            0%, 100% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
        }

        /* 시간 표시 */
        .pixel-time-display {
            display: flex;
            justify-content: space-between;
            color: #66FFFF;
            font-size: 7px;
            text-shadow: 1px 1px 0 #000;
        }

        /* 재생 상태 */
        .pixel-play-status {
            text-align: center;
            padding: 8px;
            background: rgba(0, 0, 0, 0.3);
            border-top: 2px solid #333;
        }

        .pixel-status-icon {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #FFFF66;
            margin-right: 8px;
            position: relative;
            background: rgba(255, 255, 102, 0.2);
        }

        .pixel-status-icon.playing::before {
            content: '';
            position: absolute;
            top: 2px;
            left: 3px;
            width: 2px;
            height: 8px;
            background: #FFFF66;
            box-shadow: 4px 0 0 #FFFF66;
        }

        .pixel-status-icon.paused::before {
            content: '';
            position: absolute;
            top: 2px;
            left: 4px;
            width: 0;
            height: 0;
            border-left: 6px solid #FFFF66;
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
        }

        .pixel-status-text {
            display: inline-block;
            color: #FFFF66;
            font-size: 8px;
            text-shadow: 1px 1px 0 #000;
            vertical-align: top;
            margin-top: 2px;
        }

        /* 인증 메시지 */
        .pixel-auth-message {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, 
                rgba(0, 0, 0, 0.95) 0%,
                rgba(20, 20, 40, 0.98) 100%);
            border: 4px solid #FF66CC;
            padding: 24px;
            text-align: center;
            box-shadow: 
                0 0 0 2px rgba(0, 0, 0, 0.8),
                inset 0 0 0 2px rgba(255, 102, 204, 0.3),
                0 8px 0 0 #CC0066,
                0 16px 32px rgba(0, 0, 0, 0.8),
                0 0 40px rgba(255, 102, 204, 0.6);
            z-index: 200;
            animation: pixelBlink 2s ease-in-out infinite;
        }

        .pixel-auth-title {
            color: #FF66CC;
            font-size: 12px;
            margin-bottom: 16px;
            text-shadow: 1px 1px 0 #000;
        }

        .pixel-auth-button {
            background: linear-gradient(135deg, #FF66CC, #FFFF66);
            border: 3px solid #FF66CC;
            color: #000;
            padding: 8px 16px;
            font-size: 8px;
            font-family: 'Press Start 2P', monospace;
            cursor: pointer;
            text-transform: uppercase;
            box-shadow: 
                0 0 0 1px #000,
                0 4px 0 0 #CC0066,
                0 0 15px rgba(255, 102, 204, 0.4);
            transition: all 0.1s;
        }

        .pixel-auth-button:hover {
            background: linear-gradient(135deg, #FFFF66, #FF66CC);
            transform: translateY(1px);
            box-shadow: 
                0 0 0 1px #000,
                0 3px 0 0 #CC0066,
                0 0 20px rgba(255, 102, 204, 0.6);
        }

        .pixel-auth-button:active {
            transform: translateY(2px);
            box-shadow: 
                0 0 0 1px #000,
                0 2px 0 0 #CC0066,
                0 0 10px rgba(255, 102, 204, 0.4);
        }

        @keyframes pixelBlink {
            0%, 100% {
                opacity: 0.9;
            }
            50% {
                opacity: 1;
            }
        }

        /* 반응형 */
        @media (max-width: 1366px) {
            .pixel-music-player {
                transform: scale(0.8);
                right: 20px;
                top: 20px;
            }
        }

        @media (max-width: 1024px) {
            .pixel-music-player {
                transform: scale(0.7);
                right: 15px;
                top: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="pixel-auth-message" id="authMessage">
        <h3 class="pixel-auth-title">🕹️ SPOTIFY CONNECT REQUIRED 🕹️</h3>
        <button class="pixel-auth-button" onclick="authenticate()">▶ CONNECT</button>
    </div>
    
    <div class="pixel-music-player hidden" id="musicPlayer">
        <div class="crt-header">
            <div class="pixel-title">🎵 RETRO MUSIC SYSTEM 🎵</div>
        </div>
        
        <div class="album-section">
            <div class="pixel-album-art" id="albumArt">
                ♪
            </div>
            
            <div class="pixel-track-info">
                <div class="pixel-track-name" id="trackName">NO TRACK</div>
                <div class="pixel-artist-name" id="artistName">NO ARTIST</div>
                <div class="pixel-album-name" id="albumName">NO ALBUM</div>
            </div>
        </div>
        
        <div class="pixel-progress-section">
            <div class="pixel-progress-bar">
                <div class="pixel-progress-fill" id="progressBar" style="width: 0%"></div>
            </div>
            <div class="pixel-time-display" id="timeDisplay">
                <span id="currentTime">0:00</span>
                <span id="totalTime">0:00</span>
            </div>
        </div>
        
        <div class="pixel-play-status">
            <div class="pixel-status-icon paused" id="statusIcon"></div>
            <div class="pixel-status-text" id="statusText">PAUSED</div>
        </div>
    </div>

    <script>
        let isAuthenticated = false;
        let currentTrack = null;
        let localProgressMs = 0;
        let lastUpdateTime = 0;
        let isLocallyPlaying = false;
        
        function authenticate() {
            window.open('/auth', '_blank', 'width=600,height=700');
        }
        
        function formatTime(ms) {
            if (!ms) return '0:00';
            const minutes = Math.floor(ms / 60000);
            const seconds = Math.floor((ms % 60000) / 1000);
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        
        function updateLocalProgress() {
            if (isLocallyPlaying && lastUpdateTime > 0) {
                const now = Date.now();
                const elapsed = now - lastUpdateTime;
                localProgressMs += elapsed;
                lastUpdateTime = now;
                
                // UI 업데이트
                const totalTime = currentTrack?.duration_ms || 1;
                const progress = Math.min((localProgressMs / totalTime) * 100, 100);
                
                document.getElementById('currentTime').textContent = formatTime(localProgressMs);
                document.getElementById('progressBar').style.width = `${progress}%`;
            } else if (isLocallyPlaying) {
                lastUpdateTime = Date.now();
            }
        }
        
        async function updateTrackInfo() {
            try {
                const response = await fetch('/api/current-track');
                const data = await response.json();
                
                const authMessage = document.getElementById('authMessage');
                const musicPlayer = document.getElementById('musicPlayer');
                const albumArt = document.getElementById('albumArt');
                const trackName = document.getElementById('trackName');
                const artistName = document.getElementById('artistName');
                const albumName = document.getElementById('albumName');
                const progressBar = document.getElementById('progressBar');
                const statusIcon = document.getElementById('statusIcon');
                const statusText = document.getElementById('statusText');
                const totalTime = document.getElementById('totalTime');
                
                if (data && Object.keys(data).length > 0) {
                    isAuthenticated = true;
                    authMessage.style.display = 'none';
                    musicPlayer.classList.remove('hidden');
                    
                    if (data.track_name && data.track_name !== '재생 중인 음악 없음') {
                        currentTrack = data;
                        
                        // 진행률 동기화
                        localProgressMs = data.progress_ms || 0;
                        lastUpdateTime = Date.now();
                        
                        // 트랙 정보 업데이트
                        trackName.textContent = (data.track_name || 'NO TRACK').toUpperCase();
                        artistName.textContent = (data.artist_name || 'NO ARTIST').toUpperCase();
                        albumName.textContent = (data.album_name || 'NO ALBUM').toUpperCase();
                        
                        // 앨범 아트 업데이트
                        if (data.album_image) {
                            albumArt.innerHTML = `<img src="${data.album_image}" alt="Album Art">`;
                        } else {
                            albumArt.innerHTML = '♪';
                        }
                        
                        // 재생 상태 업데이트
                        if (data.is_playing) {
                            albumArt.classList.add('playing');
                            statusIcon.className = 'pixel-status-icon playing';
                            statusText.textContent = 'PLAYING';
                            isLocallyPlaying = true;
                        } else {
                            albumArt.classList.remove('playing');
                            statusIcon.className = 'pixel-status-icon paused';
                            statusText.textContent = 'PAUSED';
                            isLocallyPlaying = false;
                        }
                        
                        // 시간 표시 업데이트
                        totalTime.textContent = formatTime(data.duration_ms);
                        
                        // 초기 진행률 설정
                        if (data.duration_ms > 0) {
                            const progress = (localProgressMs / data.duration_ms) * 100;
                            progressBar.style.width = `${progress}%`;
                        }
                        
                    } else {
                        // 재생 중인 음악이 없음
                        trackName.textContent = 'NO TRACK PLAYING';
                        artistName.textContent = '';
                        albumName.textContent = '';
                        albumArt.innerHTML = '♪';
                        albumArt.classList.remove('playing');
                        statusIcon.className = 'pixel-status-icon paused';
                        statusText.textContent = 'STOPPED';
                        progressBar.style.width = '0%';
                        isLocallyPlaying = false;
                    }
                } else if (!isAuthenticated) {
                    // 인증이 필요함
                    authMessage.style.display = 'block';
                    musicPlayer.classList.add('hidden');
                }
                
            } catch (error) {
                console.error('PIXEL MUSIC ERROR:', error);
            }
        }
        
        // 실시간 진행률 업데이트 (100ms마다)
        setInterval(updateLocalProgress, 100);
        
        // 1초마다 트랙 정보 업데이트
        setInterval(updateTrackInfo, 1000);
        
        // 초기 로드
        updateTrackInfo();
        
        // 페이지 포커스 시 즉시 업데이트
        window.addEventListener('focus', updateTrackInfo);
    </script>
</body>
</html>"""

    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

def start_pastel_spotify_server():
    """파스텔 스포티파이 서버 시작"""
    try:
        port = 8888
        with socketserver.TCPServer(("", port), PastelSpotifyHTTPHandler) as httpd:
            logger.info(f"🌸 파스텔 스포티파이 오버레이 서버 시작: http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            logger.error(f"❌ 포트 {port}가 이미 사용 중입니다. 다른 포트를 사용하거나 기존 프로세스를 종료하세요.")
        else:
            logger.error(f"❌ 서버 시작 실패: {e}")
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")

def update_track_data():
    """트랙 데이터 업데이트"""
    spotify_api = SpotifyAPI()
    while True:
        try:
            spotify_api.get_current_track()
            time.sleep(1)  # 1초마다 업데이트
        except Exception as e:
            logger.error(f"❌ 트랙 데이터 업데이트 오류: {e}")
            time.sleep(5)  # 오류 시 5초 대기

def main():
    """메인 함수"""
    print("🌸✨ 파스텔 스포티파이 오버레이 ✨🌸")
    print("=" * 50)
    
    # HTTP 서버 시작
    server_thread = threading.Thread(target=start_pastel_spotify_server, daemon=True)
    server_thread.start()
    
    # 트랙 데이터 업데이트 스레드 시작
    update_thread = threading.Thread(target=update_track_data, daemon=True)
    update_thread.start()
    
    # Spotify 인증 시작
    spotify_api = SpotifyAPI()
    auth_url = spotify_api.get_auth_url()
    
    print("\n" + "="*60)
    print("🌸 파스텔 스포티파이 오버레이 설정")
    print("="*60)
    print(f"📱 브라우저에서 다음 URL을 열어 Spotify 인증을 완료하세요:")
    print(f"🔗 {auth_url}")
    print("\n🎯 인증 완료 후 OBS 브라우저 소스 URL:")
    print("🌐 http://localhost:8888/")
    print("="*60)
    
    # 자동으로 브라우저 열기
    try:
        webbrowser.open(auth_url)
        logger.info("🌸 브라우저에서 인증 페이지를 열었습니다.")
    except Exception as e:
        logger.warning(f"⚠️ 브라우저 자동 열기 실패: {e}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🌸 사용자에 의해 중단됨")

if __name__ == "__main__":
    main() 