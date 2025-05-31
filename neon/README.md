# 🎮 네온 오버레이 시스템

방송용 오버레이 통합 관리 시스템입니다. 치지직 채팅, Spotify 음악, 배경 효과를 하나의 관리패널에서 제어할 수 있습니다.

## ✨ 주요 기능

### 🎯 통합 관리
- **단일 포트 (8080)로 모든 모듈 통합**
- **직관적인 웹 관리패널**
- **모듈별 개별 on/off 제어**
- **설정 자동 저장 및 복원**

### 💬 치지직 채팅 오버레이
- 실시간 채팅 표시
- 스트리머 전용 별 표시 (크기 개선됨)
- 사이버펑크 네온 스타일
- 선명한 구분선과 애니메이션 효과

### 🎵 Spotify 음악 오버레이
- 현재 재생 중인 음악 정보 표시
- 실시간 진행률 업데이트
- 간소화된 재생/일시정지 아이콘
- 앨범 커버 이미지 지원

### ✨ 배경 효과
- 2가지 배경 효과 모듈
- 강도 조절 가능 (0.0 - 1.0)
- 실시간 설정 변경

## 🚀 빠른 시작

### 1. 실행
```bash
python main.py
```

### 2. 관리패널 접속
자동으로 브라우저가 열리거나, 직접 접속:
```
http://localhost:8080/admin
```

### 3. OBS 설정
브라우저 소스에 다음 URL 추가:

**채팅 오버레이:**
```
http://localhost:8080/chat/overlay
```

**Spotify 오버레이:**
```
http://localhost:8080/spotify/overlay
```

**배경 효과 1:**
```
http://localhost:8080/background1/overlay
```

**배경 효과 2:**
```
http://localhost:8080/background2/overlay
```

## ⚙️ 설정 방법

### 치지직 채팅 설정
1. 관리패널에서 치지직 채팅 모듈 활성화
2. 채널 ID 입력 (예: `789d1d9c5b58c847f9f18c8e5073c580`)
3. 설정 저장

### Spotify 설정
1. 관리패널에서 Spotify 모듈 활성화
2. Spotify 개발자 앱에서 가져온 정보 입력:
   - 클라이언트 ID
   - 클라이언트 시크릿
   - 리다이렉트 URI (기본값: `http://localhost:8080/spotify/callback`)
3. 설정 저장 후 인증 진행

## 📁 파일 구조

```
neon/
├── main.py                 # 메인 실행 파일
├── unified_server.py       # 통합 서버
├── config.py              # 설정 관리
├── admin_panel.py         # 관리패널
├── chat_client.py         # 치지직 채팅 클라이언트
├── chat_server.py         # 채팅 서버
├── spotify_api.py         # Spotify API
├── spotify_server.py      # Spotify 서버
├── requirements.txt       # 의존성 패키지
├── README.md             # 이 파일
└── neon_overlay_config.json  # 설정 파일 (자동 생성)
```

## 🔧 고급 설정

### 포트 변경
`config.py` 파일에서 기본 포트 변경 가능:
```python
"server": {
    "port": 8080,  # 원하는 포트로 변경
    "host": "localhost"
}
```

### 설정 내보내기/가져오기
관리패널에서 설정을 JSON 파일로 내보내거나 가져올 수 있습니다.

### 모듈 확장
새로운 모듈을 추가하려면:
1. `config.py`의 `DEFAULT_CONFIG`에 모듈 정보 추가
2. `unified_server.py`에 핸들러 추가
3. `admin_panel.py`에 UI 추가

## 🎨 URL 구조

- **관리패널:** `/admin`
- **채팅 모듈:** `/chat/*`
- **Spotify 모듈:** `/spotify/*`
- **배경 효과 1:** `/background1/*`
- **배경 효과 2:** `/background2/*`
- **API:** `/api/*`

## 📱 앱 빌드 준비

시스템은 PyInstaller나 cx_freeze를 사용하여 독립 실행 파일로 빌드할 수 있도록 설계되었습니다:

```bash
# PyInstaller 사용 예시
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## 🐛 문제 해결

### 포트 사용 중 오류
- 다른 프로그램이 포트 8080을 사용하고 있는지 확인
- 설정에서 다른 포트로 변경

### 채팅 연결 실패
- 채널 ID가 올바른지 확인
- 방송이 진행 중인지 확인

### Spotify 인증 실패
- 클라이언트 ID와 시크릿이 올바른지 확인
- 리다이렉트 URI가 Spotify 앱 설정과 일치하는지 확인

## 📝 업데이트 로그

### v2.0.0 (현재)
- ✅ 스트리머 별 크기 증대 (16px → 20px)
- ✅ 구분선 선명도 개선 (opacity 0.3 → 0.6)
- ✅ 대기 메시지 제거
- ✅ Spotify 재생 애니메이션 간소화
- ✅ 포트 통일화 (8080)
- ✅ URL 구조 정리
- ✅ 통합 관리패널
- ✅ 설정 자동 저장
- ✅ 모듈별 on/off 제어

### v1.x.x (이전)
- 개별 오버레이 파일들
- 분산된 포트 구조
- 수동 설정 관리

## 💡 개발자 정보

이 시스템은 모듈화와 확장성을 고려하여 설계되었습니다. 새로운 오버레이 모듈을 쉽게 추가할 수 있으며, 설정 시스템을 통해 사용자 친화적인 관리가 가능합니다. 