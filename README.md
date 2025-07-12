# 🎮 ChzzkStreamDeck v2.0

**CHZZK (치지직) 스트리밍 위젯 시스템**

OBS Studio에서 사용할 수 있는 실시간 채팅 오버레이 시스템입니다.

## ✨ 주요 기능

- 🎨 **다중 테마 지원**: 마법같은 Simple Purple, 사이버펑크 Neon Green
- 💬 **실시간 채팅**: CHZZK WebSocket 연결
- 😀 **이모티콘 지원**: CHZZK 이모티콘 실시간 표시
- 📡 **Server-Sent Events**: 실시간 데이터 스트리밍
- 🎛️ **웹 컨트롤 패널**: 브라우저에서 설정 관리
- 🎥 **방송 최적화**: 깔끔한 오버레이 인터페이스
- ✨ **고급 애니메이션**: 부드러운 입장/퇴장 효과
- 🔧 **모듈화된 구조**: 깔끔한 코드 아키텍처

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
npm install
```

### 2. 서버 시작
```bash
node server.js
```

### 3. 브라우저에서 접속
- **컨트롤 패널**: http://localhost:3000
- **채팅 오버레이**: http://localhost:3000/chat-overlay.html

## 📁 프로젝트 구조

```
ChzzkStreamDeck/
├── 📁 src/                          # 소스 코드
│   ├── 🎮 chat-client.js            # CHZZK 채팅 클라이언트
│   └── 🎨 chat-overlay.html         # 채팅 오버레이 (OBS용)
├── 📁 js/                           # 기존 JavaScript 파일들
│   ├── 📁 modules/
│   │   ├── chat.js                  # 채팅 모듈
│   │   └── spotify.js               # Spotify 모듈
│   └── 📁 utils/
│       ├── settings.js              # 설정 유틸리티
│       └── ui.js                    # UI 유틸리티
├── 📁 css/                          # 스타일시트
│   ├── components.css               # 컴포넌트 스타일
│   ├── main.css                     # 메인 스타일
│   └── themes.css                   # 테마 스타일
├── 📁 test/                         # 테스트 파일들 (기존)
│   ├── chzzk-chat-terminal.js       # 작동하는 채팅 터미널
│   └── TERMINAL_TEST_GUIDE.md       # 테스트 가이드
├── 🌐 server.js                     # 메인 백엔드 서버
├── 🏠 index.html                    # 메인 대시보드
└── 📦 package.json                  # 프로젝트 설정
```

## 🎯 사용 방법

### 1. 실제 CHZZK 채팅 사용

1. **서버 시작**:
   ```bash
   node server.js
   ```

2. **컨트롤 패널에서 설정**:
   - http://localhost:3000 접속
   - 채널 ID 입력 (32자리 영숫자)
   - **채팅 시작** 버튼 클릭

3. **OBS 설정**:
   - 소스 추가 → 브라우저
   - URL: `http://localhost:3000/chat-overlay.html`
   - 크기: 400x600px

## 🎨 테마 시스템

### Simple Purple ✨
- 마법같은 보라색 그라데이션 (#667eea, #764ba2)
- 고급 애니메이션 효과 (bounce, scale, blur)
- 호버 시 언더라인 확장 효과
- 다층 그림자와 글로우 효과
- 환상적인 배경 라디얼 그라데이션

### Neon Green
- 네온 그린 색상 (#00ff00)
- 사이버펑크 스타일
- 글로우 효과 및 네온 애니메이션

## 🔧 API 엔드포인트

### 메인 서버 (포트 3000)
- `POST /api/chat/start` - 채팅 모듈 시작
- `POST /api/chat/stop` - 채팅 모듈 중지  
- `GET /api/chat/stream` - 실시간 채팅 스트림 (SSE)
- `GET /api/chat/messages` - 채팅 메시지 조회
- `GET /api/status` - 서버 상태 확인

## 🛠️ 개발 가이드

### 채팅 클라이언트 직접 실행
```bash
node src/chat-client.js <채널ID> [--verbose]
```

### 채팅 오버레이 사용
- **설정**: 메인 대시보드(`http://localhost:3000`)에서 모든 설정 관리
- **오버레이**: 순수 채팅 표시 전용 (`http://localhost:3000/chat-overlay.html`)
- **실시간 동기화**: 설정 변경 시 오버레이에 즉시 반영
- **설정 항목**: 테마, 최대 메시지 수, 메시지 지속 시간, 정렬 방식
- **채널 연동**: 메인 대시보드에서 CHZZK 채널 ID 설정

## 📋 요구사항

- **Node.js**: 14.0.0 이상
- **npm**: 6.0.0 이상
- **브라우저**: Chrome, Firefox, Edge (ES6+ 지원)
- **OBS Studio**: 27.0.0 이상 권장

## 🎮 OBS 설정 가이드

### 브라우저 소스 추가
1. OBS Studio 열기
2. **소스** → **추가** → **브라우저**
3. 설정:
   - **URL**: `http://localhost:3000/chat-overlay.html`
   - **너비**: 400
   - **높이**: 600
   - **CSS**: `body { background: transparent !important; }`

### 채팅 오버레이 특징
- 깔끔한 UI: 방송용으로 최적화된 인터페이스  
- 자연스러운 페이드: 상단 메시지 자동 페이드아웃 효과
- 이모티콘 지원: CHZZK 이모티콘 실시간 표시
- 고급 애니메이션: 마법같은 Simple Purple 테마 효과
- 정렬 옵션: 왼쪽/오른쪽/중앙 정렬 지원
- 실시간 설정: 메인 대시보드 설정이 즉시 반영
- 스마트 관리: 메시지 수 및 지속 시간 자동 제어

### 권장 설정
- **새로고침**: 체크 해제
- **페이지 권한**: 모두 허용
- **하드웨어 가속**: 활성화

## 🔍 문제 해결

### 자주 발생하는 문제

#### 1. "앱 업데이트 후에 정상 시청 가능합니다"
- **원인**: 방송이 진행 중이 아니거나 채널 ID 오류
- **해결**: 라이브 방송 중인 채널 ID 확인

#### 2. 채팅 메시지가 안 나타남
- **원인**: 서버 연결 문제 또는 API 제한
- **해결**: 
  1. 서버 상태 확인 (`GET /api/status`)
  2. 브라우저 콘솔 오류 확인
  3. 방화벽 설정 확인

#### 3. WebSocket 연결 실패
- **원인**: 네트워크 문제 또는 서버 과부하
- **해결**: 
  1. 다른 채널 ID로 테스트
  2. VPN 사용 시 해제
  3. 서버 재시작 후 다시 시도

## 📈 버전 히스토리

### v2.0.0 (2024-12-19)
- ✨ 전체 코드 리팩토링
- 🏗️ 모듈화된 아키텍처
- 🎨 마법같은 Simple Purple 테마 시스템
- 😀 CHZZK 이모티콘 완전 지원
- 📡 안정적인 SSE 연결
- 🎯 간편한 URL 접근
- 🎥 방송 최적화 오버레이
- ✨ 고급 애니메이션 및 시각 효과
- 🔄 실시간 설정 동기화
- 🎨 자연스러운 상단 페이드 효과
- 📐 다양한 정렬 옵션 (왼쪽/오른쪽/중앙)

### v1.x.x
- 기본 채팅 기능
- 간단한 오버레이

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성합니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙏 감사의 말

- **CHZZK API**: 실시간 채팅 데이터 제공
- **OBS Studio**: 강력한 스트리밍 소프트웨어
- **Node.js 커뮤니티**: 훌륭한 생태계

---

💡 **팁**: 문제가 발생하면 먼저 테스트 서버로 오버레이가 정상 작동하는지 확인해보세요!

🎮 **해피 스트리밍!** 🎮 