@echo off
chcp 65001 >nul

rem 스트리밍 컨트롤 센터 - 데스크톱 앱 모드 실행 스크립트
rem 실행: start_app.bat 더블클릭 또는 터미널에서 start_app.bat

echo 🎮 스트리밍 컨트롤 센터 시작 중...
echo 📱 데스크톱 앱 모드로 실행합니다.
echo.

rem Python 설치 및 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 오류: Python이 설치되지 않았습니다.
    echo    Python 3.13.3을 설치한 후 다시 실행해주세요.
    echo    설치 링크: https://www.python.org/downloads/
    pause
    exit /b 1
)

rem Python 버전 확인 (3.13.3 권장)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% detected

rem 권장 버전과 비교
echo %PYTHON_VERSION% | findstr "3.13.3" >nul
if not errorlevel 1 (
    echo ✅ Recommended Python version 3.13.3 confirmed
) else (
    echo ⚠️  Warning: Current Python version is %PYTHON_VERSION%
    echo    Recommended version is 3.13.3 for optimal compatibility
    echo    Some packages may not work correctly with different versions
    echo.
)

rem 현재 디렉토리 확인
if not exist "neon" (
    echo ❌ 오류: neon 폴더를 찾을 수 없습니다.
    echo    스크립트를 프로젝트 루트 디렉토리에서 실행해주세요.
    pause
    exit /b 1
)

rem 가상환경 생성 및 활성화
if not exist ".venv" (
    echo 🔨 가상환경을 생성 중...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 오류: 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
    echo ✅ 가상환경이 생성되었습니다.
)

echo 🐍 가상환경 활성화 중...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 오류: 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)

rem 의존성 설치 확인 및 설치
if not exist "requirements.txt" (
    echo ❌ 오류: requirements.txt 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

echo 📦 Checking dependencies...

rem 의존성 체크 로그 파일 생성 (.deps_check 폴더에)
if not exist ".deps_check" mkdir ".deps_check"
set DEPS_LOG=".deps_check\package_status.log"

rem 설치된 패키지 목록을 로그 파일에 저장
echo 🔍 Checking installed packages...
pip list --format=freeze > "%DEPS_LOG%" 2>nul

rem requirements.txt에서 각 패키지 확인
echo 🔍 Checking required packages...
for /f "tokens=*" %%i in (requirements.txt) do (
    echo %%i | findstr /r "^[a-zA-Z]" >nul
    if not errorlevel 1 (
        for /f "tokens=1 delims==^>=^<" %%j in ("%%i") do (
            pip show "%%j" >nul 2>&1
            if errorlevel 1 (
                echo 📥 Installing %%j...
                echo [%date% %time%] Installing: %%j >> "%DEPS_LOG%"
                pip install "%%i" --quiet
                if errorlevel 1 (
                    echo ❌ Failed to install %%j
                    echo [%date% %time%] Failed: %%j >> "%DEPS_LOG%"
                    pause
                    exit /b 1
                ) else (
                    echo ✅ %%j installed
                    echo [%date% %time%] Success: %%j >> "%DEPS_LOG%"
                )
            ) else (
                echo ✅ %%j already installed
                echo [%date% %time%] Already installed: %%j >> "%DEPS_LOG%"
            )
        )
    )
)

echo 📝 Dependency check log saved to %DEPS_LOG%

echo ✅ All dependencies installed successfully.

rem Python 실행
echo 🚀 Starting application...
python main.py --app

rem 스크립트 종료 후 대기
echo.
echo 앱이 종료되었습니다.
pause 