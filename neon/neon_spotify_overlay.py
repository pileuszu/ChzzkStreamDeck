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

class SpotifyHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Spotify 오버레이 HTTP 핸들러"""
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/callback':
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
                            <title>Spotify 인증 완료</title>
                            <style>
                                body { font-family: Arial; text-align: center; padding: 50px; background: #1DB954; color: white; }
                                .success { font-size: 24px; margin: 20px 0; }
                            </style>
                        </head>
                        <body>
                            <h1>🎵 Spotify 인증 완료!</h1>
                            <div class="success">이제 브라우저를 닫고 OBS에서 오버레이를 사용할 수 있습니다.</div>
                            <p>OBS 브라우저 소스 URL: <strong>http://localhost:8888/overlay</strong></p>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode('utf-8'))
                    else:
                        self.send_error(400, "인증 실패")
                else:
                    self.send_error(400, "인증 코드 없음")
            
            elif parsed_path.path == '/' or parsed_path.path == '/overlay':
                # Spotify 오버레이 HTML 제공
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                
                html = self.get_overlay_html()
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                
                try:
                    self.wfile.write(html.encode('utf-8'))
                    self.wfile.flush()
                except (ConnectionAbortedError, BrokenPipeError) as e:
                    logger.debug(f"클라이언트 연결 끊어짐: {e}")
                    return
                    
            elif parsed_path.path == '/api/current-track':
                # 현재 트랙 API
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                
                track_json = json.dumps(current_track_data, ensure_ascii=False)
                self.send_header('Content-Length', str(len(track_json.encode('utf-8'))))
                self.end_headers()
                
                try:
                    self.wfile.write(track_json.encode('utf-8'))
                    self.wfile.flush()
                except (ConnectionAbortedError, BrokenPipeError) as e:
                    logger.debug(f"클라이언트 연결 끊어짐: {e}")
                    return
            
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"HTTP 요청 처리 오류: {e}")
            try:
                self.send_response(500)
                self.end_headers()
            except:
                pass
    
    def get_overlay_html(self):
        """Spotify 오버레이 HTML"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify 음악 오버레이</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
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
            font-family: 'Noto Sans KR', sans-serif;
        }
        
        .spotify-overlay {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 400px;
            background: linear-gradient(135deg, 
                rgba(0, 255, 175, 0.05) 0%, 
                rgba(0, 255, 175, 0.1) 50%, 
                rgba(0, 255, 175, 0.05) 100%);
            border: 1px solid rgba(0, 255, 175, 0.3);
            border-radius: 20px;
            backdrop-filter: blur(25px);
            box-shadow: 
                0 15px 50px rgba(0, 255, 175, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.1),
                0 0 30px rgba(0, 255, 175, 0.1);
            padding: 20px;
            animation: fadeIn 1s ease-out;
            transform: translateY(100px);
            opacity: 0;
        }
        
        .spotify-overlay.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        .spotify-overlay.hide {
            transform: translateY(100px);
            opacity: 0;
        }
        
        .track-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .album-cover {
            width: 80px;
            height: 80px;
            border-radius: 15px;
            background: linear-gradient(135deg, #9b4de0, #00ffaf);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        .album-cover img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 13px;
        }
        
        .album-cover.playing {
            box-shadow: 
                0 8px 25px rgba(0, 0, 0, 0.3),
                0 0 30px rgba(155, 77, 224, 0.5);
        }
        
        .track-details {
            flex: 1;
            min-width: 0;
        }
        
        .track-name {
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 5px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
        }
        
        .artist-name {
            font-size: 14px;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 10px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        
        .progress-container {
            width: 100%;
            margin-top: 15px;
        }
        
        .time-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00FFAF, #00E5A0);
            border-radius: 3px;
            transition: width 0.5s ease;
            position: relative;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 20px;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3));
            animation: shimmer 2s ease-in-out infinite;
        }
        
        .play-status {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
        }
        
        .play-icon {
            width: 12px;
            height: 12px;
            position: relative;
            margin-left: 5px; /* 왼쪽으로 이동 */
        }
        
        /* 재생 아이콘 (삼각형) */
        .play-icon.play::before {
            content: '';
            position: absolute;
            left: 2px;
            top: 50%;
            transform: translateY(-50%);
            width: 0;
            height: 0;
            border-left: 8px solid rgba(0, 255, 175, 0.9);
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
        }
        
        /* 일시정지 아이콘 (두 줄) */
        .play-icon.pause::before {
            content: '';
            position: absolute;
            left: 2px;
            top: 1px;
            width: 2px;
            height: 10px;
            background: rgba(0, 255, 175, 0.9);
            border-radius: 1px;
        }
        
        .play-icon.pause::after {
            content: '';
            position: absolute;
            right: 2px;
            top: 1px;
            width: 2px;
            height: 10px;
            background: rgba(0, 255, 175, 0.9);
            border-radius: 1px;
        }
        
        .play-icon:hover {
            transform: scale(1.1);
            box-shadow: 
                0 6px 20px rgba(0, 255, 175, 0.6),
                0 0 0 10px rgba(0, 255, 175, 0.1);
        }
        
        .play-icon.playing {
            animation: playingPulse 2s ease-in-out infinite;
        }
        
        .play-icon.paused {
            animation: none;
        }
        
        .status-text {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            font-weight: 500;
        }
        
        .no-music {
            text-align: center;
            color: rgba(255, 255, 255, 0.6);
            font-size: 16px;
            padding: 20px;
        }
        
        /* 애니메이션 정의 */
        @keyframes fadeIn {
            0% {
                transform: translateY(100px);
                opacity: 0;
            }
            100% {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
                box-shadow: 0 8px 25px rgba(0, 255, 175, 0.3);
            }
            50% {
                transform: scale(1.05);
                box-shadow: 0 12px 35px rgba(0, 255, 175, 0.5);
            }
        }
        
        @keyframes shimmer {
            0% {
                transform: translateX(-20px);
                opacity: 0;
            }
            50% {
                opacity: 1;
            }
            100% {
                transform: translateX(20px);
                opacity: 0;
            }
        }
        
        /* 새로운 애니메이션 */
        @keyframes playingPulse {
            0%, 100% {
                box-shadow: 
                    0 4px 15px rgba(0, 255, 175, 0.4),
                    0 0 0 0 rgba(0, 255, 175, 0.7);
            }
            50% {
                box-shadow: 
                    0 6px 20px rgba(0, 255, 175, 0.6),
                    0 0 0 8px rgba(0, 255, 175, 0.2);
            }
        }
        
        /* 반응형 */
        @media (max-width: 768px) {
            .spotify-overlay {
                width: calc(100vw - 60px);
                right: 30px;
            }
        }
    </style>
</head>
<body>
    <div class="spotify-overlay" id="spotifyOverlay">
        <div class="no-music" id="noMusic">
            🎵 재생 중인 음악 없음
        </div>
        
        <div class="track-info" id="trackInfo" style="display: none;">
            <div class="album-cover" id="albumCover">
                🎵
            </div>
            
            <div class="track-details">
                <div class="track-name" id="trackName">트랙 제목</div>
                <div class="artist-name" id="artistName">아티스트</div>
                
                <div class="play-status">
                    <div class="play-icon pause paused" id="playIcon"></div>
                    <div class="status-text" id="statusText">일시정지</div>
                </div>
            </div>
        </div>
        
        <div class="progress-container" id="progressContainer" style="display: none;">
            <div class="time-info">
                <span id="currentTime">0:00</span>
                <span id="totalTime">0:00</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
        </div>
    </div>

    <script>
        let lastTrackData = null;
        
        // 실시간 진행률 업데이트를 위한 변수
        let localProgressMs = 0;
        let lastUpdateTime = 0;
        let isLocallyPlaying = false;
        
        function formatTime(ms) {
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
                const totalTime = lastTrackData?.duration_ms || 1;
                const progress = Math.min((localProgressMs / totalTime) * 100, 100);
                
                document.getElementById('currentTime').textContent = formatTime(localProgressMs);
                document.getElementById('progressFill').style.width = `${progress}%`;
            } else if (isLocallyPlaying) {
                lastUpdateTime = Date.now();
            }
        }
        
        function updateSpotifyOverlay(data) {
            const overlay = document.getElementById('spotifyOverlay');
            const noMusic = document.getElementById('noMusic');
            const trackInfo = document.getElementById('trackInfo');
            const progressContainer = document.getElementById('progressContainer');
            
            if (!data || !data.track_name || data.track_name === '재생 중인 음악 없음') {
                // 음악 없음
                noMusic.style.display = 'block';
                trackInfo.style.display = 'none';
                progressContainer.style.display = 'none';
                overlay.classList.add('show');
                isLocallyPlaying = false;
                return;
            }
            
            // 트랙 정보 업데이트
            noMusic.style.display = 'none';
            trackInfo.style.display = 'flex';
            progressContainer.style.display = 'block';
            
            // 앨범 커버
            const albumCover = document.getElementById('albumCover');
            if (data.album_image) {
                albumCover.innerHTML = `<img src="${data.album_image}" alt="앨범 커버">`;
            } else {
                albumCover.innerHTML = '🎵';
            }
            
            // 재생 상태에 따른 클래스만 적용 (애니메이션 제거)
            if (data.is_playing) {
                albumCover.classList.add('playing');
                isLocallyPlaying = true;
            } else {
                albumCover.classList.remove('playing');
                isLocallyPlaying = false;
            }
            
            // 진행률 동기화
            localProgressMs = data.progress_ms || 0;
            lastUpdateTime = Date.now();
            
            // 트랙 정보
            document.getElementById('trackName').textContent = data.track_name;
            document.getElementById('artistName').textContent = data.artist_name || '알 수 없는 아티스트';
            
            // 재생 상태
            const playIcon = document.getElementById('playIcon');
            const statusText = document.getElementById('statusText');
            
            // 기존 클래스 제거
            playIcon.className = 'play-icon';
            
            if (data.is_playing) {
                playIcon.classList.add('pause', 'playing');
                statusText.textContent = '재생 중';
            } else {
                playIcon.classList.add('play', 'paused');
                statusText.textContent = '일시정지';
            }
            
            // 진행률 (서버 데이터로 초기화)
            const totalTime = data.duration_ms || 1;
            const progress = (localProgressMs / totalTime) * 100;
            
            document.getElementById('currentTime').textContent = formatTime(localProgressMs);
            document.getElementById('totalTime').textContent = formatTime(totalTime);
            document.getElementById('progressFill').style.width = `${progress}%`;
            
            overlay.classList.add('show');
        }
        
        async function fetchCurrentTrack() {
            try {
                const response = await fetch('/api/current-track');
                const data = await response.json();
                
                // 데이터 변경 확인
                const dataString = JSON.stringify(data);
                if (dataString !== JSON.stringify(lastTrackData)) {
                    updateSpotifyOverlay(data);
                    lastTrackData = data;
                }
                
            } catch (e) {
                console.error('트랙 정보 업데이트 실패:', e);
            }
        }
        
        // 실시간 진행률 업데이트 (100ms마다)
        setInterval(updateLocalProgress, 100);
        
        // 3초마다 트랙 정보 업데이트
        setInterval(fetchCurrentTrack, 3000);
        
        // 초기 로드
        fetchCurrentTrack();
    </script>
</body>
</html>"""
    
    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

def start_spotify_server():
    """Spotify HTTP 서버 시작"""
    try:
        server = http.server.ThreadingHTTPServer(("", 8888), SpotifyHTTPHandler)
        server.timeout = 10
        logger.info("🌐 Spotify 서버 시작: http://localhost:8888")
        server.serve_forever()
    except OSError as e:
        if e.errno == 10048:
            logger.error("❌ 포트 8888이 이미 사용 중입니다.")
        else:
            logger.error(f"❌ Spotify 서버 시작 실패: {e}")
    except Exception as e:
        logger.error(f"❌ Spotify 서버 오류: {e}")

def update_track_data():
    """백그라운드에서 트랙 데이터 업데이트"""
    spotify_api = SpotifyAPI()
    
    while True:
        try:
            if access_token:
                spotify_api.get_current_track()
            time.sleep(5)  # 5초마다 업데이트
        except Exception as e:
            logger.error(f"❌ 트랙 데이터 업데이트 오류: {e}")
            time.sleep(10)

def main():
    """메인 함수"""
    logger.info("🎵 Spotify 오버레이 시작!")
    
    # HTTP 서버를 별도 스레드에서 실행
    server_thread = threading.Thread(target=start_spotify_server, daemon=True)
    server_thread.start()
    
    # 트랙 데이터 업데이트를 별도 스레드에서 실행
    update_thread = threading.Thread(target=update_track_data, daemon=True)
    update_thread.start()
    
    # Spotify 인증 시작
    spotify_api = SpotifyAPI()
    auth_url = spotify_api.get_auth_url()
    
    print("\n" + "="*60)
    print("🎵 Spotify 오버레이 설정")
    print("="*60)
    print(f"📱 브라우저에서 다음 URL을 열어 Spotify 인증을 완료하세요:")
    print(f"🔗 {auth_url}")
    print("\n🎯 인증 완료 후 OBS 브라우저 소스 URL:")
    print("🌐 http://localhost:8888/overlay")
    print("="*60)
    
    # 자동으로 브라우저 열기
    try:
        webbrowser.open(auth_url)
        logger.info("🌐 브라우저에서 인증 페이지를 열었습니다.")
    except Exception as e:
        logger.warning(f"⚠️ 브라우저 자동 열기 실패: {e}")
    
    try:
        # 메인 스레드 유지
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Spotify 오버레이를 종료합니다.")

if __name__ == "__main__":
    main() 