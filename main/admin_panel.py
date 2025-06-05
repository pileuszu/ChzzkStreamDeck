#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
관리자 패널 로직 처리
UI는 별도 테마 폴더에서 처리
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json, logging, threading, time, os, sys
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class AdminPanelLogicHandler(BaseHTTPRequestHandler):
    """관리자 패널 로직 처리 (UI 분리)"""
    
    def log_message(self, format, *args):
        logger.debug(f"Admin Panel: {format % args}")
    
    def do_GET(self):
        """GET 요청 처리"""
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/admin' or parsed_path.path == '/':
                # 메인 관리자 패널 페이지
                html = self.get_admin_panel_html()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                
            elif parsed_path.path == '/api/config':
                # 설정 불러오기 API
                from config import CONFIG_MANAGER
                config = CONFIG_MANAGER.get_config()
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(config, ensure_ascii=False).encode('utf-8'))
                
            elif parsed_path.path == '/api/modules/status':
                # 모듈 상태 확인 API
                status = self.get_modules_status()
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(status, ensure_ascii=False).encode('utf-8'))
                
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"GET 요청 처리 중 오류: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_POST(self):
        """POST 요청 처리"""
        try:
            parsed_path = urlparse(self.path)
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
            
            if parsed_path.path == '/api/config/save':
                # 설정 저장 API
                try:
                    config_data = json.loads(post_data)
                    from config import CONFIG_MANAGER
                    
                    success = CONFIG_MANAGER.save_config(config_data)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    if success:
                        response = {"success": True, "message": "설정이 성공적으로 저장되었습니다."}
                    else:
                        response = {"success": False, "message": "설정 저장에 실패했습니다."}
                    
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"success": False, "message": "잘못된 JSON 형식입니다."}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            elif parsed_path.path == '/api/config/export':
                # 설정 내보내기 API
                try:
                    import os
                    from datetime import datetime
                    
                    # 설정 데이터 파싱
                    config_data = json.loads(post_data)
                    
                    # 기본 파일명 생성
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"overlay_config_backup_{timestamp}.json"
                    
                    # 현재 디렉토리에 저장 (사용자가 쉽게 찾을 수 있도록)
                    file_path = os.path.join(os.getcwd(), filename)
                    
                    # 파일 저장
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=2, ensure_ascii=False)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"success": True, "message": "설정이 성공적으로 내보내졌습니다.", "filepath": file_path}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"success": False, "message": f"설정 내보내기 실패: {e}"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            elif parsed_path.path == '/api/shutdown':
                # 앱 종료 API
                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"success": True, "message": "앱을 종료합니다."}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    
                    # 즉시 종료 시도
                    def shutdown_app():
                        try:
                            logger.info("사용자 요청에 의해 앱을 종료합니다.")
                            import signal
                            import subprocess
                            import psutil
                            
                            # 현재 프로세스와 모든 자식 프로세스 종료
                            current_process = psutil.Process()
                            children = current_process.children(recursive=True)
                            
                            for child in children:
                                try:
                                    child.terminate()
                                except:
                                    pass
                            
                            # 2초 후 강제 종료
                            time.sleep(2)
                            for child in children:
                                try:
                                    child.kill()
                                except:
                                    pass
                            
                            # 메인 프로세스 종료
                            os._exit(0)
                            
                        except Exception as e:
                            logger.error(f"앱 종료 중 오류: {e}")
                            # 강제 종료
                            os._exit(1)
                    
                    threading.Thread(target=shutdown_app, daemon=True).start()
                    
                except Exception as e:
                    logger.error(f"Shutdown API 오류: {e}")
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"success": False, "message": f"앱 종료 실패: {e}"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"POST 요청 처리 중 오류: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_OPTIONS(self):
        """CORS preflight 요청 처리"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_modules_status(self):
        """모듈 실행 상태 확인"""
        # 실제 모듈 상태 확인 로직 (임시)
        return {
            "modules": {
                "chat": {"running": False},
                "spotify": {"running": False}
            }
        }
    
    def get_admin_panel_html(self):
        """테마별 관리자 패널 HTML 로드"""
        try:
            from config import CONFIG_MANAGER
            config = CONFIG_MANAGER.get_config()
            current_theme = config.get('ui', {}).get('admin_theme', 'neon')
            
            if current_theme == "neon" or current_theme == "default":
                # Neon 테마 UI 사용
                import sys
                import os
                neon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'neon')
                if neon_dir not in sys.path:
                    sys.path.insert(0, neon_dir)
                
                try:
                    from neon_admin_ui import get_neon_admin_template
                    return get_neon_admin_template()
                except ImportError as e:
                    logger.warning(f"Neon 관리자 UI를 불러올 수 없습니다: {e}. 기본 UI를 사용합니다.")
            
            # 기본 UI (간단한 백업)
            return self.get_default_admin_html()
            
        except Exception as e:
            logger.error(f"관리자 패널 HTML 로드 중 오류: {e}")
            return self.get_default_admin_html()
    
    def get_default_admin_html(self):
        """기본 관리자 패널 HTML (백업)"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>관리자 패널</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #333; }
        .card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        input, select { padding: 8px; margin: 5px 0; width: 100%; max-width: 300px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>스트리밍 컨트롤 센터</h1>
        <div class="card">
            <h2>설정</h2>
            <p>관리자 패널이 정상적으로 작동 중입니다.</p>
            <button class="btn-primary" onclick="location.reload()">새로고침</button>
        </div>
    </div>
</body>
</html>"""


class AdminPanelManager:
    """관리자 패널 매니저"""
    
    def __init__(self, port=8081):
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False
    
    def start(self):
        """관리자 패널 서버 시작"""
        if self.is_running:
            logger.warning("관리자 패널이 이미 실행 중입니다.")
            return
        
        try:
            self.server = HTTPServer(('localhost', self.port), AdminPanelLogicHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self.is_running = True
            logger.info(f"관리자 패널이 포트 {self.port}에서 실행 중입니다.")
        except Exception as e:
            logger.error(f"관리자 패널 시작 실패: {e}")
    
    def stop(self):
        """관리자 패널 서버 중지"""
        if self.server and self.is_running:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            logger.info("관리자 패널이 중지되었습니다.")
    
    def get_url(self):
        """관리자 패널 URL 반환"""
        return f"http://localhost:{self.port}/admin" 