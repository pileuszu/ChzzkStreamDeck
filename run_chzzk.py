#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChzzkStreamDeck 안전 실행 래퍼
exe가 바로 꺼지는 문제 해결용
"""

import os
import sys
import time
import traceback
import subprocess

def show_startup_info():
    """시작 정보 표시"""
    print("🎮 ChzzkStreamDeck 안전 실행 도구")
    print("=" * 60)
    print("📍 현재 경로:", os.getcwd())
    print("🐍 Python 버전:", sys.version)
    print("🖥️  시스템:", sys.platform)
    print("=" * 60)

def check_files():
    """필요한 파일들 확인"""
    print("\n📁 파일 확인 중...")
    
    required_files = ['main.py']
    optional_files = ['overlay_config.json', 'requirements.txt']
    
    missing_required = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_required.append(file)
            print(f"❌ {file} - 필수 파일 누락!")
    
    for file in optional_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"⚠️  {file} - 선택적 파일 (없어도 됨)")
    
    if missing_required:
        print(f"\n❌ 필수 파일 누락: {', '.join(missing_required)}")
        return False
    
    print("\n✅ 파일 확인 완료")
    return True

def check_python_modules():
    """파이썬 모듈 확인"""
    print("\n🔍 Python 모듈 확인 중...")
    
    modules = ['json', 'os', 'sys', 'time', 'traceback']
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    print("✅ 기본 모듈 확인 완료")
    return True

def safe_main_import():
    """안전한 main 모듈 임포트 및 실행"""
    print("\n🚀 메인 프로그램 시작...")
    
    try:
        # main.py가 현재 디렉토리에 있는지 확인
        if not os.path.exists('main.py'):
            print("❌ main.py 파일을 찾을 수 없습니다!")
            return False
        
        # main.py 실행
        print("📄 main.py 실행 중...")
        result = subprocess.run([sys.executable, 'main.py'] + sys.argv[1:], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ 프로그램이 정상적으로 완료되었습니다.")
            return True
        else:
            print(f"⚠️  프로그램이 오류 코드 {result.returncode}으로 종료되었습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        traceback.print_exc()
        return False

def main():
    """메인 실행 함수"""
    try:
        show_startup_info()
        
        # 시작 전 잠시 대기 (빠른 종료 방지)
        print("⏳ 시작 준비 중... (3초)")
        time.sleep(3)
        
        # 파일 확인
        if not check_files():
            print("\n❌ 필수 파일이 누락되어 실행할 수 없습니다.")
            input("\n⏎ Enter 키를 눌러 종료하세요...")
            return
        
        # 파이썬 모듈 확인  
        if not check_python_modules():
            print("\n❌ 필수 Python 모듈이 누락되어 실행할 수 없습니다.")
            input("\n⏎ Enter 키를 눌러 종료하세요...")
            return
        
        # 메인 프로그램 실행
        success = safe_main_import()
        
        if not success:
            print("\n⚠️  프로그램 실행 중 문제가 발생했습니다.")
            print("💡 해결책:")
            print("  1. 관리자 권한으로 실행해보세요")
            print("  2. 바이러스 백신 예외에 추가하세요")
            print("  3. 설정된 포트가 사용 중인지 확인하세요")
            print("  4. 다른 포트로 실행해보세요: python run_chzzk.py --port 8081 (또는 8082, 8083 등)")
        
    except KeyboardInterrupt:
        print("\n👋 사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
        traceback.print_exc()
    
    finally:
        print("\n" + "=" * 60)
        print("💡 ChzzkStreamDeck 실행 완료")  
        print("❓ 문제가 지속되면 GitHub Issues에 신고해주세요.")
        input("\n⏎ Enter 키를 눌러 창을 닫으세요...")

if __name__ == "__main__":
    main() 