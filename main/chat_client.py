import asyncio
import websockets
import json
import logging
from datetime import datetime
import urllib.request

# 로깅 설정
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        """채팅 채널 ID 조회 (동기 방식) - Old version과 동일한 검증된 로직"""
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
                        
                        # 방송이 꺼져있어도 채팅방 접근 허용 (Old version 방식)
                        if not is_live:
                            logger.warning("현재 방송이 꺼져있지만 채팅방 연결을 시도합니다.")
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
                        
                        # 채팅 채널 ID 추출 (Old version과 동일한 방식)
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
                            logger.debug(f"채팅 채널 ID 없음 - 다음 API 시도: {endpoint}")
                            continue
                    else:
                        logger.debug(f"API 응답 실패 ({response.status}) - 다음 API 시도: {endpoint}")
                        continue
            except Exception as e:
                logger.debug(f"API 호출 실패 - 다음 API 시도: {endpoint}, 오류: {e}")
                continue
        
        # 최후의 수단: 채널 ID를 채팅 채널 ID로 사용
        logger.info("채널 ID를 채팅 채널 ID로 사용합니다.")
        self.chat_channel_id = self.channel_id
        return True
    
    def get_access_token_sync(self):
        """액세스 토큰 획득 - 성공했던 간단한 로직"""
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
        """웹소켓 연결 - Old version과 동일한 검증된 로직"""
        logger.info("=== 채팅방 연결 시작 ===")
        
        # 1단계: 채팅 채널 ID 획득
        logger.info("1단계: 채팅 채널 ID 획득 중...")
        loop = asyncio.get_event_loop()
        if not await loop.run_in_executor(None, self.get_chat_channel_id_sync):
            logger.error("❌ 채팅 채널 ID 획득 실패")
            return False
        logger.info("✅ 채팅 채널 ID 획득 성공")
        
        # 2단계: 액세스 토큰 획득
        logger.info("2단계: 액세스 토큰 획득 중...")
        if not await loop.run_in_executor(None, self.get_access_token_sync):
            logger.error("❌ 액세스 토큰 획득 실패")
            return False
        logger.info("✅ 액세스 토큰 획득 성공")
        
        # 3단계: 웹소켓 연결
        logger.info("3단계: 웹소켓 연결 시도 중...")
        for i, endpoint in enumerate(self.endpoints, 1):
            try:
                logger.info(f"웹소켓 서버 {i}/{len(self.endpoints)} 연결 시도: {endpoint}")
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Origin": "https://chzzk.naver.com"
                }
                self.websocket = await websockets.connect(endpoint, additional_headers=headers)
                self.is_connected = True
                logger.info(f"✅ 웹소켓 연결 성공: {endpoint}")
                logger.info("=== 채팅방 연결 완료 ===")
                return True
            except Exception as e:
                logger.warning(f"❌ 웹소켓 서버 {i} 연결 실패: {e}")
                continue
        
        logger.error("❌ 모든 웹소켓 서버 연결 실패")
        logger.error("💡 해결 방법:")
        logger.error("   1. 네트워크 연결 확인")
        logger.error("   2. 채널 ID가 올바른지 확인")
        logger.error("   3. 방화벽 설정 확인")
        return False
    
    async def send_join_message(self):
        """채팅방 참가 메시지 전송 - 성공했던 간단한 로직"""
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
    
    async def listen_messages(self, message_callback=None):
        """메시지 수신 대기 - 연결 안정성 개선"""
        logger.info("채팅 메시지 수신 시작")
        
        # 하트비트 태스크 시작
        heartbeat_task = asyncio.create_task(self.keep_alive())
        
        try:
            message_count = 0
            async for message in self.websocket:
                try:
                    if message.strip():
                        data = json.loads(message)
                        await self.handle_message(data, message_callback)
                        message_count += 1
                        
                        # 주기적으로 연결 상태 확인
                        if message_count % 100 == 0:
                            logger.debug(f"메시지 {message_count}개 처리됨 - 연결 상태 양호")
                            
                except json.JSONDecodeError:
                    logger.debug(f"JSON 파싱 실패: {message[:100] if len(message) > 100 else message}...")
                except Exception as e:
                    logger.error(f"메시지 처리 오류: {e}")
                    # 메시지 처리 오류는 연결을 끊지 않고 계속 진행
                    continue
                    
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"웹소켓 연결 종료: {e}")
            self.is_connected = False
        except websockets.exceptions.InvalidState as e:
            logger.warning(f"웹소켓 상태 오류 - 재연결 필요: {e}")
            self.is_connected = False
        except websockets.exceptions.WebSocketException as e:
            logger.error(f"웹소켓 오류: {e}")
            self.is_connected = False
        except Exception as e:
            logger.error(f"예상치 못한 메시지 수신 오류: {e}")
            self.is_connected = False
        finally:
            logger.info(f"메시지 수신 종료됨 (총 {message_count}개 처리)")
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
    
    async def handle_message(self, data, message_callback=None):
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
                await self.process_chat_message(data, message_callback)
    
    async def process_chat_message(self, data, message_callback=None):
        """채팅 메시지 파싱 및 저장 - 중복 방지 및 안정성 개선"""
        try:
            cmd = data.get('cmd')
            bdy_list = data.get('bdy', [])
            
            if not bdy_list:
                return
            
            # 배열의 모든 메시지 처리 (Old version은 단일 메시지만 처리했지만 여기서는 개선)
            if isinstance(bdy_list, list):
                # 여러 메시지가 한번에 올 수 있으므로 모두 처리
                for bdy in bdy_list:
                    await self._process_single_message(bdy, cmd, message_callback)
            else:
                # 단일 메시지 처리
                await self._process_single_message(bdy_list, cmd, message_callback)
                    
        except Exception as e:
            logger.error(f"채팅 메시지 파싱 오류: {e}")
    
    async def _process_single_message(self, bdy, cmd, message_callback=None):
        """단일 메시지 처리 - 중복 방지 로직 포함"""
        try:
            # 메시지 ID 기반 중복 체크
            message_id = bdy.get('msgId') or bdy.get('id') or bdy.get('uid', '') + str(bdy.get('msgTime', ''))
            
            # 빈 메시지나 중복 메시지 필터링
            message_text = bdy.get('msg', '').strip()
            if not message_text or not message_id:
                return
            
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
                'id': message_id,  # 중복 방지용 ID 추가
                'type': 'donation' if is_donation else 'chat',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'user_id': bdy.get('uid', ''),
                'nickname': profile.get('nickname', '익명'),
                'message': message_text,
                'is_streamer': is_streamer,
                'user_role': user_role,
                'badge_url': badge.get('imageUrl', '') if badge else '',
                'title_name': title.get('name', '') if title else '',
                'title_color': title.get('color', '#FFFFFF') if title else '#FFFFFF',
                'profile_image': profile.get('profileImageUrl', ''),
                'verified': profile.get('verifiedMark', False),
                'amount': bdy.get('payAmount', 0) if is_donation else 0,
                'msg_time': bdy.get('msgTime', 0)  # 메시지 시간 추가
            }
            
            # 콜백 함수가 있으면 호출
            if message_callback:
                message_callback(chat_data)
            
            # 콘솔 출력
            role_emoji = "👑" if is_streamer else ("💰" if is_donation else "💬")
            amount_text = f" ({chat_data['amount']}원)" if is_donation else ""
            print(f"{role_emoji} [{chat_data['timestamp']}] {chat_data['nickname']}: {chat_data['message']}{amount_text}")
                    
        except Exception as e:
            logger.error(f"단일 메시지 처리 오류: {e}")
    
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