#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Purple 테마 Spotify 오버레이 (컴팩트 버전)
앨범 이미지 없이 노래 제목과 가수만 한 줄로 표시
"""

import json
import logging

logger = logging.getLogger(__name__)

def get_purple_compact_template():
    """Purple 테마 컴팩트 Spotify 오버레이 HTML 템플릿"""
    return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Purple Compact Spotify Overlay</title>
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
            height: 80px;
            background: linear-gradient(135deg, 
                rgba(138, 43, 226, 0.95), 
                rgba(75, 0, 130, 0.95),
                rgba(138, 43, 226, 0.95));
            border-radius: 20px;
            padding: 15px 20px;
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
            animation: shimmer 4s infinite;
        }
        
        /* 곡 정보 영역 */
        .track-info {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 40px;
            overflow: hidden;
            position: relative;
            width: 100%;
        }
        
        .track-text {
            font-size: 16px;
            font-weight: 600;
            color: white;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            white-space: nowrap;
            animation: marquee 12s linear infinite;
            animation-play-state: running;
        }
        
        /* 진행바 영역 */
        .progress-section {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 20px;
            gap: 10px;
        }
        
        .time-display {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 500;
            min-width: 35px;
        }
        
        .progress-bar-container {
            flex: 1;
            height: 4px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 2px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, 
                rgba(255, 255, 255, 0.9),
                rgba(138, 43, 226, 0.8),
                rgba(255, 255, 255, 0.9));
            border-radius: 2px;
            width: 0%;
            transition: width 0.5s ease;
            position: relative;
        }
        
        .progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 8px;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 2px;
            box-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
        }
        
        /* 애니메이션 */
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.8; }
            50% { transform: scale(1.1); opacity: 1; }
        }
        
        @keyframes marquee {
            0% { transform: translateX(100%); }
            50% { transform: translateX(-200%); }
            50.01% { transform: translateX(100%); }
            100% { transform: translateX(100%); }
        }
        
        /* 재생 중이 아닐 때 숨김 */
        .spotify-container.hidden {
            display: none;
        }
        
        /* 반응형 */
        @media (max-width: 450px) {
            .spotify-container {
                width: calc(100vw - 40px);
                margin: 0 20px;
            }
            
            .track-text {
                font-size: 14px;
            }
            
            .time-display {
                font-size: 10px;
                min-width: 30px;
            }
        }
    </style>
</head>
<body>
    <div class="spotify-container" id="spotifyContainer">
        <div class="track-info">
            <div class="track-text" id="trackText">곡을 재생해주세요</div>
        </div>
        
        <div class="progress-section">
            <div class="time-display" id="currentTime">0:00</div>
            <div class="progress-bar-container">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div class="time-display" id="totalTime">0:00</div>
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
            
            // 곡 정보를 한 줄로 표시
            const trackText = `${data.track_name || '알 수 없는 곡'} - ${data.artist_name || '알 수 없는 아티스트'}`;
            trackTextEl.textContent = trackText;
            
            // 재생 상태 업데이트
            isPlaying = data.is_playing || false;
            
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
                        isPlaying = data.is_playing || false;
                        
                        // Marquee 효과 제어 - 재생 상태에 따라
                        const trackTextEl = document.getElementById('trackText');
                        if (isPlaying) {
                            trackTextEl.style.animationPlayState = 'running';
                        } else {
                            trackTextEl.style.animationPlayState = 'paused';
                        }
                    } else {
                        document.getElementById('spotifyContainer').classList.add('hidden');
                        isPlaying = false;
                    }
                } else {
                    // API 호출 실패시에는 숨기지 않고 기존 상태 유지
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
        
        // 100ms마다 진행률 실시간 업데이트 (로컬 계산)
        setInterval(updateProgressRealtime, 100);
    </script>
</body>
</html>"""

def render_purple_compact_overlay():
    """Purple 테마 컴팩트 Spotify 오버레이 렌더링"""
    return get_purple_compact_template() 