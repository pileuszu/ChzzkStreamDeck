# 🎵 Chat & Music Overlay System

실시간 채팅과 음악 정보를 화면에 오버레이로 표시하는 스트리밍 도구입니다.

## ✨ 기능

### 📡 지원 서비스
- **Spotify**: 현재 재생 중인 음악 정보 표시
- **네이버 게임 채팅**: 실시간 채팅 메시지 표시

## 🚀 빠른 시작

### 1. 환경 설정

먼저 환경 변수 파일을 설정하세요:

```bash
# env.example을 복사하여 .env 파일 생성
cp env.example .env
```

`.env` 파일에서 다음 정보를 입력하세요:

```env
# Spotify API 설정 (https://developer.spotify.com/dashboard 에서 발급)
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# 서버 설정
SERVER_HOST=localhost
SERVER_PORT=8080

# 네이버 게임 채팅 설정 (필요시)
NAVER_CHAT_CHANNEL_ID=your_channel_id_here
```

### 2. 의존성 설치

```bash
# Python 가상환경 생성 (권장)
python -m venv .venv

# 가상환경 활성화
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 실행

#### Neon 테마 (통합 서버)
```bash
cd neon
python main.py
```

#### 자동 실행 스크립트 사용
```bash
# Windows
start_app.bat

# Linux/Mac
./start_app.sh
```

## 📁 프로젝트 구조

```
├── neon/                    # Neon 테마 (통합 서버)
│   ├── unified_server.py    # 통합 웹 서버
│   ├── admin_panel.py       # 관리자 패널
│   ├── config.py           # 설정 관리
│   ├── spotify_api.py      # Spotify API 연동
│   ├── chat_server.py      # 채팅 서버
│   └── ...
├── pastel/                  # Pastel 테마 (개별 실행)
│   ├── spotify_pixel_overlay.py
│   ├── pixel_chat_overlay.py
│   └── background_effect_2.py
├── .env                    # 환경 변수 (자동 무시됨)
├── env.example             # 환경 변수 템플릿
├── .gitignore             # Git 무시 파일 목록
└── README.md              # 이 파일
```

## ⚙️ 설정

### Spotify API 설정

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) 접속
2. 새 앱 생성
3. Client ID와 Client Secret 복사
4. Redirect URI 설정: `http://localhost:8080/spotify/callback`
5. `.env` 파일에 정보 입력

### 네이버 게임 채팅 설정

1. 네이버 게임 방송 채널 ID 확인
2. `.env` 파일에 `NAVER_CHAT_CHANNEL_ID` 설정

## 🔧 사용법

### 웹 인터페이스 (Neon 테마)
브라우저에서 `http://localhost:8080` 접속하여 관리자 패널 사용

### OBS 설정
1. 소스 추가 → 브라우저 소스
2. URL 입력:
   - Spotify: `http://localhost:8080/spotify`
   - 채팅: `http://localhost:8080/chat`
   - 백그라운드: `http://localhost:8080/background1` 또는 `background2`
3. 투명 배경 활성화

## 🛠️ 개발

### 요구사항
- Python 3.8+
- pygame
- tkinter
- PIL (Pillow)
- requests
- numpy

### 코드 구조
- `neon/`: 모던한 웹 기반 인터페이스
- `pastel/`: 경량화된 독립 실행 오버레이

## 📝 라이선스

이 프로젝트는 개인 및 비상업적 용도로 자유롭게 사용할 수 있습니다.

## 🤝 기여

이슈 제보나 기능 제안은 GitHub Issues를 통해 해주세요.

## ⚠️ 주의사항

- `.env` 파일은 절대 공개 저장소에 업로드하지 마세요
- Spotify API 키는 안전하게 보관하세요
- 방송 중 개인정보가 노출되지 않도록 주의하세요 