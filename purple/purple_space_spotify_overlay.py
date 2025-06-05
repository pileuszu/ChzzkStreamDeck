def get_purple_space_template():
    """Purple Space 테마 - 우주인 컨셉 Spotify 오버레이 템플릿"""
    return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify Space Overlay</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: transparent;
            font-family: 'Exo 2', sans-serif;
            overflow: hidden;
            position: relative;
        }
        
        /* 우주 배경 */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                /* 성운 효과 */
                radial-gradient(ellipse at 20% 30%, rgba(138, 43, 226, 0.4) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 70%, rgba(75, 0, 130, 0.3) 0%, transparent 50%),
                radial-gradient(ellipse at 40% 80%, rgba(147, 0, 211, 0.2) 0%, transparent 50%),
                /* 별들 */
                radial-gradient(2px 2px at 20% 40%, rgba(255, 255, 255, 0.9), transparent),
                radial-gradient(1px 1px at 70% 20%, rgba(255, 255, 255, 0.7), transparent),
                radial-gradient(1px 1px at 90% 60%, rgba(255, 255, 255, 0.8), transparent),
                radial-gradient(2px 2px at 10% 80%, rgba(255, 255, 255, 0.6), transparent),
                radial-gradient(1px 1px at 60% 90%, rgba(255, 255, 255, 0.9), transparent),
                radial-gradient(1px 1px at 30% 10%, rgba(255, 255, 255, 0.8), transparent),
                /* 우주 배경 */
                linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 30%, #16213e 60%, #0f0f0f 100%);
            background-size: 
                300px 300px, 400px 400px, 250px 250px,
                200px 200px, 300px 300px, 250px 250px, 
                150px 150px, 180px 180px, 220px 220px,
                100% 100%;
            animation: galaxyRotate 60s linear infinite, twinkle 3s ease-in-out infinite alternate;
            z-index: -1;
        }
        
        /* 떠다니는 우주 먼지 */
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(1px 1px at 15% 25%, rgba(138, 43, 226, 0.6), transparent),
                radial-gradient(1px 1px at 85% 35%, rgba(75, 0, 130, 0.5), transparent),
                radial-gradient(1px 1px at 45% 65%, rgba(147, 0, 211, 0.4), transparent),
                radial-gradient(1px 1px at 25% 85%, rgba(138, 43, 226, 0.7), transparent),
                radial-gradient(1px 1px at 75% 15%, rgba(75, 0, 130, 0.6), transparent);
            background-size: 400px 400px, 350px 350px, 300px 300px, 280px 280px, 320px 320px;
            animation: dustFloat 25s linear infinite;
            z-index: -1;
        }
        
        .spotify-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 420px;
            min-height: 160px;
            background: 
                linear-gradient(135deg, 
                    rgba(138, 43, 226, 0.15) 0%,
                    rgba(75, 0, 130, 0.25) 25%,
                    rgba(30, 30, 60, 0.4) 50%,
                    rgba(75, 0, 130, 0.25) 75%,
                    rgba(138, 43, 226, 0.15) 100%);
            border-radius: 25px;
            padding: 25px;
            border: 2px solid rgba(138, 43, 226, 0.6);
            box-shadow: 
                0 0 30px rgba(138, 43, 226, 0.4),
                0 0 60px rgba(75, 0, 130, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            position: relative;
            overflow: hidden;
        }
        
        /* 홀로그램 효과 */
        .spotify-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: 
                linear-gradient(45deg, 
                    transparent 40%, 
                    rgba(138, 43, 226, 0.1) 50%, 
                    transparent 60%);
            animation: hologramScan 4s ease-in-out infinite;
            z-index: 1;
            pointer-events: none;
        }
        
        /* 우주선 장식 */
        .spotify-container::after {
            content: '🚀';
            position: absolute;
            top: -10px;
            right: -10px;
            font-size: 24px;
            animation: rocketFloat 6s ease-in-out infinite;
            z-index: 2;
        }
        
        /* 메인 콘텐츠 영역 */
        .main-content {
            position: relative;
            z-index: 10;
        }
        
        /* 헤더 영역 - 우주인 아이콘과 타이틀 */
        .header {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            position: relative;
        }
        
        .astronaut-icon {
            font-size: 28px;
            margin-right: 10px;
            animation: astronautFloat 4s ease-in-out infinite;
        }
        
        .title {
            font-family: 'Orbitron', monospace;
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            text-shadow: 0 0 10px rgba(138, 43, 226, 0.8);
            letter-spacing: 2px;
        }
        
        /* 곡 정보 영역 */
        .track-info {
            text-align: center;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .track-text {
            font-family: 'Exo 2', sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            text-shadow: 0 0 8px rgba(138, 43, 226, 0.6);
            white-space: nowrap;
            animation: spaceMarquee 15s linear infinite;
        }
        
        /* 진행바 영역 */
        .progress-section {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .time-display {
            font-family: 'Orbitron', monospace;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 600;
            min-width: 40px;
            text-align: center;
            text-shadow: 0 0 5px rgba(138, 43, 226, 0.5);
        }
        
        .progress-container {
            flex: 1;
            height: 8px;
            background: 
                linear-gradient(90deg, 
                    rgba(75, 0, 130, 0.3) 0%, 
                    rgba(138, 43, 226, 0.2) 50%, 
                    rgba(75, 0, 130, 0.3) 100%);
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            border: 1px solid rgba(138, 43, 226, 0.4);
        }
        
        .progress-bar {
            height: 100%;
            background: 
                linear-gradient(90deg, 
                    rgba(138, 43, 226, 0.9) 0%,
                    rgba(255, 255, 255, 0.8) 50%,
                    rgba(138, 43, 226, 0.9) 100%);
            border-radius: 10px;
            width: 0%;
            position: relative;
            transition: width 0.5s ease;
            box-shadow: 0 0 15px rgba(138, 43, 226, 0.6);
        }
        
        .progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 12px;
            height: 100%;
            background: 
                radial-gradient(circle, 
                    rgba(255, 255, 255, 1) 0%, 
                    rgba(138, 43, 226, 0.8) 70%, 
                    transparent 100%);
            border-radius: 50%;
            animation: energyPulse 2s ease-in-out infinite;
        }
        
        /* 상태 표시 영역 */
        .status-info {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .planet-decoration {
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            opacity: 0.6;
        }
        
        .planet-1 {
            top: 10px;
            left: 10px;
            background: radial-gradient(circle, rgba(138, 43, 226, 0.8), rgba(75, 0, 130, 0.4));
            animation: planetOrbit1 20s linear infinite;
        }
        
        .planet-2 {
            bottom: 10px;
            right: 50px;
            background: radial-gradient(circle, rgba(147, 0, 211, 0.8), rgba(75, 0, 130, 0.4));
            animation: planetOrbit2 25s linear infinite;
        }
        
        /* 애니메이션 정의 */
        @keyframes galaxyRotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes twinkle {
            0% { opacity: 0.8; }
            100% { opacity: 1; }
        }
        
        @keyframes dustFloat {
            0% { transform: translateY(0px) rotate(0deg); }
            100% { transform: translateY(-20px) rotate(360deg); }
        }
        
        @keyframes spaceMarquee {
            0% { transform: translateX(100%); }
            50% { transform: translateX(-200%); }
            50.01% { transform: translateX(100%); }
            100% { transform: translateX(100%); }
        }
        
        @keyframes hologramScan {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(100%) rotate(45deg); }
        }
        
        @keyframes rocketFloat {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-10px) rotate(15deg); }
        }
        
        @keyframes astronautFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        
        @keyframes energyPulse {
            0%, 100% { 
                box-shadow: 0 0 5px rgba(138, 43, 226, 0.6);
                transform: scale(1);
            }
            50% { 
                box-shadow: 0 0 20px rgba(138, 43, 226, 0.9);
                transform: scale(1.1);
            }
        }
        
        @keyframes planetOrbit1 {
            0% { transform: rotate(0deg) translateX(30px) rotate(0deg); }
            100% { transform: rotate(360deg) translateX(30px) rotate(-360deg); }
        }
        
        @keyframes planetOrbit2 {
            0% { transform: rotate(0deg) translateX(25px) rotate(0deg); }
            100% { transform: rotate(-360deg) translateX(25px) rotate(360deg); }
        }
        
        /* 숨김 상태 */
        .spotify-container.hidden {
            display: none;
        }
        
        /* 반응형 */
        @media (max-width: 500px) {
            .spotify-container {
                width: calc(100vw - 40px);
                margin: 0 20px;
            }
            
            .track-text {
                font-size: 14px;
            }
            
            .title {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="spotify-container" id="spotifyContainer">
        <!-- 행성 장식 -->
        <div class="planet-decoration planet-1"></div>
        <div class="planet-decoration planet-2"></div>
        
        <div class="main-content">
            <!-- 헤더 -->
            <div class="header">
                <div class="astronaut-icon">👨‍🚀</div>
                <div class="title">SPACE MUSIC</div>
            </div>
            
            <!-- 곡 정보 -->
            <div class="track-info">
                <div class="track-text" id="trackText">🌌 우주로 떠나는 음악 여행을 준비하세요...</div>
            </div>
            
            <!-- 진행바 -->
            <div class="progress-section">
                <div class="time-display" id="currentTime">0:00</div>
                <div class="progress-container">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <div class="time-display" id="totalTime">0:00</div>
            </div>
            
            <!-- 상태 정보 -->
            <div class="status-info">
                <span>🎵</span>
                <span id="statusText">대기 중...</span>
                <span>⭐</span>
            </div>
        </div>
    </div>

    <script>
        let isPlaying = false;
        let lastFetchTime = 0;
        let lastProgressMs = 0;
        let totalDurationMs = 0;
        
        function updateTrackInfo(data) {
            if (!data) return;
            
            const trackTextEl = document.getElementById('trackText');
            const currentTimeEl = document.getElementById('currentTime');
            const totalTimeEl = document.getElementById('totalTime');
            const progressBarEl = document.getElementById('progressBar');
            const statusTextEl = document.getElementById('statusText');
            
            // 곡 정보 업데이트
            const trackText = `🎵 ${data.track_name || '알 수 없는 곡'} - ${data.artist_name || '알 수 없는 아티스트'} 🎵`;
            trackTextEl.textContent = trackText;
            
            // 재생 상태 업데이트
            isPlaying = data.is_playing || false;
            statusTextEl.textContent = isPlaying ? '재생 중' : '일시정지';
            
            // 마르키 애니메이션 제어
            if (isPlaying) {
                trackTextEl.style.animationPlayState = 'running';
            } else {
                trackTextEl.style.animationPlayState = 'paused';
            }
            
            // 시간 정보 업데이트
            lastFetchTime = Date.now();
            lastProgressMs = data.progress_ms || 0;
            totalDurationMs = data.duration_ms || 0;
            
            updateProgress(lastProgressMs, totalDurationMs);
        }
        
        function updateProgress(currentMs, totalMs) {
            const currentTimeEl = document.getElementById('currentTime');
            const totalTimeEl = document.getElementById('totalTime');
            const progressBarEl = document.getElementById('progressBar');
            
            currentTimeEl.textContent = formatTime(currentMs);
            totalTimeEl.textContent = formatTime(totalMs);
            
            // 진행바 업데이트
            if (totalMs > 0) {
                const progressPercent = (currentMs / totalMs) * 100;
                progressBarEl.style.width = `${Math.min(progressPercent, 100)}%`;
            } else {
                progressBarEl.style.width = '0%';
            }
        }
        
        function updateProgressRealtime() {
            if (isPlaying && totalDurationMs > 0) {
                const now = Date.now();
                const elapsedSinceLastFetch = now - lastFetchTime;
                const estimatedCurrentMs = lastProgressMs + elapsedSinceLastFetch;
                
                if (estimatedCurrentMs <= totalDurationMs) {
                    updateProgress(estimatedCurrentMs, totalDurationMs);
                }
            }
        }
        
        function formatTime(ms) {
            const totalSeconds = Math.floor(ms / 1000);
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = totalSeconds % 60;
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        
        async function fetchCurrentTrack() {
            try {
                const response = await fetch('/spotify/api/track');
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.track_name && data.track_name !== '재생 중인 음악 없음') {
                        document.getElementById('spotifyContainer').classList.remove('hidden');
                        updateTrackInfo(data);
                    } else {
                        document.getElementById('spotifyContainer').classList.add('hidden');
                        isPlaying = false;
                    }
                } else {
                    isPlaying = false;
                }
            } catch (error) {
                console.error('Spotify 데이터 가져오기 실패:', error);
                isPlaying = false;
            }
        }
        
        // 즉시 로드 (테마 변경 시에도 바로 반영)
        fetchCurrentTrack();
        
        // 페이지 로드 후 추가 로드 (혹시 모를 지연 대비)
        setTimeout(fetchCurrentTrack, 500);
        
        // 5초마다 서버에서 데이터 업데이트
        setInterval(fetchCurrentTrack, 5000);
        
        // 100ms마다 진행률 실시간 업데이트
        setInterval(updateProgressRealtime, 100);
    </script>
</body>
</html>"""

def render_purple_space_overlay():
    """Purple Space 테마 Spotify 오버레이 렌더링"""
    return get_purple_space_template() 