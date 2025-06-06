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

echo [96m===========================================[0m
echo [95m   🎮 ChzzkStreamDeck 백그라운드 실행[0m
echo [96m===========================================[0m
echo.

:: 현재 디렉토리 정보 표시
echo [94m📁 작업 디렉토리: %CD%[0m
echo.

:: 실행 파일 경로 확인
if exist "ChzzkStreamDeck.exe" (
    echo [92m✅ 실행 파일 확인됨: ChzzkStreamDeck.exe[0m
    echo [96m🚀 백그라운드에서 서버 시작 중...[0m
    echo.
    
    :: 기존 프로세스 종료
    echo [93m🔄 기존 프로세스 정리 중...[0m
    taskkill /f /im ChzzkStreamDeck.exe >nul 2>&1
    timeout /t 2 >nul
    
    :: 백그라운드에서 실행 파일 시작
    echo [94m🌐 서버를 백그라운드에서 시작합니다...[0m
    start /min "ChzzkStreamDeck Server" "ChzzkStreamDeck.exe" --app
    
    :: 서버 시작 대기
    echo [93m⏳ 서버 시작 대기 중... (5초)[0m
    timeout /t 5 >nul
    
    :: 상태 확인 및 URL 열기
    echo [92m✅ 서버가 백그라운드에서 실행 중입니다![0m
    echo.
    echo [96m📱 관리패널을 브라우저에서 열기 중...[0m
    start http://localhost:8080/admin
    
    echo.
    echo [96m===================== 실행 상태 =====================[0m
    echo [92m🌐 서버 URL: http://localhost:8080[0m
    echo [92m🎮 관리패널: http://localhost:8080/admin[0m
    echo [92m💬 채팅 오버레이: http://localhost:8080/chat/overlay[0m
    echo [92m🎵 Spotify 오버레이: http://localhost:8080/spotify/overlay[0m
    echo [96m================================================[0m
    echo.
    echo [93m💡 서버는 백그라운드에서 계속 실행됩니다.[0m
    echo [93m💡 종료하려면 시스템 트레이에서 종료하거나[0m
    echo [93m   작업 관리자에서 ChzzkStreamDeck.exe를 종료하세요.[0m
    echo.
    
    :: 상태 모니터링 옵션 제공
    echo [94m🔍 실시간 상태를 모니터링하시겠습니까? (Y/N)[0m
    set /p "monitor=선택: "
    
    if /i "%monitor%"=="Y" (
        goto :monitor_mode
    ) else (
        echo [92m✅ 백그라운드 실행 완료! 이 창을 닫아도 됩니다.[0m
        echo.
        pause
        exit /b 0
    )
    
) else if exist "main.py" (
    echo [93m⚠️  실행 파일을 찾을 수 없습니다. 개발 모드로 실행합니다.[0m
    echo.
    
    :: Python 설치 확인
    python --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [91m❌ Python이 설치되지 않았습니다![0m
        echo [93m💡 Python 3.8+ 설치 후 다시 실행해주세요.[0m
        pause
        exit /b 1
    )
    
    :: 가상환경 활성화 (있는 경우)
    if exist ".venv\Scripts\activate.bat" (
        echo [96m🔧 가상환경 활성화 중...[0m
        call .venv\Scripts\activate.bat
    )
    
    :: 백그라운드에서 Python 실행
    echo [94m🚀 Python 백그라운드 실행 중...[0m
    start /min "ChzzkStreamDeck Python" python main.py --app
    
    :: 서버 시작 대기
    timeout /t 5 >nul
    
    :: 관리패널 열기
    start http://localhost:8080/admin
    
    echo [92m✅ 개발 모드로 백그라운드 실행 완료![0m
    pause
    exit /b 0
    
) else (
    echo [91m❌ 실행할 파일을 찾을 수 없습니다![0m
    echo.
    echo [93m📋 해결 방법:[0m
    echo [96m   1. ChzzkStreamDeck.exe가 같은 폴더에 있는지 확인[0m
    echo [96m   2. 압축 파일을 올바르게 해제했는지 확인[0m
    echo.
    pause
    exit /b 1
)

:monitor_mode
cls
title ChzzkStreamDeck 상태 모니터링
echo [96m===========================================[0m
echo [95m   🎮 ChzzkStreamDeck 상태 모니터링[0m
echo [96m===========================================[0m
echo.

:monitor_loop
:: 프로세스 상태 확인
tasklist /fi "imagename eq ChzzkStreamDeck.exe" 2>nul | find /i "ChzzkStreamDeck.exe" >nul
if %errorlevel%==0 (
    echo [92m✅ %date% %time% - 서버 실행 중[0m
) else (
    echo [91m❌ %date% %time% - 서버가 중단되었습니다![0m
    echo [93m🔄 서버를 다시 시작하시겠습니까? (Y/N)[0m
    set /p "restart=선택: "
    if /i "%restart%"=="Y" (
        start /min "ChzzkStreamDeck Server" "ChzzkStreamDeck.exe" --app
        echo [94m🚀 서버 재시작 중...[0m
        timeout /t 3 >nul
    ) else (
        echo [93m👋 모니터링을 종료합니다.[0m
        pause
        exit /b 0
    )
)

:: 포트 상태 확인
netstat -an | find "8080" | find "LISTENING" >nul
if %errorlevel%==0 (
    echo [92m🌐 %date% %time% - 포트 8080 활성화[0m
) else (
    echo [93m⚠️  %date% %time% - 포트 8080 확인 중...[0m
)

echo [94m💡 Ctrl+C로 모니터링 종료 | Enter로 새로고침[0m
echo.

:: 5초 대기 (사용자가 Enter를 누르면 즉시 새로고침)
timeout /t 5 >nul
goto :monitor_loop 