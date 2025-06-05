# 🎮 ChzzkStreamDeck - 치지직 스트리밍 컨트롤 센터

실시간 채팅 오버레이와 Spotify 음악 정보를 OBS에서 사용할 수 있는 올인원 스트리밍 도구입니다.

<!-- 메인 스크린샷 영역 -->
*[메인 관리패널 스크린샷 자리]*

## ✨ 주요 기능

- 🎬 **치지직 채팅 오버레이**: 실시간 채팅을 OBS 화면에 표시
- 🎵 **Spotify 음악 정보**: 현재 재생 중인 곡 정보를 오버레이로 표시  
- 🎨 **2가지 테마**: Neon 테마와 Purple 테마 지원
- 🔧 **관리패널**: 웹 기반 설정 및 모듈 제어
- 🖥️ **데스크톱 앱**: webview 기반 독립 실행

## 🚀 빠른 시작

### 1. 다운로드 및 실행
1. [Releases](https://github.com/your-username/ChzzkStreamDeck/releases)에서 최신 버전 다운로드
2. 압축 해제 후 `ChzzkStreamDeck.exe` 실행
3. Windows Defender 경고 시 "추가 정보" → "실행" 클릭

### 2. 기본 설정
1. 관리패널이 자동으로 열림 (http://localhost:8080/admin)
2. 필요한 정보 입력:
   - **치지직 채널 ID**: 채팅을 가져올 채널 ID
   - **Spotify 클라이언트 정보**: 음악 정보 연동용

<!-- 설정 화면 스크린샷 영역 -->
*[관리패널 설정 화면 스크린샷 자리]*

### 3. OBS 설정
1. 소스 추가 → **브라우저 소스**
2. URL 입력:
   - **채팅 오버레이**: `http://localhost:8080/chat/overlay`
   - **Spotify 오버레이**: `http://localhost:8080/spotify/overlay`
3. 해상도: 1920x1080 권장
4. **사용자 지정 CSS** 및 **투명 배경** 체크

<!-- OBS 설정 스크린샷 영역 -->
*[OBS 브라우저 소스 설정 스크린샷 자리]*

## 🔧 고급 사용법

### Spotify 연동 설정
1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) 접속
2. "Create app" 클릭하여 새 앱 생성
3. 앱 설정에서 Redirect URI 추가: `http://localhost:8080/spotify/callback`
4. Client ID와 Client Secret을 관리패널에 입력
5. Spotify 계정 인증 완료

<!-- Spotify 설정 스크린샷 영역 -->
*[Spotify 인증 화면 스크린샷 자리]*

### 포트 변경
기본 포트(8080)가 사용 중인 경우:
```bash
ChzzkStreamDeck.exe --port 8081
```

## 📋 시스템 요구사항

- **OS**: Windows 10/11 (64bit)
- **메모리**: 최소 4GB RAM 권장
- **네트워크**: 인터넷 연결 필요

## 🛠️ 문제 해결

### 실행 안 될 때
- 관리자 권한으로 실행
- Windows Defender 예외 목록에 추가
- 방화벽에서 포트 허용 설정

### 채팅이 안 보일 때  
- 치지직 채널 ID 확인
- 인터넷 연결 상태 확인
- 브라우저에서 직접 접속해보기

### Spotify 연동 안 될 때
- Client ID/Secret 재확인
- Redirect URI 정확히 입력했는지 확인
- Spotify 앱에서 사용자 인증 완료했는지 확인

## 🔒 보안 및 개인정보

- 모든 설정은 로컬에 저장됨
- 외부 서버로 개인정보 전송 안 함
- Spotify API는 공식 OAuth 2.0 사용
- 채널 ID 등 민감 정보는 암호화 저장

## 📞 지원 및 문의

- **이슈 제보**: [GitHub Issues](https://github.com/your-username/ChzzkStreamDeck/issues)
- **기능 요청**: [GitHub Discussions](https://github.com/your-username/ChzzkStreamDeck/discussions)
- **업데이트**: [Releases](https://github.com/your-username/ChzzkStreamDeck/releases) 페이지 확인