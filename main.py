#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChzzkStreamDeck - 치지직 스트리밍 컨트롤 센터
빠른 시작을 위한 최적화된 메인 실행 파일
"""

import os
import sys
import traceback

def setup_paths():
    """PyInstaller 환경에 맞는 경로 설정"""
    try:
        # PyInstaller 실행 환경 감지
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 실행 파일인 경우
            application_path = sys._MEIPASS
            executable_dir = os.path.dirname(sys.executable)
            
            print(f"🔧 PyInstaller 환경 감지")
            print(f"📁 실행 파일 경로: {sys.executable}")
            print(f"📂 임시 디렉토리: {application_path}")
            print(f"📂 실행 디렉토리: {executable_dir}")
            
            # main 디렉토리를 Python 경로에 추가
            main_dir = os.path.join(application_path, 'main')
            if os.path.exists(main_dir):
                sys.path.insert(0, main_dir)
                print(f"✅ main 디렉토리 추가: {main_dir}")
            else:
                print(f"❌ main 디렉토리 없음: {main_dir}")
                
            # 작업 디렉토리를 실행 파일이 있는 디렉토리로 변경
            os.chdir(executable_dir)
            print(f"📍 작업 디렉토리 변경: {executable_dir}")
            
            return executable_dir, application_path
        else:
            # 개발 환경에서 Python으로 실행하는 경우
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_dir = os.path.join(script_dir, 'main')
            
            print(f"🐍 개발 환경 감지")
            print(f"📂 스크립트 디렉토리: {script_dir}")
            
            if os.path.exists(main_dir):
                sys.path.insert(0, main_dir)
                print(f"✅ main 디렉토리 추가: {main_dir}")
            else:
                print(f"❌ main 디렉토리 없음: {main_dir}")
            
            os.chdir(script_dir)
            return script_dir, script_dir
            
    except Exception as e:
        print(f"❌ 경로 설정 중 오류: {e}")
        traceback.print_exc()
        return None, None

def check_dependencies():
    """필수 의존성 확인"""
    try:
        print("🔍 의존성 확인 중...")
        
        # 필수 모듈들 확인
        required_modules = [
            'websockets', 'aiohttp', 'requests', 'psutil'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                missing_modules.append(module)
                print(f"❌ {module} - 누락")
        
        if missing_modules:
            print(f"⚠️  누락된 모듈들: {', '.join(missing_modules)}")
            return False
        
        print("✅ 모든 의존성 확인 완료")
        return True
        
    except Exception as e:
        print(f"❌ 의존성 확인 중 오류: {e}")
        return False

def create_default_config():
    """기본 설정 파일 생성"""
    try:
        config_file = "overlay_config.json"
        if not os.path.exists(config_file):
            print(f"📄 기본 설정 파일 생성: {config_file}")
            
            default_config = {
                "server": {
                    "port": 8080,
                    "host": "localhost"
                },
                "modules": {
                    "chat": {
                        "enabled": False,
                        "channel_id": "",
                        "url_path": "/chat",
                        "max_messages": 10,
                        "show_recent_only": True,
                        "single_chat_mode": False,
                        "streamer_align_left": False,
                        "background_enabled": True,
                        "background_opacity": 0.3,
                        "remove_outer_effects": False
                    },
                    "spotify": {
                        "enabled": False,
                        "client_id": "",
                        "client_secret": "",
                        "redirect_uri": "http://localhost:8080/spotify/callback",
                        "url_path": "/spotify",
                        "simplified_mode": False,
                        "theme": "default"
                    }
                },
                "ui": {
                    "theme": "neon",
                    "admin_theme": "neon",
                    "language": "ko",
                    "chat_background": "transparent",
                    "dark_mode": True
                }
            }
            
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            print("✅ 기본 설정 파일 생성 완료")
        else:
            print(f"✅ 설정 파일 존재: {config_file}")
            
    except Exception as e:
        print(f"❌ 설정 파일 생성 중 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🎮 ChzzkStreamDeck 시작")
    print("=" * 50)
    
    try:
        # 1. 경로 설정
        executable_dir, app_path = setup_paths()
        if not executable_dir:
            raise Exception("경로 설정 실패")
        
        # 2. 의존성 확인
        if not check_dependencies():
            raise Exception("필수 의존성 누락")
        
        # 3. 기본 설정 파일 생성
        create_default_config()
        
        # 4. 메인 서버 모듈 임포트 및 실행
        print("🚀 서버 모듈 로딩 중...")
        try:
            from unified_server import main as server_main
            print("✅ 서버 모듈 로딩 완료")
            
            print("🌐 서버 시작 중...")
            server_main()
            
        except ImportError as e:
            print(f"❌ 서버 모듈 임포트 실패: {e}")
            print("💡 해결책:")
            print("  1. main 디렉토리가 올바른 위치에 있는지 확인")
            print("  2. unified_server.py 파일이 존재하는지 확인")
            print("  3. 모든 파일이 올바르게 압축 해제되었는지 확인")
            raise
        
    except KeyboardInterrupt:
        print("\n👋 사용자가 프로그램을 종료했습니다.")
    except Exception as e:
        print(f"\n❌ 실행 중 오류 발생:")
        print(f"   오류 내용: {e}")
        print(f"\n📋 상세 오류 정보:")
        traceback.print_exc()
        
        print(f"\n🔧 문제 해결 방법:")
        print(f"  1. 프로그램을 관리자 권한으로 실행해보세요")
        print(f"  2. 바이러스 백신에서 이 폴더를 예외로 추가하세요") 
        print(f"  3. Windows Defender에서 실시간 보호를 잠시 비활성화하세요")
        print(f"  4. 포트 8080이 다른 프로그램에서 사용 중인지 확인하세요")
    
    finally:
        print("\n" + "=" * 50)
        print("프로그램이 종료됩니다.")
        input("Enter 키를 눌러 창을 닫으세요...")

if __name__ == "__main__":
    main() 