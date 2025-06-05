#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Neon 테마 Spotify 오버레이 UI
"""

def get_neon_spotify_template():
    """Neon 테마 Spotify 오버레이 HTML 템플릿"""
    return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neon Spotify Overlay</title>
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
            top: 50%;
            right: 18%; /* 오른쪽끝(0%)과 중앙점(50%) 사이 */
            transform: translateY(-50%); /* 상하 중앙 정렬 */
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
            opacity: 0;
        }
        
        .spotify-overlay.show {
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
            margin-left: 5px;
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
                opacity: 0;
                transform: translateY(-50%) scale(0.8);
            }
            100% {
                opacity: 1;
                transform: translateY(-50%) scale(1);
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
            const playIcon = document.getElementById('playIcon');
            const statusText = document.getElementById('statusText');
            
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
            
            // 재생 상태 (애니메이션 제거됨)
            if (data.is_playing) {
                playIcon.className = 'play-icon play';
                statusText.textContent = '재생 중';
                isLocallyPlaying = true;
            } else {
                playIcon.className = 'play-icon pause';
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