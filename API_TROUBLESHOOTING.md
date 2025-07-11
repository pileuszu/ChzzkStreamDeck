# 🔧 치지직 API 문제 해결 가이드

## ❌ "앱 업데이트 후 정상 시청 가능합니다" 오류 해결

### 1. 📋 문제 확인
```bash
# API 테스트 실행
npm run api-test [채널ID]

# 예시
npm run api-test 9ae7d38b629b78f48e49fb3106218ff5
```

### 2. 🔍 단계별 해결 방법

#### 방법 1: 다른 채널 ID 시도
```bash
# 현재 라이브 중인 다른 채널 ID 사용
npm run chat-test [다른채널ID]
```

#### 방법 2: 브라우저에서 채널 ID 재확인
1. 치지직 웹사이트에서 라이브 방송 중인 채널 접속
2. URL에서 정확한 32자리 채널 ID 복사
3. 복사한 ID로 재시도

#### 방법 3: 네트워크 설정 확인
```bash
# DNS 설정 확인
nslookup api.chzzk.naver.com

# 네트워크 연결 테스트
ping api.chzzk.naver.com
```

### 3. 🛠️ 고급 해결 방법

#### 방법 A: 프록시 사용
```bash
# 필요시 프록시 서버를 통해 접속
# (프록시 설정은 환경에 따라 다름)
```

#### 방법 B: VPN 사용
```bash
# 지역 제한이 있는 경우 VPN을 통해 접속
```

#### 방법 C: 쿠키 시뮬레이션
```javascript
// 브라우저 쿠키를 시뮬레이션하는 방법
// (고급 사용자용)
```

### 4. 📊 성공적인 테스트 사례

#### 성공 패턴 1: 모바일 User-Agent
```
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15
```

#### 성공 패턴 2: 완전한 브라우저 헤더
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json, text/plain, */*
Referer: https://chzzk.naver.com/
```

### 5. 🎯 테스트 시나리오

#### 시나리오 1: 기본 테스트
```bash
# 1. API 테스트 실행
npm run api-test

# 2. 결과 확인
# ✅ 성공시: 채팅 테스트 진행
# ❌ 실패시: 다른 채널 ID 시도
```

#### 시나리오 2: 문제 해결 테스트
```bash
# 1. 다른 채널 ID로 테스트
npm run api-test [다른채널ID]

# 2. 여러 채널 ID 시도
npm run api-test 9ae7d38b629b78f48e49fb3106218ff5
npm run api-test [다른채널ID1]
npm run api-test [다른채널ID2]
```

### 6. 🔄 대안 방법

#### 대안 1: 웹 브라우저 테스트
```bash
# 웹 브라우저에서 직접 테스트
# test/chzzk-chat-test.html 파일 열기
```

#### 대안 2: 다른 API 엔드포인트
```bash
# 다른 API 엔드포인트 시도
# - service/v1/channels/
# - polling/v1/channels/
# - polling/v2/channels/
```

### 7. 📝 문제 리포팅

#### 성공 사례 공유
```
✅ 성공한 설정:
- 채널 ID: [성공한채널ID]
- 시도 방법: [방법번호]
- 환경: [OS/네트워크환경]
```

#### 실패 사례 공유
```
❌ 실패한 설정:
- 채널 ID: [실패한채널ID]
- 오류 메시지: [정확한오류메시지]
- 시도한 방법: [시도한방법들]
```

### 8. 🆘 최종 해결책

#### 해결책 1: 시간 차이를 두고 재시도
```bash
# 5-10분 후 재시도
# 치지직 API 서버 상태가 변경될 수 있음
```

#### 해결책 2: 다른 네트워크 환경
```bash
# 모바일 핫스팟 사용
# 다른 인터넷 연결 시도
```

#### 해결책 3: 브라우저 개발자 도구 활용
```bash
# 1. 실제 브라우저에서 치지직 접속
# 2. F12 개발자 도구 열기
# 3. Network 탭에서 실제 요청 헤더 확인
# 4. 동일한 헤더로 스크립트 수정
```

---

## 💡 추가 팁

### 채널 ID 찾기
1. 치지직 메인 페이지에서 "라이브" 섹션 확인
2. 현재 방송 중인 채널 클릭
3. URL에서 32자리 ID 복사

### 성공률 높이는 방법
- 인기 있는 대형 채널 ID 사용
- 확실히 라이브 방송 중인 채널 선택
- 피크 시간대 (저녁 7-11시) 테스트

### 실시간 디버깅
```bash
# 상세 로그 확인
DEBUG=* npm run chat-test [채널ID]
```

---

💡 **중요**: 치지직 API는 공식 API가 아니므로 언제든 변경될 수 있습니다. 지속적인 업데이트와 테스트가 필요합니다. 