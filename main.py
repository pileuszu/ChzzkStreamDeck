#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChzzkStreamDeck - 치지직 스트리밍 컨트롤 센터
빠른 시작을 위한 최적화된 메인 실행 파일
"""

import os
import sys

def optimize_startup():
    """실행 파일 시작 최적화"""
    # PyInstaller 실행 환경 감지 및 최적화
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행 파일인 경우
        application_path = sys._MEIPASS
        main_dir = os.path.join(application_path, 'main')
    else:
        # 개발 환경에서 Python으로 실행하는 경우
        main_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main')
    
    # Python 경로에 main 디렉토리 추가 (중복 방지)
    if main_dir not in sys.path:
        sys.path.insert(0, main_dir)
    
    return main_dir

def main():
    """메인 실행 함수"""
    try:
        # 시작 최적화
        optimize_startup()
        
        # 통합 서버 실행
        from unified_server import main as server_main
        server_main()
        
    except ImportError as e:
        print(f"❌ 모듈 로딩 실패: {e}")
        print("💡 main 디렉토리의 파일들이 올바르게 설치되었는지 확인하세요.")
        input("Enter 키를 눌러 종료...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        input("Enter 키를 눌러 종료...")
        sys.exit(1)

if __name__ == "__main__":
    main() 