// 메인 애플리케이션 초기화

class App {
    constructor() {
        this.settingsManager = new SettingsManager();
        this.uiManager = new UIManager(this);
        this.spotifyModule = new SpotifyModule(this.settingsManager);
        this.chatModule = new ChatModule(this.settingsManager);
        
        this.init();
    }
    
    init() {

        
        // 설정 로드
        this.settingsManager.loadSettings();
        
        // UI 이벤트 리스너 설정
        this.setupEventListeners();
        
        // 모듈 상태 업데이트
        this.updateModuleStates();
        
        // 테마 적용
        this.uiManager.applyTheme('spotify', this.settingsManager.getModuleSettings('spotify').theme);
        this.uiManager.applyTheme('chat', this.settingsManager.getModuleSettings('chat').theme);
        
        // 스포티파이 인증 상태 확인
        this.checkSpotifyAuthStatus();
        
        // URL 파라미터에서 인증 코드 확인
        this.handleSpotifyAuthCallback();
        

    }
    
    setupEventListeners() {
        // Spotify 토글
        document.getElementById('spotify-toggle').addEventListener('change', async (e) => {
            if (e.target.checked) {
                const success = await this.spotifyModule.start();
                if (!success) {
                    e.target.checked = false;
                }
            } else {
                this.spotifyModule.stop();
            }
            this.uiManager.updateModuleCard('spotify', this.spotifyModule.isActive);
        });
        
        // 채팅 토글
        document.getElementById('chat-toggle').addEventListener('change', async (e) => {
            if (e.target.checked) {
                const success = await this.chatModule.start();
                if (!success) {
                    e.target.checked = false;
                }
            } else {
                await this.chatModule.stop();
            }
            this.uiManager.updateModuleCard('chat', this.chatModule.isActive);
        });
        
        // 모달 외부 클릭시 닫기
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('settings-modal');
            if (e.target === modal) {
                this.uiManager.closeSettings();
            }
        });
    }
    
    updateModuleStates() {
        this.uiManager.updateModuleCard('spotify', this.spotifyModule.isActive);
        this.uiManager.updateModuleCard('chat', this.chatModule.isActive);
    }
    
    // 스포티파이 인증 상태 확인
    checkSpotifyAuthStatus() {
        const accessToken = localStorage.getItem('spotify-access-token');
        const tokenExpiry = localStorage.getItem('spotify-token-expiry');
        
        if (accessToken && tokenExpiry) {
            const isExpired = Date.now() > parseInt(tokenExpiry);
            this.updateSpotifyAuthStatus(isExpired ? 'expired' : 'authenticated');
        } else {
            this.updateSpotifyAuthStatus('not_authenticated');
        }
    }
    
    // 스포티파이 인증 상태 업데이트
    updateSpotifyAuthStatus(status) {
        const authButton = document.getElementById('spotify-auth-btn');
        
        if (!authButton) return;
        
        switch (status) {
            case 'authenticated':
                authButton.innerHTML = '<i class="fab fa-spotify"></i> 재인증';
                break;
            case 'expired':
                authButton.innerHTML = '<i class="fab fa-spotify"></i> 재인증';
                break;
            case 'not_authenticated':
                authButton.innerHTML = '<i class="fab fa-spotify"></i> 인증받기';
                break;
        }
    }
    
    // 스포티파이 인증 콜백 처리
    handleSpotifyAuthCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const authStatus = urlParams.get('spotify-auth');
        
        if (authStatus === 'success' && code) {

            this.exchangeSpotifyCodeForToken(code);
            
            // URL 정리
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }
    
    // 스포티파이 토큰 교환
    async exchangeSpotifyCodeForToken(code) {
        const clientId = localStorage.getItem('spotify-client-id');
        const clientSecret = localStorage.getItem('spotify-client-secret');
        
        if (!clientId || !clientSecret) {
            alert('Spotify Client ID와 Client Secret을 먼저 설정해주세요.');
            return;
        }
        
        try {
            const response = await fetch('https://accounts.spotify.com/api/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Basic ' + btoa(`${clientId}:${clientSecret}`)
                },
                body: new URLSearchParams({
                    grant_type: 'authorization_code',
                    code: code,
                    redirect_uri: 'http://localhost:7112/spotify/callback'
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                // 토큰 저장
                localStorage.setItem('spotify-access-token', data.access_token);
                localStorage.setItem('spotify-refresh-token', data.refresh_token);
                localStorage.setItem('spotify-token-expiry', Date.now() + (data.expires_in * 1000));
                

                this.updateSpotifyAuthStatus('authenticated');
                
                // 성공 메시지 표시
                if (this.uiManager) {
                    this.uiManager.showSuccess('스포티파이 인증이 완료되었습니다!');
                }
            } else {
                throw new Error(data.error_description || '토큰 교환 실패');
            }
        } catch (error) {
            console.error('❌ 스포티파이 토큰 교환 실패:', error);
            alert('스포티파이 인증 실패: ' + error.message);
        }
    }
}

// 애플리케이션 시작
const app = new App();

// 전역 함수들 (HTML에서 호출)
window.openSettings = (moduleName) => {
    app.uiManager.openSettings(moduleName);
};

window.closeSettings = () => {
    app.uiManager.closeSettings();
};

window.saveSettings = () => {
    app.uiManager.saveSettings();
};

window.copyToClipboard = (elementId) => {
    app.uiManager.copyToClipboard(elementId);
};

// 스포티파이 인증 함수
window.authenticateSpotify = () => {
    const clientId = localStorage.getItem('spotify-client-id');
    const clientSecret = localStorage.getItem('spotify-client-secret');
    
    if (!clientId || !clientSecret) {
        alert('Spotify Client ID와 Client Secret을 먼저 입력하고 저장해주세요.');
        return;
    }
    
    // 스포티파이 인증 URL 생성
    const authUrl = 'https://accounts.spotify.com/authorize?' + new URLSearchParams({
        response_type: 'code',
        client_id: clientId,
        scope: 'user-read-currently-playing user-read-playback-state',
        redirect_uri: 'http://localhost:7112/spotify/callback',
        show_dialog: 'true'
    });
    

    
    // 새 창으로 인증 페이지 열기
    const authWindow = window.open(authUrl, 'spotify-auth', 'width=600,height=700');
    
    // 메시지 리스너 등록
    const messageListener = (event) => {
        if (event.data.type === 'spotify-auth-success') {

            window.removeEventListener('message', messageListener);
            app.exchangeSpotifyCodeForToken(event.data.code);
        }
    };
    
    window.addEventListener('message', messageListener);
    
    // 창이 닫히면 리스너 제거
    const checkClosed = setInterval(() => {
        if (authWindow.closed) {
            clearInterval(checkClosed);
            window.removeEventListener('message', messageListener);

        }
    }, 1000);
};

// 앱 인스턴스를 전역에서 접근 가능하도록
window.app = app; 