#!/bin/bash

# 스트리밍 컨트롤 센터 - 브라우저 모드 실행 스크립트
# Git Bash에서 실행: ./start_browser.sh

echo "🎮 스트리밍 컨트롤 센터 시작 중..."
echo "🌐 브라우저 모드로 실행합니다."
echo ""

# 현재 디렉토리 확인
if [ ! -d "neon" ]; then
    echo "❌ 오류: neon 폴더를 찾을 수 없습니다."
    echo "   스크립트를 프로젝트 루트 디렉토리에서 실행해주세요."
    read -p "엔터 키를 눌러서 종료..."
    exit 1
fi

# 가상환경 활성화 (있는 경우)
if [ -d ".venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
fi

# Python 실행
echo "🚀 앱 실행 중..."
echo "💡 브라우저가 자동으로 열립니다. 종료하려면 Ctrl+C를 누르세요."
python neon/main.py

# 스크립트 종료 후 대기
echo ""
echo "앱이 종료되었습니다."
read -p "엔터 키를 눌러서 종료..." 