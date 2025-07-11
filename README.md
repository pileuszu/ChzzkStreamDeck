# 치지직 스트림덱 2.0 📺

OBS에서 사용할 수 있는 브라우저 소스 커스텀 위젯 대시보드입니다.

## 🚀 빠른 시작

1. **의존성 설치**
   ```bash
   npm install
   ```

2. **연결 테스트 (중요!)**
   ```bash
   # 1단계: API 연결 테스트 (필수)
   npm run api-test 789d1d9c5b58c847f9f18c8e5073c580
   
   # 2단계: 채널 정보 전체 확인
   npm run channel-info 789d1d9c5b58c847f9f18c8e5073c580
   
   # 3단계: API 성공 시 채팅 테스트
   npm run chat-test 789d1d9c5b58c847f9f18c8e5073c580
   
   # 사용법 확인
   npm test
   ```

3. **대시보드 실행**
   - 브라우저에서 `index.html` 파일을 열어주세요.
   - 각 모듈의 설정을 완료한 후 활성화할 수 있습니다.

## 🎮 지원하는 모듈

### 1. Spotify 모듈
- **기능**: 현재 재생 중인 곡 정보를 실시간으로 표시
- **필요한 설정**: 
  - Spotify Client ID
  - Spotify Client Secret
- **테마**: Simple Purple, Neon Green

### 2. 채팅 모듈
- **기능**: 치지직 채팅을 실시간으로 표시
- **필요한 설정**: 
  - 치지직 Channel ID
  - 최대 메시지 수
  - 메시지 사라지는 시간
- **테마**: Simple Purple, Neon Green

## 🛠️ 설정 방법

### Spotify API 설정
1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)에서 앱 생성
2. Client ID와 Client Secret 복사
3. 대시보드에서 Spotify 설정에 입력

### 치지직 채널 ID 확인
1. 치지직 방송 페이지 URL에서 채널 ID 확인
   - 예: `https://chzzk.naver.com/live/9ae7d38b629b78f48e49fb3106218ff5`
   - 여기서 `9ae7d38b629b78f48e49fb3106218ff5`이 채널 ID
   - 채널 ID는 32자리 영문+숫자 조합입니다

## 🧪 테스트 기능

### 웹 브라우저 테스트
- `test/chzzk-chat-test.html` 파일을 브라우저에서 열어 치지직 채팅 연결을 테스트할 수 있습니다.

### API 연결 테스트
치지직 API 접근 문제를 진단하고 해결하는 전용 도구입니다.

```bash
# API 연결 테스트
npm run api-test [채널ID]

# 예시
npm run api-test 9ae7d38b629b78f48e49fb3106218ff5
```

**API 테스트 특징:**
- 🔍 **다양한 헤더 조합**: 기본, 브라우저, 모바일, curl 등 4가지 방법
- 📊 **명확한 결과 구분**: 성공/실패를 한눈에 구분 가능
- 📋 **자동 요약 리포트**: 어떤 API가 성공했는지 명확한 요약 제공
- 💡 **자동 해결책 제안**: 실패 시 구체적인 해결 방법 안내
- 🎯 **채널 정보 표시**: 성공 시 채널명, 상태, 채팅 ID 등 자동 표시

### 채널 정보 상세 조회
성공한 API 엔드포인트의 전체 응답 데이터를 확인하는 전용 도구입니다.

```bash
# 특정 채널 정보 전체 조회
npm run channel-info [채널ID]

# 예시
npm run channel-info 789d1d9c5b58c847f9f18c8e5073c580

# 기본 채널들 모두 테스트
node test/chzzk-channel-info.js --all
```

**채널 정보 도구 특징:**
- 📋 **전체 API 응답**: JSON 전체 내용을 보기 좋게 포맷팅
- 🎯 **구조화된 출력**: 카테고리별로 정리된 채널 정보
- 📊 **상세 통계**: 팔로워 수, 구독자 수, 시청자 수 등
- 🔴 **라이브 정보**: 현재 방송 상태, 제목, 시청자 수 등
- 💡 **숨겨진 데이터**: API가 제공하는 모든 필드 확인 가능

### 터미널 테스트
치지직 채팅 웹소켓 연결을 터미널에서 테스트할 수 있습니다.

```bash
# 채널 ID로 채팅 연결 테스트
node test/chzzk-chat-terminal.js [채널ID]

# 예시 (실제 치지직 채널 ID 사용)
node test/chzzk-chat-terminal.js 9ae7d38b629b78f48e49fb3106218ff5

# 또는 npm script 사용
npm run chat-test [채널ID]
```

📖 **상세 가이드**: [터미널 테스트 가이드](test/TERMINAL_TEST_GUIDE.md)를 참고하세요.

**터미널 테스트 특징:**
- 🔄 **자동 서버 전환**: kr-ss1 → kr-ss2 → kr-ss3 순서로 자동 시도
- 📡 **실시간 채팅 메시지 표시**: 닉네임, 시간, 메시지 내용
- 🔍 **연결 과정 상세 로그**: API 호출 및 웹소켓 연결 상태 실시간 확인
- 📊 **메시지 카운터**: 수신한 채팅 메시지 개수 표시
- 💓 **자동 핑퐁**: 20초마다 연결 상태 확인
- ⌨️ **안전한 종료**: Ctrl+C 또는 "quit" 입력으로 종료

## 🎨 OBS 설정

1. **브라우저 소스 추가**
   - 소스 추가 → 브라우저 소스
   - URL: `http://localhost:포트번호/[모듈명].html`

2. **위젯 사용**
   - 대시보드에서 모듈 활성화
   - 브라우저 소스 URL 복사 버튼 사용
   - OBS에서 해당 URL 설정

## 📁 파일 구조

```
ChzzkStreamDeck 2.0/
├── index.html              # 메인 대시보드
├── package.json             # Node.js 프로젝트 설정
├── README.md               # 사용 설명서
├── API_TROUBLESHOOTING.md  # API 문제 해결 가이드
├── css/                    # 스타일시트
│   ├── main.css           # 메인 스타일
│   ├── components.css     # 컴포넌트 스타일
│   └── themes.css         # 테마 스타일
├── js/                     # JavaScript 모듈
│   ├── main.js            # 메인 애플리케이션
│   ├── modules/           # 위젯 모듈
│   │   ├── spotify.js     # Spotify 모듈
│   │   └── chat.js        # 채팅 모듈
│   └── utils/             # 유틸리티
│       ├── settings.js    # 설정 관리
│       └── ui.js          # UI 관리
└── test/                   # 테스트 파일
    ├── chzzk-chat-test.html      # 웹 브라우저 테스트
    ├── chzzk-chat-test.js        # 웹 테스트 스크립트
    ├── chzzk-chat-terminal.js    # 터미널 테스트 스크립트
    ├── chzzk-api-test.js         # API 연결 테스트
    ├── chzzk-channel-info.js     # 채널 정보 상세 조회
    └── TERMINAL_TEST_GUIDE.md    # 터미널 테스트 가이드
```

## 🎯 주요 기능

- **모듈화된 구조**: 각 위젯을 독립적으로 관리
- **실시간 업데이트**: 웹소켓 및 API 연동
- **테마 시스템**: 다양한 디자인 테마 지원
- **설정 관리**: 로컬 스토리지 기반 설정 저장
- **반응형 디자인**: 다양한 화면 크기 지원
- **OBS 최적화**: 브라우저 소스용 최적화

## 🔧 개발 정보

### 기술 스택
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **API**: Spotify Web API, 치지직 API
- **웹소켓**: 치지직 채팅 실시간 연결
- **테스트**: Node.js, WebSocket (ws)

### 브라우저 지원
- Chrome 80+
- Firefox 74+
- Safari 13.1+
- Edge 80+

## 📝 라이센스

MIT License - 자유롭게 사용하세요!

## 🐛 문제 해결

### 자주 발생하는 문제

1. **설정 창이 안 열릴 때**
   - 브라우저 개발자 도구에서 JavaScript 오류 확인
   - 모든 파일이 올바른 위치에 있는지 확인

2. **Spotify 연결 실패**
   - Client ID/Client Secret 확인
   - 네트워크 연결 상태 확인

3. **채팅 연결 실패**
   - 채널 ID 형식 확인 (32자리 영문+숫자)
   - 방송 상태 확인 (라이브 중이어야 함)
   - 웹소켓 서버 자동 전환 기능으로 안정성 향상

4. **"앱 업데이트 후 정상 시청 가능" 오류**
   - User-Agent 헤더 자동 추가로 해결
   - 브라우저 환경 시뮬레이션으로 API 접근
   - 📖 **자세한 해결 가이드**: [API 문제 해결 가이드](API_TROUBLESHOOTING.md)

5. **터미널 테스트 실행 오류**
   ```bash
   # Node.js 버전 확인 (14.0.0 이상 필요)
   node --version
   
   # 의존성 재설치
   npm install
   ```

### 디버깅 팁
- 브라우저 개발자 도구 콘솔 확인
- 네트워크 탭에서 API 요청 상태 확인
- 터미널에서 실시간 로그 확인

### 문제 해결 우선순위
1. **API 연결 테스트 먼저 실행**: `npm run api-test [채널ID]`
2. **성공하면 채팅 테스트**: `npm run chat-test [채널ID]`
3. **실패하면 다른 채널 ID 시도**: 현재 라이브 중인 채널 사용
4. **지속적 실패시**: [API 문제 해결 가이드](API_TROUBLESHOOTING.md) 참조 