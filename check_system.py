#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChzzkStreamDeck 시스템 요구사항 체크
Python 버전 확인 및 설치 가이드 제공
"""

import sys
import os
import subprocess
import platform

def check_python_version():
    """Python 버전 확인"""
    print("🐍 Python 버전 확인 중...")
    
    current_version = sys.version_info
    required_version = (3, 7)
    recommended_version = (3, 13, 3)
    
    print(f"✅ 현재 Python 버전: {current_version.major}.{current_version.minor}.{current_version.micro}")
    
    if current_version >= recommended_version:
        print(f"✅ 권장 버전 ({recommended_version[0]}.{recommended_version[1]}.{recommended_version[2]}) 이상입니다!")
        return True
    elif current_version >= required_version:
        print(f"⚠️  최소 요구사항 ({required_version[0]}.{required_version[1]}) 이상이지만 권장 버전으로 업데이트를 고려하세요.")
        return True
    else:
        print(f"❌ Python {required_version[0]}.{required_version[1]} 이상이 필요합니다!")
        return False

def check_pip():
    """pip 설치 확인"""
    print("\n📦 pip 패키지 관리자 확인 중...")
    try:
        import pip
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pip 사용 가능: {result.stdout.strip()}")
            return True
        else:
            print("❌ pip 실행 실패")
            return False
    except ImportError:
        print("❌ pip이 설치되지 않았습니다!")
        return False

def show_python_install_guide():
    """Python 설치 가이드 표시"""
    system = platform.system()
    
    print("\n" + "="*60)
    print("🔧 Python 설치 가이드")
    print("="*60)
    
    if system == "Windows":
        print("""
🪟 Windows 설치:
1. https://www.python.org/downloads/ 접속
2. 최신 Python 3.13.x 다운로드
3. 설치 시 '✅ Add Python to PATH' 체크박스 반드시 선택!
4. Install Now 클릭
5. 설치 완료 후 CMD에서 'python --version' 확인

📥 직접 다운로드:
   https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe
        """)
    
    elif system == "Darwin":  # macOS
        print("""
🍎 macOS 설치:
1. Homebrew 설치 (없는 경우):
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
2. Python 설치:
   brew install python@3.13
   
3. 또는 공식 사이트에서 다운로드:
   https://www.python.org/downloads/macos/
        """)
    
    elif system == "Linux":
        print("""
🐧 Linux 설치:

Ubuntu/Debian:
   sudo apt update
   sudo apt install python3.13 python3.13-pip python3.13-venv

CentOS/RHEL/Fedora:
   sudo dnf install python3.13 python3.13-pip

Arch Linux:
   sudo pacman -S python python-pip
        """)
    
    print("\n⚠️  설치 후 터미널/CMD를 재시작하고 다시 실행하세요!")

def check_dependencies():
    """필수 의존성 패키지 확인"""
    print("\n📋 필수 패키지 확인 중...")
    
    required_packages = [
        'websockets',
        'aiohttp', 
        'requests',
        'pywebview',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (누락)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 누락된 패키지 설치:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_port_availability(port=8080):
    """포트 사용 가능 여부 확인"""
    print(f"\n🔌 포트 {port} 사용 가능 여부 확인 중...")
    
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print(f"✅ 포트 {port} 사용 가능")
            return True
    except OSError:
        print(f"❌ 포트 {port} 이미 사용 중")
        
        # 대안 포트 제안
        alternative_ports = [8081, 8082, 8083, 8090, 9000]
        for alt_port in alternative_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', alt_port))
                    print(f"💡 대안 포트: {alt_port} 사용 가능")
                    return alt_port
            except OSError:
                continue
        
        print("❌ 사용 가능한 대안 포트를 찾을 수 없습니다.")
        return False

def main():
    """메인 시스템 체크 함수"""
    print("🔍 ChzzkStreamDeck 시스템 요구사항 체크")
    print("="*60)
    
    all_checks_passed = True
    
    # Python 버전 체크
    if not check_python_version():
        all_checks_passed = False
        show_python_install_guide()
        return False
    
    # pip 체크
    if not check_pip():
        all_checks_passed = False
        print("\n💡 pip 설치 방법:")
        print("curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
        print("python get-pip.py")
    
    # 의존성 체크 (선택적)
    print("\n" + "="*60)
    print("📦 의존성 패키지 체크 (선택적)")
    print("="*60)
    dependencies_ok = check_dependencies()
    
    if not dependencies_ok:
        print("\n💡 의존성 설치:")
        print("pip install -r requirements.txt")
    
    # 포트 체크
    available_port = check_port_availability()
    
    # 최종 결과
    print("\n" + "="*60)
    print("📋 시스템 체크 결과")
    print("="*60)
    
    if all_checks_passed:
        print("✅ 모든 필수 요구사항이 충족되었습니다!")
        print("🚀 ChzzkStreamDeck을 실행할 수 있습니다.")
        
        if not dependencies_ok:
            print("\n⚠️  의존성 패키지를 먼저 설치하세요:")
            print("pip install -r requirements.txt")
        
        if available_port != True:
            if isinstance(available_port, int):
                print(f"\n💡 포트 충돌이 있습니다. --port {available_port} 옵션을 사용하세요.")
        
        return True
    else:
        print("❌ 시스템 요구사항이 충족되지 않았습니다.")
        print("위의 가이드에 따라 Python을 설치한 후 다시 시도하세요.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            input("\n아무 키나 눌러 종료...")
            sys.exit(1)
        else:
            print("\n✅ 시스템 체크 완료!")
    except KeyboardInterrupt:
        print("\n\n❌ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 시스템 체크 중 오류 발생: {e}")
        input("\n아무 키나 눌러 종료...")
        sys.exit(1) 