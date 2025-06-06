#!/bin/bash

# ChzzkStreamDeck - Git Bash 실행 스크립트
# UTF-8 인코딩 지원 및 경로 문제 해결

# 색상 코드 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}===========================================${NC}"
echo -e "${PURPLE}   🎮 ChzzkStreamDeck 시작 중...${NC}"
echo -e "${CYAN}===========================================${NC}"
echo ""

# 현재 디렉토리 확인
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"

echo -e "${BLUE}📁 작업 디렉토리: $(pwd)${NC}"
echo ""

# 실행 파일 존재 확인
if [ -f "ChzzkStreamDeck.exe" ]; then
    echo -e "${GREEN}✅ 실행 파일 확인됨: ChzzkStreamDeck.exe${NC}"
    echo -e "${YELLOW}🚀 앱 시작 중... (첫 실행 시 시간이 걸릴 수 있습니다)${NC}"
    echo ""
    
    # 실행 파일 실행 (앱 모드)
    echo -e "${BLUE}🚀 실행 파일 시작 중...${NC}"
    ./ChzzkStreamDeck.exe --app
    
    echo -e "${GREEN}🏁 앱이 종료되었습니다.${NC}"
    echo -e "${CYAN}📱 데스크톱 앱 모드로 관리패널이 열립니다${NC}"
    echo -e "${YELLOW}💡 만약 앱이 열리지 않으면 관리패널에 접속하세요${NC}"
    
elif [ -f "main.py" ]; then
    echo -e "${YELLOW}⚠️  실행 파일을 찾을 수 없습니다. 개발 모드로 실행합니다.${NC}"
    echo ""
    
    # Python 설치 확인
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python이 설치되지 않았습니다!${NC}"
        echo -e "${YELLOW}💡 Python 3.8+ 설치 후 다시 실행해주세요.${NC}"
        read -p "Enter 키를 눌러 종료..."
        exit 1
    fi
    
    # Python 명령어 선택
    PYTHON_CMD="python"
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    fi
    
    echo -e "${BLUE}🐍 Python 명령어: $PYTHON_CMD${NC}"
    
    # 가상환경 활성화 (있는 경우)
    if [ -d ".venv" ]; then
        echo -e "${CYAN}🔧 가상환경 활성화 중...${NC}"
        
        # Git Bash에서 가상환경 활성화
        if [ -f ".venv/Scripts/activate" ]; then
            source .venv/Scripts/activate
        elif [ -f ".venv/bin/activate" ]; then
            source .venv/bin/activate
        fi
        
        echo -e "${GREEN}✅ 가상환경 활성화됨${NC}"
    fi
    
    # 시스템 요구사항 체크
    if [ -f "check_system.py" ]; then
        echo -e "${CYAN}🔍 시스템 요구사항 확인 중...${NC}"
        $PYTHON_CMD check_system.py
        
        if [ $? -ne 0 ]; then
            echo ""
            echo -e "${RED}❌ 시스템 요구사항을 충족하지 않습니다.${NC}"
            echo -e "${YELLOW}💡 위의 가이드를 따라 필요한 패키지를 설치하세요.${NC}"
            read -p "Enter 키를 눌러 종료..."
            exit 1
        fi
    fi
    
    # 의존성 설치 확인
    echo -e "${CYAN}📦 필요한 패키지 확인 중...${NC}"
    if [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt --quiet
        echo -e "${GREEN}✅ 패키지 확인 완료${NC}"
    fi
    
    # Python으로 실행
    echo ""
    echo -e "${BLUE}🚀 Python으로 실행 중...${NC}"
    $PYTHON_CMD main.py --app
    
else
    echo -e "${RED}❌ 실행할 파일을 찾을 수 없습니다!${NC}"
    echo ""
    echo -e "${YELLOW}📋 해결 방법:${NC}"
    echo -e "   ${CYAN}1. ChzzkStreamDeck.exe가 같은 폴더에 있는지 확인${NC}"
    echo -e "   ${CYAN}2. 압축 파일을 올바르게 해제했는지 확인${NC}"
    echo -e "   ${CYAN}3. 또는 main.py가 있는 소스 코드 폴더에서 실행${NC}"
    echo ""
    read -p "Enter 키를 눌러 종료..."
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 ChzzkStreamDeck이 실행되었습니다!${NC}"
echo -e "${CYAN}📱 관리패널: 화면에 표시된 URL을 확인하세요${NC}"
echo ""
echo -e "${YELLOW}💡 앱을 종료하려면 이 창을 닫거나 Ctrl+C를 누르세요${NC}"
echo -e "${CYAN}============================================${NC}"

# 종료 대기
echo ""
echo -e "${BLUE}🔄 앱이 백그라운드에서 실행 중입니다...${NC}"
read -p "Enter 키를 눌러 종료..." 