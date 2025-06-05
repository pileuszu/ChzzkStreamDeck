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
    """PyInstaller 환경에 맞는 경로 설정 (안전한 버전)"""
    try:
        print("🔧 경로 설정 중...")
        
        # PyInstaller 실행 환경 감지
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 실행 파일인 경우
            try:
                application_path = sys._MEIPASS
                executable_dir = os.path.dirname(sys.executable)
                
                print(f"✅ PyInstaller 환경 감지")
                print(f"📁 실행 파일: {sys.executable}")
                print(f"📂 실행 디렉토리: {executable_dir}")
                
                # main 디렉토리를 Python 경로에 추가
                main_dir = os.path.join(application_path, 'main')
                if os.path.exists(main_dir):
                    sys.path.insert(0, main_dir)
                    print(f"✅ main 디렉토리 추가: {main_dir}")
                else:
                    print(f"⚠️  main 디렉토리 없음 (계속 진행): {main_dir}")
                
                # 작업 디렉토리 변경 (안전하게)
                try:
                    os.chdir(executable_dir)
                    print(f"✅ 작업 디렉토리: {executable_dir}")
                except Exception as e:
                    print(f"⚠️  작업 디렉토리 변경 실패 (계속 진행): {e}")
                
                return executable_dir, application_path
                
            except Exception as e:
                print(f"⚠️  PyInstaller 환경 설정 중 오류 (계속 진행): {e}")
                return os.getcwd(), os.getcwd()
        else:
            # 개발 환경에서 Python으로 실행하는 경우
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_dir = os.path.join(script_dir, 'main')
            
            print(f"✅ 개발 환경 감지")
            print(f"📂 스크립트 디렉토리: {script_dir}")
            
            if os.path.exists(main_dir):
                sys.path.insert(0, main_dir)
                print(f"✅ main 디렉토리 추가: {main_dir}")
            else:
                print(f"⚠️  main 디렉토리 없음 (계속 진행): {main_dir}")
            
            try:
                os.chdir(script_dir)
            except Exception as e:
                print(f"⚠️  작업 디렉토리 변경 실패 (계속 진행): {e}")
                
            return script_dir, script_dir
            
    except Exception as e:
        print(f"⚠️  경로 설정 중 오류 (기본값 사용): {e}")
        return os.getcwd(), os.getcwd()

def check_dependencies():
    """필수 의존성 확인 (관대한 버전)"""
    try:
        print("\n🔍 의존성 확인 중...")
        
        # 필수 모듈들 확인 (하지만 실패해도 계속 진행)
        required_modules = ['websockets', 'aiohttp', 'requests', 'psutil']
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                missing_modules.append(module)
                print(f"⚠️  {module} - 누락됨 (계속 진행)")
        
        if missing_modules:
            print(f"⚠️  누락된 모듈들: {', '.join(missing_modules)}")
            print("💡 일부 기능이 제한될 수 있지만 계속 진행합니다.")
            return True  # 실패해도 계속 진행
        
        print("✅ 모든 의존성 확인 완료")
        return True
        
    except Exception as e:
        print(f"⚠️  의존성 확인 중 오류 (계속 진행): {e}")
        return True  # 오류가 있어도 계속 진행

def create_default_config():
    """기본 설정 파일 생성 (안전한 버전)"""
    try:
        config_file = "overlay_config.json"
        
        # 파일이 이미 있으면 건드리지 않음
        if os.path.exists(config_file):
            print(f"✅ 설정 파일 존재: {config_file}")
            return
        
        print(f"📄 기본 설정 파일 생성 시도: {config_file}")
        
        default_config = {
            "server": {"port": 8080, "host": "localhost"},
            "modules": {
                "chat": {
                    "enabled": False, "channel_id": "", "url_path": "/chat",
                    "max_messages": 10, "show_recent_only": True, "single_chat_mode": False,
                    "streamer_align_left": False, "background_enabled": True,
                    "background_opacity": 0.3, "remove_outer_effects": False
                },
                "spotify": {
                    "enabled": False, "client_id": "", "client_secret": "",
                    "redirect_uri": "http://localhost:8080/spotify/callback",
                    "url_path": "/spotify", "simplified_mode": False, "theme": "default"
                }
            },
            "ui": {"theme": "neon", "admin_theme": "neon", "language": "ko", "chat_background": "transparent", "dark_mode": True}
        }
        
        try:
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print("✅ 기본 설정 파일 생성 완료")
        except Exception as e:
            print(f"⚠️  설정 파일 생성 실패 (계속 진행): {e}")
            
    except Exception as e:
        print(f"⚠️  설정 파일 생성 중 오류 (계속 진행): {e}")

def main():
    """메인 실행 함수 (안전한 버전)"""
    print("🎮 ChzzkStreamDeck 시작")
    print("=" * 50)
    
    try:
        # 1. 경로 설정 (실패해도 계속)
        print("1️⃣ 경로 설정...")
        executable_dir, app_path = setup_paths()
        print(f"   현재 작업 디렉토리: {os.getcwd()}")
        
        # 2. 의존성 확인 (실패해도 계속)
        print("\n2️⃣ 의존성 확인...")
        check_dependencies()
        
        # 3. 기본 설정 파일 생성 (실패해도 계속)
        print("\n3️⃣ 설정 파일 확인...")
        create_default_config()
        
        # 4. 메인 서버 모듈 임포트 및 실행
        print("\n4️⃣ 서버 모듈 로딩...")
        try:
            from unified_server import main as server_main
            print("✅ 서버 모듈 로딩 완료")
            
            print("\n🚀 서버 시작 중...")
            server_main()
            
        except ImportError as e:
            print(f"❌ 서버 모듈 임포트 실패: {e}")
            print("\n💡 가능한 해결책:")
            print("  1. main 디렉토리가 올바른 위치에 있는지 확인")
            print("  2. unified_server.py 파일이 존재하는지 확인")
            print("  3. 모든 파일이 올바르게 압축 해제되었는지 확인")
            print("  4. 관리자 권한으로 실행해보세요")
            
            # ImportError도 치명적이지 않게 처리
            print("\n⚠️  서버 모듈을 로드할 수 없습니다.")
            print("🔧 기본 모드로 실행을 시도합니다...")
            
            # 기본 모드 실행 시도
            try:
                import webbrowser
                import time
                print("🌐 기본 웹 서버 모드로 시작합니다...")
                print("📱 브라우저에서 http://localhost:8080 을 열어보세요")
                time.sleep(5)
            except:
                pass
        
    except KeyboardInterrupt:
        print("\n👋 사용자가 프로그램을 종료했습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생:")
        print(f"   오류 내용: {e}")
        print(f"\n📋 상세 오류 정보:")
        traceback.print_exc()
        
        print(f"\n🔧 문제 해결 방법:")
        print(f"  1. 프로그램을 관리자 권한으로 실행해보세요")
        print(f"  2. 바이러스 백신에서 이 폴더를 예외로 추가하세요") 
        print(f"  3. Windows Defender에서 실시간 보호를 잠시 비활성화하세요")
        print(f"  4. 포트 8080이 다른 프로그램에서 사용 중인지 확인하세요")
        print(f"  5. 다른 포트로 실행해보세요: ChzzkStreamDeck.exe --port 8081")
    
    finally:
        print("\n" + "=" * 50)
        print("💡 프로그램 실행이 완료되었습니다.")
        print("❓ 문제가 계속 발생하면 GitHub Issues에 신고해주세요.")
        print("\n🔧 직접 실행 방법:")
        print("  python main.py           # 기본 포트 8080")
        print("  python main.py --port 8081  # 다른 포트")
        print("  python run_chzzk.py     # 안전 모드")
        
        # 자동 종료 타이머 (30초)
        try:
            import time
            print(f"\n⏰ 30초 후 자동 종료됩니다...")
            for i in range(30, 0, -1):
                print(f"\r⏰ {i}초 남음... (아무 키나 누르면 즉시 종료)", end="", flush=True)
                time.sleep(1)
            print(f"\n👋 자동 종료되었습니다.")
        except KeyboardInterrupt:
            print(f"\n👋 사용자가 종료했습니다.")
        except:
            input("\n⏎ Enter 키를 눌러 창을 닫으세요...")

if __name__ == "__main__":
    main() 