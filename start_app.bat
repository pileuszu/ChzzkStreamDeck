@echo off
chcp 65001 >nul
title ChzzkStreamDeck 시작 중...
cls

:: 색상 설정 (Windows 10 이상)
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%VERSION%" geq "10.0" (
    :: ANSI 색상 지원 활성화 (Windows 10 이상)
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1
)

echo.
echo [96m===========================================[0m
echo [95m   🎮 ChzzkStreamDeck 시작 중...[0m
echo [96m===========================================[0m
echo.

:: 현재 디렉토리 정보 표시
echo [94m📁 작업 디렉토리: %CD%[0m
echo.

:: 실행 파일 경로 확인
if exist "ChzzkStreamDeck.exe" (
    echo [92m✅ 실행 파일 확인됨: ChzzkStreamDeck.exe[0m
    echo [93m🚀 앱 시작 중... (첫 실행 시 시간이 걸릴 수 있습니다)[0m
    echo.
    
    :: 실행 파일이 있는 경우 (빌드된 버전) - 앱 모드로 실행
    echo [94m🚀 실행 파일 시작 중...[0m
    echo [96m💡 데스크톱 앱 모드로 관리패널이 열립니다[0m
    echo [93m💡 만약 앱이 열리지 않으면 브라우저에서 관리패널에 접속하세요[0m
    echo.
    
    :: 화면 갱신 문제 해결을 위한 추가 설정
    echo [94m🔄 터미널 설정 최적화 중...[0m
    mode con cols=100 lines=30
    
    "ChzzkStreamDeck.exe" --app
    
    :: 종료 후 상태 확인
    if %ERRORLEVEL% EQU 0 (
        echo [92m🏁 앱이 정상적으로 종료되었습니다.[0m
    ) else (
        echo [91m⚠️  앱이 오류와 함께 종료되었습니다. (코드: %ERRORLEVEL%)[0m
    )
    
) else if exist "main.py" (
    echo [93m⚠️  실행 파일을 찾을 수 없습니다. 개발 모드로 실행합니다.[0m
    echo.
    
    :: Python 설치 확인
    python --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [91m❌ Python이 설치되지 않았습니다![0m
        echo [93m💡 Python 3.8+ 설치 후 다시 실행해주세요.[0m
        echo [93m📥 다운로드: https://www.python.org/downloads/[0m
        pause
        exit /b 1
    )
    
    :: Python 버전 확인
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [94m🐍 Python 버전: %PYTHON_VERSION%[0m
    
    :: 가상환경 활성화 (있는 경우)
    if exist ".venv\Scripts\activate.bat" (
        echo [96m🔧 가상환경 활성화 중...[0m
        call .venv\Scripts\activate.bat
        echo [92m✅ 가상환경 활성화됨[0m
    )
    
    :: 시스템 요구사항 체크
    if exist "check_system.py" (
        echo [96m🔍 시스템 요구사항 확인 중...[0m
        python check_system.py
        if errorlevel 1 (
            echo.
            echo [91m❌ 시스템 요구사항을 충족하지 않습니다.[0m
            echo [93m💡 위의 가이드를 따라 Python을 설치하세요.[0m
            pause
            exit /b 1
        )
        echo [92m✅ 시스템 요구사항 충족[0m
    )
    
    :: 의존성 설치 확인
    if exist "requirements.txt" (
        echo [96m📦 필요한 패키지 확인 중...[0m
        python -m pip install -r requirements.txt --quiet --disable-pip-version-check
        if %ERRORLEVEL% EQU 0 (
            echo [92m✅ 패키지 확인 완료[0m
        ) else (
            echo [93m⚠️  일부 패키지 설치에 문제가 있을 수 있습니다.[0m
        )
    )
    
    :: 화면 갱신 문제 해결을 위한 설정
    echo [96m🔄 터미널 설정 최적화 중...[0m
    mode con cols=100 lines=30
    
    :: Python으로 실행
    echo.
    echo [94m🚀 Python으로 실행 중...[0m
    python main.py --app
    
) else (
    echo [91m❌ 실행할 파일을 찾을 수 없습니다![0m
    echo.
    echo [93m📋 해결 방법:[0m
    echo [96m   1. ChzzkStreamDeck.exe가 같은 폴더에 있는지 확인[0m
    echo [96m   2. 압축 파일을 올바르게 해제했는지 확인[0m  
    echo [96m   3. 또는 main.py가 있는 소스 코드 폴더에서 실행[0m
    echo.
    pause
    exit /b 1
)

echo.
echo [92m🎉 ChzzkStreamDeck이 실행되었습니다![0m
echo [96m📱 관리패널: 화면에 표시된 URL을 확인하세요[0m
echo.
echo [93m💡 앱을 종료하려면 이 창을 닫거나 Ctrl+C를 누르세요[0m
echo [93m💡 터미널 갱신 문제가 있다면 Git Bash 스크립트를 사용하세요:[0m
echo [96m    ./start_app_gitbash.sh[0m
echo [96m============================================[0m

:: 사용자가 창을 닫을 때까지 대기
echo.
echo [94m🔄 앱이 백그라운드에서 실행 중입니다...[0m
echo [93m💡 Git Bash로 실행하려면: ./start_app_gitbash.sh[0m
pause >nul 