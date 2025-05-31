@echo off
chcp 65001 >nul

rem 스트리밍 컨트롤 센터 - 데스크톱 앱 모드 실행 스크립트
rem 실행: start_app.bat 더블클릭 또는 터미널에서 start_app.bat

echo 🎮 스트리밍 컨트롤 센터 시작 중...
echo 📱 데스크톱 앱 모드로 실행합니다.
echo.

rem 현재 디렉토리 확인
if not exist "neon" (
    echo ❌ 오류: neon 폴더를 찾을 수 없습니다.
    echo    스크립트를 프로젝트 루트 디렉토리에서 실행해주세요.
    pause
    exit /b 1
)

rem 가상환경 활성화 (있는 경우)
if exist ".venv" (
    echo 🐍 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
)

rem Python 실행
echo 🚀 앱 실행 중...
python neon/main.py --app

rem 스크립트 종료 후 대기
echo.
echo 앱이 종료되었습니다.
pause 