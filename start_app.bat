@echo off
chcp 65001 >nul
title ChzzkStreamDeck 시작 중...

echo.
echo ==========================================
echo   🎮 ChzzkStreamDeck 시작 중...
echo ==========================================
echo.

REM 실행 파일 경로 확인
if exist "ChzzkStreamDeck.exe" (
    echo ✅ 실행 파일 확인됨: ChzzkStreamDeck.exe
    echo 🚀 앱 시작 중... (첫 실행 시 시간이 걸릴 수 있습니다)
    echo.
    
    REM 실행 파일이 있는 경우 (빌드된 버전)
    start "" "ChzzkStreamDeck.exe"
    
    echo 📱 브라우저에서 관리패널이 자동으로 열립니다
    echo 💡 만약 열리지 않으면 http://localhost:8080/admin 접속하세요
    
) else if exist "main.py" (
    echo ⚠️  실행 파일을 찾을 수 없습니다. 개발 모드로 실행합니다.
    echo.
    
    REM 시스템 요구사항 체크
    echo 🔍 시스템 요구사항 확인 중...
    
    if exist "check_system.py" (
        python check_system.py
        if errorlevel 1 (
            echo.
            echo ❌ 시스템 요구사항을 충족하지 않습니다.
            echo 💡 위의 가이드를 따라 Python을 설치하세요.
            pause
            exit /b 1
        )
    )
    
    REM Python으로 실행
    echo 🐍 Python으로 실행 중...
    python main.py
    
) else (
    echo ❌ 실행할 파일을 찾을 수 없습니다!
    echo.
    echo 📋 해결 방법:
    echo   1. ChzzkStreamDeck.exe가 같은 폴더에 있는지 확인
    echo   2. 압축 파일을 올바르게 해제했는지 확인  
    echo   3. 또는 main.py가 있는 소스 코드 폴더에서 실행
    echo.
    pause
    exit /b 1
)

echo.
echo 🎉 ChzzkStreamDeck이 실행되었습니다!
echo 📱 관리패널: http://localhost:8080/admin
echo.
echo 💡 앱을 종료하려면 이 창을 닫거나 Ctrl+C를 누르세요
echo ============================================

REM 사용자가 창을 닫을 때까지 대기
timeout /t 3 >nul
echo 🔄 앱이 백그라운드에서 실행 중입니다...
pause >nul 