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
        self.channel_id = channel_id.strip() if channel_id else ""
        self.chat_channel_id = None
        self.access_token = None
        self.websocket = None
        self.is_connected = False
        
        # 입력 검증
        if not self.channel_id:
            raise ValueError("❌ 채널 ID가 비어있습니다!")
        
        logger.info(f"📺 채팅 클라이언트 초기화: 채널 ID = {self.channel_id}")
        
        # 웹소켓 엔드포인트들
        self.endpoints = [
            f"wss://kr-ss{i}.chat.naver.com/chat" for i in range(1, 6)
        ]
    
    def get_chat_channel_id_sync(self):
        """채팅 채널 ID 조회 (동기 방식)"""
        # 1단계: 다중 API로 채널 정보 조회
        channel_apis = [
            f"https://api.chzzk.naver.com/service/v1/channels/{self.channel_id}",
            f"https://api.chzzk.naver.com/service/v2/channels/{self.channel_id}",
        ]
        
        channel_info = None
        for api_url in channel_apis:
            try:
                req = urllib.request.Request(api_url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                req.add_header('Accept', 'application/json')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        channel_data = json.loads(response.read().decode('utf-8'))
                        
                        if 'content' in channel_data and channel_data['content']:
                            channel_info = channel_data['content']
                            break
            except Exception as e:
                logger.debug(f"API 시도 실패 {api_url}: {e}")
                continue
        
        if not channel_info:
            logger.error("채널 정보를 찾을 수 없습니다. 채널 ID를 확인해주세요.")
            return False
        
        # 채널 기본 정보 확인
        channel_name = channel_info.get('channelName', '알 수 없음')
        logger.info(f"📺 채널명: {channel_name}")
        
        # 방송 상태는 여러 방법으로 체크 (openLive가 항상 정확하지 않음)
        is_live_basic = channel_info.get('openLive', False)
        logger.info(f"🔴 기본 방송 상태: {'방송 중' if is_live_basic else '방송 종료'}")
        
        # 기본 체크에서 방송이 꺼져있어도 라이브 디테일을 확인해보자
        if not is_live_basic:
            logger.info("기본 상태가 방송 종료지만 라이브 상세 정보를 확인합니다...")
        
        return True  # 기본 정보만으로도 진행
        
        # 2단계: 라이브 상세 정보에서 채팅 채널 ID 획득
        api_endpoints = [
            f"https://api.chzzk.naver.com/service/v2/channels/{self.channel_id}/live-detail",
            f"https://api.chzzk.naver.com/service/v1/channels/{self.channel_id}/live-detail",
            f"https://api.chzzk.naver.com/service/v1/channels/{self.channel_id}/live-status",
            f"https://api.chzzk.naver.com/polling/v2/channels/{self.channel_id}/live-status",
            f"https://api.chzzk.naver.com/polling/v1/channels/{self.channel_id}/live-status",
        ]
        
        for i, endpoint in enumerate(api_endpoints):
            try:
                logger.info(f"🔍 라이브 정보 조회 시도 ({i+1}/{len(api_endpoints)}): {endpoint}")
                req = urllib.request.Request(endpoint)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                req.add_header('Accept', 'application/json')
                req.add_header('Referer', 'https://chzzk.naver.com/')
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        # 채팅 채널 ID 추출 (다양한 경로 시도)
                        chat_channel_id = None
                        
                        # 경로 1: content.chatChannelId
                        if 'content' in data and data['content'] and 'chatChannelId' in data['content']:
                            chat_channel_id = data['content']['chatChannelId']
                        
                        # 경로 2: content.live.chatChannelId  
                        elif 'content' in data and data['content'] and 'live' in data['content'] and data['content']['live'] and 'chatChannelId' in data['content']['live']:
                            chat_channel_id = data['content']['live']['chatChannelId']
                        
                        # 경로 3: content.liveDetail.chatChannelId
                        elif 'content' in data and data['content'] and 'liveDetail' in data['content'] and data['content']['liveDetail'] and 'chatChannelId' in data['content']['liveDetail']:
                            chat_channel_id = data['content']['liveDetail']['chatChannelId']
                        
                        # 경로 4: content.status 확인
                        elif 'content' in data and data['content']:
                            status = data['content'].get('status', 'CLOSE')
                            logger.info(f"📊 방송 상태: {status}")
                            
                            if status == 'OPEN':
                                logger.info("✅ 방송이 진행 중입니다!")
                                # 채널 ID를 채팅 채널 ID로 사용
                                chat_channel_id = self.channel_id
                        
                        if chat_channel_id:
                            self.chat_channel_id = chat_channel_id
                            logger.info(f"✅ 채팅 채널 ID 획득: {self.chat_channel_id}")
                            return True
                        else:
                            logger.debug(f"응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
                            continue
                    else:
                        logger.debug(f"API 응답 실패: {response.status}")
                        continue
            except Exception as e:
                logger.debug(f"API 호출 실패 {endpoint}: {e}")
                continue
        
        # 최후의 수단: 채널 ID를 채팅 채널 ID로 사용
        logger.info("⚠️ 채팅 채널 ID를 찾지 못했습니다. 채널 ID를 채팅 채널 ID로 사용합니다.")
        self.chat_channel_id = self.channel_id
        return True
    
    def get_access_token_sync(self):
        """액세스 토큰 획득"""
        if not self.chat_channel_id:
            logger.error("채팅 채널 ID가 없습니다.")
            return False
        
        # 다양한 토큰 API 엔드포인트 시도
        token_apis = [
            f"https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId={self.chat_channel_id}&chatType=STREAMING",
            f"https://comm-api.game.naver.com/nng_main/v2/chats/access-token?channelId={self.chat_channel_id}&chatType=STREAMING",
            f"https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId={self.chat_channel_id}",
        ]
        
        for i, url in enumerate(token_apis):
            try:
                logger.info(f"🔑 액세스 토큰 조회 시도 ({i+1}/{len(token_apis)})")
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                req.add_header('Accept', 'application/json')
                req.add_header('Referer', 'https://chzzk.naver.com/')
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        # 토큰 추출 (다양한 경로)
                        access_token = None
                        if 'content' in data and 'accessToken' in data['content']:
                            access_token = data['content']['accessToken']
                        elif 'content' in data and 'access_token' in data['content']:
                            access_token = data['content']['access_token']
                        elif 'accessToken' in data:
                            access_token = data['accessToken']
                        
                        if access_token:
                            self.access_token = access_token
                            logger.info("✅ 액세스 토큰 획득 성공")
                            return True
                        else:
                            logger.debug(f"토큰 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
                            continue
                    else:
                        logger.debug(f"토큰 API 응답 실패: {response.status}")
                        continue
            except Exception as e:
                logger.debug(f"토큰 API 호출 실패: {e}")
                continue
        
        # 토큰 없이도 진행 시도 (일부 채널에서는 토큰이 필요 없을 수 있음)
        logger.warning("⚠️ 액세스 토큰을 얻지 못했지만 토큰 없이 연결을 시도합니다.")
        self.access_token = None
        return True
    
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
        for attempt in range(3):  # 3번 재시도
            for endpoint in self.endpoints:
                try:
                    logger.info(f"웹소켓 연결 시도 ({attempt+1}/3): {endpoint}")
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Origin": "https://chzzk.naver.com"
                    }
                    self.websocket = await websockets.connect(
                        endpoint, 
                        additional_headers=headers,
                        ping_timeout=20,
                        ping_interval=20,
                        close_timeout=10
                    )
                    self.is_connected = True
                    logger.info(f"웹소켓 연결 성공: {endpoint}")
                    return True
                except Exception as e:
                    logger.warning(f"연결 실패 {endpoint}: {e}")
                    continue
            
            # 재시도 전 잠시 대기
            if attempt < 2:
                logger.info(f"재시도 전 대기 중... ({attempt+1}/3)")
                await asyncio.sleep(2)
        
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
    
    async def listen_messages(self, message_callback=None):
        """메시지 수신 대기"""
        logger.info("채팅 메시지 수신 시작")
        
        # 하트비트 태스크 시작
        heartbeat_task = asyncio.create_task(self.keep_alive())
        
        try:
            async for message in self.websocket:
                try:
                    if message.strip():
                        data = json.loads(message)
                        await self.handle_message(data, message_callback)
                except json.JSONDecodeError:
                    logger.warning(f"JSON 파싱 실패: {message[:100]}...")
                except Exception as e:
                    logger.error(f"메시지 처리 오류: {e}")
                    
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"웹소켓 연결 종료: {e}")
            self.is_connected = False
        except websockets.exceptions.InvalidState as e:
            logger.warning(f"웹소켓 상태 오류: {e}")
            self.is_connected = False
        except Exception as e:
            logger.error(f"메시지 수신 오류: {e}")
            self.is_connected = False
        finally:
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
            
            # 콜백 함수가 있으면 호출
            if message_callback:
                message_callback(chat_data)
            
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