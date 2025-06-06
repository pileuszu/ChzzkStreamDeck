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
# 로깅 설정 (먼저 설정)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from chat_client import ChzzkChatClient
from spotify_api import SpotifyAPI, get_current_track_data

# webview 라이브러리 임포트 (선택적)
try:
    import webview
    WEBVIEW_AVAILABLE = True
    logger.info("✅ pywebview 라이브러리가 감지되었습니다 - 데스크톱 앱 모드 사용 가능")
except ImportError:
    WEBVIEW_AVAILABLE = False
    logger.info("💡 pywebview 라이브러리가 없어 브라우저 모드로 실행됩니다.")
    logger.info("   ✅ 이는 정상적인 동작이며, 모든 기능을 사용할 수 있습니다.")
    logger.info("   🖥️  데스크톱 앱 모드를 원한다면: pip install pywebview")

# 글로벌 채팅 메시지 저장소 (Old version과 동일)
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
    """새 채팅 메시지 추가 - Old version과 동일한 간단한 방식"""
    global chat_messages
    
    # 기본 검증만 수행 (Old version과 동일)
    if not message_data or not message_data.get('message', '').strip():
        return
    
    # 간단한 중복 체크: 마지막 메시지와만 비교 (Old version 방식)
    if (chat_messages and 
        chat_messages[-1].get('message') == message_data.get('message') and
        chat_messages[-1].get('nickname') == message_data.get('nickname')):
        logger.debug(f"중복 메시지 무시: {message_data.get('nickname')}")
        return
    
    # 메시지 추가 (Old version과 동일)
    chat_messages.append(message_data)
    
    # 최대 메시지 수 제한 (Old version과 동일)
    if len(chat_messages) > MAX_MESSAGES:
        chat_messages.pop(0)
    
    logger.debug(f"✅ 새 채팅: {message_data.get('nickname', '익명')}: {message_data.get('message', '')[:25]}...")

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
                        # 로그 출력 빈도 줄이기 - 디버그 레벨로 변경
                        logger.debug(f"Spotify 인증 상태 조회: {authenticated}")
                        
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
        
        elif parsed_path.path == '/api/config/import':
            # 설정 가져오기 API
            try:
                import_data = json.loads(post_data)
                
                # 설정 데이터 검증
                if 'config' in import_data:
                    imported_config = import_data['config']
                    
                    # 기본 구조 검증
                    required_keys = ['server', 'modules', 'ui']
                    if all(key in imported_config for key in required_keys):
                        # 설정 업데이트
                        config_manager.config = imported_config
                        success = config_manager.save_config()
                        
                        self.send_response(200 if success else 500)
                        self.send_header('Content-type', 'application/json; charset=utf-8')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        response = {"success": success, "message": "설정을 성공적으로 가져왔습니다." if success else "설정 저장에 실패했습니다."}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    else:
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json; charset=utf-8')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        response = {"success": False, "message": "잘못된 설정 파일 형식입니다."}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"success": False, "message": "설정 데이터가 없습니다."}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"success": False, "message": "잘못된 JSON 형식입니다."}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"success": False, "message": f"설정 가져오기 실패: {e}"}
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
                                # 현재 프로세스와 부모 프로세스 모두 종료
                                subprocess.run(['taskkill', '/f', '/t', '/pid', str(current_pid)], 
                                            shell=True, capture_output=True, timeout=2)
                                subprocess.run(['taskkill', '/f', '/t', '/pid', str(parent_pid)], 
                                            shell=True, capture_output=True, timeout=2)
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
                result = server_manager._start_chat_service()
                if not result:
                    logger.error("💬 채팅 모듈 시작 실패!")
                    logger.error("💡 채널 ID가 설정되어 있는지 확인하세요.")
                return result
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
                logger.info(f"💬 {module_name} 정지됨")
                return True
            elif module_name == 'spotify':
                services_running['spotify'] = False
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
                            <p><code>http://localhost:{config_manager.get_server_port()}/spotify/overlay</code></p>
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
        """채팅 오버레이 HTML - Old version과 동일한 네온 테마 복원"""
        # Old version과 정확히 동일한 HTML 반환
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>치지직 채팅 오버레이</title>
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
            position: relative;
        }

        /* 사이버펑크 배경 - 데이터 스트림과 네온 그리드 */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                /* 네온 그리드 */
                linear-gradient(90deg, rgba(0,255,175,0.03) 1px, transparent 1px),
                linear-gradient(180deg, rgba(155,77,224,0.03) 1px, transparent 1px),
                /* 데이터 스트림 파티클 */
                radial-gradient(2px 2px at 20% 30%, rgba(0,255,175,0.8), transparent),
                radial-gradient(1px 1px at 80% 20%, rgba(155,77,224,0.6), transparent),
                radial-gradient(3px 3px at 45% 70%, rgba(255,215,0,0.4), transparent),
                radial-gradient(2px 2px at 90% 80%, rgba(255,255,255,0.3), transparent);
            background-size: 50px 50px, 50px 50px, 300px 300px, 250px 250px, 400px 400px, 200px 200px;
            animation: dataStreamFlow 15s linear infinite, cyberGrid 8s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }

        /* 추가 홀로그램 레이어 */
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                /* 스캔라인 효과 */
                repeating-linear-gradient(
                    0deg,
                    transparent 0px,
                    rgba(0,255,175,0.03) 1px,
                    transparent 2px,
                    transparent 4px
                );
            animation: scanlines 2s linear infinite;
            pointer-events: none;
            z-index: 1;
        }
        
        .chat_wrap {
            position: fixed;
            top: 50%;
            left: 10%; /* 왼쪽끝(0%)과 중앙점(50%) 사이 */
            transform: translateY(-50%); /* 상하 중앙 정렬 */
            width: 640px; /* 글로우 효과를 위해 너비도 약간 증가 */
            height: 720px; /* 글로우 효과를 위해 높이도 약간 증가 - Old version과 동일 */
            background: transparent;
            z-index: 1000;
            font-family: 'Noto Sans KR', sans-serif;
            overflow: hidden;
            padding: 60px; /* 글로우 효과가 잘리지 않도록 패딩 대폭 증가 */
        }

        .chat_list {
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            gap: 15px;
            height: 100%; /* Old version과 동일 - 고정 높이 */
            overflow: hidden;
            position: relative;
            z-index: 2;
            /* 위쪽 자연스러운 페이드아웃 마스크 - Old version과 동일 */
            mask: linear-gradient(to bottom, 
                transparent 0%, 
                rgba(0,0,0,0.05) 5%, 
                rgba(0,0,0,0.2) 15%, 
                rgba(0,0,0,0.6) 30%, 
                black 45%, 
                black 100%);
            -webkit-mask: linear-gradient(to bottom, 
                transparent 0%, 
                rgba(0,0,0,0.05) 5%, 
                rgba(0,0,0,0.2) 15%, 
                rgba(0,0,0,0.6) 30%, 
                black 45%, 
                black 100%);
        }

        .chat_box.naver.chat {
            padding: 18px 25px;
            margin: 20px 40px;
            position: relative;
            z-index: 2;
            animation: messageEntrance 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            transform: translateX(-120px) rotateY(-15deg) scale(0.8);
            opacity: 0;
            max-width: calc(100% - 80px);
            filter: drop-shadow(0 0 0 transparent);
            overflow: visible;
        }

        /* 스트리머용 왼쪽 상단 별 */
        .chat_box.naver.chat.streamer::before {
            content: '';
            position: absolute;
            top: -12px;
            left: -12px;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            background: transparent;
            border-radius: 50%;
            animation: starTwinkle 1.5s ease-in-out infinite alternate;
            z-index: 100;
            filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.9));
        }

        .chat_box.naver.chat p.name {
            display: block;
            font-weight: 900;
            font-size: 15px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 2px;
            position: relative;
            overflow: hidden;
        }

        .chat_box.naver.chat.streamer p.name {
            color: #9b4de0;
            text-shadow: 
                0 0 15px rgba(155, 77, 224, 0.9),
                0 0 30px rgba(155, 77, 224, 0.5),
                0 0 45px rgba(155, 77, 224, 0.3);
            animation: royalGlow 3s ease-in-out infinite alternate;
        }

        .chat_box.naver.chat:not(.streamer) p.name {
            color: #00FFAF;
            text-shadow: 
                0 0 15px rgba(0, 255, 175, 0.9),
                0 0 30px rgba(0, 255, 175, 0.5),
                0 0 45px rgba(0, 255, 175, 0.3);
            animation: emeraldGlow 3s ease-in-out infinite alternate;
        }

        /* 이름과 텍스트 사이 구분선 */
        .chat_box.naver.chat::after {
            content: '';
            position: absolute;
            left: 25px;
            right: 25px;
            top: calc(15px + 8px + 15px + 3px);
            height: 4px;
            background: linear-gradient(90deg, 
                transparent 0%,
                white 20%,
                white 80%,
                transparent 100%);
            opacity: 0.6;
            transform: scaleX(0);
            animation: separatorExpand 1.5s ease-out 0.8s forwards;
            z-index: 1;
        }

        .chat_box.naver.chat p.text {
            color: #ffffff;
            font-size: 17px;
            line-height: 1.5;
            font-weight: 400;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
            animation: typeWriter 1.5s ease-out 0.3s forwards;
            opacity: 0;
            position: relative;
        }

        .chat_box.naver.chat:not(.streamer) {
            align-self: flex-start;
            background: linear-gradient(135deg, 
                rgba(0, 255, 175, 0.03) 0%, 
                rgba(0, 255, 175, 0.08) 30%,
                rgba(0, 255, 175, 0.12) 50%, 
                rgba(0, 255, 175, 0.08) 70%,
                rgba(0, 255, 175, 0.03) 100%);
            border: 1px solid rgba(0, 255, 175, 0.25);
            border-radius: 25px 25px 25px 8px;
            backdrop-filter: blur(20px);
            box-shadow: 
                0 12px 20px rgba(0, 255, 175, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.06),
                0 0 15px rgba(0, 255, 175, 0.1);
        }

        .chat_box.naver.chat.streamer {
            align-self: flex-end;
            background: linear-gradient(135deg, 
                rgba(155, 77, 224, 0.03) 0%, 
                rgba(155, 77, 224, 0.08) 30%,
                rgba(155, 77, 224, 0.12) 50%, 
                rgba(155, 77, 224, 0.08) 70%,
                rgba(155, 77, 224, 0.03) 100%);
            border: 1px solid rgba(155, 77, 224, 0.25);
            border-radius: 25px 25px 8px 25px;
            backdrop-filter: blur(20px);
            box-shadow: 
                0 12px 20px rgba(155, 77, 224, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.06),
                0 0 15px rgba(155, 77, 224, 0.1);
            animation: messageEntranceRight 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            transform: translateX(120px) rotateY(15deg) scale(0.8);
        }

        @keyframes messageEntrance {
            0% {
                transform: translateX(-120px) rotateY(-15deg) scale(0.8);
                opacity: 0;
                filter: blur(10px);
            }
            100% {
                transform: translateX(0) rotateY(0deg) scale(1);
                opacity: 1;
                filter: blur(0px);
            }
        }

        @keyframes messageEntranceRight {
            0% {
                transform: translateX(120px) rotateY(15deg) scale(0.8);
                opacity: 0;
                filter: blur(10px);
            }
            100% {
                transform: translateX(0) rotateY(0deg) scale(1);
                opacity: 1;
                filter: blur(0px);
            }
        }

        @keyframes starTwinkle {
            0% {
                filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.8));
                opacity: 1;
            }
            100% {
                filter: drop-shadow(0 0 15px rgba(255, 215, 0, 1)) drop-shadow(0 0 25px rgba(255, 215, 0, 0.5));
                opacity: 0.8;
            }
        }

        @keyframes royalGlow {
            0% {
                text-shadow: 
                    0 0 15px rgba(155, 77, 224, 0.9),
                    0 0 30px rgba(155, 77, 224, 0.5),
                    0 0 45px rgba(155, 77, 224, 0.3);
            }
            100% {
                text-shadow: 
                    0 0 25px rgba(155, 77, 224, 1),
                    0 0 40px rgba(155, 77, 224, 0.8),
                    0 0 60px rgba(155, 77, 224, 0.5),
                    0 0 80px rgba(155, 77, 224, 0.3);
            }
        }

        @keyframes emeraldGlow {
            0% {
                text-shadow: 
                    0 0 15px rgba(0, 255, 175, 0.9),
                    0 0 30px rgba(0, 255, 175, 0.5),
                    0 0 45px rgba(0, 255, 175, 0.3);
            }
            100% {
                text-shadow: 
                    0 0 25px rgba(0, 255, 175, 1),
                    0 0 25px rgba(0, 255, 175, 0.8),
                    0 0 25px rgba(0, 255, 175, 0.5),
                    0 0 25px rgba(0, 255, 175, 0.3);
            }
        }

        @keyframes typeWriter {
            0% {
                opacity: 0;
                transform: translateY(20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes separatorExpand {
            0% {
                transform: scaleX(0);
            }
            100% {
                transform: scaleX(1);
            }
        }

        @keyframes dataStreamFlow {
            0% {
                transform: translateY(0) translateX(0);
                opacity: 0.4;
            }
            50% {
                transform: translateY(-50px) translateX(25px);
                opacity: 0.8;
            }
            100% {
                transform: translateY(-100px) translateX(50px);
                opacity: 0.2;
            }
        }

        @keyframes cyberGrid {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1);
            }
            50% {
                opacity: 0.6;
                transform: scale(1.02);
            }
        }

        @keyframes scanlines {
            0% {
                transform: translateY(0);
            }
            100% {
                transform: translateY(4px);
            }
        }
    </style>
</head>
<body>
    <div class="chat_wrap">
        <div class="chat_list">
        </div>
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
                            
                            // 클래스 설정 - Old version과 동일
                            let className = 'chat_box naver chat';
                            if (data.is_streamer) {
                                className += ' streamer';
                            }
                            messageDiv.className = className;
                            
                            messageDiv.innerHTML = `
                                <p class="name">${escapeHtml(data.nickname)}</p>
                                <p class="text">${escapeHtml(data.message)}</p>
                            `;
                            
                            container.appendChild(messageDiv);
                            
                            // 최대 15개 메시지 유지 - Old version과 동일
                            while (container.children.length > 15) {
                                const firstChild = container.firstChild;
                                if (firstChild) {
                                    firstChild.remove();
                                }
                            }
                        }, index * 200);
                    });
                    
                    lastMessageCount = messages.length;
                }
            } catch (e) {
                console.error('메시지 업데이트 실패:', e);
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // 2초마다 새 메시지 체크 - Old version과 동일
        setInterval(updateMessages, 2000);
        
        // 초기 로드
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
    
    def update_port(self, new_port):
        """포트 업데이트"""
        self.port = new_port
        logger.info(f"서버 매니저 포트 업데이트: {new_port}")
    
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
        """채팅 서비스 시작 (Old version과 동일한 방식)"""
        logger.info("💬 채팅 서비스 시작 요청됨")
        
        # 시작 버튼을 누르면 모듈을 활성화
        config_manager.set("modules.chat.enabled", True)
        logger.info("채팅 모듈이 활성화되었습니다.")
        
        try:
            channel_id = config_manager.get("modules.chat.channel_id")
            if not channel_id:
                logger.warning("채팅 채널 ID가 설정되지 않았습니다.")
                return False
            
            logger.info(f"설정된 채널 ID: {channel_id}")
            
            # 기존 채팅 서비스 정리
            if self.chat_task:
                self.chat_task.cancel()
                logger.info("기존 채팅 서비스 정리됨")
            
            # 새 채팅 클라이언트 시작 (Old version과 동일한 방식)
            def run_chat():
                try:
                    # 새 이벤트 루프에서 실행
                    import asyncio
                    asyncio.run(self._run_chat_client_simple(channel_id))
                except Exception as e:
                    logger.error(f"채팅 클라이언트 스레드 오류: {e}")
            
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
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries and services_running.get('chat', False):
            try:
                def filtered_message_callback(message_data):
                    """필터링된 메시지 콜백 - 추가 검증 포함"""
                    # 더 엄격한 필터링 조건
                    if (message_data and 
                        message_data.get('message', '').strip() and  # 빈 메시지 제외
                        message_data.get('nickname', '').strip() and  # 빈 닉네임 제외
                        message_data.get('nickname') != '익명'):  # 익명 메시지 제외 (Old version과 동일)
                        add_chat_message(message_data)
                        logger.debug(f"채팅 메시지 처리됨: {message_data.get('nickname')}")
                    else:
                        logger.debug(f"메시지 필터링됨: {message_data.get('nickname', 'None')}")
                
                logger.info(f"채팅 클라이언트 시작 시도 ({retry_count + 1}/{max_retries})")
                
                try:
                    self.chat_client = ChzzkChatClient(channel_id)
                except ValueError as ve:
                    logger.error(f"채팅 클라이언트 생성 실패: {ve}")
                    return
                except Exception as ce:
                    logger.error(f"채팅 클라이언트 생성 중 오류: {ce}")
                    return
                
                if await self.chat_client.connect():
                    logger.info("채팅방 연결 성공! 메시지 수신 시작...")
                    await self.chat_client.send_join_message()
                    await self.chat_client.listen_messages(message_callback=filtered_message_callback)
                    # 정상 종료된 경우 재시도하지 않음
                    break
                else:
                    logger.error(f"채팅방 연결 실패 ({retry_count + 1}/{max_retries})")
                    retry_count += 1
                    
            except Exception as e:
                logger.error(f"채팅 클라이언트 오류 ({retry_count + 1}/{max_retries}): {e}")
                retry_count += 1
                
            # 재시도 전 대기 (마지막 시도가 아닌 경우)
            if retry_count < max_retries and services_running.get('chat', False):
                wait_time = min(5 * retry_count, 30)  # 최대 30초 대기
                logger.info(f"재시도 전 {wait_time}초 대기...")
                await asyncio.sleep(wait_time)
        
        if retry_count >= max_retries:
            logger.error("채팅 클라이언트 최대 재시도 횟수 초과")
        
        services_running['chat'] = False
        logger.info("채팅 서비스 종료됨")
    
    async def _run_chat_client_simple(self, channel_id):
        """스포티파이와 충돌하지 않는 안정화된 채팅 클라이언트"""
        logger.info("=== 안정화된 채팅 클라이언트 시작 ===")
        
        # 스포티파이와 충돌 방지를 위한 약간의 지연
        await asyncio.sleep(0.8)
        
        try:
            def filtered_message_callback(message_data):
                """필터링된 메시지 콜백 - 스레드 안전 보장"""
                try:
                    # 더 엄격한 필터링 조건
                    if (message_data and 
                        isinstance(message_data, dict) and  # dict 타입 확인
                        message_data.get('message', '').strip() and  # 빈 메시지 제외
                        message_data.get('nickname', '').strip() and  # 빈 닉네임 제외
                        message_data.get('nickname') != '익명'):  # 익명 메시지 제외 (Old version과 동일)
                        
                        # 스레드 안전하게 메시지 추가
                        add_chat_message(message_data)
                        logger.debug(f"💬 {message_data.get('nickname')}: {message_data.get('message', '')[:25]}...")
                    else:
                        logger.debug(f"메시지 필터링됨: {message_data}")
                except Exception as cb_error:
                    logger.error(f"메시지 콜백 오류: {cb_error}")
            
            # 채팅 클라이언트 생성
            logger.info("📱 채팅 클라이언트 생성 중...")
            client = ChzzkChatClient(channel_id)
            
            # 재연결 루프 (안정성 향상)
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries and services_running.get('chat', False):
                try:
                    # 연결 시도
                    if await client.connect():
                        logger.info("✅ 채팅방 연결 성공! 메시지 수신 시작...")
                        await client.send_join_message()
                        
                        # 메시지 수신 (스포티파이와 격리됨)
                        while services_running.get('chat', False):
                            try:
                                await client.listen_messages(message_callback=filtered_message_callback)
                                # listen_messages가 종료되면 서비스가 정지된 것임
                                if services_running.get('chat', False):
                                    logger.warning("⚠️ 메시지 수신 중단됨, 재연결 시도...")
                                    break
                            except Exception as listen_error:
                                logger.error(f"메시지 수신 오류: {listen_error}")
                                if services_running.get('chat', False):
                                    await asyncio.sleep(3)
                                    break
                                else:
                                    return
                        
                        # 정상 종료인 경우 재시도 안함
                        if not services_running.get('chat', False):
                            break
                            
                        # 재연결 시도
                        retry_count += 1
                        if retry_count < max_retries:
                            logger.info(f"🔄 재연결 시도 ({retry_count}/{max_retries})")
                            await asyncio.sleep(5)
                    else:
                        logger.error(f"❌ 채팅방 연결 실패 ({retry_count + 1}/{max_retries})")
                        retry_count += 1
                        if retry_count < max_retries:
                            await asyncio.sleep(5)
                        
                except Exception as connect_error:
                    logger.error(f"연결 시도 중 오류: {connect_error}")
                    retry_count += 1
                    if retry_count < max_retries and services_running.get('chat', False):
                        await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"채팅 클라이언트 실행 오류: {e}")
        finally:
            logger.info("💬 채팅 클라이언트 종료됨")
            services_running['chat'] = False
            
            # 정리 작업
            try:
                await client.disconnect()
            except:
                pass
    
    def _start_spotify_service(self):
        """스포티파이 서비스 시작 (내부 메서드) - 채팅 모듈과 격리"""
        # 시작 버튼을 누르면 모듈을 활성화
        config_manager.set("modules.spotify.enabled", True)
        logger.info("🎵 스포티파이 모듈이 활성화되었습니다.")
        
        try:
            # 기존 스포티파이 서비스 정리
            if hasattr(self, 'spotify_update_thread') and self.spotify_update_thread:
                services_running['spotify'] = False
                time.sleep(0.5)  # 기존 스레드가 종료될 시간 제공
            
            # 새 스포티파이 업데이트 스레드 시작 (채팅과 완전히 격리)
            def update_spotify_data():
                """스포티파이 데이터 업데이트 - 별도 스레드에서 실행"""
                logger.info("🎵 스포티파이 데이터 업데이트 스레드 시작")
                spotify_api = SpotifyAPI()
                error_count = 0
                
                while services_running.get('spotify', False):
                    try:
                        if config_manager.is_module_enabled('spotify'):
                            # 스포티파이 API 호출을 try-catch로 보호
                            track_data = spotify_api.get_current_track()
                            if track_data:
                                logger.debug("🎵 스포티파이 트랙 정보 업데이트됨")
                                error_count = 0  # 성공 시 에러 카운트 리셋
                            time.sleep(3)  # 3초로 간격 단축 (더 반응적)
                        else:
                            time.sleep(5)  # 비활성화 상태에서는 5초 대기
                    except Exception as e:
                        error_count += 1
                        logger.debug(f"스포티파이 데이터 업데이트 오류 ({error_count}): {e}")
                        # 에러가 연속으로 발생하면 대기 시간 증가
                        sleep_time = min(10 + error_count * 2, 30)
                        time.sleep(sleep_time)
                
                logger.info("🎵 스포티파이 데이터 업데이트 스레드 종료")
            
            # 스포티파이 서비스 시작
            services_running['spotify'] = True
            self.spotify_update_thread = threading.Thread(target=update_spotify_data, daemon=True, name="SpotifyUpdateThread")
            self.spotify_update_thread.start()
            
            logger.info("🎵 스포티파이 서비스 시작됨 (채팅 모듈과 격리됨)")
            return True
            
        except Exception as e:
            logger.error(f"스포티파이 서비스 시작 실패: {e}")
            services_running['spotify'] = False
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
            
            import psutil
            import platform
            import subprocess
            
            current_pid = os.getpid()
            print(f"🔄 프로세스 정리 중... (PID: {current_pid})")
            
            # 모든 관련 프로세스 종료
            try:
                current_process = psutil.Process(current_pid)
                children = current_process.children(recursive=True)
                
                for child in children:
                    try:
                        child.terminate()
                    except:
                        pass
                
                time.sleep(1)
                
                for child in children:
                    try:
                        if child.is_running():
                            child.kill()
                    except:
                        pass
                        
            except Exception as e:
                print(f"⚠️  프로세스 정리 중 오류: {e}")
            
            # Windows에서 추가 정리
            if platform.system() == "Windows":
                try:
                    subprocess.run(['taskkill', '/f', '/pid', str(current_pid)], 
                                 shell=True, capture_output=True, timeout=3)
                except:
                    pass
            
            print("✅ 정리 완료")
            
        except Exception as e:
            print(f"❌ 정리 중 오류: {e}")
        finally:
            os._exit(0)
    
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
    
    # 실행 파일인 경우 자동으로 앱 모드 활성화 (pywebview 포함된 경우에만)
    is_frozen = getattr(sys, 'frozen', False)
    is_exe = sys.executable.endswith('.exe') and 'python' not in sys.executable.lower()
    
    if is_frozen or is_exe:
        # 실행 파일에서는 pywebview가 있으면 앱 모드, 없으면 브라우저 모드
        APP_MODE = WEBVIEW_AVAILABLE
        print(f"🚀 실행 파일 감지 (frozen={is_frozen}, exe={is_exe})")
        print(f"📁 실행 경로: {sys.executable}")
        if WEBVIEW_AVAILABLE:
            print("✅ pywebview 포함됨 - 데스크톱 앱 모드 활성화")
        else:
            print("⚠️ pywebview 미포함 - 브라우저 모드로 실행")
    else:
        APP_MODE = args.app
        print(f"🐍 개발 모드 - 선택적 앱 모드 (app={APP_MODE})")
    
    print("🎮 네온 오버레이 통합 시스템 시작!")
    print("="*60)
    
    if APP_MODE and WEBVIEW_AVAILABLE:
        print("📱 데스크톱 앱 모드")
    else:
        print("🌐 브라우저 모드")
        if (is_frozen or is_exe) and not WEBVIEW_AVAILABLE:
            print("💡 이 실행 파일은 pywebview가 포함되지 않은 경량 버전입니다.")
            print("   ✅ 브라우저에서 동일한 기능을 모두 사용할 수 있습니다.")
            print("   🖥️  데스크톱 앱 버전을 원한다면 Full 버전을 다운로드하세요.")
        elif APP_MODE and not WEBVIEW_AVAILABLE:
            print("💡 pywebview 라이브러리가 없어 브라우저 모드로 실행됩니다.")
            print("   ✅ 이는 정상적인 동작이며, 모든 기능을 사용할 수 있습니다.")
            print("   🖥️  데스크톱 앱 모드를 원한다면: pip install pywebview")
    
    # 포트 설정 적용 (항상)
    current_config_port = config_manager.get_server_port()
    if args.port != current_config_port:
        config_manager.update_port(args.port)
        print(f"🔧 포트 설정: {current_config_port} → {args.port}")
        print(f"🔄 관련 URL들이 자동으로 업데이트되었습니다.")
    
    # 서버 관리자 생성 (포트 설정 후)
    server_manager = UnifiedServerManager()
    
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
            """매우 간단하고 확실한 종료"""
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
                
                # 3. 모든 프로세스 강제 종료 (부모 프로세스 포함)
                import psutil
                import subprocess
                import platform
                
                current_pid = os.getpid()
                parent_pid = os.getppid()
                
                print(f"🔄 프로세스 종료: PID={current_pid}, 부모PID={parent_pid}")
                
                # Windows에서 부모 프로세스(CMD)도 함께 종료
                if platform.system() == "Windows":
                    try:
                        # 현재 프로세스와 부모 프로세스 모두 종료
                        subprocess.run(['taskkill', '/f', '/t', '/pid', str(current_pid)], 
                                     shell=True, capture_output=True, timeout=2)
                        subprocess.run(['taskkill', '/f', '/t', '/pid', str(parent_pid)], 
                                     shell=True, capture_output=True, timeout=2)
                    except:
                        pass
                
                # 4. 바로 강제 종료
                print("강제 종료 실행")
                os._exit(0)
                
            except Exception as e:
                print(f"❌ 종료 중 오류: {e}")
                # 최후의 수단
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