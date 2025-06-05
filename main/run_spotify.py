#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네온 스포티파이 오버레이 실행기
"""

import time
import threading
import webbrowser
import logging
from spotify_api import SpotifyAPI, get_current_track_data
from spotify_server import run_server_thread

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_track_data():
    """백그라운드에서 트랙 데이터 업데이트"""
    spotify_api = SpotifyAPI()
    
    while True:
        try:
            spotify_api.get_current_track()
            time.sleep(5)  # 5초마다 업데이트
        except Exception as e:
            logger.error(f"❌ 트랙 데이터 업데이트 오류: {e}")
            time.sleep(10)

def main():
    """메인 함수"""
    # 설정
    server_port = 8888  # HTTP 서버 포트
    
    print("🎵 네온 스포티파이 오버레이 시작!")
    print("="*60)
    
    # HTTP 서버를 별도 스레드에서 실행
    server_thread = run_server_thread(server_port)
    
    # 트랙 데이터 업데이트를 별도 스레드에서 실행
    update_thread = threading.Thread(target=update_track_data, daemon=True)
    update_thread.start()
    
    # Spotify 인증 시작
    spotify_api = SpotifyAPI()
    auth_url = spotify_api.get_auth_url()
    
    print(f"🌐 HTTP 서버 시작: http://localhost:{server_port}")
    print(f"📱 브라우저에서 다음 URL을 열어 Spotify 인증을 완료하세요:")
    print(f"🔗 {auth_url}")
    print(f"\n🎯 인증 완료 후 OBS 브라우저 소스 URL:")
    print(f"📺 http://localhost:{server_port}/overlay")
    print("="*60)
    
    # 자동으로 브라우저 열기
    try:
        webbrowser.open(auth_url)
        logger.info("🌐 브라우저에서 인증 페이지를 열었습니다.")
    except Exception as e:
        logger.warning(f"⚠️ 브라우저 자동 열기 실패: {e}")
    
    try:
        # 메인 스레드 유지
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 네온 스포티파이 오버레이를 종료합니다.")

if __name__ == "__main__":
    main() 