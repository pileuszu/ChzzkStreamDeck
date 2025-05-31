import json
import logging
import http.server
import threading
from urllib.parse import urlparse, parse_qs
from spotify_api import SpotifyAPI, get_current_track_data

# 로깅 설정
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SpotifyHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """스포티파이 오버레이용 HTTP 핸들러"""
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/callback':
                # Spotify 인증 콜백 처리
                query_params = parse_qs(parsed_path.query)
                
                if 'code' in query_params:
                    auth_code = query_params['code'][0]
                    spotify_api = SpotifyAPI()
                    
                    if spotify_api.get_access_token(auth_code):
                        # 인증 성공 페이지
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        
                        success_html = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Spotify 인증 완료</title>
                            <style>
                                body { 
                                    font-family: Arial, sans-serif; 
                                    text-align: center; 
                                    padding: 50px;
                                    background: linear-gradient(135deg, #1db954, #191414);
                                    color: white;
                                }
                                .success { 
                                    background: rgba(255,255,255,0.1); 
                                    padding: 30px; 
                                    border-radius: 15px;
                                    backdrop-filter: blur(10px);
                                }
                            </style>
                        </head>
                        <body>
                            <div class="success">
                                <h1>✅ Spotify 인증 완료!</h1>
                                <p>이제 OBS에서 오버레이를 사용할 수 있습니다.</p>
                                <p><strong>OBS 브라우저 소스 URL:</strong></p>
                                <p><code>http://localhost:8888/overlay</code></p>
                                <p>이 창을 닫아도 됩니다.</p>
                            </div>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode('utf-8'))
                    else:
                        # 인증 실패
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        
                        error_html = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>인증 실패</title>
                            <style>
                                body { 
                                    font-family: Arial, sans-serif; 
                                    text-align: center; 
                                    padding: 50px;
                                    background: #ff4444;
                                    color: white;
                                }
                            </style>
                        </head>
                        <body>
                            <h1>❌ Spotify 인증 실패</h1>
                            <p>다시 시도해주세요.</p>
                        </body>
                        </html>
                        """
                        self.wfile.write(error_html.encode('utf-8'))
                else:
                    # 인증 거부
                    self.send_response(400)
                    self.end_headers()
            
            elif parsed_path.path == '/overlay' or parsed_path.path == '/':
                # 스포티파이 오버레이 HTML 제공
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
            
            elif parsed_path.path == '/spotify/api/track':
                # 현재 트랙 정보 API
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                track_data = get_current_track_data()
                track_json = json.dumps(track_data, ensure_ascii=False)
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
        """OBS용 스포티파이 오버레이 HTML"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify 오버레이</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: transparent;
            font-family: 'Noto Sans KR', sans-serif;
            overflow: hidden;
        }
        
        .spotify-overlay {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 380px;
            background: linear-gradient(135deg, 
                rgba(0, 0, 0, 0.85) 0%, 
                rgba(30, 30, 30, 0.9) 50%, 
                rgba(0, 0, 0, 0.85) 100%);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 175, 0.2);
            animation: fadeIn 1s ease-out;
            transform: translateY(100px);
            opacity: 0;
        }
        
        .spotify-overlay.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        .track-info {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 15px;
        }
        
        .album-cover {
            width: 80px;
            height: 80px;
            border-radius: 12px;
            background: linear-gradient(45deg, #333, #555);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: rgba(255, 255, 255, 0.6);
            overflow: hidden;
            position: relative;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        
        .album-cover img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 12px;
        }
        
        .album-cover::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, 
                rgba(0, 255, 175, 0.1) 0%, 
                transparent 50%, 
                rgba(155, 77, 224, 0.1) 100%);
            border-radius: 12px;
            animation: shimmer 3s ease-in-out infinite;
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
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .artist-name {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 400;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
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
            /* animation: playingPulse 2s ease-in-out infinite; 애니메이션 제거 */
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
        
        .progress-container {
            margin-top: 15px;
        }
        
        .time-info {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            margin-bottom: 8px;
        }
        
        .progress-bar {
            width: 100%;
            height: 4px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 2px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00FFAF, #9b4de0);
            border-radius: 2px;
            transition: width 0.1s ease;
            position: relative;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 8px;
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 2px;
            box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
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
                playIcon.className = 'play-icon play playing';
                statusText.textContent = '재생 중';
                isLocallyPlaying = true;
            } else {
                playIcon.className = 'play-icon pause paused';
                statusText.textContent = '일시정지';
                isLocallyPlaying = false;
            }
            
            // 트랙 정보
            document.getElementById('trackName').textContent = data.track_name || '알 수 없음';
            document.getElementById('artistName').textContent = data.artist_name || '알 수 없음';
            
            // 진행률 정보
            const currentTime = data.progress_ms || 0;
            const totalTime = data.duration_ms || 1;
            
            // 로컬 진행률 동기화
            localProgressMs = currentTime;
            lastUpdateTime = Date.now();
            
            document.getElementById('currentTime').textContent = formatTime(currentTime);
            document.getElementById('totalTime').textContent = formatTime(totalTime);
            
            const progress = (currentTime / totalTime) * 100;
            document.getElementById('progressFill').style.width = `${progress}%`;
            
            overlay.classList.add('show');
            lastTrackData = data;
        }
        
        async function fetchTrackData() {
            try {
                const response = await fetch('/spotify/api/track');
                const data = await response.json();
                updateSpotifyOverlay(data);
            } catch (error) {
                console.error('트랙 데이터 가져오기 실패:', error);
            }
        }
        
        // 100ms마다 로컬 진행률 업데이트
        setInterval(updateLocalProgress, 100);
        
        // 5초마다 서버에서 트랙 데이터 가져오기
        setInterval(fetchTrackData, 5000);
        
        // 초기 로드
        fetchTrackData();
    </script>
</body>
</html>"""
    
    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

def start_spotify_server(port=8888):
    """HTTP 서버 시작"""
    try:
        server = http.server.ThreadingHTTPServer(("", port), SpotifyHTTPHandler)
        server.timeout = 10
        logger.info(f"🌐 Spotify HTTP 서버 시작: http://localhost:{port}")
        server.serve_forever()
    except OSError as e:
        if e.errno == 10048:
            logger.error(f"❌ 포트 {port}가 이미 사용 중입니다.")
        else:
            logger.error(f"❌ HTTP 서버 시작 실패: {e}")
    except Exception as e:
        logger.error(f"❌ HTTP 서버 오류: {e}")

def run_server_thread(port=8888):
    """HTTP 서버를 별도 스레드에서 실행"""
    server_thread = threading.Thread(target=start_spotify_server, args=(port,), daemon=True)
    server_thread.start()
    return server_thread 