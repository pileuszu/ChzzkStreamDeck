import json
import logging
import base64
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from config import config_manager

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 글로벌 토큰 저장소
access_token = None
refresh_token = None
token_expires_at = None
current_track_data = {}

class SpotifyAPI:
    """Spotify API 클라이언트"""
    
    def __init__(self):
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        
    def get_client_credentials(self):
        """설정에서 클라이언트 인증 정보 가져오기"""
        return {
            'client_id': config_manager.get("modules.spotify.client_id"),
            'client_secret': config_manager.get("modules.spotify.client_secret"),
            'redirect_uri': config_manager.get("modules.spotify.redirect_uri")
        }
        
    def get_auth_url(self):
        """인증 URL 생성"""
        credentials = self.get_client_credentials()
        
        params = {
            'client_id': credentials['client_id'],
            'response_type': 'code',
            'redirect_uri': credentials['redirect_uri'],
            'scope': "user-read-currently-playing user-read-playback-state",
            'show_dialog': 'true'
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"https://accounts.spotify.com/authorize?{query_string}"
    
    def get_access_token(self, auth_code):
        """인증 코드로 액세스 토큰 획득"""
        global access_token, refresh_token, token_expires_at
        
        credentials = self.get_client_credentials()
        
        # Basic Auth 헤더 생성
        credentials_str = f"{credentials['client_id']}:{credentials['client_secret']}"
        credentials_b64 = base64.b64encode(credentials_str.encode()).decode()
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': credentials['redirect_uri']
        }
        
        try:
            data_encoded = urllib.parse.urlencode(data).encode()
            req = urllib.request.Request(self.auth_url, data=data_encoded, method='POST')
            req.add_header('Authorization', f'Basic {credentials_b64}')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode())
                    access_token = result['access_token']
                    refresh_token = result['refresh_token']
                    expires_in = result['expires_in']
                    token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    logger.info("✅ Spotify 액세스 토큰 획득 성공!")
                    return True
                else:
                    logger.error(f"❌ 토큰 획득 실패: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ 토큰 획득 오류: {e}")
            return False
    
    def refresh_access_token(self):
        """리프레시 토큰으로 액세스 토큰 갱신"""
        global access_token, token_expires_at
        
        if not refresh_token:
            return False
            
        credentials = self.get_client_credentials()
        
        # Basic Auth 헤더 생성
        credentials_str = f"{credentials['client_id']}:{credentials['client_secret']}"
        credentials_b64 = base64.b64encode(credentials_str.encode()).decode()
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        try:
            data_encoded = urllib.parse.urlencode(data).encode()
            req = urllib.request.Request(self.auth_url, data=data_encoded, method='POST')
            req.add_header('Authorization', f'Basic {credentials_b64}')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode())
                    access_token = result['access_token']
                    expires_in = result['expires_in']
                    token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    logger.info("🔄 Spotify 토큰 갱신 성공!")
                    return True
                else:
                    logger.error(f"❌ 토큰 갱신 실패: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ 토큰 갱신 오류: {e}")
            return False
    
    def get_current_track(self):
        """현재 재생 중인 트랙 정보 가져오기"""
        global current_track_data
        
        if not access_token:
            return None
            
        # 토큰 만료 확인
        if token_expires_at and datetime.now() >= token_expires_at:
            if not self.refresh_access_token():
                return None
        
        url = f"{self.base_url}/me/player/currently-playing"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'Bearer {access_token}')
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    
                    if data and 'item' in data:
                        track = data['item']
                        current_track_data = {
                            'is_playing': data.get('is_playing', False),
                            'progress_ms': data.get('progress_ms', 0),
                            'track_name': track.get('name', '알 수 없음'),
                            'artist_name': ', '.join([artist['name'] for artist in track.get('artists', [])]),
                            'album_name': track.get('album', {}).get('name', '알 수 없음'),
                            'album_image': track.get('album', {}).get('images', [{}])[0].get('url', ''),
                            'duration_ms': track.get('duration_ms', 0),
                            'external_url': track.get('external_urls', {}).get('spotify', ''),
                            'popularity': track.get('popularity', 0)
                        }
                        return current_track_data
                elif response.status == 204:
                    # 재생 중인 트랙 없음
                    current_track_data = {'is_playing': False, 'track_name': '재생 중인 음악 없음'}
                    return current_track_data
                else:
                    logger.warning(f"⚠️ API 응답 오류: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ 현재 트랙 조회 오류: {e}")
            return None

def get_current_track_data():
    """현재 트랙 데이터 반환"""
    return current_track_data

def is_authenticated():
    """인증 상태 확인"""
    global access_token, token_expires_at
    
    # 토큰이 없으면 인증되지 않음
    if not access_token:
        return False
    
    # 토큰이 만료되었으면 갱신 시도
    if token_expires_at and datetime.now() >= token_expires_at:
        logger.info("Spotify 토큰이 만료되었습니다. 갱신을 시도합니다.")
        spotify_api = SpotifyAPI()
        if spotify_api.refresh_access_token():
            logger.info("Spotify 토큰 갱신 성공!")
            return True
        else:
            logger.warning("Spotify 토큰 갱신 실패!")
            return False
    
    return True 