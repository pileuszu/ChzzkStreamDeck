# 🛠️ 설정 가이드

## 1. 저장소 클론 후 초기 설정

```bash
# 저장소 클론
git clone <your-repository-url>
cd Chat

# 환경 변수 파일 생성
cp env.example .env
```

## 2. 환경 변수 설정

`.env` 파일을 열어서 다음 정보를 입력하세요:

### 🎵 Spotify API 설정

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) 방문
2. "Create App" 클릭
3. 앱 정보 입력:
   - **App name**: `Chat Overlay` (원하는 이름)
   - **App description**: `Stream overlay for chat and music`
   - **Redirect URI**: `http://localhost:8080/spotify/callback`
4. 생성된 **Client ID**와 **Client Secret**를 복사
5. `.env` 파일에 입력:

```env
SPOTIFY_CLIENT_ID=복사한_클라이언트_ID
SPOTIFY_CLIENT_SECRET=복사한_클라이언트_시크릿
```

### 🎮 네이버 게임 채팅 설정 (선택사항)

네이버 게임 방송의 채팅을 표시하려면:

1. 네이버 게임 방송 페이지에서 채널 ID 확인
2. `.env` 파일에 추가:

```env
NAVER_CHAT_CHANNEL_ID=your_channel_id
```

## 3. 의존성 설치

```bash
# 가상환경 생성 (권장)
python -m venv .venv

# 가상환경 활성화
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

## 4. 실행 및 테스트

### 🌟 Neon 테마 (권장)
```bash
cd neon
python main.py
```

브라우저에서 `http://localhost:8080` 접속하여 관리자 패널 확인

### 🎨 Pastel 테마
```bash
cd pastel
python spotify_pixel_overlay.py
```

## 5. OBS Studio 설정

1. **소스 추가** → **브라우저 소스**
2. URL 설정:
   - **Spotify**: `http://localhost:8080/spotify`
   - **채팅**: `http://localhost:8080/chat`
   - **백그라운드**: `http://localhost:8080/background1`
3. **사용자 지정 CSS** (투명 배경):
```css
body { background-color: rgba(0, 0, 0, 0); }
```

## 6. 문제 해결

### ❌ Spotify 연결 실패
- Client ID/Secret 확인
- Redirect URI가 정확한지 확인: `http://localhost:8080/spotify/callback`
- Spotify 앱에서 해당 URI가 등록되어 있는지 확인

### ❌ 모듈 import 오류
```bash
pip install --upgrade -r requirements.txt
```

### ❌ 포트 충돌
`.env` 파일에서 `SERVER_PORT` 변경:
```env
SERVER_PORT=8081
```

## 7. 보안 주의사항

⚠️ **절대로 하지 말 것:**
- `.env` 파일을 Git에 커밋하지 마세요
- API 키를 코드에 하드코딩하지 마세요  
- 스트림에서 설정 화면을 공유하지 마세요

✅ **권장사항:**
- `.env` 파일은 로컬에만 보관
- API 키는 정기적으로 재생성
- 방송 전 오버레이가 개인정보를 표시하지 않는지 확인 