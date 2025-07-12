# 🎮 치지직 터미널 채팅 테스트 가이드

## 📋 개요

터미널에서 치지직 실시간 채팅을 받아볼 수 있는 테스트 도구입니다. 
Socket.IO와 WebSocket을 활용하여 실시간 채팅 메시지를 콘솔에 출력합니다.

## 🚀 빠른 시작

### 1. 필요 조건

- Node.js 14.0.0 이상
- npm 또는 yarn
- 인터넷 연결

### 2. 의존성 설치

```bash
# 프로젝트 루트에서 실행
npm install

# 또는 개별 설치
npm install node-fetch ws socket.io-client
```

### 3. 실행 방법

```bash
# 기본 실행
node test/chzzk-chat-terminal.js [채널ID]

# npm 스크립트 사용
npm run chat-test [채널ID]
```

### 4. 예시

```bash
# 예시 채널 ID로 테스트
node test/chzzk-chat-terminal.js 255a2ea465c44920aa3e93b8d60a72e0

# 또는
npm run chat-test 255a2ea465c44920aa3e93b8d60a72e0
```

## 🎯 채널 ID 찾는 방법

### 방법 1: 브라우저 URL에서 추출

1. 치지직 웹사이트에서 원하는 채널 방문
2. 브라우저 주소창에서 URL 확인
3. 마지막 부분의 32자리 영문+숫자 조합이 채널 ID

```
https://chzzk.naver.com/live/255a2ea465c44920aa3e93b8d60a72e0
                              ↑ 이 부분이 채널 ID
```

### 방법 2: 개발자 도구 사용

1. F12로 개발자 도구 열기
2. Network 탭에서 API 호출 확인
3. `channels/` 또는 `live-status` 요청에서 채널 ID 확인

## 🔧 기능 설명

### 주요 기능

- **실시간 채팅**: 치지직 채팅 메시지 실시간 수신
- **다중 연결**: Socket.IO 실패 시 WebSocket으로 대체
- **컬러 로그**: 터미널에서 색상으로 구분된 로그 출력
- **오류 복구**: 여러 API 엔드포인트 시도
- **안전한 종료**: Ctrl+C로 깔끔한 연결 종료

### 로그 색상 가이드

- 🔵 **[INFO]**: 일반 정보 메시지
- 🟢 **[SUCCESS]**: 성공 메시지
- 🔴 **[ERROR]**: 오류 메시지
- 🟡 **[WARNING]**: 경고 메시지
- 🟦 **[채팅]**: 채팅 메시지 (사용자별 색상)
- ⚫ **[SYSTEM]**: 시스템 메시지

### 출력 예시

```
[INFO] 치지직 채팅 클라이언트 시작...
[INFO] 채널 ID: 255a2ea465c44920aa3e93b8d60a72e0
[SUCCESS] 채널 정보 획득 성공
[INFO] 채널명: 테스트채널
[SUCCESS] 라이브 상태 확인 성공
[INFO] 방송 상태: OPEN
[SUCCESS] 액세스 토큰 획득 성공
[SUCCESS] Socket.IO 연결 성공!
[INFO] 채팅 메시지를 기다리는 중...
[사용자1] 안녕하세요!
[사용자2] 방송 잘 보고 있어요
[💰 사용자3 (1000원 후원)] 화이팅!
```

## 🛠️ 문제 해결

### 자주 발생하는 문제

#### 1. "채널 정보를 가져올 수 없습니다"

**원인**: 잘못된 채널 ID 또는 네트워크 문제
**해결책**:
- 채널 ID가 32자리 영문+숫자인지 확인
- 다른 채널 ID로 시도
- 네트워크 연결 확인

#### 2. "액세스 토큰을 가져올 수 없습니다"

**원인**: API 접근 제한 또는 방송 종료
**해결책**:
- 현재 라이브 방송 중인 채널 사용
- 잠시 후 다시 시도
- 다른 채널로 테스트

#### 3. WebSocket 연결 실패

**원인**: 서버 접속 제한 또는 네트워크 문제
**해결책**:
- 방화벽 설정 확인
- VPN 사용 시 해제 후 재시도
- 다른 네트워크에서 테스트

#### 4. 채팅 메시지가 안 나옴

**원인**: 채팅이 비활성화되어 있거나 메시지 형식 변경
**해결책**:
- 웹 브라우저에서 채팅 활성화 확인
- 디버그 모드로 원본 데이터 확인
- 채팅이 활발한 채널에서 테스트

### 디버그 모드

더 자세한 로그를 보려면 환경 변수 설정:

```bash
# Windows
set DEBUG=* && node test/chzzk-chat-terminal.js [채널ID]

# macOS/Linux
DEBUG=* node test/chzzk-chat-terminal.js [채널ID]
```

## 📈 고급 사용법

### 1. 코드 수정

채팅 메시지 처리 로직을 수정하려면 `handleChatMessage` 메서드를 편집하세요:

```javascript
handleChatMessage(data) {
    // 커스텀 메시지 처리 로직
    const nickname = data.profile?.nickname || '익명';
    const message = data.message || '';
    
    // 특정 조건에 따른 처리
    if (message.includes('!명령어')) {
        log.system(`명령어 감지: ${message}`);
    }
    
    log.chat(nickname, message);
}
```

### 2. 메시지 저장

채팅 메시지를 파일로 저장하려면:

```javascript
const fs = require('fs');

// 메시지 저장 함수
function saveMessage(nickname, message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${nickname}: ${message}\n`;
    fs.appendFileSync('chat_log.txt', logEntry);
}
```

### 3. 봇 응답

특정 키워드에 자동 응답하려면:

```javascript
handleChatMessage(data) {
    const message = data.message || '';
    
    if (message.includes('안녕')) {
        // 봇 응답 로직 (실제 메시지 전송은 별도 API 필요)
        log.system('인사 메시지 감지됨');
    }
}
```

## 📊 성능 최적화

### 1. 메모리 사용량 감소

```javascript
// 메시지 버퍼 크기 제한
const MAX_MESSAGES = 100;
let messageBuffer = [];

handleChatMessage(data) {
    messageBuffer.push(data);
    if (messageBuffer.length > MAX_MESSAGES) {
        messageBuffer.shift(); // 오래된 메시지 제거
    }
}
```

### 2. 연결 안정성 향상

```javascript
// 재연결 로직
async function reconnect() {
    await new Promise(resolve => setTimeout(resolve, 5000));
    log.info('재연결 시도 중...');
    await this.start();
}
```

## 🧪 테스트 시나리오

### 1. 기본 테스트

```bash
# 1단계: 인기 채널에서 테스트
node test/chzzk-chat-terminal.js [인기채널ID]

# 2단계: 소규모 채널에서 테스트
node test/chzzk-chat-terminal.js [소규모채널ID]

# 3단계: 방송 종료된 채널에서 테스트
node test/chzzk-chat-terminal.js [비활성채널ID]
```

### 2. 압력 테스트

```bash
# 여러 채널 동시 연결
node test/chzzk-chat-terminal.js [채널1] &
node test/chzzk-chat-terminal.js [채널2] &
node test/chzzk-chat-terminal.js [채널3] &
```

### 3. 장기 실행 테스트

```bash
# 백그라운드 실행
nohup node test/chzzk-chat-terminal.js [채널ID] > chat.log 2>&1 &

# 로그 확인
tail -f chat.log
```

## 🔐 보안 고려사항

### 1. 토큰 보안

- 액세스 토큰을 로그에 노출하지 않음
- 환경 변수로 민감 정보 관리
- 토큰 만료 시 자동 갱신

### 2. 네트워크 보안

- HTTPS/WSS 연결 사용
- 신뢰할 수 있는 도메인만 접근
- 요청 빈도 제한

## 📝 로그 파일 관리

### 로그 파일 생성

```bash
# 로그 파일로 출력
node test/chzzk-chat-terminal.js [채널ID] > chat_$(date +%Y%m%d_%H%M%S).log 2>&1
```

### 로그 분석

```bash
# 특정 사용자 메시지 검색
grep "사용자명" chat.log

# 시간대별 메시지 통계
grep "$(date +%Y-%m-%d)" chat.log | wc -l
```

## 🆘 지원 및 문의

### 문제 해결 순서

1. **로그 확인**: 에러 메시지 자세히 읽기
2. **네트워크 확인**: 인터넷 연결 및 방화벽 설정
3. **채널 확인**: 다른 채널 ID로 테스트
4. **버전 확인**: Node.js 및 의존성 버전
5. **이슈 리포트**: 구체적인 오류 내용과 환경 정보

### 디버그 정보 수집

```bash
# 시스템 정보
node --version
npm --version
cat package.json

# 네트워크 테스트
ping api.chzzk.naver.com
nslookup api.chzzk.naver.com
```

---

## 📄 라이선스

MIT License - 자유롭게 사용하세요!

## 🎯 주요 업데이트

- **v1.0.0**: 기본 채팅 수신 기능
- **v1.1.0**: Socket.IO 지원 추가
- **v1.2.0**: 오류 복구 기능 강화
- **v1.3.0**: 컬러 로그 시스템 개선

---

*이 가이드가 도움이 되었나요? 문제가 있거나 개선 사항이 있으면 언제든 알려주세요!* 