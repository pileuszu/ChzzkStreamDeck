#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Purple 테마 Spotify 오버레이
보라색 컨셉의 단순한 2단 구조 UI
"""

import json
import logging

logger = logging.getLogger(__name__)

def get_purple_spotify_template():
    """Purple 테마 Spotify 오버레이 HTML 템플릿"""
    return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Purple Spotify Overlay</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Sans KR', sans-serif;
            background: transparent;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .spotify-container {
            width: 400px;
            height: 120px;
            background: linear-gradient(135deg, 
                rgba(138, 43, 226, 0.95), 
                rgba(75, 0, 130, 0.95),
                rgba(138, 43, 226, 0.95));
            border-radius: 20px;
            padding: 20px;
            box-shadow: 
                0 10px 30px rgba(138, 43, 226, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }
        
        .spotify-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 255, 255, 0.1), 
                transparent);
            animation: shimmer 3s infinite;
        }
        
        /* 상단: 곡 정보 */
        .track-info {
            display: flex;
            align-items: center;
            gap: 15px;
            height: 50px;
        }
        
        .album-cover {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        
        .track-details {
            flex: 1;
            min-width: 0;
        }
        
        .track-name {
            font-size: 16px;
            font-weight: 600;
            color: white;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .artist-name {
            font-size: 14px;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.8);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-top: 2px;
        }
        
        /* 하단: 재생 바 */
        .playback-info {
            display: flex;
            align-items: center;
            gap: 12px;
            height: 30px;
        }
        
        .time-current {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 500;
            width: 35px;
            text-align: right;
        }
        
        .progress-container {
            flex: 1;
            height: 6px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #ff6b9d, #c44569);
            border-radius: 3px;
            width: 0%;
            transition: width 0.3s ease;
            position: relative;
        }
        
        .progress-bar::after {
            content: '';
            position: absolute;
            top: 50%;
            right: -4px;
            transform: translateY(-50%);
            width: 8px;
            height: 8px;
            background: white;
            border-radius: 50%;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .time-total {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 500;
            width: 35px;
            text-align: left;
        }
        
        /* 음표 아이콘 애니메이션 */
        .music-note {
            position: absolute;
            top: 10px;
            right: 15px;
            font-size: 16px;
            color: rgba(255, 255, 255, 0.6);
            animation: noteFloat 4s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        @keyframes noteFloat {
            0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.6; }
            50% { transform: translateY(-5px) rotate(5deg); opacity: 1; }
        }
        
        /* 재생 중이 아닐 때 숨김 */
        .spotify-container.hidden {
            display: none;
        }
        
        /* 긴 텍스트 스크롤 효과 */
        .scrolling-text {
            animation: scroll-text 10s linear infinite;
        }
        
        @keyframes scroll-text {
            0% { transform: translateX(0); }
            100% { transform: translateX(-100%); }
        }
    </style>
</head>
<body>
    <div class="spotify-container" id="spotifyContainer">
        <div class="music-note">♪</div>
        
        <!-- 상단: 곡 정보 -->
        <div class="track-info">
            <div class="album-cover" id="albumCover">
                🎵
            </div>
            <div class="track-details">
                <div class="track-name" id="trackName">곡을 재생해주세요</div>
                <div class="artist-name" id="artistName">아티스트</div>
            </div>
        </div>
        
        <!-- 하단: 재생 바 -->
        <div class="playback-info">
            <div class="time-current" id="currentTime">0:00</div>
            <div class="progress-container">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div class="time-total" id="totalTime">0:00</div>
        </div>
    </div>

    <script>
        let currentTrack = null;
        let isPlaying = false;
        let lastFetchTime = 0;
        let lastProgressMs = 0;
        let totalDurationMs = 0;
        
        function formatTime(ms) {
            const seconds = Math.floor(ms / 1000);
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        }
        
        function updateProgress(current, total) {
            const percentage = total > 0 ? (current / total) * 100 : 0;
            document.getElementById('progressBar').style.width = `${percentage}%`;
            document.getElementById('currentTime').textContent = formatTime(current);
            document.getElementById('totalTime').textContent = formatTime(total);
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
        
        function updateTrackInfo(data) {
            if (!data) return;
            
            const trackNameEl = document.getElementById('trackName');
            const artistNameEl = document.getElementById('artistName');
            const albumCoverEl = document.getElementById('albumCover');
            
            trackNameEl.textContent = data.track_name || '알 수 없는 곡';
            artistNameEl.textContent = data.artist_name || '알 수 없는 아티스트';
            
            // 앨범 커버 이미지 설정
            if (data.album_image) {
                const img = document.createElement('img');
                img.src = data.album_image;
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
                img.style.borderRadius = '12px';
                albumCoverEl.innerHTML = '';
                albumCoverEl.appendChild(img);
            } else {
                albumCoverEl.innerHTML = '🎵';
            }
            
            // 긴 제목에 대한 스크롤 효과
            if (trackNameEl.scrollWidth > trackNameEl.clientWidth) {
                trackNameEl.classList.add('scrolling-text');
            } else {
                trackNameEl.classList.remove('scrolling-text');
            }
        }
        
        async function fetchCurrentTrack() {
            try {
                const response = await fetch('/spotify/api/track');
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.is_playing && data.track_name && data.track_name !== '재생 중인 음악 없음') {
                        document.getElementById('spotifyContainer').classList.remove('hidden');
                        updateTrackInfo(data);
                        
                        // 시간 정보 업데이트
                        lastFetchTime = Date.now();
                        lastProgressMs = data.progress_ms || 0;
                        totalDurationMs = data.duration_ms || 0;
                        
                        updateProgress(lastProgressMs, totalDurationMs);
                        isPlaying = true;
                    } else {
                        document.getElementById('spotifyContainer').classList.add('hidden');
                        isPlaying = false;
                    }
                } else {
                    document.getElementById('spotifyContainer').classList.add('hidden');
                    isPlaying = false;
                }
            } catch (error) {
                console.error('Spotify 데이터 가져오기 실패:', error);
                document.getElementById('spotifyContainer').classList.add('hidden');
                isPlaying = false;
            }
        }
        
        // 초기 로드
        fetchCurrentTrack();
        
        // 3초마다 서버에서 데이터 업데이트
        setInterval(fetchCurrentTrack, 3000);
        
        // 1초마다 진행률 실시간 업데이트 (로컬 계산)
        setInterval(updateProgressRealtime, 1000);
    </script>
</body>
</html>"""

def render_purple_spotify_overlay():
    """Purple 테마 Spotify 오버레이 렌더링"""
    return get_purple_spotify_template() 