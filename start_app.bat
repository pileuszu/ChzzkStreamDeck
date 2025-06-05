@echo off
chcp 65001 >nul
setlocal

echo ====================================
echo 🎮 치지직 스트림덱 컨트롤러 시작
echo ====================================
echo.

rem 시스템 요구사항 체크
echo 🔍 시스템 요구사항 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 오류: Python이 설치되지 않았습니다.
    echo.
    echo 📋 Python 설치 가이드:
    echo 1. https://www.python.org/downloads/ 접속
    echo 2. Python 3.13.x 다운로드
    echo 3. 설치 시 "Add Python to PATH" 체크박스 선택
    echo 4. 설치 완료 후 이 스크립트 다시 실행
    echo.
    echo 💡 또는 check_system.py를 실행하여 상세한 가이드 확인
    echo.
    pause
    exit /b 1
)

rem 상세 시스템 체크 (선택적)
if exist "check_system.py" (
    echo 🔍 상세 시스템 체크 실행 중...
    python check_system.py
    if errorlevel 1 (
        echo.
        echo ⚠️  시스템 체크에서 문제가 발견되었습니다.
        echo    계속 진행하시겠습니까? ^(Y/N^)
        set /p CONTINUE="계속: "
        if /i not "%CONTINUE%"=="Y" (
            echo 설치를 중단합니다.
            pause
            exit /b 1
        )
    )
)

rem Python 버전 확인
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% 확인됨

rem 프로젝트 디렉토리 확인
if not exist "main" (
    echo ❌ 오류: main 폴더를 찾을 수 없습니다.
    echo    이 스크립트를 프로젝트 루트에서 실행해주세요.
    echo.
    pause
    exit /b 1
)

if not exist "main.py" (
    echo ❌ 오류: main.py 파일을 찾을 수 없습니다.
    echo.
    pause
    exit /b 1
)

rem 가상환경 확인 및 생성
if not exist ".venv" (
    echo 🔨 가상환경 생성 중...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 가상환경 생성 실패
        pause
        exit /b 1
    )
    echo ✅ 가상환경 생성 완료
) else (
    echo ✅ 가상환경 확인됨
)

rem 가상환경 활성화
echo 🐍 가상환경 활성화...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 가상환경 활성화 실패
    pause
    exit /b 1
)

rem 의존성 설치
echo 📦 의존성 패키지 확인 및 설치...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo ❌ 패키지 설치 실패
    echo.
    echo 수동으로 설치해보세요:
    echo pip install flask flask-socketio requests beautifulsoup4 psutil pywebview
    echo.
    pause
    exit /b 1
)

echo ✅ 모든 준비 완료

rem 현재 배치 파일의 PID 저장 (종료 처리용)
set BATCH_PID=%RANDOM%

echo.
echo 🚀 스트리밍 컨트롤 센터 시작...
echo.
echo 💡 사용법:
echo    - 관리패널에서 '앱 종료' 버튼으로 완전 종료
echo    - 또는 이 창에서 Ctrl+C로 강제 종료
echo    - 창을 최소화하지 마세요 (성능 저하 방지)
echo.
echo 🔧 프로세스 ID: %BATCH_PID%
echo ====================================
echo.

rem 메인 애플리케이션 실행
python main.py --app

rem 앱이 정상 종료된 경우
echo.
echo 🏁 앱이 정상 종료되었습니다.
echo.

rem 프로세스 정리
echo 🧹 프로세스 정리 중...
taskkill /f /im python.exe /fi "commandline eq *main.py*" 2>nul >nul
taskkill /f /im pythonw.exe /fi "commandline eq *main.py*" 2>nul >nul

echo ✅ 정리 완료
echo.
echo 👋 3초 후 창이 자동으로 닫힙니다...
timeout /t 3 /nobreak >nul

exit /b 0 