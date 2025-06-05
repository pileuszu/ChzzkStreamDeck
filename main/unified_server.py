#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네온 오버레이 통합 서버
포트 8080 하나로 모든 모듈 관리
"""

import json
import logging
import http.server
import threading
import asyncio
import time
import webbrowser
import sys
import argparse
from urllib.parse import urlparse, parse_qs
from config import config_manager
from chat_client import ChzzkChatClient
from spotify_api import SpotifyAPI, get_current_track_data

# webview 라이브러리 임포트 (선택적)
try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 글로벌 채팅 메시지 저장소
chat_messages = []
MAX_MESSAGES = 50

# 글로벌 서비스 상태
services_running = {
    'chat': False,
    'spotify': False
}

# 앱 모드 설정
APP_MODE = False

def add_chat_message(message_data):
    """새 채팅 메시지 추가"""
    global chat_messages
    chat_messages.append(message_data)
    if len(chat_messages) > MAX_MESSAGES:
        chat_messages.pop(0)

class UnifiedServerHandler(http.server.SimpleHTTPRequestHandler):
    """통합 서버 HTTP 핸들러"""
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            path_parts = parsed_path.path.strip('/').split('/')
            
            # 관리패널
            if parsed_path.path in ['/', '/admin']:
                return self._handle_admin_panel()
            
            # 관리패널 API
            elif parsed_path.path.startswith('/api/'):
                return self._handle_admin_api()
            
            # 채팅 모듈
            elif path_parts[0] == 'chat':
                return self._handle_chat_module(path_parts[1:])
            
            # 스포티파이 모듈
            elif path_parts[0] == 'spotify':
                return self._handle_spotify_module(path_parts[1:])
            
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
            
            # 관리패널 API
            if parsed_path.path.startswith('/api/'):
                return self._handle_admin_api_post()
            
            # 스포티파이 인증 콜백
            elif parsed_path.path == '/spotify/callback':
                return self._handle_spotify_callback()
            
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
    
    def _handle_admin_panel(self):
        """관리패널 처리 - 네온 테마 사용"""
        try:
            # 네온 관리 UI 사용
            import sys
            import os
            # neon 폴더를 Python 경로에 추가
            neon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'neon')
            if neon_dir not in sys.path:
                sys.path.insert(0, neon_dir)
            
            from neon_admin_ui import get_neon_admin_template
            html = get_neon_admin_template()
            logger.info("네온 관리 패널이 성공적으로 로드되었습니다.")
            
        except ImportError as e:
            logger.warning(f"네온 관리 패널을 불러올 수 없습니다: {e}. 기본 패널을 사용합니다.")
            # 폴백: 기본 관리 패널
            from admin_panel import AdminPanelLogicHandler
            temp_handler = AdminPanelLogicHandler.__new__(AdminPanelLogicHandler)
            html = temp_handler.get_admin_panel_html()
        except Exception as e:
            logger.error(f"관리 패널 로드 중 오류: {e}")
            # 폴백: 기본 관리 패널
            from admin_panel import AdminPanelLogicHandler
            temp_handler = AdminPanelLogicHandler.__new__(AdminPanelLogicHandler)
            html = temp_handler.get_admin_panel_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _handle_admin_api(self):
        """관리패널 API 처리"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/config':
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
                module_status = {
                    "enabled": module_config.get("enabled", False),
                    "running": services_running.get(module_name.replace('_effect', ''), False),
                    "url": f"http://localhost:{config_manager.get_server_port()}{module_config.get('url_path', '')}/overlay"
                }
                
                # Spotify 모듈의 경우 인증 상태 추가
                if module_name == 'spotify':
                    try:
                        from spotify_api import is_authenticated
                        authenticated = is_authenticated()
                        module_status["authenticated"] = authenticated
                        logger.info(f"Spotify 인증 상태 조회: {authenticated}")
                        
                        # 추가: 토큰 정보도 로그로 확인
                        from spotify_api import access_token, token_expires_at
                        logger.info(f"Spotify 토큰 존재: {access_token is not None}")
                        if token_expires_at:
                            from datetime import datetime
                            logger.info(f"Spotify 토큰 만료: {token_expires_at}, 현재: {datetime.now()}")
                        
                    except Exception as e:
                        logger.warning(f"Spotify 인증 상태 확인 실패: {e}")
                        module_status["authenticated"] = False
                
                status["modules"][module_name] = module_status
            
            status_json = json.dumps(status, ensure_ascii=False)
            self.wfile.write(status_json.encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def _handle_admin_api_post(self):
        """관리패널 API POST 처리"""
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
        
        elif parsed_path.path == '/api/shutdown':
            # 앱 종료 API
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"success": True, "message": "앱이 종료됩니다."}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
                # 1초 후 앱 종료
                def shutdown_app():
                    import time
                    time.sleep(1)
                    import os
                    os._exit(0)
                
                shutdown_thread = threading.Thread(target=shutdown_app, daemon=True)
                shutdown_thread.start()
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"success": False, "message": f"앱 종료 실패: {e}"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        elif parsed_path.path == '/api/modules/start':
            # 모듈 시작 API
            try:
                data = json.loads(post_data)
                module_name = data.get('module')
                
                success = self._start_module(module_name)
                
                self.send_response(200 if success else 500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"success": success, "message": f"{module_name} 모듈이 {'시작' if success else '시작 실패'}되었습니다."}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                
                response = {"success": False, "message": f"모듈 시작 실패: {e}"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        elif parsed_path.path == '/api/modules/stop':
            # 모듈 정지 API
            try:
                data = json.loads(post_data)
                module_name = data.get('module')
                
                success = self._stop_module(module_name)
                
                self.send_response(200 if success else 500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"success": success, "message": f"{module_name} 모듈이 {'정지' if success else '정지 실패'}되었습니다."}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                
                response = {"success": False, "message": f"모듈 정지 실패: {e}"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        elif parsed_path.path == '/api/shutdown':
            # 앱 종료 API
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"success": True, "message": "앱이 종료됩니다..."}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
                # 즉시 강제 종료 (최대한 단순하게)
                import threading
                def force_shutdown():
                    import time
                    import os
                    import subprocess
                    import platform
                    
                    time.sleep(0.5)  # 응답 전송 후 짧은 대기
                    
                    print("🔥 앱 강제 종료 중...")
                    
                    try:
                        current_pid = os.getpid()
                        parent_pid = os.getppid()
                        
                        print(f"🔄 프로세스 종료: PID={current_pid}, 부모PID={parent_pid}")
                        
                        # Windows에서 부모 프로세스(CMD)도 함께 종료
                        if platform.system() == "Windows":
                            try:
                                # 프로세스 트리 전체를 강제 종료
                                current_process = psutil.Process(current_pid)
                                parent_process = None
                                
                                # 부모 프로세스 확인 및 종료
                                try:
                                    parent_process = current_process.parent()
                                    if parent_process and 'cmd.exe' in parent_process.name().lower():
                                        print(f"🚪 CMD 창 종료 중: {parent_process.pid}")
                                        subprocess.run(['taskkill', '/f', '/t', '/pid', str(parent_process.pid)], 
                                                     shell=True, capture_output=True, timeout=2)
                                except:
                                    pass
                                
                                # 현재 프로세스 트리 전체 종료
                                subprocess.run(['taskkill', '/f', '/t', '/pid', str(current_pid)], 
                                             shell=True, capture_output=True, timeout=2)
                                
                                # 혹시 남은 부모 프로세스도 강제 종료
                                if parent_process:
                                    try:
                                        subprocess.run(['taskkill', '/f', '/pid', str(parent_process.pid)], 
                                                     shell=True, capture_output=True, timeout=1)
                                    except:
                                        pass
                                    
                            except Exception as clean_ex:
                                print(f"⚠️  Windows 정리 중 오류: {clean_ex}")
                                # 최후의 수단: 프로세스 이름으로 전체 종료
                                try:
                                    subprocess.run(['taskkill', '/f', '/im', 'ChzzkStreamDeck.exe'], 
                                                 shell=True, capture_output=True, timeout=1)
                                    subprocess.run(['taskkill', '/f', '/im', 'cmd.exe'], 
                                                 shell=True, capture_output=True, timeout=1)
                                except:
                                    pass
                        
                        # 바로 강제 종료
                        os._exit(0)
                        
                    except Exception as e:
                        print(f"강제 종료 중 오류: {e}")
                        os._exit(1)
                
                threading.Thread(target=force_shutdown, daemon=True).start()
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                
                response = {"success": False, "message": f"앱 종료 실패: {e}"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        elif parsed_path.path == '/api/config/update':
            # 설정 업데이트 API
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    update_data = json.loads(post_data.decode('utf-8'))
                    
                    # 기존 설정 백업
                    old_config = config_manager.config.copy()
                    
                    # 설정 업데이트
                    for key, value in update_data.items():
                        if '.' in key:
                            config_manager.set(key, value)
                        else:
                            config_manager.config[key] = value
                    
                    # 설정 저장
                    success = config_manager.save_config()
                    
                    if success:
                        # 채팅 설정이 변경된 경우 서비스 재시작
                        if any(key.startswith('modules.chat.') for key in update_data.keys()):
                            logger.info("채팅 설정 변경 감지 - 서비스 재시작 중...")
                            if services_running.get('chat', False):
                                self._stop_module('chat')
                                time.sleep(0.5)  # 잠시 대기
                                if config_manager.is_module_enabled('chat'):
                                    self._start_module('chat')
                                    logger.info("채팅 서비스 재시작 완료")
                        
                        # Spotify 설정이 변경된 경우 서비스 재시작
                        if any(key.startswith('modules.spotify.') for key in update_data.keys()):
                            logger.info("Spotify 설정 변경 감지 - 서비스 재시작 중...")
                            if services_running.get('spotify', False):
                                self._stop_module('spotify')
                                time.sleep(0.5)  # 잠시 대기
                                if config_manager.is_module_enabled('spotify'):
                                    self._start_module('spotify')
                                    logger.info("Spotify 서비스 재시작 완료")
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json; charset=utf-8')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {"success": True, "message": "설정이 업데이트되었습니다."}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    else:
                        # 설정 저장 실패 시 롤백
                        config_manager.config = old_config
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json; charset=utf-8')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {"success": False, "message": "설정 저장에 실패했습니다."}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"success": False, "message": "잘못된 JSON 데이터입니다."}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except Exception as e:
                    logger.error(f"설정 업데이트 오류: {e}")
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"success": False, "message": f"설정 업데이트 오류: {e}"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(400)
            self.end_headers()
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def _start_module(self, module_name):
        """모듈 시작"""
        global server_manager
        try:
            if not server_manager:
                logger.error("서버 관리자가 초기화되지 않았습니다.")
                return False
                
            if module_name == 'chat':
                return server_manager._start_chat_service()
            elif module_name == 'spotify':
                return server_manager._start_spotify_service()
            return False
        except Exception as e:
            logger.error(f"모듈 {module_name} 시작 실패: {e}")
            return False
    
    def _stop_module(self, module_name):
        """모듈 정지"""
        try:
            if module_name == 'chat':
                services_running['chat'] = False
                # 채팅 클라이언트 정리
                if hasattr(server_manager, 'chat_task') and server_manager.chat_task:
                    server_manager.chat_task.cancel()
                    server_manager.chat_task = None
                if hasattr(server_manager, 'chat_client') and server_manager.chat_client:
                    server_manager.chat_client = None
                logger.info(f"💬 {module_name} 정지됨")
                return True
            elif module_name == 'spotify':
                services_running['spotify'] = False
                # 스포티파이 업데이트 스레드 정리
                if hasattr(server_manager, 'spotify_update_thread') and server_manager.spotify_update_thread:
                    server_manager.spotify_update_thread = None
                logger.info(f"🎵 {module_name} 정지됨")
                return True
            return False
        except Exception as e:
            logger.error(f"모듈 {module_name} 정지 실패: {e}")
            return False
    
    def _handle_chat_module(self, path_parts):
        """채팅 모듈 처리"""
        # 오버레이는 항상 표시 (설정 안내 포함)
        if path_parts and path_parts[0] != 'overlay' and not config_manager.is_module_enabled('chat'):
            # API 호출만 모듈 활성화 상태 체크
            if path_parts and path_parts[0] == 'api':
                self.send_response(503)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'{"error": "Chat module is disabled", "enabled": false}')
                return
        
        if not path_parts or path_parts[0] == 'overlay':
            # 채팅 오버레이 HTML
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            html = self._get_chat_overlay_html()
            self.wfile.write(html.encode('utf-8'))
        
        elif path_parts[0] == 'api' and len(path_parts) > 1 and path_parts[1] == 'messages':
            # 채팅 메시지 API
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            messages_json = json.dumps(chat_messages, ensure_ascii=False)
            self.wfile.write(messages_json.encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def _handle_spotify_module(self, path_parts):
        """스포티파이 모듈 처리"""
        # Spotify 모듈 활성화 체크를 OAuth 콜백에서만 수행
        if path_parts and path_parts[0] == 'callback':
            # OAuth 콜백은 항상 허용 (인증 완료 후 모듈 활성화)
            pass
        elif path_parts and path_parts[0] == 'overlay':
            # 오버레이는 항상 표시 (설정 안내 포함)
            pass
        elif not config_manager.is_module_enabled('spotify'):
            # API 호출만 모듈 활성화 상태 체크
            if path_parts and path_parts[0] == 'api':
                self.send_response(503)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'{"error": "Spotify module is disabled", "enabled": false}')
                return
        
        if path_parts[0] == 'callback':
            # 스포티파이 인증 콜백
            query = parse_qs(urlparse(self.path).query)
            auth_code = query.get('code', [None])[0]
            
            if auth_code:
                spotify_api = SpotifyAPI()
                if spotify_api.get_access_token(auth_code):
                    # 인증 완료 후 자동으로 Spotify 모듈 활성화
                    config_manager.set_module_enabled('spotify', True)
                    config_manager.save_config()
                    logger.info("Spotify 인증 완료 - 모듈 자동 활성화")
                    
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
                            .countdown {
                                font-size: 18px;
                                color: #1db954;
                                font-weight: bold;
                                margin-top: 20px;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="success">
                            <h1>✅ Spotify 인증 완료!</h1>
                            <p>이제 OBS에서 오버레이를 사용할 수 있습니다.</p>
                            <p><strong>OBS 브라우저 소스 URL:</strong></p>
                            <p><code>http://localhost:8080/spotify/overlay</code></p>
                            <div class="message">이 창을 닫고 관리패널에서 Spotify 모듈 상태를 확인하세요.</div>
                        </div>
                        <script>
                            // 3초 후 자동으로 창 닫기
                            setTimeout(() => {
                                window.close();
                            }, 3000);
                        </script>
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
        
        elif not path_parts or path_parts[0] == 'overlay':
            # 스포티파이 오버레이 HTML
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            html = self._get_spotify_overlay_html()
            self.wfile.write(html.encode('utf-8'))
        
        elif path_parts[0] == 'api' and len(path_parts) > 1 and path_parts[1] == 'track':
            # 스포티파이 트랙 API
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            track_data = get_current_track_data()
            track_json = json.dumps(track_data, ensure_ascii=False)
            self.wfile.write(track_json.encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def _get_chat_overlay_html(self):
        """채팅 오버레이 HTML - 네온 테마 사용"""
        import sys
        import os
        # neon 폴더를 Python 경로에 추가
        neon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'neon')
        if neon_dir not in sys.path:
            sys.path.insert(0, neon_dir)
        
        try:
            # 이미 import된 모듈이 있다면 reload (설정 변경 반영을 위해)
            if 'neon_chat_overlay' in sys.modules:
                import importlib
                importlib.reload(sys.modules['neon_chat_overlay'])
                
            from neon_chat_overlay import OverlayHTTPHandler
            logger.info("Neon 채팅 오버레이가 성공적으로 로드되었습니다.")
            
            # 임시 핸들러 생성하고 HTML만 가져오기
            temp_handler = OverlayHTTPHandler.__new__(OverlayHTTPHandler)
            html = temp_handler.get_overlay_html()
            # API 엔드포인트를 통합 서버 경로로 수정
            html = html.replace('/api/messages', '/chat/api/messages')
            logger.info("채팅 오버레이 HTML 생성 완료 (설정값 적용됨)")
            return html
            
        except ImportError as e:
            logger.warning(f"Neon 채팅 오버레이를 불러올 수 없습니다: {e}. 기본 템플릿을 사용합니다.")
        except Exception as e:
            logger.error(f"Neon 채팅 오버레이 로드 중 오류: {e}")
        
        # Fallback - 기본 템플릿
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>채팅 오버레이</title>
    <style>
        body { background: transparent; font-family: 'Noto Sans KR', sans-serif; }
        .chat_wrap { position: fixed; bottom: 20px; left: 20px; width: 520px; height: 600px; }
        .chat_list { display: flex; flex-direction: column; justify-content: flex-end; gap: 15px; height: 100%; overflow: hidden; }
        .chat_box { padding: 15px; margin: 10px; background: rgba(0,0,0,0.7); border-radius: 10px; color: white; }
        .chat_box.streamer { border: 2px solid #9b4de0; }
        .name { font-weight: bold; margin-bottom: 5px; }
        .text { font-size: 14px; }
    </style>
</head>
<body>
    <div class="chat_wrap">
        <div class="chat_list"></div>
    </div>
    <script>
        let lastMessageCount = 0;
        async function updateMessages() {
            try {
                const response = await fetch('/chat/api/messages');
                const messages = await response.json();
                if (messages.length > lastMessageCount) {
                    const container = document.querySelector('.chat_list');
                    const newMessages = messages.slice(lastMessageCount);
                    newMessages.forEach((data, index) => {
                        setTimeout(() => {
                            const messageDiv = document.createElement('div');
                            let className = 'chat_box';
                            if (data.is_streamer) className += ' streamer';
                            messageDiv.className = className;
                            messageDiv.innerHTML = `<div class="name">${data.nickname}</div><div class="text">${data.message}</div>`;
                            container.appendChild(messageDiv);
                            while (container.children.length > 10) {
                                container.removeChild(container.firstChild);
                            }
                        }, index * 200);
                    });
                    lastMessageCount = messages.length;
                }
            } catch (e) {
                console.error('메시지 업데이트 실패:', e);
            }
        }
        setInterval(updateMessages, 2000);
        updateMessages();
    </script>
</body>
</html>"""
    
    def _get_spotify_overlay_html(self):
        """스포티파이 오버레이 HTML - 테마에 따라 다른 UI 제공"""
        current_theme = config_manager.get_spotify_theme()
        
        if current_theme == "purple":
            # Purple 테마 사용
            import sys
            import os
            # purple 폴더를 Python 경로에 추가
            purple_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'purple')
            if purple_dir not in sys.path:
                sys.path.insert(0, purple_dir)
            
            try:
                # 이미 import된 모듈이 있다면 reload
                if 'purple_spotify_overlay' in sys.modules:
                    import importlib
                    importlib.reload(sys.modules['purple_spotify_overlay'])
                    
                from purple_spotify_overlay import get_purple_spotify_template
                logger.info("Purple 테마가 성공적으로 로드되었습니다.")
                return get_purple_spotify_template()
            except ImportError as e:
                logger.warning(f"Purple 테마를 불러올 수 없습니다: {e}. 기본 테마를 사용합니다.")
            except Exception as e:
                logger.error(f"Purple 테마 로드 중 오류: {e}")
        
        elif current_theme == "purple_compact":
            # Purple 컴팩트 테마 사용
            import sys
            import os
            # purple 폴더를 Python 경로에 추가
            purple_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'purple')
            if purple_dir not in sys.path:
                sys.path.insert(0, purple_dir)
            
            try:
                # 이미 import된 모듈이 있다면 reload
                if 'purple_compact_spotify_overlay' in sys.modules:
                    import importlib
                    importlib.reload(sys.modules['purple_compact_spotify_overlay'])
                    
                from purple_compact_spotify_overlay import get_purple_compact_template
                logger.info("Purple 컴팩트 테마가 성공적으로 로드되었습니다.")
                return get_purple_compact_template()
            except ImportError as e:
                logger.warning(f"Purple 컴팩트 테마를 불러올 수 없습니다: {e}. 기본 테마를 사용합니다.")
            except Exception as e:
                logger.error(f"Purple 컴팩트 테마 로드 중 오류: {e}")
        
        elif current_theme in ["default", "neon"]:
            # Neon 테마 사용
            import sys
            import os
            # neon 폴더를 Python 경로에 추가
            neon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'neon')
            if neon_dir not in sys.path:
                sys.path.insert(0, neon_dir)
            
            try:
                # 이미 import된 모듈이 있다면 reload
                if 'neon_spotify_ui' in sys.modules:
                    import importlib
                    importlib.reload(sys.modules['neon_spotify_ui'])
                    
                from neon_spotify_ui import get_neon_spotify_template
                logger.info("Neon 테마가 성공적으로 로드되었습니다.")
                return get_neon_spotify_template()
            except ImportError as e:
                logger.warning(f"Neon 테마를 불러올 수 없습니다: {e}. 기본 테마를 사용합니다.")
            except Exception as e:
                logger.error(f"Neon 테마 로드 중 오류: {e}")
        
        # 기본 네온 테마 (fallback)
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
    
    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

class UnifiedServerManager:
    """통합 서버 관리자"""
    
    def __init__(self):
        self.server = None
        self.server_thread = None
        self.chat_client = None
        self.chat_task = None
        self.spotify_update_thread = None
        self.port = config_manager.get_server_port()
    
    def start_server(self):
        """통합 서버 시작"""
        try:
            self.server = http.server.ThreadingHTTPServer(("", self.port), UnifiedServerHandler)
            self.server.timeout = 10
            
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            logger.info(f"🌐 통합 서버 시작: http://localhost:{self.port}")
            logger.info(f"🎮 관리패널: http://localhost:{self.port}/admin")
            
            return True
        except OSError as e:
            if e.errno == 10048:
                logger.error(f"❌ 포트 {self.port}가 이미 사용 중입니다.")
            else:
                logger.error(f"❌ 서버 시작 실패: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 서버 오류: {e}")
            return False
    
    def _start_chat_service(self):
        """채팅 서비스 시작 (내부 메서드)"""
        if not config_manager.is_module_enabled('chat'):
            return False
        
        try:
            channel_id = config_manager.get("modules.chat.channel_id")
            if not channel_id:
                logger.warning("채팅 채널 ID가 설정되지 않았습니다.")
                return False
            
            # 기존 채팅 서비스 정리
            if self.chat_task:
                self.chat_task.cancel()
            
            # 새 채팅 클라이언트 시작
            loop = asyncio.new_event_loop()
            def run_chat():
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._run_chat_client(channel_id))
            
            chat_thread = threading.Thread(target=run_chat, daemon=True)
            chat_thread.start()
            
            services_running['chat'] = True
            logger.info("💬 채팅 서비스 시작됨")
            return True
            
        except Exception as e:
            logger.error(f"채팅 서비스 시작 실패: {e}")
            return False
    
    async def _run_chat_client(self, channel_id):
        """채팅 클라이언트 실행"""
        try:
            def filtered_message_callback(message_data):
                """필터링된 메시지 콜백"""
                # 빈 메시지나 익명 샘플 데이터 필터링
                if (message_data and 
                    message_data.get('message', '').strip() and  # 빈 메시지 제외
                    message_data.get('nickname', '').strip() and  # 빈 닉네임 제외
                    message_data.get('nickname') != '익명'):  # 익명 메시지 제외
                    add_chat_message(message_data)
            
            self.chat_client = ChzzkChatClient(channel_id)
            
            if await self.chat_client.connect():
                await self.chat_client.send_join_message()
                await self.chat_client.listen_messages(message_callback=filtered_message_callback)
            else:
                logger.error("채팅방 연결 실패")
        except Exception as e:
            logger.error(f"채팅 클라이언트 오류: {e}")
        finally:
            services_running['chat'] = False
    
    def _start_spotify_service(self):
        """스포티파이 서비스 시작 (내부 메서드)"""
        if not config_manager.is_module_enabled('spotify'):
            return False
        
        try:
            # 기존 스포티파이 서비스 정리
            if self.spotify_update_thread:
                # 스레드는 데몬이므로 자동으로 정리됨
                pass
            
            # 새 스포티파이 업데이트 스레드 시작
            def update_spotify_data():
                spotify_api = SpotifyAPI()
                while services_running['spotify']:
                    try:
                        if config_manager.is_module_enabled('spotify'):
                            spotify_api.get_current_track()
                        time.sleep(5)
                    except Exception as e:
                        logger.error(f"스포티파이 데이터 업데이트 오류: {e}")
                        time.sleep(10)
            
            services_running['spotify'] = True
            self.spotify_update_thread = threading.Thread(target=update_spotify_data, daemon=True)
            self.spotify_update_thread.start()
            
            logger.info("🎵 스포티파이 서비스 시작됨")
            return True
            
        except Exception as e:
            logger.error(f"스포티파이 서비스 시작 실패: {e}")
            return False
    
    def start_all_services(self):
        """모든 활성화된 서비스 시작 - 수동 시작으로 변경됨"""
        # 자동 시작 비활성화 - 사용자가 패널에서 직접 시작해야 함
        logger.info("📋 모든 모듈이 비활성화 상태로 시작됩니다.")
        logger.info("🎮 관리패널에서 원하는 모듈을 수동으로 시작하세요.")
    
    def stop_server(self):
        """서버 정지"""
        if self.server:
            self.server.shutdown()
            logger.info("서버가 정지되었습니다.")
    
    def restart_services(self):
        """서비스 재시작"""
        logger.info("서비스를 재시작합니다...")
        
        # 기존 서비스 정리
        services_running.update({
            'chat': False,
            'spotify': False
        })
        
        time.sleep(2)  # 정리 시간
        
        # 새 서비스 시작 (수동 시작으로 변경)
        logger.info("📋 모든 모듈이 정지되었습니다. 관리패널에서 다시 시작하세요.")

# 전역 서버 관리자 인스턴스
server_manager = None

def main():
    """메인 함수"""
    global server_manager, APP_MODE
    
    # 종료 신호 처리기 등록
    import signal
    import atexit
    
    def signal_handler(signum, frame):
        """시그널 핸들러"""
        print(f"\n📶 종료 신호 수신: {signum}")
        cleanup_and_exit()
    
    def cleanup_and_exit():
        """정리 작업 후 종료"""
        try:
            print("🧹 정리 작업 중...")
            if server_manager:
                server_manager.stop_server()
            
            import platform
            
            current_pid = os.getpid()
            print(f"🔄 안전한 프로세스 종료: PID={current_pid}")
            
            # Windows에서도 taskkill 대신 더 안전한 방식 사용
            if platform.system() == "Windows":
                try:
                    # psutil을 사용한 안전한 종료
                    import psutil
                    current_process = psutil.Process(current_pid)
                    
                    # 자식 프로세스들을 먼저 정리
                    children = current_process.children(recursive=True)
                    for child in children:
                        try:
                            child.terminate()
                        except:
                            pass
                    
                    # 잠시 대기 후 강제 종료
                    time.sleep(1)
                    for child in children:
                        try:
                            if child.is_running():
                                child.kill()
                        except:
                            pass
                                
                except Exception as clean_ex:
                    print(f"⚠️  프로세스 정리 중 오류: {clean_ex}")
            
            # 4. 정상적인 종료
            print("✅ 정상 종료")
            os._exit(0)
            
        except Exception as e:
            print(f"❌ 종료 중 오류: {e}")
            os._exit(1)
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup_and_exit)
    
    # 명령줄 인수 파싱
    parser = argparse.ArgumentParser(description='네온 오버레이 통합 시스템')
    parser.add_argument('--app', action='store_true', help='데스크톱 앱 모드로 실행')
    parser.add_argument('--browser', action='store_true', help='브라우저 모드로 실행 (기본값)')
    parser.add_argument('--port', type=int, default=8080, help='서버 포트 번호 (기본값: 8080)')
    args = parser.parse_args()
    
    # 실행 파일인 경우 자동으로 앱 모드 활성화 (강제)
    is_frozen = getattr(sys, 'frozen', False)
    is_exe = sys.executable.endswith('.exe') and 'python' not in sys.executable.lower()
    
    if is_frozen or is_exe:
        APP_MODE = True  # 실행 파일에서는 무조건 앱 모드
        print(f"🚀 실행 파일 감지 - 강제 앱 모드 활성화 (frozen={is_frozen}, exe={is_exe})")
        print(f"📁 실행 경로: {sys.executable}")
    else:
        APP_MODE = args.app
        print(f"🐍 개발 모드 - 선택적 앱 모드 (app={APP_MODE})")
    
    print("🎮 네온 오버레이 통합 시스템 시작!")
    print("="*60)
    
    if APP_MODE and WEBVIEW_AVAILABLE:
        print("📱 데스크톱 앱 모드")
    else:
        print("🌐 브라우저 모드")
        if APP_MODE and not WEBVIEW_AVAILABLE:
            print("⚠️  webview 라이브러리가 설치되지 않았습니다. 브라우저 모드로 실행합니다.")
            print("   데스크톱 앱 모드를 사용하려면: pip install webview")
    
    # 서버 관리자 생성 및 시작
    server_manager = UnifiedServerManager()
    
    # 포트 설정 적용
    if args.port != 8080:
        config_manager.config["server"]["port"] = args.port
        print(f"🔧 포트 설정: {args.port}")
        
        # 포트 변경 시 관련 URL들도 업데이트
        config_manager.update_port(args.port)
        print(f"🔗 관련 URL들 자동 업데이트 완료")
    
    if server_manager.start_server():
        # 모듈 자동 시작 비활성화 - 수동 시작만 허용
        server_manager.start_all_services()
        
        print(f"🌐 통합 서버: http://localhost:{server_manager.port}")
        print(f"🎮 관리패널: http://localhost:{server_manager.port}/admin")
        print(f"💬 채팅 오버레이: http://localhost:{server_manager.port}/chat/overlay")
        print(f"🎵 스포티파이 오버레이: http://localhost:{server_manager.port}/spotify/overlay")
        print("="*60)
        print("📋 모든 모듈이 정지 상태입니다.")
        print("🎮 관리패널에서 원하는 모듈을 시작하세요!")
        print("="*60)
        
        # 앱 모드 또는 브라우저 모드로 관리패널 열기
        if APP_MODE and WEBVIEW_AVAILABLE:
            # 데스크톱 앱 모드 (메인 스레드에서 실행)
            start_desktop_app(server_manager.port)
        else:
            # 브라우저 모드
            try:
                webbrowser.open(f"http://localhost:{server_manager.port}/admin")
            except:
                pass
            
            try:
                # 메인 루프 유지
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 네온 오버레이 시스템을 종료합니다.")
                server_manager.stop_server()
    else:
        print("❌ 서버 시작에 실패했습니다.")

def start_desktop_app(port):
    """데스크톱 앱 모드로 관리패널 시작"""
    try:
        # 서버가 시작될 때까지 잠시 대기
        time.sleep(2)
        
        # 매우 간단한 종료 함수
        def simple_shutdown():
            """안전하고 확실한 종료 (바이러스 오탐 방지)"""
            print("\n🔥 앱 종료 중...")
            try:
                # 1. webview 창 닫기 시도
                try:
                    webview.destroy_window()
                except:
                    pass
                
                # 2. 서버 정리
                if server_manager:
                    try:
                        server_manager.stop_server()
                    except:
                        pass
                
                # 3. 안전한 프로세스 종료 (덜 의심스러운 방식)
                import platform
                
                current_pid = os.getpid()
                print(f"🔄 안전한 프로세스 종료: PID={current_pid}")
                
                # Windows에서도 taskkill 대신 더 안전한 방식 사용
                if platform.system() == "Windows":
                    try:
                        # psutil을 사용한 안전한 종료
                        import psutil
                        current_process = psutil.Process(current_pid)
                        
                        # 자식 프로세스들을 먼저 정리
                        children = current_process.children(recursive=True)
                        for child in children:
                            try:
                                child.terminate()
                            except:
                                pass
                        
                        # 잠시 대기 후 강제 종료
                        time.sleep(1)
                        for child in children:
                            try:
                                if child.is_running():
                                    child.kill()
                            except:
                                pass
                                
                    except Exception as clean_ex:
                        print(f"⚠️  프로세스 정리 중 오류: {clean_ex}")
                
                # 4. 정상적인 종료
                print("✅ 정상 종료")
                os._exit(0)
                
            except Exception as e:
                print(f"❌ 종료 중 오류: {e}")
                os._exit(1)
        
        # 백그라운드에서 강제 종료를 처리할 스레드
        shutdown_thread = None
        
        # API 클래스 (webview에서 호출 가능)
        class AppAPI:
            def shutdown_app(self):
                """JavaScript에서 호출 가능한 종료 함수"""
                nonlocal shutdown_thread
                print("📱 webview에서 종료 요청됨")
                if shutdown_thread is None or not shutdown_thread.is_alive():
                    shutdown_thread = threading.Thread(target=simple_shutdown, daemon=True)
                    shutdown_thread.start()
                return "Shutting down..."
        
        # 앱 창 설정
        window = webview.create_window(
            title="🎮 스트리밍 컨트롤 센터",
            url=f"http://localhost:{port}/admin",
            width=1200,
            height=800,
            min_size=(1000, 700),
            resizable=True,
            shadow=True,
            on_top=False,
            text_select=True,
            js_api=AppAPI()  # API 등록
        )
        
        # 이벤트 핸들러 등록
        def on_window_closing():
            """창이 닫히기 전 호출"""
            print("🚪 창 닫기 감지됨")
            simple_shutdown()
        
        def on_window_closed():
            """창이 닫힌 후 호출"""
            print("🚪 창이 완전히 닫힘")
            simple_shutdown()
        
        # webview 이벤트 등록
        window.events.closing += on_window_closing
        window.events.closed += on_window_closed
        
        print("🖥️  webview 앱 시작 중...")
        
        # 창 시작 (블로킹)
        webview.start(debug=False)
        
        # webview가 종료되면 여기 도달
        print("🏁 webview 종료됨")
        simple_shutdown()
        
    except Exception as e:
        logger.error(f"데스크톱 앱 시작 실패: {e}")
        print("⚠️  브라우저 모드로 대체합니다.")
        webbrowser.open(f"http://localhost:{port}/admin")
        
        # 브라우저 모드로 대체 시 메인 루프 유지
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 네온 오버레이 시스템을 종료합니다.")
            if server_manager:
                server_manager.stop_server()
            cleanup_and_exit()

if __name__ == "__main__":
    main() 