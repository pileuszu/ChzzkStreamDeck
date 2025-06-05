#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네온 치지직 채팅 오버레이 실행기
"""

import asyncio
import logging
from chat_client import ChzzkChatClient
from chat_server import add_chat_message, run_server_thread
from config import AppConfig

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """메인 함수"""
    # 설정
    config = AppConfig()
    channel_id = "789d1d9c5b58c847f9f18c8e5073c580"  # 치지직 채널 ID
    server_port = config.get_server_port()  # 설정에서 포트 가져오기
    
    print("🎬 네온 치지직 채팅 오버레이 시작!")
    print("="*60)
    
    # HTTP 서버를 별도 스레드에서 실행
    server_thread = run_server_thread(server_port)
    
    print(f"🌐 HTTP 서버 시작: http://localhost:{server_port}")
    print(f"📺 OBS 브라우저 소스 URL: http://localhost:{server_port}/obs")
    print(f"🌐 일반 채팅창 URL: http://localhost:{server_port}/")
    print("="*60)
    
    # 채팅 클라이언트 생성 및 연결
    client = ChzzkChatClient(channel_id)
    
    try:
        if await client.connect():
            await client.send_join_message()
            # 메시지 콜백 함수로 서버에 전달
            await client.listen_messages(message_callback=add_chat_message)
        else:
            logger.error("❌ 채팅방 연결 실패")
    except Exception as e:
        logger.error(f"오버레이 실행 오류: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 네온 채팅 오버레이를 종료합니다.") 