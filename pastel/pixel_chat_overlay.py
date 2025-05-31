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

class PastelChatHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """파스텔 채팅 오버레이 HTTP 핸들러"""
    
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
                html = self.get_pastel_chat_html()
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
    
    def get_pastel_chat_html(self):
        """레트로 픽셀 파스텔 컨셉의 채팅 오버레이 HTML"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕹️ Retro Pixel Pastel Chat 🕹️</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        
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
            font-family: 'Press Start 2P', 'Noto Sans KR', monospace;
        }

        /* 레트로 픽셀 배경 효과 */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(255, 102, 204, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(102, 255, 255, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(255, 255, 102, 0.10) 0%, transparent 50%),
                linear-gradient(45deg, transparent 49%, rgba(255, 102, 204, 0.03) 50%, transparent 51%),
                linear-gradient(-45deg, transparent 49%, rgba(102, 255, 255, 0.03) 50%, transparent 51%);
            background-size: 400px 400px, 300px 300px, 200px 200px, 20px 20px, 20px 20px;
            animation: pixelFloat 8s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }

        @keyframes pixelFloat {
            0%, 100% { 
                transform: translate(0, 0);
                opacity: 0.8;
            }
            25% { 
                transform: translate(10px, -5px);
                opacity: 0.6;
            }
            50% { 
                transform: translate(-5px, 10px);
                opacity: 1;
            }
            75% { 
                transform: translate(-10px, -5px);
                opacity: 0.7;
            }
        }
        
        .chat_wrap {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 540px;
            height: 620px;
            background: transparent;
            z-index: 1000;
            overflow: hidden;
            padding: 15px;
        }

        .chat_list {
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            gap: 12px;
            height: 100%;
            overflow: hidden;
            position: relative;
            z-index: 2;
            /* 픽셀 스타일 페이드아웃 */
            mask: linear-gradient(to bottom, 
                transparent 0%, 
                rgba(0,0,0,0.1) 8%, 
                rgba(0,0,0,0.4) 20%, 
                rgba(0,0,0,0.8) 35%, 
                black 50%, 
                black 100%);
            -webkit-mask: linear-gradient(to bottom, 
                transparent 0%, 
                rgba(0,0,0,0.1) 8%, 
                rgba(0,0,0,0.4) 20%, 
                rgba(0,0,0,0.8) 35%, 
                black 50%, 
                black 100%);
        }

        .chat_box.pixel.chat {
            padding: 12px 16px;
            margin: 8px 30px;
            position: relative;
            z-index: 2;
            animation: pixelPop 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
            transform: translateX(-100px) scale(0.8);
            opacity: 0;
            max-width: calc(100% - 60px);
            background: linear-gradient(135deg, 
                rgba(0, 0, 0, 0.7) 0%,
                rgba(20, 20, 40, 0.8) 100%);
            border: 3px solid;
            box-shadow: 
                0 0 0 2px rgba(0, 0, 0, 0.8),
                inset 0 0 0 1px rgba(255, 255, 255, 0.2),
                0 4px 0 0 rgba(0, 0, 0, 0.5),
                0 8px 16px rgba(0, 0, 0, 0.4);
            image-rendering: pixelated;
        }

        /* 픽셀 스타일 등장 애니메이션 */
        @keyframes pixelPop {
            0% {
                transform: translateX(-100px) scale(0.8);
                opacity: 0;
            }
            70% {
                transform: translateX(8px) scale(1.1);
                opacity: 0.9;
            }
            100% {
                transform: translateX(0) scale(1);
                opacity: 1;
            }
        }

        /* 스트리머 스타일 - 핫 핑크 네온 */
        .chat_box.pixel.chat.streamer {
            border-color: #FF66CC;
            background: linear-gradient(135deg, 
                rgba(255, 102, 204, 0.2) 0%,
                rgba(20, 20, 40, 0.9) 100%);
            box-shadow: 
                0 0 0 2px #FF66CC,
                inset 0 0 0 1px rgba(255, 102, 204, 0.3),
                0 4px 0 0 #CC0066,
                0 8px 16px rgba(255, 102, 204, 0.4),
                0 0 20px rgba(255, 102, 204, 0.6);
            align-self: flex-end;
            border-radius: 0 0 0 8px;
        }

        /* 일반 유저 스타일 - 시안 네온 */
        .chat_box.pixel.chat:not(.streamer):not(.donation) {
            border-color: #66FFFF;
            background: linear-gradient(135deg, 
                rgba(102, 255, 255, 0.2) 0%,
                rgba(20, 20, 40, 0.9) 100%);
            box-shadow: 
                0 0 0 2px #66FFFF,
                inset 0 0 0 1px rgba(102, 255, 255, 0.3),
                0 4px 0 0 #0066CC,
                0 8px 16px rgba(102, 255, 255, 0.4),
                0 0 20px rgba(102, 255, 255, 0.6);
            align-self: flex-start;
            border-radius: 0 0 8px 0;
        }

        /* 후원 메시지 스타일 - 골드 네온 */
        .chat_box.pixel.chat.donation {
            border-color: #FFFF66;
            background: linear-gradient(135deg, 
                rgba(255, 255, 102, 0.2) 0%,
                rgba(40, 40, 20, 0.9) 100%);
            box-shadow: 
                0 0 0 2px #FFFF66,
                inset 0 0 0 1px rgba(255, 255, 102, 0.3),
                0 4px 0 0 #CCCC00,
                0 8px 16px rgba(255, 255, 102, 0.4),
                0 0 20px rgba(255, 255, 102, 0.6);
            animation: pixelGoldPop 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
        }

        @keyframes pixelGoldPop {
            0% {
                transform: translateY(30px) scale(0.5);
                opacity: 0;
            }
            50% {
                transform: translateY(-10px) scale(1.2);
                opacity: 0.8;
            }
            100% {
                transform: translateY(0) scale(1);
                opacity: 1;
            }
        }

        .chat_box.pixel.chat p.name {
            display: block;
            font-weight: normal;
            font-size: 10px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
            font-family: 'Press Start 2P', monospace;
            line-height: 12px;
        }

        .chat_box.pixel.chat.streamer p.name {
            color: #FF66CC;
            text-shadow: 
                1px 1px 0 #CC0066,
                0 0 10px rgba(255, 102, 204, 0.8);
            animation: pixelGlowPink 2s ease-in-out infinite alternate;
        }

        .chat_box.pixel.chat:not(.streamer):not(.donation) p.name {
            color: #66FFFF;
            text-shadow: 
                1px 1px 0 #0066CC,
                0 0 10px rgba(102, 255, 255, 0.8);
            animation: pixelGlowCyan 2s ease-in-out infinite alternate;
        }

        .chat_box.pixel.chat.donation p.name {
            color: #FFFF66;
            text-shadow: 
                1px 1px 0 #CCCC00,
                0 0 10px rgba(255, 255, 102, 0.8);
            animation: pixelGlowGold 1.5s ease-in-out infinite alternate;
        }

        @keyframes pixelGlowPink {
            0% { 
                text-shadow: 1px 1px 0 #CC0066, 0 0 10px rgba(255, 102, 204, 0.8); 
            }
            100% { 
                text-shadow: 1px 1px 0 #CC0066, 0 0 20px rgba(255, 102, 204, 1), 0 0 30px rgba(255, 102, 204, 0.6); 
            }
        }

        @keyframes pixelGlowCyan {
            0% { 
                text-shadow: 1px 1px 0 #0066CC, 0 0 10px rgba(102, 255, 255, 0.8); 
            }
            100% { 
                text-shadow: 1px 1px 0 #0066CC, 0 0 20px rgba(102, 255, 255, 1), 0 0 30px rgba(102, 255, 255, 0.6); 
            }
        }

        @keyframes pixelGlowGold {
            0% { 
                text-shadow: 1px 1px 0 #CCCC00, 0 0 10px rgba(255, 255, 102, 0.8); 
            }
            100% { 
                text-shadow: 1px 1px 0 #CCCC00, 0 0 20px rgba(255, 255, 102, 1), 0 0 30px rgba(255, 255, 102, 0.6); 
            }
        }

        /* 픽셀 구분선 */
        .chat_box.pixel.chat::after {
            content: '';
            position: absolute;
            left: 16px;
            right: 16px;
            top: calc(12px + 8px + 12px);
            height: 2px;
            background: currentColor;
            opacity: 0.6;
            transform: scaleX(0);
            animation: pixelLine 1s ease-out 0.5s forwards;
            z-index: 1;
            image-rendering: pixelated;
        }

        @keyframes pixelLine {
            0% { transform: scaleX(0); }
            100% { transform: scaleX(1); }
        }

        .chat_box.pixel.chat p.text {
            color: #FFFFFF;
            font-size: 9px;
            line-height: 14px;
            font-weight: normal;
            text-shadow: 1px 1px 0 rgba(0, 0, 0, 0.8);
            animation: pixelType 1s ease-out 0.3s forwards;
            opacity: 0;
            position: relative;
            font-family: 'Press Start 2P', monospace;
        }

        @keyframes pixelType {
            0% {
                opacity: 0;
                transform: translateY(10px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .donation-amount {
            display: inline-block;
            background: linear-gradient(135deg, #FFFF66, #FFCC00);
            color: #000000;
            padding: 2px 6px;
            font-size: 8px;
            font-weight: normal;
            margin-left: 6px;
            border: 2px solid #CCCC00;
            box-shadow: 
                0 0 0 1px #FFFF66,
                0 2px 0 0 #999900,
                0 0 10px rgba(255, 255, 102, 0.6);
            animation: pixelCoin 1s ease-in-out 0.6s;
            transform: scale(0);
            font-family: 'Press Start 2P', monospace;
            image-rendering: pixelated;
        }

        @keyframes pixelCoin {
            0% {
                transform: scale(0) rotate(0deg);
                opacity: 0;
            }
            50% {
                transform: scale(1.3) rotate(180deg);
                opacity: 0.8;
            }
            100% {
                transform: scale(1) rotate(360deg);
                opacity: 1;
            }
        }

        .waiting-message {
            text-align: center;
            color: #66FFFF;
            padding: 16px;
            background: linear-gradient(135deg, 
                rgba(0, 0, 0, 0.8) 0%, 
                rgba(20, 20, 40, 0.9) 100%);
            border: 3px solid #66FFFF;
            box-shadow: 
                0 0 0 2px rgba(0, 0, 0, 0.8),
                inset 0 0 0 1px rgba(102, 255, 255, 0.3),
                0 4px 0 0 #0066CC,
                0 0 20px rgba(102, 255, 255, 0.6);
            animation: pixelBlink 2s ease-in-out infinite;
            position: relative;
            overflow: hidden;
            font-family: 'Press Start 2P', monospace;
            font-size: 10px;
            line-height: 14px;
            text-shadow: 1px 1px 0 #0066CC;
            image-rendering: pixelated;
        }

        @keyframes pixelBlink {
            0%, 100% {
                opacity: 0.8;
                box-shadow: 
                    0 0 0 2px rgba(0, 0, 0, 0.8),
                    inset 0 0 0 1px rgba(102, 255, 255, 0.3),
                    0 4px 0 0 #0066CC,
                    0 0 20px rgba(102, 255, 255, 0.6);
            }
            50% {
                opacity: 1;
                box-shadow: 
                    0 0 0 2px rgba(0, 0, 0, 0.8),
                    inset 0 0 0 1px rgba(102, 255, 255, 0.5),
                    0 4px 0 0 #0066CC,
                    0 0 30px rgba(102, 255, 255, 1);
            }
        }

        /* 8비트 스타일 페이드아웃 */
        @keyframes pixelFadeOut {
            0% {
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.5;
                transform: scale(0.9);
            }
            100% {
                opacity: 0;
                transform: scale(0.8) translateY(-20px);
            }
        }
    </style>
</head>
<body>
    <div class="chat_wrap">
        <div class="chat_list">
            <div class="waiting-message">
                🕹️ PIXEL CHAT LOADING...
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
                        waitingMsg.style.animation = 'pixelFadeOut 1s ease-out forwards';
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
                            let className = 'chat_box pixel chat';
                            if (data.is_streamer) {
                                className += ' streamer';
                            } else if (data.type === 'donation') {
                                className += ' donation';
                            }
                            messageDiv.className = className;
                            
                            // 후원 금액 표시
                            const donationAmount = data.type === 'donation' ? 
                                `<span class="donation-amount">💰 ${data.amount ? data.amount.toLocaleString() : 0}C</span>` : '';
                            
                            messageDiv.innerHTML = `
                                <p class="name">${escapeHtml(data.nickname)}${donationAmount}</p>
                                <p class="text">${escapeHtml(data.message)}</p>
                            `;
                            
                            container.appendChild(messageDiv);
                            
                            // 최대 12개 메시지 유지 (픽셀 스타일에 맞게)
                            while (container.children.length > 12) {
                                const firstChild = container.firstChild;
                                if (firstChild && !firstChild.classList.contains('waiting-message')) {
                                    firstChild.style.animation = 'pixelFadeOut 1s ease-out forwards';
                                    setTimeout(() => {
                                        if (firstChild.parentNode) {
                                            firstChild.remove();
                                        }
                                    }, 1000);
                                    break;
                                }
                            }
                        }, index * 300); // 픽셀 스타일에 맞게 조금 더 느리게
                    });
                    
                    lastMessageCount = messages.length;
                }
            } catch (e) {
                console.error('PIXEL CHAT ERROR:', e);
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // 2초마다 새 메시지 체크
        setInterval(updateMessages, 2000);
        
        // 초기 로드
        updateMessages();
    </script>
</body>
</html>"""

    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

def start_http_server():
    """HTTP 서버 시작"""
    try:
        # ThreadingHTTPServer 사용으로 동시 연결 처리 개선
        server = http.server.ThreadingHTTPServer(("", 8081), PastelChatHTTPHandler)
        server.timeout = 10  # 10초 타임아웃 설정
        logger.info("🎨 파스텔 채팅 HTTP 서버 시작: http://localhost:8081")
        server.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            logger.error("❌ 포트 8081이 이미 사용 중입니다. 다른 프로그램을 종료하거나 포트를 변경하세요.")
        else:
            logger.error(f"❌ HTTP 서버 시작 실패: {e}")
    except Exception as e:
        logger.error(f"❌ HTTP 서버 오류: {e}")

async def start_pastel_chat_overlay():
    """파스텔 채팅 오버레이 시작"""
    channel_id = "789d1d9c5b58c847f9f18c8e5073c580"
    
    # HTTP 서버를 별도 스레드에서 실행
    server_thread = threading.Thread(target=start_http_server, daemon=True)
    server_thread.start()
    
    # 채팅 클라이언트 생성 및 연결
    client = ChzzkChatClient(channel_id)
    
    print("🎨 파스텔 채팅 오버레이 시작!")
    print("📺 OBS 브라우저 소스 URL: http://localhost:8081/obs")
    print("🌐 일반 채팅창 URL: http://localhost:8081/")
    
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
        asyncio.run(start_pastel_chat_overlay())
    except KeyboardInterrupt:
        print("\n👋 파스텔 채팅 오버레이를 종료합니다.") 
        print("\n👋 파스텔 채팅 오버레이를 종료합니다.") 