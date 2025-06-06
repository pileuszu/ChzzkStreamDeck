#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChzzkStreamDeck PyInstaller 빌드 스크립트
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from build_config import BuildConfig

def install_build_deps():
    """빌드에 필요한 의존성 설치"""
    print("📦 빌드 의존성 설치 중...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("✅ PyInstaller 설치 완료")
    except subprocess.CalledProcessError:
        print("❌ PyInstaller 설치 실패")
        return False
    return True

def create_spec_file():
    """PyInstaller spec 파일 생성"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('neon', 'neon'),
        ('purple', 'purple'),
        ('main', 'main'),
        ('requirements.txt', '.'),
        ('config_build.json', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'websockets',
        'aiohttp',
        'requests',
        'pywebview',
        'psutil',
        'asyncio',
        'threading',
        'json',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChzzkStreamDeck',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('ChzzkStreamDeck.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("📄 PyInstaller spec 파일 생성됨")

def build_executable():
    """실행 파일 빌드"""
    print("🔨 실행 파일 빌드 시작...")
    
    try:
        # 빌드 전 정리
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        # PyInstaller 실행
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--log-level=INFO',
            'ChzzkStreamDeck.spec'
        ]
        
        print("📋 빌드 명령어:", ' '.join(cmd))
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # 빌드 결과 확인
        exe_path = Path('dist/ChzzkStreamDeck.exe')
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ 빌드 성공! 파일 크기: {file_size:.1f}MB")
            
            # 간단한 실행 테스트
            print("🧪 빌드된 파일 테스트 중...")
            test_result = subprocess.run([str(exe_path), '--version'], 
                                       capture_output=True, text=True, timeout=10)
            if test_result.returncode == 0:
                print("✅ 빌드된 파일이 정상적으로 실행됩니다")
            else:
                print("⚠️  빌드된 파일 테스트에서 경고가 있습니다")
                
        else:
            print("❌ 실행 파일이 생성되지 않았습니다")
            return False
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")
        print(f"표준 출력: {e.stdout}")
        print(f"오류 출력: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  빌드된 파일 테스트 시간 초과 (정상일 수 있음)")
        return True
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def create_release_package():
    """릴리스 패키지 생성"""
    print("📦 릴리스 패키지 생성 중...")
    
    # 릴리스 디렉토리 생성
    release_dir = Path('release')
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 실행 파일 복사
    exe_path = Path('dist/ChzzkStreamDeck.exe')
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / 'ChzzkStreamDeck.exe')
    else:
        # Linux/Mac의 경우
        exe_path = Path('dist/ChzzkStreamDeck')
        if exe_path.exists():
            shutil.copy2(exe_path, release_dir / 'ChzzkStreamDeck')
    
    # 설정 파일 복사
    config_files = ['config_build.json', 'README.md', 'check_system.py']
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, release_dir / config_file)
    
    # 사용자 가이드 생성
    user_guide = """# ChzzkStreamDeck 사용 가이드

## 🎮 첫 실행 설정

1. **ChzzkStreamDeck.exe** 실행
2. 관리패널이 자동으로 열림
3. 다음 정보를 입력하세요:

### 📺 채팅 모듈 설정
- **채널 ID**: 치지직 채널 ID 입력
- **최대 메시지 수**: 화면에 표시할 채팅 개수 (기본값: 10)

### 🎵 Spotify 모듈 설정  
- **클라이언트 ID**: Spotify 앱의 클라이언트 ID
- **클라이언트 Secret**: Spotify 앱의 클라이언트 시크릿
- **설정 저장** 후 **Spotify 인증** 버튼 클릭

## 🔧 Spotify 개발자 앱 설정

1. https://developer.spotify.com/dashboard 접속
2. 새 앱 생성
3. **Redirect URIs**에 추가: `http://localhost:8080/spotify/callback`
   (포트를 변경했다면 해당 포트 사용)

## ⚠️ 주의사항

- 첫 실행 시 Windows Defender에서 경고가 나올 수 있습니다
- "추가 정보" → "실행" 클릭하여 실행하세요
- 방화벽에서 접근 허용이 필요할 수 있습니다

## 🆘 문제 해결

- 포트 충돌 시: 다른 포트로 실행하거나 기존 프로그램 종료
- 인증 실패 시: Spotify 앱 설정 재확인
- 채팅 안 보임: 채널 ID 정확성 확인

## 📞 지원

GitHub Issues: https://github.com/your-repo/ChzzkStreamDeck/issues
"""
    
    with open(release_dir / 'USER_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(user_guide)
    
    print(f"✅ 릴리스 패키지가 {release_dir} 폴더에 생성되었습니다")
    print("📁 포함된 파일:")
    for file in release_dir.iterdir():
        print(f"   - {file.name}")

def main():
    """메인 빌드 프로세스"""
    print("🏗️  ChzzkStreamDeck 빌드 시작")
    print("=" * 50)
    
    # 1. 빌드 설정
    print("1️⃣ 빌드 설정 생성")
    build_config = BuildConfig()
    build_config.select_port()
    build_config.save_build_config()
    
    # 2. 빌드 의존성 설치
    print("\n2️⃣ 빌드 의존성 설치")
    if not install_build_deps():
        print("❌ 빌드 중단")
        return
    
    # 3. spec 파일 생성
    print("\n3️⃣ PyInstaller 설정 생성")
    create_spec_file()
    
    # 4. 실행 파일 빌드
    print("\n4️⃣ 실행 파일 빌드")
    if not build_executable():
        print("❌ 빌드 중단")
        return
    
    # 5. 릴리스 패키지 생성
    print("\n5️⃣ 릴리스 패키지 생성")
    create_release_package()
    
    print("\n🎉 빌드 완료!")
    print("📦 release 폴더에서 배포 파일을 확인하세요")

if __name__ == "__main__":
    main() 