#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Neon 테마 관리자 패널 UI
네온 글로우 스타일의 관리자 인터페이스
"""

def get_neon_admin_template():
    """Neon 테마 관리자 패널 HTML 템플릿"""
    return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>스트리밍 컨트롤 센터</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Sans KR', sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f0f1e);
            color: #ffffff;
            min-height: 100vh;
            overflow-x: auto;
            margin: 0;
            padding: 0;
        }
        
        /* 앱 모드 최적화 */
        @media (max-width: 1300px) {
            .container {
                max-width: 95%;
                padding: 15px;
            }
            
            .grid {
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            
            .header h1 {
                font-size: 2.5em;
            }
        }
        
        @media (max-width: 900px) {
            .grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .control-btn {
                padding: 12px 20px;
                font-size: 14px;
            }
        }
        
        /* 컨테이너 */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        /* 헤더 */
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
        }
        
        .header h1 {
            font-size: 3.2em;
            font-weight: 900;
            background: linear-gradient(45deg, #00FFAF, #9b4de0, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
            margin-bottom: 15px;
            animation: neonPulse 3s ease-in-out infinite alternate;
        }
        
        .header p {
            font-size: 1.3em;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 300;
        }
        
        /* 네비게이션 탭 */
        .tab-navigation {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            padding: 15px 30px;
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid rgba(0, 255, 175, 0.3);
            border-radius: 15px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        
        .tab-btn.active {
            background: rgba(0, 255, 175, 0.2);
            border-color: #00FFAF;
            color: #00FFAF;
            box-shadow: 0 0 30px rgba(0, 255, 175, 0.4);
        }
        
        .tab-btn:hover {
            border-color: #00FFAF;
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 255, 175, 0.3);
        }
        
        .tab-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            transition: all 0.3s ease;
        }
        
        .tab-btn:hover::before {
            left: 100%;
        }
        
        /* 탭 컨텐츠 */
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* 탭 내 카드들의 간격 개선 */
        .tab-content .card + .card {
            margin-top: 30px;
        }
        
        /* 그리드 */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        /* 서버 상태 카드와 탭 컨텐츠 간격 */
        .server-status-card {
            margin-bottom: 40px;
        }
        
        /* 카드 */
        .card {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(0, 255, 175, 0.2);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 255, 175, 0.2);
            border-color: rgba(0, 255, 175, 0.4);
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #00FFAF, #9b4de0, #ff6b9d);
        }
        
        .card h2 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #00FFAF;
            font-weight: 700;
        }
        
        /* 상태 표시와 폼 그룹 사이 간격 */
        .status {
            margin-bottom: 20px;
            font-size: 14px;
            font-weight: 600;
        }
        
        .card.running {
            border-color: rgba(0, 255, 175, 0.6);
            box-shadow: 0 0 30px rgba(0, 255, 175, 0.3);
        }
        
        .card.running::before {
            background: #00FFAF;
            box-shadow: 0 0 10px rgba(0, 255, 175, 0.8);
        }
        
        /* 서버 상태 카드 */
        .server-status-card {
            grid-column: 1 / -1;
            background: linear-gradient(135deg, rgba(0, 255, 175, 0.1), rgba(155, 77, 224, 0.1));
        }
        
        /* 폼 그룹 */
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 600;
            font-size: 14px;
        }
        
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 12px 15px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 255, 175, 0.3);
            border-radius: 10px;
            color: white;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .form-group select {
            padding-right: 35px;
            appearance: none;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2300FFAF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right 12px center;
            background-size: 16px;
        }
        
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #00FFAF;
            box-shadow: 0 0 20px rgba(0, 255, 175, 0.3);
        }
        
        .form-group select option {
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 10px;
        }
        
        /* URL 표시 영역 개선 */
        .url-container {
            margin: 20px 0;
            padding: 15px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 175, 0.2);
        }
        
        .url-label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .url-content {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .url-text {
            flex: 1;
            min-width: 200px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #00FFAF;
            word-break: break-all;
            line-height: 1.4;
        }
        
        .copy-btn {
            padding: 8px 16px;
            font-size: 12px;
            background: rgba(0, 255, 175, 0.2);
            border: 1px solid rgba(0, 255, 175, 0.4);
            border-radius: 6px;
            color: #00FFAF;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
            flex-shrink: 0;
        }
        
        .copy-btn:hover {
            background: rgba(0, 255, 175, 0.3);
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(0, 255, 175, 0.3);
        }
        
        /* 버튼 그룹 개선 */
        .btn-group {
            display: flex;
            gap: 10px;
            margin-top: 25px; /* 설정 저장 버튼 위 여백 추가 */
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            background: linear-gradient(45deg, #00FFAF, #9b4de0);
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            flex: 1;
            min-width: 120px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 255, 175, 0.4);
        }
        
        .btn.secondary {
            background: linear-gradient(45deg, #666, #888);
        }
        
        .btn.danger {
            background: linear-gradient(45deg, #ff4757, #ff3838);
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-indicator.active {
            background: #00FFAF;
            box-shadow: 0 0 10px rgba(0, 255, 175, 0.7);
            animation: statusPulse 2s ease-in-out infinite;
        }
        
        .status-indicator.inactive {
            background: #666;
        }
        
        .save-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: linear-gradient(45deg, #00FFAF, #9b4de0);
            border-radius: 10px;
            color: white;
            font-weight: 600;
            transform: translateX(400px);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .save-notification.show {
            transform: translateX(0);
        }
        
        /* 전체 설정 카드 개선 */
        .global-settings-card {
            margin-top: 30px;
        }
        
        @keyframes neonPulse {
            0% {
                text-shadow: 0 0 30px rgba(0, 255, 175, 0.5);
            }
            100% {
                text-shadow: 0 0 50px rgba(0, 255, 175, 0.8), 0 0 80px rgba(155, 77, 224, 0.6);
            }
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(200%); }
        }
        
        @keyframes statusPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .server-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: rgba(0, 255, 175, 0.1);
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 스트리밍 컨트롤 센터</h1>
            <p>모든 스트리밍 오버레이를 통합 관리하세요</p>
        </div>
        
        <div class="tab-navigation">
            <button class="tab-btn active" onclick="showTab('chat')">💬 채팅</button>
            <button class="tab-btn" onclick="showTab('spotify')">🎵 스포티파이</button>
            <button class="tab-btn" onclick="showTab('settings')">⚙️ 설정</button>
        </div>
        
        <div class="card server-status-card">
            <h2>🌐 서버 상태</h2>
            <div class="server-info">
                <div>
                    <strong>서버 주소:</strong> <span id="serverAddress">http://localhost:<span id="serverPort">8080</span></span>
                </div>
                <div>
                    <strong>상태:</strong> <span class="status-indicator active"></span>실행 중
                </div>
            </div>
        </div>
        
        <!-- 채팅 탭 -->
        <div id="chat-tab" class="tab-content active">
            <div class="grid">
                <div class="card" id="chat-module">
                    <h2>💬 치지직 채팅 오버레이</h2>
                    <div id="chat-status" class="status"><span class="status-indicator inactive"></span>정지</div>
                    <div class="form-group">
                        <label>채널 ID</label>
                        <input type="text" id="chat-channel-id" placeholder="치지직 채널 ID를 입력하세요">
                    </div>
                    <div class="url-container">
                        <div class="url-label">OBS 브라우저 소스 URL</div>
                        <div class="url-content">
                            <div class="url-text" id="chat-url">
                                http://localhost:8080/chat/overlay
                            </div>
                            <button class="copy-btn" onclick="copyToClipboard('chat-url')">복사</button>
                        </div>
                    </div>
                    <div class="btn-group">
                        <button class="btn" onclick="saveModuleConfig('chat')">설정 저장</button>
                        <button class="btn secondary" onclick="toggleModule('chat')" id="chat-toggle-btn">시작</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 스포티파이 탭 -->
        <div id="spotify-tab" class="tab-content">
            <div class="grid">
                <div class="card" id="spotify-module">
                    <h2>🎵 Spotify 현재 재생 곡 오버레이</h2>
                    <div id="spotify-status" class="status"><span class="status-indicator inactive"></span>정지</div>
                    <div class="form-group">
                        <label>클라이언트 ID</label>
                        <input type="text" id="spotify-client-id" placeholder="Spotify Client ID">
                    </div>
                    <div class="form-group">
                        <label>클라이언트 시크릿</label>
                        <input type="password" id="spotify-client-secret" placeholder="Spotify Client Secret">
                    </div>
                    <div class="form-group">
                        <label>리다이렉트 URI</label>
                        <input type="text" id="spotify-redirect-uri" placeholder="http://localhost:8080/spotify/callback">
                    </div>
                    <div class="form-group">
                        <label>테마 선택</label>
                        <select id="spotify-theme">
                            <option value="default">기본 네온 테마</option>
                            <option value="purple">퍼플 테마</option>
                            <option value="purple_compact">퍼플 컴팩트</option>
                        </select>
                    </div>
                    <div class="url-container">
                        <div class="url-label">OBS 브라우저 소스 URL</div>
                        <div class="url-content">
                            <div class="url-text" id="spotify-url">
                                http://localhost:8080/spotify/overlay
                            </div>
                            <button class="copy-btn" onclick="copyToClipboard('spotify-url')">복사</button>
                        </div>
                    </div>
                    <div class="btn-group">
                        <button class="btn" onclick="saveModuleConfig('spotify')">설정 저장</button>
                        <button class="btn secondary" onclick="authenticateSpotify()">Spotify 인증</button>
                        <button class="btn secondary" onclick="toggleModule('spotify')" id="spotify-toggle-btn">시작</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 전체 설정 탭 -->
        <div id="settings-tab" class="tab-content">
            <div class="grid">
                <div class="card global-settings-card">
                    <h2>⚙️ 전체 설정</h2>
                    <div class="btn-group">
                        <button class="btn" onclick="exportConfig()">설정 내보내기</button>
                        <button class="btn secondary" onclick="importConfig()">설정 가져오기</button>
                        <button class="btn danger" onclick="resetConfig()">초기화</button>
                    </div>
                    <div class="btn-group" style="margin-top: 20px;">
                        <button class="btn danger" onclick="shutdownApp()" style="background: linear-gradient(45deg, #ff1744, #d50000);">🔴 앱 종료</button>
                    </div>
                    <input type="file" id="config-import" accept=".json" style="display: none;" onchange="handleConfigImport(event)">
                </div>
            </div>
        </div>
    </div>
    
    <div class="save-notification" id="notification">설정이 저장되었습니다!</div>

    <script>
        let currentConfig = {};
        
        // 탭 기능
        function showTab(tabName) {
            // 모든 탭 컨텐츠 숨기기
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 모든 탭 버튼 비활성화
            const tabBtns = document.querySelectorAll('.tab-btn');
            tabBtns.forEach(btn => btn.classList.remove('active'));
            
            // 선택된 탭 표시
            const targetTab = document.getElementById(tabName + '-tab');
            if (targetTab) {
                targetTab.classList.add('active');
            }
            
            // 선택된 탭 버튼 활성화
            event.target.classList.add('active');
        }
        
        // 초기 로드
        document.addEventListener('DOMContentLoaded', function() {
            loadConfig();
            setupEventListeners();
            // 상태 주기적 업데이트
            setInterval(updateModuleStatus, 3000);
        });
        
        // 창 닫기 이벤트 감지
        window.addEventListener('beforeunload', function(e) {
            // 앱 종료 요청
            fetch('/api/shutdown', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                keepalive: true
            }).catch(() => {
                // 에러 무시 (앱이 이미 종료 중일 수 있음)
            });
        });
        
        function setupEventListeners() {
            // 강도 슬라이더 이벤트는 더 이상 필요 없음
        }
        
        async function loadConfig() {
            try {
                const response = await fetch('/api/config');
                currentConfig = await response.json();
                updateUI();
            } catch (error) {
                console.error('설정 로드 실패:', error);
            }
        }
        
        async function updateModuleStatus() {
            try {
                const response = await fetch('/api/modules/status');
                const status = await response.json();
                
                // 각 모듈의 실행 상태 업데이트
                Object.keys(status.modules).forEach(moduleName => {
                    const moduleStatus = status.modules[moduleName];
                    updateModuleStatusDisplay(moduleName, moduleStatus.running);
                });
            } catch (error) {
                console.error('상태 업데이트 실패:', error);
            }
        }
        
        function updateModuleStatusDisplay(moduleName, isRunning) {
            const statusMap = {
                'chat': 'chat-status',
                'spotify': 'spotify-status'
            };
            
            const statusElementId = statusMap[moduleName];
            if (statusElementId) {
                const statusElement = document.getElementById(statusElementId);
                const moduleCard = document.getElementById(moduleName + '-module');
                const toggleBtn = document.getElementById(moduleName + '-toggle-btn');
                
                if (isRunning) {
                    statusElement.innerHTML = '<span class="status-indicator active"></span>실행 중';
                    moduleCard.classList.add('running');
                    if (toggleBtn) {
                        toggleBtn.textContent = '정지';
                        toggleBtn.classList.remove('secondary');
                        toggleBtn.classList.add('danger');
                    }
                } else {
                    statusElement.innerHTML = '<span class="status-indicator inactive"></span>정지';
                    moduleCard.classList.remove('running');
                    if (toggleBtn) {
                        toggleBtn.textContent = '시작';
                        toggleBtn.classList.remove('danger');
                        toggleBtn.classList.add('secondary');
                    }
                }
            }
        }
        
        function authenticateSpotify() {
            // Spotify 인증 URL로 이동
            const clientId = document.getElementById('spotify-client-id').value;
            if (!clientId) {
                showNotification('먼저 Spotify 클라이언트 ID를 입력하고 저장하세요.');
                return;
            }
            
            const authUrl = `https://accounts.spotify.com/authorize?client_id=${clientId}&response_type=code&redirect_uri=http://localhost:8080/spotify/callback&scope=user-read-currently-playing user-read-playback-state&show_dialog=true`;
            window.open(authUrl, '_blank');
        }
        
        function updateUI() {
            // 서버 포트 표시
            document.getElementById('serverPort').textContent = currentConfig.server?.port || 8080;
            
            // 모듈별 설정 업데이트
            const modules = currentConfig.modules || {};
            
            // 채팅 모듈
            if (modules.chat) {
                document.getElementById('chat-channel-id').value = modules.chat.channel_id || '';
            }
            
            // 스포티파이 모듈
            if (modules.spotify) {
                document.getElementById('spotify-client-id').value = modules.spotify.client_id || '';
                document.getElementById('spotify-client-secret').value = modules.spotify.client_secret || '';
                document.getElementById('spotify-redirect-uri').value = modules.spotify.redirect_uri || '';
                document.getElementById('spotify-theme').value = modules.spotify.theme || 'default';
            }
        }
        
        async function saveModuleConfig(moduleName) {
            // 현재 UI 값들을 설정에 반영
            if (moduleName === 'chat') {
                currentConfig.modules.chat.channel_id = document.getElementById('chat-channel-id').value;
            } else if (moduleName === 'spotify') {
                currentConfig.modules.spotify.client_id = document.getElementById('spotify-client-id').value;
                currentConfig.modules.spotify.client_secret = document.getElementById('spotify-client-secret').value;
                currentConfig.modules.spotify.redirect_uri = document.getElementById('spotify-redirect-uri').value;
                currentConfig.modules.spotify.theme = document.getElementById('spotify-theme').value;
            }
            
            try {
                const response = await fetch('/api/config/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(currentConfig)
                });
                
                const result = await response.json();
                if (result.success) {
                    showNotification(result.message);
                } else {
                    console.error('설정 저장 실패:', result.message);
                }
            } catch (error) {
                console.error('설정 저장 요청 실패:', error);
            }
        }
        
        function copyToClipboard(elementId) {
            const element = document.getElementById(elementId);
            const text = element.textContent.trim();
            
            navigator.clipboard.writeText(text).then(() => {
                showNotification('URL이 클립보드에 복사되었습니다!');
            });
        }
        
        function showNotification(message) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
        
        async function exportConfig() {
            try {
                const response = await fetch('/api/config/export', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(currentConfig)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        showNotification(`설정이 ${result.filepath}에 저장되었습니다!`);
                    } else {
                        showNotification('설정 내보내기 실패: ' + result.message);
                    }
                } else {
                    showNotification('설정 내보내기 요청 실패');
                }
            } catch (error) {
                console.error('설정 내보내기 실패:', error);
                showNotification('설정 내보내기 실패');
            }
        }
        
        function importConfig() {
            document.getElementById('config-import').click();
        }
        
        function handleConfigImport(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        const importedConfig = JSON.parse(e.target.result);
                        currentConfig = importedConfig;
                        updateUI();
                        saveConfig();
                        showNotification('설정을 가져왔습니다!');
                    } catch (error) {
                        alert('잘못된 설정 파일입니다.');
                    }
                };
                reader.readAsText(file);
            }
        }
        
        async function resetConfig() {
            if (confirm('모든 설정을 초기화하시겠습니까?')) {
                // 기본값으로 초기화 (실제로는 서버에서 기본값을 가져와야 함)
                location.reload();
            }
        }
        
        async function toggleModule(moduleName) {
            const toggleBtn = document.getElementById(moduleName + '-toggle-btn');
            const isRunning = toggleBtn.textContent === '정지';
            
            try {
                const endpoint = isRunning ? '/api/modules/stop' : '/api/modules/start';
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ module: moduleName })
                });
                
                const result = await response.json();
                if (result.success) {
                    showNotification(result.message);
                    // 상태 즉시 업데이트
                    setTimeout(updateModuleStatus, 500);
                } else {
                    showNotification('모듈 제어 실패: ' + result.message);
                }
            } catch (error) {
                console.error('모듈 제어 요청 실패:', error);
                showNotification('모듈 제어 요청 실패');
            }
        }

        async function shutdownApp() {
            if (confirm('정말로 앱을 종료하시겠습니까?')) {
                try {
                    const response = await fetch('/api/shutdown', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                    
                    if (response.ok) {
                        showNotification('앱이 종료됩니다...');
                        
                        // 3초 후 창 닫기 시도
                        setTimeout(() => {
                            if (window.close) {
                                window.close();
                            } else {
                                alert('앱이 종료되었습니다. 브라우저 탭을 닫아주세요.');
                            }
                        }, 3000);
                    } else {
                        showNotification('앱 종료 요청 실패');
                    }
                    
                } catch (error) {
                    console.error('앱 종료 요청 실패:', error);
                    showNotification('앱 종료 요청 실패');
                }
            }
        }
        
        async function saveConfig() {
            try {
                const response = await fetch('/api/config/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(currentConfig)
                });
                
                const result = await response.json();
                return result.success;
            } catch (error) {
                console.error('설정 저장 실패:', error);
                return false;
            }
        }
    </script>
</body>
</html>""" 