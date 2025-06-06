import asyncio
import websockets
import json
import logging
from datetime import datetime
import urllib.request
import http.server
import socketserver
import threading
from urllib.parse import urlparse
import sys
import os

# 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'main'))
from config import ConfigManager

# 로깅 설정
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 정보성 메시지만 INFO 레벨로 표시
logger.setLevel(logging.INFO)

# 글로벌 메시지 저장소
chat_messages = []
MAX_MESSAGES = 50

class ChzzkChatClient:
    """치지직 채팅 클라이언트"""
    
    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        self.chat_channel_id = None
        self.access_token = None
        self.websocket = None
        self.is_connected = False
        
        # 웹소켓 엔드포인트들
        self.endpoints = [
            f"wss://kr-ss{i}.chat.naver.com/chat" for i in range(1, 6)
        ]
    
    def get_chat_channel_id_sync(self):
        """채팅 채널 ID 조회 (동기 방식)"""
        # 1단계: 채널 정보 조회로 방송 상태 확인
        channel_info_url = f"https://api.chzzk.naver.com/service/v1/channels/{self.channel_id}"
        
        try:
            req = urllib.request.Request(channel_info_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    channel_data = json.loads(response.read().decode('utf-8'))
                    
                    if 'content' in channel_data and channel_data['content']:
                        is_live = channel_data['content'].get('openLive', False)
                        channel_name = channel_data['content'].get('channelName', '알 수 없음')
                        
                        logger.info(f"채널명: {channel_name}")
                        logger.info(f"방송 상태: {'방송 중' if is_live else '방송 종료'}")
                        
                        if not is_live:
                            logger.warning("현재 방송이 꺼져있습니다.")
                            return False
                    else:
                        logger.error("채널 정보를 찾을 수 없습니다.")
                        return False
                else:
                    logger.error(f"채널 정보 조회 실패: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"채널 정보 조회 실패: {e}")
            return False
        
        # 2단계: 라이브 상세 정보에서 채팅 채널 ID 획득
        api_endpoints = [
            f"https://api.chzzk.naver.com/service/v2/channels/{self.channel_id}/live-detail",
            f"https://api.chzzk.naver.com/service/v1/channels/{self.channel_id}/live-detail",
            f"https://api.chzzk.naver.com/service/v1/channels/{self.channel_id}/live-status",
        ]
        
        for endpoint in api_endpoints:
            try:
                req = urllib.request.Request(endpoint)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                with urllib.request.urlopen(req) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        # 채팅 채널 ID 추출
                        chat_channel_id = None
                        if 'content' in data and data['content'] and 'chatChannelId' in data['content']:
                            chat_channel_id = data['content']['chatChannelId']
                        elif 'content' in data and data['content'] and 'live' in data['content'] and data['content']['live'] and 'chatChannelId' in data['content']['live']:
                            chat_channel_id = data['content']['live']['chatChannelId']
                        
                        if chat_channel_id:
                            self.chat_channel_id = chat_channel_id
                            logger.info(f"채팅 채널 ID 획득: {self.chat_channel_id}")
                            return True
                        else:
                            continue
                    else:
                        continue
            except Exception as e:
                continue
        
        # 최후의 수단: 채널 ID를 채팅 채널 ID로 사용
        logger.info("채널 ID를 채팅 채널 ID로 사용합니다.")
        self.chat_channel_id = self.channel_id
        return True
    
    def get_access_token_sync(self):
        """액세스 토큰 획득"""
        if not self.chat_channel_id:
            logger.error("채팅 채널 ID가 없습니다.")
            return False
            
        url = f"https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId={self.chat_channel_id}&chatType=STREAMING"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    if 'content' in data and 'accessToken' in data['content']:
                        self.access_token = data['content']['accessToken']
                        logger.info("액세스 토큰 획득 성공")
                        return True
                    else:
                        logger.error("액세스 토큰을 찾을 수 없습니다.")
                        return False
                else:
                    logger.error(f"액세스 토큰 조회 실패: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"액세스 토큰 조회 실패: {e}")
            return False
    
    async def connect(self):
        """웹소켓 연결"""
        # 1단계: 채팅 채널 ID 획득
        loop = asyncio.get_event_loop()
        if not await loop.run_in_executor(None, self.get_chat_channel_id_sync):
            return False
        
        # 2단계: 액세스 토큰 획득
        if not await loop.run_in_executor(None, self.get_access_token_sync):
            return False
        
        # 3단계: 웹소켓 연결
        for endpoint in self.endpoints:
            try:
                logger.info(f"웹소켓 연결 시도: {endpoint}")
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Origin": "https://chzzk.naver.com"
                }
                self.websocket = await websockets.connect(endpoint, additional_headers=headers)
                self.is_connected = True
                logger.info(f"웹소켓 연결 성공: {endpoint}")
                return True
            except Exception as e:
                logger.warning(f"연결 실패 {endpoint}: {e}")
                continue
        
        logger.error("모든 웹소켓 연결 실패")
        return False
    
    async def send_join_message(self):
        """채팅방 참가 메시지 전송"""
        if not self.chat_channel_id or not self.access_token:
            logger.error("채팅 채널 ID 또는 액세스 토큰이 없습니다.")
            return
        
        connect_message = {
            "ver": "2",
            "cmd": 100,
            "svcid": "game",
            "cid": self.chat_channel_id,
            "bdy": {
                "uid": None,
                "devType": 2001,
                "accTkn": self.access_token,
                "auth": "READ"
            },
            "tid": 1
        }
        
        try:
            await self.websocket.send(json.dumps(connect_message))
            logger.info("채팅방 참가 메시지 전송 완료")
        except Exception as e:
            logger.error(f"참가 메시지 전송 실패: {e}")
    
    async def listen_messages(self):
        """메시지 수신 대기"""
        logger.info("채팅 메시지 수신 시작")
        
        # 하트비트 태스크 시작
        heartbeat_task = asyncio.create_task(self.keep_alive())
        
        try:
            async for message in self.websocket:
                try:
                    if message.strip():
                        data = json.loads(message)
                        await self.handle_message(data)
                except json.JSONDecodeError:
                    logger.warning(f"JSON 파싱 실패: {message}")
                except Exception as e:
                    logger.error(f"메시지 처리 오류: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("웹소켓 연결 종료")
            self.is_connected = False
        except Exception as e:
            logger.error(f"메시지 수신 오류: {e}")
            self.is_connected = False
        finally:
            heartbeat_task.cancel()
    
    async def handle_message(self, data):
        """메시지 처리"""
        if isinstance(data, dict):
            # 하트비트 응답
            if data.get('cmd') == 0 and data.get('ver') == '2':
                heartbeat_response = {"ver": "2", "cmd": 10000}
                try:
                    await self.websocket.send(json.dumps(heartbeat_response))
                except Exception as e:
                    logger.error(f"하트비트 응답 실패: {e}")
                return
            
            # 연결 응답 처리
            elif data.get('cmd') == 10000:
                ret_code = data.get('retCode')
                if ret_code == 200:
                    logger.info("채팅방 연결 성공!")
                else:
                    logger.error(f"연결 실패: {data.get('retMsg', '')}")
                return
            
            # 채팅 메시지 처리
            elif 'bdy' in data:
                await self.process_chat_message(data)
    
    async def process_chat_message(self, data):
        """채팅 메시지 파싱 및 저장"""
        try:
            cmd = data.get('cmd')
            bdy_list = data.get('bdy', [])
            
            if not bdy_list:
                return
            
            bdy = bdy_list[0] if isinstance(bdy_list, list) else bdy_list
            
            # 프로필 정보 파싱
            profile_str = bdy.get('profile', '{}')
            try:
                profile = json.loads(profile_str) if isinstance(profile_str, str) else profile_str
            except json.JSONDecodeError:
                profile = {}
            
            # 사용자 역할 확인
            user_role = profile.get('userRoleCode', 'common_user')
            is_streamer = (user_role == 'streamer')
            
            # 후원 메시지 확인 (추정)
            is_donation = cmd == 93102 or bdy.get('payAmount', 0) > 0
            
            # 배지 및 제목 정보
            badge = profile.get('badge', {})
            title = profile.get('title', {})
            
            chat_data = {
                'type': 'donation' if is_donation else 'chat',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'user_id': bdy.get('uid', ''),
                'nickname': profile.get('nickname', '익명'),
                'message': bdy.get('msg', ''),
                'is_streamer': is_streamer,
                'user_role': user_role,
                'badge_url': badge.get('imageUrl', '') if badge else '',
                'title_name': title.get('name', '') if title else '',
                'title_color': title.get('color', '#FFFFFF') if title else '#FFFFFF',
                'profile_image': profile.get('profileImageUrl', ''),
                'verified': profile.get('verifiedMark', False),
                'amount': bdy.get('payAmount', 0) if is_donation else 0
            }
            
            # 글로벌 메시지 저장소에 추가
            add_chat_message(chat_data)
            
            # 콘솔 출력
            role_emoji = "👑" if is_streamer else ("💰" if is_donation else "💬")
            amount_text = f" ({chat_data['amount']}원)" if is_donation else ""
            print(f"{role_emoji} [{chat_data['timestamp']}] {chat_data['nickname']}: {chat_data['message']}{amount_text}")
                    
        except Exception as e:
            logger.error(f"채팅 메시지 파싱 오류: {e}")
    
    async def keep_alive(self):
        """하트비트 전송으로 연결 유지"""
        try:
            while self.is_connected:
                await asyncio.sleep(20)  # 20초마다
                if self.websocket and not self.websocket.closed:
                    heartbeat = {"ver": "2", "cmd": 0}
                    await self.websocket.send(json.dumps(heartbeat))
        except Exception as e:
            logger.debug(f"하트비트 종료: {e}")
    
    async def disconnect(self):
        """연결 종료"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False

def add_chat_message(message_data):
    """새 채팅 메시지 추가"""
    global chat_messages
    chat_messages.append(message_data)
    if len(chat_messages) > MAX_MESSAGES:
        chat_messages.pop(0)

class OverlayHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """오버레이용 HTTP 핸들러"""
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/' or parsed_path.path == '/obs':
                # 채팅 오버레이 HTML 제공
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                html = self.get_overlay_html()
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                
                # 연결 상태 확인 후 전송
                try:
                    self.wfile.write(html.encode('utf-8'))
                    self.wfile.flush()
                except (ConnectionAbortedError, BrokenPipeError) as e:
                    logger.debug(f"클라이언트 연결 끊어짐: {e}")
                    return
            
            elif parsed_path.path == '/api/messages':
                # 메시지 API
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                messages_json = json.dumps(chat_messages, ensure_ascii=False)
                self.send_header('Content-Length', str(len(messages_json.encode('utf-8'))))
                self.end_headers()
                
                try:
                    self.wfile.write(messages_json.encode('utf-8'))
                    self.wfile.flush()
                except (ConnectionAbortedError, BrokenPipeError) as e:
                    logger.debug(f"클라이언트 연결 끊어짐: {e}")
                    return
            
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"HTTP 요청 처리 오류: {e}")
            try:
                self.send_response(500)
                self.end_headers()
            except:
                pass
    
    def get_overlay_html(self):
        """OBS용 채팅 오버레이 HTML - 설정값 적용"""
        # 설정 관리자 import (동적으로)
        try:
            # main 폴더를 Python 경로에 추가
            main_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'main')
            if main_dir not in sys.path:
                sys.path.insert(0, main_dir)
            
            from config import config_manager, ConfigManager
            
            # 채팅 모듈 설정 가져오기
            chat_config = config_manager.get_module_config('chat')
            max_messages = chat_config.get('max_messages', 10)
            streamer_align_left = chat_config.get('streamer_align_left', False)
            background_enabled = chat_config.get('background_enabled', True)
            background_opacity = chat_config.get('background_opacity', 0.3)
            remove_outer_effects = chat_config.get('remove_outer_effects', False)
            
            logger.info(f"채팅 설정 적용: max_messages={max_messages}, streamer_align_left={streamer_align_left}, background_enabled={background_enabled}, background_opacity={background_opacity}, remove_outer_effects={remove_outer_effects}")
            
        except Exception as e:
            logger.warning(f"설정 로드 실패, 기본값 사용: {e}")
            # 기본값들
            max_messages = 10
            streamer_align_left = False
            background_enabled = True
            background_opacity = 0.3
            remove_outer_effects = False
        
        # 동적 CSS 생성
        dynamic_css = self._generate_dynamic_css(
            max_messages=max_messages,
            streamer_align_left=streamer_align_left,
            background_enabled=background_enabled,
            background_opacity=background_opacity,
            remove_outer_effects=remove_outer_effects
        )
        
        html_template = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>치지직 채팅 오버레이</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: transparent;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            position: relative;
        }

        /* 사이버펑크 배경 - 데이터 스트림과 네온 그리드 */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                /* 네온 그리드 */
                linear-gradient(90deg, rgba(0,255,175,0.03) 1px, transparent 1px),
                linear-gradient(180deg, rgba(155,77,224,0.03) 1px, transparent 1px),
                /* 데이터 스트림 파티클 */
                radial-gradient(2px 2px at 20% 30%, rgba(0,255,175,0.8), transparent),
                radial-gradient(1px 1px at 80% 20%, rgba(155,77,224,0.6), transparent),
                radial-gradient(3px 3px at 45% 70%, rgba(255,215,0,0.4), transparent),
                radial-gradient(2px 2px at 90% 80%, rgba(255,255,255,0.3), transparent);
            background-size: 50px 50px, 50px 50px, 300px 300px, 250px 250px, 400px 400px, 200px 200px;
            animation: dataStreamFlow 15s linear infinite, cyberGrid 8s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }

        /* 추가 홀로그램 레이어 */
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                /* 스캔라인 효과 */
                repeating-linear-gradient(
                    0deg,
                    transparent 0px,
                    rgba(0,255,175,0.03) 1px,
                    transparent 2px,
                    transparent 4px
                );
            animation: scanlines 2s linear infinite;
            pointer-events: none;
            z-index: 1;
        }
        
        .chat_wrap {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 520px;  /* 원래 크기로 복원 */
            height: 600px; /* 원래 크기로 복원 */
            background: transparent;
            z-index: 1000;
            font-family: 'Noto Sans KR', sans-serif;
            overflow: hidden;
            padding: 20px; /* 적절한 패딩으로 복원 */
        }

        .chat_list {
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            gap: 15px;
            height: 100%;
            overflow: hidden;
            position: relative;
            z-index: 2;
            /* 위쪽 자연스러운 페이드아웃 마스크 - 더 부드럽게 */
            mask: linear-gradient(to bottom, 
                transparent 0%, 
                rgba(0,0,0,0.05) 5%, 
                rgba(0,0,0,0.2) 15%, 
                rgba(0,0,0,0.6) 30%, 
                black 45%, 
                black 100%);
            -webkit-mask: linear-gradient(to bottom, 
                transparent 0%, 
                rgba(0,0,0,0.05) 5%, 
                rgba(0,0,0,0.2) 15%, 
                rgba(0,0,0,0.6) 30%, 
                black 45%, 
                black 100%);
        }

        .chat_box.naver.chat {
            padding: 18px 25px;
            margin: 20px 40px;
            position: relative;
            z-index: 2;
            animation: messageEntrance 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            transform: translateX(-120px) rotateY(-15deg) scale(0.8);
            opacity: 0;
            max-width: calc(100% - 80px);
            filter: drop-shadow(0 0 0 transparent);
            overflow: hidden;
        }

        /* 홀로그램 글리치 효과 레이어 */
        .chat_box.naver.chat:before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(255,255,255,0.03) 25%,
                transparent 26%,
                transparent 74%,
                rgba(0,255,175,0.05) 75%,
                transparent 100%
            );
            animation: hologramScan 3s ease-in-out infinite;
            z-index: -1;
            pointer-events: none;
        }

        /* 네온 파티클 트레일 */
        .chat_box.naver.chat:after {
            content: '';
            position: absolute;
            top: -5px;
            left: -5px;
            right: -5px;
            bottom: -5px;
            background: 
                radial-gradient(circle at 10% 20%, rgba(0,255,175,0.1) 0%, transparent 50%),
                radial-gradient(circle at 90% 80%, rgba(155,77,224,0.1) 0%, transparent 50%),
                radial-gradient(circle at 50% 10%, rgba(255,215,0,0.08) 0%, transparent 50%);
            animation: particleFlow 4s ease-in-out infinite;
            z-index: -2;
            pointer-events: none;
            filter: blur(1px);
        }

        /* 스트리머용 왼쪽 상단 별 */
        .chat_box.naver.chat.streamer::before {
            content: '';
            position: absolute;
            top: -8px;
            left: -8px;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            background: transparent;
            border-radius: 50%;
            animation: starTwinkle 1.5s ease-in-out infinite alternate;
            z-index: 10;
            filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.8));
        }

        .chat_box.naver.chat p.name {
            display: block;
            font-weight: 900;
            font-size: 15px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 2px;
            position: relative;
            overflow: hidden;
        }

        .chat_box.naver.chat.streamer p.name {
            color: #9b4de0;
            text-shadow: 
                0 0 15px rgba(155, 77, 224, 0.9),
                0 0 30px rgba(155, 77, 224, 0.5),
                0 0 45px rgba(155, 77, 224, 0.3);
            animation: royalGlow 3s ease-in-out infinite alternate;
        }

        .chat_box.naver.chat:not(.streamer) p.name {
            color: #00FFAF;
            text-shadow: 
                0 0 15px rgba(0, 255, 175, 0.9),
                0 0 30px rgba(0, 255, 175, 0.5),
                0 0 45px rgba(0, 255, 175, 0.3);
            animation: emeraldGlow 3s ease-in-out infinite alternate;
        }

        /* 타이핑 효과용 애니메이션 */
        .chat_box.naver.chat p.name::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transform: translateX(-100%);
            animation: shimmer 2s ease-in-out 0.5s;
        }

        .chat_box.naver.chat p.name::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 100%;
            height: 3px;
            background: currentColor;
            transform: scaleX(0);
            animation: underlineExpand 1.2s ease-out 0.4s forwards;
            border-radius: 2px;
        }

        /* 이름과 텍스트 사이 구분선 */
        .chat_box.naver.chat::after {
            content: '';
            position: absolute;
            left: 25px;
            right: 25px;
            top: calc(15px + 8px + 15px + 3px); /* 패딩 + 폰트크기 + 마진 + 언더라인 */
            height: 4px; /* 1px에서 2px로 두께 증가 */
            background: linear-gradient(90deg, 
                transparent 0%,
                currentColor 20%,
                currentColor 80%,
                transparent 100%);
            opacity: 0.3;
            transform: scaleX(0);
            animation: separatorExpand 1.5s ease-out 0.8s forwards;
            z-index: 1;
        }

        .chat_box.naver.chat.streamer::after {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(155, 77, 224, 0.6) 20%,
                rgba(155, 77, 224, 0.6) 80%,
                transparent 100%);
        }

        .chat_box.naver.chat:not(.streamer)::after {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(0, 255, 175, 0.6) 20%,
                rgba(0, 255, 175, 0.6) 80%,
                transparent 100%);
        }

        .chat_box.naver.chat.donation::after {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(255, 215, 0, 0.6) 20%,
                rgba(255, 215, 0, 0.6) 80%,
                transparent 100%);
        }

        .chat_box.naver.chat p.text {
            color: #ffffff;
            font-size: 17px;
            line-height: 1.5;
            font-weight: 400;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
            animation: typeWriter 1.5s ease-out 0.3s forwards;
            opacity: 0;
            position: relative;
        }

        /* 글자별 애니메이션 효과 제거 */
        .chat_box.naver.chat p.text::before {
            display: none;
        }

        .chat_box.naver.chat.donation {
            background: linear-gradient(135deg, 
                rgba(255, 215, 0, 0.05) 0%, 
                rgba(255, 140, 0, 0.08) 30%,
                rgba(255, 69, 0, 0.10) 70%,
                rgba(255, 215, 0, 0.05) 100%);
            border: 1px solid rgba(255, 215, 0, 0.4);
            box-shadow: 
                0 15px 50px rgba(255, 215, 0, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.15),
                0 0 40px rgba(255, 215, 0, 0.15);
            animation: goldenEntrance 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
        }

        .chat_box.naver.chat.donation:before {
            background: 
                radial-gradient(ellipse at 50% 30%, rgba(255, 215, 0, 0.8) 0%, transparent 70%),
                radial-gradient(ellipse at 80% 70%, rgba(255, 140, 0, 0.6) 0%, transparent 70%),
                linear-gradient(45deg, 
                    transparent 15%, 
                    rgba(255, 215, 0, 0.4) 35%, 
                    rgba(255, 140, 0, 0.3) 65%, 
                    transparent 85%);
            animation: goldenAura 3s ease-in-out infinite;
        }

        .chat_box.naver.chat.donation p.name {
            color: #FFD700;
            text-shadow: 
                0 0 20px rgba(255, 215, 0, 0.9),
                0 0 40px rgba(255, 215, 0, 0.6),
                0 0 60px rgba(255, 140, 0, 0.4);
            animation: goldenPulse 2s ease-in-out infinite;
        }

        .donation-amount {
            display: inline-block;
            background: linear-gradient(45deg, #FFD700, #FFA500, #FF8C00);
            color: #000;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 13px;
            font-weight: bold;
            margin-left: 10px;
            box-shadow: 
                0 4px 15px rgba(255, 215, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
            animation: coinFlip 1s ease-in-out 0.8s;
            transform: rotateY(90deg);
        }

        .waiting-message {
            text-align: center;
            color: rgba(255,255,255,0.8);
            padding: 25px;
            background: linear-gradient(135deg, 
                rgba(0,0,0,0.2) 0%, 
                rgba(50,50,50,0.3) 50%, 
                rgba(0,0,0,0.2) 100%);
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            animation: breathe 3s ease-in-out infinite;
            position: relative;
            overflow: hidden;
        }

        .waiting-message::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, 
                transparent 30%, 
                rgba(255,255,255,0.1) 50%, 
                transparent 70%);
            animation: scan 4s ease-in-out infinite;
        }

        /* 애니메이션 정의 */
        @keyframes messageEntrance {
            0% {
                transform: translateX(-120px) rotateY(-15deg) scale(0.8);
                opacity: 0;
                filter: blur(10px);
            }
            50% {
                transform: translateX(15px) rotateY(-5deg) scale(1.05);
                opacity: 0.8;
                filter: blur(2px);
            }
            80% {
                transform: translateX(-5px) rotateY(2deg) scale(1.02);
                opacity: 0.95;
                filter: blur(0px);
            }
            100% {
                transform: translateX(0) rotateY(0deg) scale(1);
                opacity: 1;
                filter: blur(0px);
            }
        }

        @keyframes messageEntranceRight {
            0% {
                transform: translateX(120px) rotateY(15deg) scale(0.8);
                opacity: 0;
                filter: blur(10px);
            }
            50% {
                transform: translateX(-15px) rotateY(5deg) scale(1.05);
                opacity: 0.8;
                filter: blur(2px);
            }
            80% {
                transform: translateX(5px) rotateY(-2deg) scale(1.02);
                opacity: 0.95;
                filter: blur(0px);
            }
            100% {
                transform: translateX(0) rotateY(0deg) scale(1);
                opacity: 1;
                filter: blur(0px);
            }
        }

        @keyframes auroraGlow {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1) rotate(0deg);
                filter: blur(8px) hue-rotate(0deg);
            }
            33% {
                opacity: 0.6;
                transform: scale(1.05) rotate(2deg);
                filter: blur(10px) hue-rotate(30deg);
            }
            66% {
                opacity: 0.4;
                transform: scale(0.98) rotate(-1deg);
                filter: blur(6px) hue-rotate(60deg);
            }
        }

        @keyframes auroraGlowPurple {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1) rotate(0deg);
                filter: blur(8px) hue-rotate(0deg);
            }
            33% {
                opacity: 0.6;
                transform: scale(1.05) rotate(-2deg);
                filter: blur(10px) hue-rotate(-30deg);
            }
            66% {
                opacity: 0.4;
                transform: scale(0.98) rotate(1deg);
                filter: blur(6px) hue-rotate(-60deg);
            }
        }

        @keyframes sparkle {
            0%, 100% {
                opacity: 0;
                transform: scale(0) rotate(0deg);
            }
            25% {
                opacity: 1;
                transform: scale(1) rotate(90deg);
            }
            50% {
                opacity: 0.8;
                transform: scale(1.2) rotate(180deg);
            }
            75% {
                opacity: 1;
                transform: scale(0.8) rotate(270deg);
            }
        }

        @keyframes royalGlow {
            0% {
                text-shadow: 
                    0 0 15px rgba(155, 77, 224, 0.9),
                    0 0 30px rgba(155, 77, 224, 0.5),
                    0 0 45px rgba(155, 77, 224, 0.3);
            }
            100% {
                text-shadow: 
                    0 0 25px rgba(155, 77, 224, 1),
                    0 0 40px rgba(155, 77, 224, 0.8),
                    0 0 60px rgba(155, 77, 224, 0.5),
                    0 0 80px rgba(155, 77, 224, 0.3);
            }
        }

        @keyframes emeraldGlow {
            0% {
                text-shadow: 
                    0 0 15px rgba(0, 255, 175, 0.9),
                    0 0 30px rgba(0, 255, 175, 0.5),
                    0 0 45px rgba(0, 255, 175, 0.3);
            }
            100% {
                text-shadow: 
                    0 0 25px rgba(0, 255, 175, 1),
                    0 0 40px rgba(0, 255, 175, 0.8),
                    0 0 60px rgba(0, 255, 175, 0.5),
                    0 0 80px rgba(0, 255, 175, 0.3);
            }
        }

        @keyframes shimmer {
            0% {
                transform: translateX(-100%);
            }
            100% {
                transform: translateX(100%);
            }
        }

        @keyframes underlineExpand {
            0% {
                transform: scaleX(0);
            }
            100% {
                transform: scaleX(1);
            }
        }

        @keyframes typeWriter {
            0% {
                opacity: 0;
                transform: translateY(20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes textReveal {
            0% {
                transform: translateX(-100%);
            }
            100% {
                transform: translateX(100%);
            }
        }

        @keyframes goldenEntrance {
            0% {
                transform: translateY(50px) scale(0.5) rotateZ(-10deg);
                opacity: 0;
                filter: brightness(0.5);
            }
            50% {
                transform: translateY(-10px) scale(1.1) rotateZ(2deg);
                opacity: 0.8;
                filter: brightness(1.2);
            }
            100% {
                transform: translateY(0) scale(1) rotateZ(0deg);
                opacity: 1;
                filter: brightness(1);
            }
        }

        @keyframes goldenAura {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1) rotate(0deg);
                filter: blur(12px) brightness(1);
            }
            50% {
                opacity: 0.7;
                transform: scale(1.1) rotate(5deg);
                filter: blur(15px) brightness(1.3);
            }
        }

        @keyframes goldenPulse {
            0%, 100% {
                transform: scale(1);
                filter: brightness(1);
            }
            50% {
                transform: scale(1.05);
                filter: brightness(1.3);
            }
        }

        @keyframes coinFlip {
            0% {
                transform: rotateY(90deg) scale(0.8);
                opacity: 0;
            }
            50% {
                transform: rotateY(0deg) scale(1.1);
                opacity: 0.8;
            }
            100% {
                transform: rotateY(0deg) scale(1);
                opacity: 1;
            }
        }

        @keyframes breathe {
            0%, 100% {
                transform: scale(1);
                opacity: 0.7;
            }
            50% {
                transform: scale(1.02);
                opacity: 0.9;
            }
        }

        @keyframes scan {
            0% {
                transform: translate(-50%, -50%) rotate(0deg);
            }
            100% {
                transform: translate(-50%, -50%) rotate(360deg);
            }
        }

        @keyframes twinkle {
            0%, 100% {
                opacity: 0.3;
            }
            50% {
                opacity: 0.8;
            }
        }

        @keyframes fadeOut {
            0% {
                opacity: 1;
                transform: scale(1) translateY(0);
                filter: blur(0px);
            }
            50% {
                opacity: 0.5;
                transform: scale(0.95) translateY(-10px);
                filter: blur(2px);
            }
            100% {
                opacity: 0;
                transform: scale(0.8) translateY(-30px);
                filter: blur(8px);
            }
        }

        @keyframes separatorExpand {
            0% {
                transform: scaleX(0);
            }
            100% {
                transform: scaleX(1);
            }
        }

        /* 반응형 */
        @media (max-width: 768px) {
            .chat_wrap {
                width: 90vw;
                left: 5vw;
                padding: 15px;
            }
            
            .chat_box.naver.chat {
                margin: 15px 20px; /* 모바일에서는 마진 조정 (위아래 포함) */
            }
        }

        /* 스파클 별도 처리 */
        .sparkle {
            position: absolute;
            top: 15%;
            right: 20%;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 50%;
            animation: sparkle 2s ease-in-out infinite;
            box-shadow: 
                10px 10px 0 -2px rgba(255, 255, 255, 0.3),
                -8px 15px 0 -2px rgba(255, 255, 255, 0.2),
                15px -5px 0 -1px rgba(255, 255, 255, 0.4);
            z-index: 3;
        }

        /* 구분선 스타일 */
        .separator {
            position: absolute;
            left: 25px;
            right: 25px;
            top: calc(15px + 8px + 15px + 3px); /* 패딩 + 폰트크기 + 마진 + 언더라인 */
            height: 1px;
            opacity: 0.4;
            transform: scaleX(0);
            animation: separatorExpand 1.5s ease-out 0.8s forwards;
            z-index: 2;
        }

        .chat_box.naver.chat.streamer .separator {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(155, 77, 224, 0.8) 20%,
                rgba(155, 77, 224, 0.8) 80%,
                transparent 100%);
        }

        .chat_box.naver.chat:not(.streamer) .separator {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(0, 255, 175, 0.8) 20%,
                rgba(0, 255, 175, 0.8) 80%,
                transparent 100%);
        }

        .chat_box.naver.chat.donation .separator {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(255, 215, 0, 0.8) 20%,
                rgba(255, 215, 0, 0.8) 80%,
                transparent 100%);
        }

        .chat_box.naver.chat:not(.streamer) {
            align-self: flex-start;
            background: linear-gradient(135deg, 
                rgba(0, 255, 175, 0.03) 0%, 
                rgba(0, 255, 175, 0.08) 30%,
                rgba(0, 255, 175, 0.12) 50%, 
                rgba(0, 255, 175, 0.08) 70%,
                rgba(0, 255, 175, 0.03) 100%);
            border: 1px solid rgba(0, 255, 175, 0.25);
            border-radius: 25px 25px 25px 8px;
            backdrop-filter: blur(20px);
            box-shadow: 
                0 12px 40px rgba(0, 255, 175, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.06),
                0 0 30px rgba(0, 255, 175, 0.1);
        }

        .chat_box.naver.chat.streamer {
            align-self: flex-end;
            background: linear-gradient(135deg, 
                rgba(155, 77, 224, 0.03) 0%, 
                rgba(155, 77, 224, 0.08) 30%,
                rgba(155, 77, 224, 0.12) 50%, 
                rgba(155, 77, 224, 0.08) 70%,
                rgba(155, 77, 224, 0.03) 100%);
            border: 1px solid rgba(155, 77, 224, 0.25);
            border-radius: 25px 25px 8px 25px;
            backdrop-filter: blur(20px);
            box-shadow: 
                0 12px 40px rgba(155, 77, 224, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.06),
                0 0 30px rgba(155, 77, 224, 0.1);
            animation: messageEntranceRight 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            transform: translateX(120px) rotateY(15deg) scale(0.8);
        }

        @keyframes starTwinkle {
            0% {
                filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.8));
                opacity: 1;
            }
            100% {
                filter: drop-shadow(0 0 15px rgba(255, 215, 0, 1)) drop-shadow(0 0 25px rgba(255, 215, 0, 0.5));
                opacity: 0.8;
            }
        }

        /* 새로운 사이버펑크 애니메이션들 */
        @keyframes dataStreamFlow {
            0% {
                transform: translateY(0) translateX(0);
                opacity: 0.4;
            }
            50% {
                transform: translateY(-50px) translateX(25px);
                opacity: 0.8;
            }
            100% {
                transform: translateY(-100px) translateX(50px);
                opacity: 0.2;
            }
        }

        @keyframes cyberGrid {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1);
            }
            50% {
                opacity: 0.6;
                transform: scale(1.02);
            }
        }

        @keyframes scanlines {
            0% {
                transform: translateY(0);
            }
            100% {
                transform: translateY(4px);
            }
        }

        @keyframes hologramScan {
            0% {
                transform: translateX(-100%);
                opacity: 0;
            }
            10% {
                opacity: 0.8;
            }
            90% {
                opacity: 0.8;
            }
            100% {
                transform: translateX(100%);
                opacity: 0;
            }
        }

        @keyframes particleFlow {
            0%, 100% {
                transform: rotate(0deg) scale(1);
                opacity: 0.3;
            }
            25% {
                transform: rotate(90deg) scale(1.2);
                opacity: 0.7;
            }
            50% {
                transform: rotate(180deg) scale(0.8);
                opacity: 0.5;
            }
            75% {
                transform: rotate(270deg) scale(1.1);
                opacity: 0.6;
            }
        }

        @keyframes hologramGlitch {
            0%, 90%, 100% {
                transform: translate(0);
                filter: hue-rotate(0deg);
            }
            10% {
                transform: translate(-2px, 2px);
                filter: hue-rotate(90deg);
            }
            20% {
                transform: translate(2px, -2px);
                filter: hue-rotate(180deg);
            }
            30% {
                transform: translate(-1px, 1px);
                filter: hue-rotate(270deg);
            }
        }
    </style>
</head>
<body>
    <div class="chat_wrap">
        <div class="chat_list">
            <div class="waiting-message">
                ✨ 치지직 채팅 대기 중...
            </div>
        </div>
    </div>

    <script>
        let lastMessageCount = 0;
        
        async function updateMessages() {
            try {
                const response = await fetch('/api/messages');
                const messages = await response.json();
                
                if (messages.length > lastMessageCount) {
                    const container = document.querySelector('.chat_list');
                    
                    // 대기 메시지 제거
                    const waitingMsg = container.querySelector('.waiting-message');
                    if (waitingMsg) {
                        waitingMsg.style.animation = 'fadeOut 1s ease-out forwards';
                        setTimeout(() => {
                            if (waitingMsg.parentNode) {
                                waitingMsg.remove();
                            }
                        }, 1000);
                    }
                    
                    const newMessages = messages.slice(lastMessageCount);
                    
                    newMessages.forEach((data, index) => {
                        setTimeout(() => {
                            const messageDiv = document.createElement('div');
                            
                            // 클래스 설정
                            let className = 'chat_box naver chat';
                            if (data.is_streamer) {
                                className += ' streamer';
                            } else if (data.type === 'donation') {
                                className += ' donation';
                            }
                            messageDiv.className = className;
                            
                            // 후원 금액 표시
                            const donationAmount = data.type === 'donation' ? 
                                `<span class="donation-amount">💰 ${data.amount ? data.amount.toLocaleString() : 0}원</span>` : '';
                            
                            messageDiv.innerHTML = `
                                <div class="sparkle"></div>
                                <div class="separator"></div>
                                <p class="name">${escapeHtml(data.nickname)}${donationAmount}</p>
                                <p class="text">${escapeHtml(data.message)}</p>
                            `;
                            
                            container.appendChild(messageDiv);
                            
                            // 설정값에 따른 최대 메시지 수 유지
                            while (container.children.length > """ + str(max_messages) + """) {
                                const firstChild = container.firstChild;
                                if (firstChild && !firstChild.classList.contains('waiting-message')) {
                                    firstChild.style.animation = 'fadeOut 1s ease-out forwards';
                                    setTimeout(() => {
                                        if (firstChild.parentNode) {
                                            firstChild.remove();
                                        }
                                    }, 1000);
                                    break;
                                }
                            }
                        }, index * 200); // 메시지별 지연 시간
                    });
                    
                    lastMessageCount = messages.length;
                }
            } catch (e) {
                console.error('메시지 업데이트 실패:', e);
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // 2초마다 새 메시지 체크
        setInterval(updateMessages, 2000);
        
        // 설정 적용 함수
        function applySettings() {
            const maxMessages = """ + str(max_messages) + """;
            const streamerAlignLeft = """ + str(streamer_align_left).lower() + """;
            
            // 최대 메시지 수 디버깅
            console.log('적용된 설정:', {
                maxMessages: maxMessages,
                streamerAlignLeft: streamerAlignLeft
            });
        }
        
        // 초기 설정 적용
        applySettings();
        
        // 초기 로드
        updateMessages();
    </script>
</body>
</html>"""
        
        # 동적 CSS 삽입
        html_template = html_template.replace('</style>', dynamic_css + '\n        </style>')
        
        return html_template
    
    def _generate_dynamic_css(self, max_messages, streamer_align_left, background_enabled, background_opacity, remove_outer_effects):
        """설정값에 따른 동적 CSS 생성"""
        css = ""
        
        # 배경 효과 제거
        if remove_outer_effects:
            css += """
        /* 외부 효과 제거 */
        body::before, body::after {
            display: none !important;
        }
        .chat_box.naver.chat:before,
        .chat_box.naver.chat:after {
            display: none !important;
        }
"""
        
        # 배경 투명도 조정
        if not background_enabled:
            css += """
        /* 배경 완전 투명 */
        .chat_box.naver.chat {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
        }
"""
        else:
            # 배경 투명도 적용
            opacity_value = background_opacity
            css += f"""
        /* 배경 투명도 조정 */
        .chat_box.naver.chat {{
            background: rgba(0, 0, 0, {opacity_value}) !important;
            backdrop-filter: blur({int(opacity_value * 20)}px) !important;
        }}
        .chat_box.naver.chat.streamer {{
            background: linear-gradient(135deg, 
                rgba(155, 77, 224, {opacity_value * 0.4}) 0%, 
                rgba(75, 0, 130, {opacity_value * 0.6}) 50%,
                rgba(138, 43, 226, {opacity_value * 0.4}) 100%) !important;
        }}
        .chat_box.naver.chat.donation {{
            background: linear-gradient(135deg, 
                rgba(255, 215, 0, {opacity_value * 0.3}) 0%, 
                rgba(255, 140, 0, {opacity_value * 0.4}) 30%,
                rgba(255, 69, 0, {opacity_value * 0.5}) 70%,
                rgba(255, 215, 0, {opacity_value * 0.3}) 100%) !important;
        }}
"""
        
        # 스트리머 메시지 왼쪽 정렬
        if streamer_align_left:
            css += """
        /* 스트리머 메시지 왼쪽 정렬 */
        .chat_box.naver.chat.streamer {
            margin-left: 20px !important;
            margin-right: 40px !important;
        }
        .chat_box.naver.chat.streamer .name {
            text-align: left !important;
        }
        .chat_box.naver.chat.streamer .text {
            text-align: left !important;
        }
"""
        else:
            css += """
        /* 스트리머 메시지 기본 정렬 */
        .chat_box.naver.chat.streamer {
            margin-left: 40px !important;
            margin-right: 20px !important;
        }
"""
        
        return css
    
    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

def start_http_server():
    """HTTP 서버 시작"""
    config = ConfigManager()
    port = config.get_server_port()
    
    try:
        # ThreadingHTTPServer 사용으로 동시 연결 처리 개선
        server = http.server.ThreadingHTTPServer(("", port), OverlayHTTPHandler)
        server.timeout = 10  # 10초 타임아웃 설정
        logger.info(f"🌐 HTTP 서버 시작: http://localhost:{port}")
        server.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            logger.error(f"❌ 포트 {port}가 이미 사용 중입니다. 다른 프로그램을 종료하거나 포트를 변경하세요.")
        else:
            logger.error(f"❌ HTTP 서버 시작 실패: {e}")
    except Exception as e:
        logger.error(f"❌ HTTP 서버 오류: {e}")

async def start_chat_overlay():
    """채팅 오버레이 시작"""
    config = ConfigManager()
    port = config.get_server_port()
    
    channel_id = "789d1d9c5b58c847f9f18c8e5073c580"
    
    # HTTP 서버를 별도 스레드에서 실행
    server_thread = threading.Thread(target=start_http_server, daemon=True)
    server_thread.start()
    
    # 채팅 클라이언트 생성 및 연결
    client = ChzzkChatClient(channel_id)
    
    print("🎬 치지직 채팅 오버레이 시작!")
    print(f"📺 OBS 브라우저 소스 URL: http://localhost:{port}/obs")
    print(f"🌐 일반 채팅창 URL: http://localhost:{port}/")
    
    try:
        if await client.connect():
            await client.send_join_message()
            await client.listen_messages()
        else:
            logger.error("❌ 채팅방 연결 실패")
    except Exception as e:
        logger.error(f"오버레이 실행 오류: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(start_chat_overlay())
    except KeyboardInterrupt:
        print("\n👋 채팅 오버레이를 종료합니다.") 