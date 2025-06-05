#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네온 오버레이 관리패널
"""

import json
import logging
import http.server
import threading
from urllib.parse import urlparse, parse_qs
from config import config_manager

logger = logging.getLogger(__name__)

class AdminPanelHandler(http.server.SimpleHTTPRequestHandler):
    """관리패널 HTTP 핸들러"""
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/' or parsed_path.path == '/admin':
                # 관리패널 메인 페이지
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                html = self.get_admin_panel_html()
                self.wfile.write(html.encode('utf-8'))
            
            elif parsed_path.path == '/api/config':
                # 설정 조회 API
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                config_json = json.dumps(config_manager.config, ensure_ascii=False, indent=2)
                self.wfile.write(config_json.encode('utf-8'))
            
            elif parsed_path.path == '/api/modules/status':
                # 모듈 상태 조회 API
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                status = {
                    "modules": {},
                    "server": {
                        "port": config_manager.get_server_port(),
                        "host": config_manager.get_server_host(),
                        "running": True
                    }
                }
                
                for module_name in config_manager.config.get("modules", {}):
                    module_config = config_manager.get_module_config(module_name)
                    status["modules"][module_name] = {
                        "enabled": module_config.get("enabled", False),
                        "url": f"http://localhost:{config_manager.get_server_port()}{module_config.get('url_path', '')}/overlay"
                    }
                
                status_json = json.dumps(status, ensure_ascii=False)
                self.wfile.write(status_json.encode('utf-8'))
            
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"GET 요청 처리 오류: {e}")
            try:
                self.send_response(500)
                self.end_headers()
            except:
                pass
    
    def do_POST(self):
        try:
            parsed_path = urlparse(self.path)
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            if parsed_path.path == '/api/config/save':
                # 설정 저장 API
                try:
                    new_config = json.loads(post_data)
                    config_manager.config = new_config
                    success = config_manager.save_config()
                    
                    self.send_response(200 if success else 500)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"success": success, "message": "설정이 저장되었습니다." if success else "설정 저장에 실패했습니다."}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except Exception as e:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.end_headers()
                    
                    response = {"success": False, "message": f"잘못된 설정 데이터: {e}"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            elif parsed_path.path == '/api/modules/toggle':
                # 모듈 on/off API
                try:
                    data = json.loads(post_data)
                    module_name = data.get('module')
                    enabled = data.get('enabled', False)
                    
                    config_manager.set_module_enabled(module_name, enabled)
                    config_manager.save_config()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"success": True, "message": f"{module_name} 모듈이 {'활성화' if enabled else '비활성화'}되었습니다."}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except Exception as e:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.end_headers()
                    
                    response = {"success": False, "message": f"모듈 설정 변경 실패: {e}"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"POST 요청 처리 오류: {e}")
            try:
                self.send_response(500)
                self.end_headers()
            except:
                pass
    
    def get_admin_panel_html(self):
        """관리패널 HTML"""
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
                font-size: 12px;
                padding: 8px 12px;
            }
        }
        
        /* 스크롤바 스타일링 */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #00FFAF, #9b4de0);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #22c55e, #a855f7);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, rgba(0, 255, 175, 0.1), rgba(155, 77, 224, 0.1));
            border-radius: 20px;
            border: 1px solid rgba(0, 255, 175, 0.3);
            backdrop-filter: blur(20px);
        }
        
        .header h1 {
            font-size: 3em;
            font-weight: 900;
            background: linear-gradient(45deg, #00FFAF, #9b4de0, #FFD700);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-shadow: 0 0 30px rgba(0, 255, 175, 0.5);
            animation: neonPulse 3s ease-in-out infinite alternate;
        }
        
        .header p {
            font-size: 1.2em;
            color: rgba(255, 255, 255, 0.8);
        }
        
        /* 탭 네비게이션 */
        .tab-navigation {
            display: flex;
            justify-content: center;
            gap: 15px; /* 탭 사이 여유 공간 추가 */
            margin-bottom: 30px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            padding: 15px 20px; /* 패딩 증가 */
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .tab-btn {
            flex: 1;
            max-width: 180px; /* 최대 너비 줄임 */
            padding: 15px 20px; /* 패딩 조정 */
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.6);
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            border-radius: 10px;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .tab-btn:hover {
            color: rgba(255, 255, 255, 0.8);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .tab-btn.active {
            color: #00FFAF;
            background: linear-gradient(45deg, rgba(0, 255, 175, 0.2), rgba(155, 77, 224, 0.2));
            box-shadow: 0 0 20px rgba(0, 255, 175, 0.3);
        }
        
        .tab-btn.active::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-top: 8px solid #00FFAF;
        }
        
        /* 탭 컨텐츠 */
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .server-status-card {
            margin-bottom: 40px; /* 서버 상태 카드 아래 여백 추가 */
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .card {
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.3), rgba(30, 30, 30, 0.5));
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #00FFAF, #9b4de0, #FFD700);
            animation: shimmer 2s ease-in-out infinite;
        }
        
        .card h2 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #00FFAF;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .module-card {
            border-left: 4px solid #00FFAF;
        }
        
        .module-card.disabled {
            border-left-color: #666;
            opacity: 0.6;
        }
        
        .module-card.running {
            border-left-color: #00FFAF;
            box-shadow: 0 0 20px rgba(0, 255, 175, 0.3);
        }
        
        .module-control {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .control-btn {
            flex: 1;
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .start-btn {
            background: linear-gradient(45deg, #00FFAF, #22c55e);
        }
        
        .start-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 255, 175, 0.4);
        }
        
        .stop-btn {
            background: linear-gradient(45deg, #ff4757, #ff3838);
        }
        
        .stop-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 71, 87, 0.4);
        }
        
        .status-display {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 15px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            margin-bottom: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #00FFAF;
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
            <h2>📊 서버 상태</h2>
            <div class="server-info">
                <span>서버 포트: <strong id="serverPort">8080</strong></span>
                <span><span class="status-indicator active"></span>실행 중</span>
            </div>
        </div>
        
        <!-- 채팅 탭 -->
        <div id="chat-tab" class="tab-content active">
            <div class="card module-card" id="chat-module">
                <h2>💬 치지직 채팅</h2>
                <div class="status-display">
                    <span>실행 상태</span>
                    <span id="chat-status"><span class="status-indicator inactive"></span>정지</span>
                </div>
                <div class="module-control">
                    <button class="control-btn start-btn" onclick="startModule('chat')">시작</button>
                    <button class="control-btn stop-btn" onclick="stopModule('chat')">정지</button>
                </div>
                <div class="form-group">
                    <label>채널 ID</label>
                    <input type="text" id="chat-channel-id" placeholder="채널 ID를 입력하세요">
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
                </div>
            </div>
        </div>
        
        <!-- 스포티파이 탭 -->
        <div id="spotify-tab" class="tab-content">
            <div class="card module-card" id="spotify-module">
                <h2>🎵 스포티파이</h2>
                <div class="status-display">
                    <span>실행 상태</span>
                    <span id="spotify-status"><span class="status-indicator inactive"></span>정지</span>
                </div>
                <div class="module-control">
                    <button class="control-btn start-btn" onclick="startModule('spotify')">시작</button>
                    <button class="control-btn stop-btn" onclick="stopModule('spotify')">정지</button>
                </div>
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
                        <option value="minimal">미니멀 테마</option>
                        <option value="retro">레트로 테마</option>
                        <option value="glass">글래스모피즘</option>
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
                </div>
            </div>
        </div>
        
        <!-- 전체 설정 탭 -->
        <div id="settings-tab" class="tab-content">
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
                
                if (isRunning) {
                    statusElement.innerHTML = '<span class="status-indicator active"></span>실행 중';
                    moduleCard.classList.add('running');
                } else {
                    statusElement.innerHTML = '<span class="status-indicator inactive"></span>정지';
                    moduleCard.classList.remove('running');
                }
            }
        }
        
        async function startModule(moduleName) {
            try {
                const response = await fetch('/api/modules/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        module: moduleName
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    showNotification(result.message);
                    updateModuleStatus();
                } else {
                    showNotification(`${moduleName} 시작 실패: ${result.message}`);
                }
            } catch (error) {
                console.error('모듈 시작 요청 실패:', error);
                showNotification(`${moduleName} 시작 요청 실패`);
            }
        }
        
        async function stopModule(moduleName) {
            try {
                const response = await fetch('/api/modules/stop', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        module: moduleName
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    showNotification(result.message);
                    updateModuleStatus();
                } else {
                    showNotification(`${moduleName} 정지 실패: ${result.message}`);
                }
            } catch (error) {
                console.error('모듈 정지 요청 실패:', error);
                showNotification(`${moduleName} 정지 요청 실패`);
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
        
        function exportConfig() {
            const dataStr = JSON.stringify(currentConfig, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'overlay_config.json';
            link.click();
            URL.revokeObjectURL(url);
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
        
        async function shutdownApp() {
            if (confirm('정말로 앱을 종료하시겠습니까?')) {
                try {
                    await fetch('/api/shutdown', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                    
                    showNotification('앱이 종료됩니다...');
                    
                    // 3초 후 창 닫기 시도
                    setTimeout(() => {
                        if (window.close) {
                            window.close();
                        } else {
                            alert('앱이 종료되었습니다. 브라우저 탭을 닫아주세요.');
                        }
                    }, 3000);
                    
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
    
    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

def start_admin_server(port=8080):
    """관리패널 서버 시작"""
    try:
        server = http.server.ThreadingHTTPServer(("", port), AdminPanelHandler)
        server.timeout = 10
        logger.info(f"🎮 관리패널 서버 시작: http://localhost:{port}/admin")
        server.serve_forever()
    except OSError as e:
        if e.errno == 10048:
            logger.error(f"❌ 포트 {port}가 이미 사용 중입니다.")
        else:
            logger.error(f"❌ 관리패널 서버 시작 실패: {e}")
    except Exception as e:
        logger.error(f"❌ 관리패널 서버 오류: {e}")

def run_admin_server_thread(port=8080):
    """관리패널 서버를 별도 스레드에서 실행"""
    server_thread = threading.Thread(target=start_admin_server, args=(port,), daemon=True)
    server_thread.start()
    return server_thread 