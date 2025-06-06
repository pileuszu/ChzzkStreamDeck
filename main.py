#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChzzkStreamDeck - 치지직 스트리밍 컨트롤 센터
빠른 시작을 위한 최적화된 메인 실행 파일
"""

import os
import sys
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def optimize_startup():
    """실행 파일 시작 최적화"""
    try:
        # PyInstaller 실행 환경 감지 및 최적화
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 실행 파일인 경우
            application_path = sys._MEIPASS
            main_dir = os.path.join(application_path, 'main')
            logger.info(f"🚀 빌드된 실행파일 모드: {application_path}")
            
            # 추가 경로들도 설정
            neon_dir = os.path.join(application_path, 'neon')
            purple_dir = os.path.join(application_path, 'purple')
            
            # 모든 필요한 경로를 Python path에 추가
            for path in [main_dir, neon_dir, purple_dir]:
                if path not in sys.path:
                    sys.path.insert(0, path)
                    
        else:
            # 개발 환경에서 Python으로 실행하는 경우
            base_dir = os.path.dirname(os.path.abspath(__file__))
            main_dir = os.path.join(base_dir, 'main')
            neon_dir = os.path.join(base_dir, 'neon')
            purple_dir = os.path.join(base_dir, 'purple')
            
            logger.info(f"🐍 개발 모드: {base_dir}")
            
            # 모든 필요한 경로를 Python path에 추가
            for path in [main_dir, neon_dir, purple_dir]:
                if path not in sys.path:
                    sys.path.insert(0, path)
        
        # 디렉토리 존재 확인
        if not os.path.exists(main_dir):
            raise FileNotFoundError(f"main 디렉토리를 찾을 수 없습니다: {main_dir}")
        
        logger.info(f"✅ 메인 디렉토리 설정 완료: {main_dir}")
        logger.info(f"✅ Python 경로 설정 완료: {len(sys.path)} 경로")
        return main_dir
        
    except Exception as e:
        logger.error(f"❌ 시작 최적화 중 오류: {e}")
        raise

def validate_environment():
    """환경 검증"""
    try:
        # Python 버전 확인
        if sys.version_info < (3, 8):
            raise RuntimeError(f"Python 3.8 이상이 필요합니다. 현재 버전: {sys.version}")
        
        # 빌드된 실행 파일인지 확인
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 경우, 파일 검증을 건너뛰고 모듈 import로 확인
            logger.info("✅ 빌드된 실행 파일 - 모듈 import 검증 수행")
            try:
                import unified_server
                import config
                logger.info("✅ 핵심 모듈 import 성공")
            except ImportError as e:
                raise ImportError(f"빌드된 실행 파일에서 모듈 로딩 실패: {e}")
        else:
            # 개발 환경에서는 파일 존재 확인
            required_files = [
                'main/unified_server.py',
                'main/config.py',
                'main/chat_client.py',
                'main/spotify_api.py'
            ]
            
            for file_path in required_files:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"필수 파일이 없습니다: {file_path}")
        
        logger.info("✅ 환경 검증 완료")
        
    except Exception as e:
        logger.error(f"❌ 환경 검증 실패: {e}")
        raise

def main():
    """메인 실행 함수"""
    try:
        logger.info("🎮 ChzzkStreamDeck 시작 중...")
        
        # 시작 최적화
        main_dir = optimize_startup()
        
        # 환경 검증
        validate_environment()
        
        # 통합 서버 실행
        logger.info("🚀 통합 서버 시작...")
        from unified_server import main as server_main
        server_main()
        
    except ImportError as e:
        logger.error(f"❌ 모듈 로딩 실패: {e}")
        print("\n" + "="*50)
        print("🔍 문제 해결 방법:")
        print("1. 모든 파일이 올바르게 설치되었는지 확인")
        print("2. main/ 디렉토리가 존재하는지 확인")
        print("3. requirements.txt의 의존성이 설치되었는지 확인")
        print("4. 'pip install -r requirements.txt' 실행")
        print("="*50)
        input("\nEnter 키를 눌러 종료...")
        sys.exit(1)
        
    except FileNotFoundError as e:
        logger.error(f"❌ 파일을 찾을 수 없음: {e}")
        print("\n" + "="*50)
        print("🔍 문제 해결 방법:")
        print("1. 압축 파일을 완전히 해제했는지 확인")
        print("2. 모든 폴더와 파일이 존재하는지 확인")
        print("3. 올바른 디렉토리에서 실행하는지 확인")
        print("="*50)
        input("\nEnter 키를 눌러 종료...")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ 실행 중 오류 발생: {e}")
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")
        print("자세한 정보는 로그를 확인하세요.")
        input("\nEnter 키를 눌러 종료...")
        sys.exit(1)

if __name__ == "__main__":
    main() 