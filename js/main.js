// 메인 애플리케이션 초기화

class App {
    constructor() {
        this.settingsManager = new SettingsManager();
        this.uiManager = new UIManager(this);
        this.spotifyModule = new SpotifyModule(this.settingsManager);
        this.chatModule = new ChatModule(this.settingsManager);
        this.musicBotModule = new MusicBotModule(this.settingsManager);
        
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

        // 음악봇 토글
        document.getElementById('musicbot-toggle').addEventListener('change', async (e) => {
            if (e.target.checked) {
                const success = await this.musicBotModule.start();
                if (!success) {
                    e.target.checked = false;
                }
            } else {
                this.musicBotModule.stop();
            }
            this.uiManager.updateModuleCard('musicbot', this.musicBotModule.isActive);
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
                authButton.className = 'btn btn-success';
                break;
            case 'expired':
                authButton.innerHTML = '<i class="fab fa-spotify"></i> 재인증';
                authButton.className = 'btn btn-warning';
                break;
            case 'not_authenticated':
                authButton.innerHTML = '<i class="fab fa-spotify"></i> 인증받기';
                authButton.className = 'btn btn-primary';
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
window.authenticateSpotify = async () => {
    console.log('🎵 인증 버튼 클릭됨');
    
    if (app.spotifyModule) {
        try {
            const result = await app.spotifyModule.authenticate();
            console.log('🎵 인증 결과:', result);
            
            if (result) {
                // 인증 성공 - 버튼 상태 업데이트
                app.updateSpotifyAuthStatus('authenticated');
            }
        } catch (error) {
            console.error('❌ 인증 중 오류:', error);
            
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError(`인증 실패: ${error.message}`);
            } else {
                alert(`인증 실패: ${error.message}`);
            }
        }
    } else {
        console.error('❌ Spotify 모듈이 초기화되지 않음');
        alert('Spotify 모듈이 초기화되지 않았습니다.');
    }
};

// 스포티파이 토큰 상태 확인 함수
window.checkSpotifyTokens = () => {
    console.log('🔍 토큰 상태 확인');
    
    const accessToken = localStorage.getItem('spotify-access-token');
    const refreshToken = localStorage.getItem('spotify-refresh-token');
    const tokenExpiry = localStorage.getItem('spotify-token-expiry');
    
    let statusMessage = '🔍 Spotify 토큰 상태:\n\n';
    
    if (!accessToken) {
        statusMessage += '❌ 액세스 토큰: 없음\n';
    } else {
        statusMessage += `✅ 액세스 토큰: 있음 (${accessToken.substring(0, 20)}...)\n`;
    }
    
    if (!refreshToken) {
        statusMessage += '❌ 리프레시 토큰: 없음\n';
    } else {
        statusMessage += `✅ 리프레시 토큰: 있음 (${refreshToken.substring(0, 20)}...)\n`;
    }
    
    if (!tokenExpiry) {
        statusMessage += '❌ 토큰 만료 시간: 없음\n';
    } else {
        const expiryDate = new Date(parseInt(tokenExpiry));
        const isExpired = Date.now() > parseInt(tokenExpiry);
        statusMessage += `🕐 토큰 만료 시간: ${expiryDate.toLocaleString()}\n`;
        statusMessage += `${isExpired ? '❌ 상태: 만료됨' : '✅ 상태: 유효함'}\n`;
    }
    
    if (window.app && window.app.uiManager) {
        window.app.uiManager.showInfo(statusMessage);
    } else {
        alert(statusMessage);
    }
};

// 스포티파이 토큰 삭제 함수
window.clearSpotifyTokens = () => {
    console.log('🗑️ 토큰 삭제');
    
    if (confirm('모든 Spotify 토큰을 삭제하시겠습니까?\n다시 인증받아야 합니다.')) {
        localStorage.removeItem('spotify-access-token');
        localStorage.removeItem('spotify-refresh-token');
        localStorage.removeItem('spotify-token-expiry');
        
        // 서버에서도 토큰 삭제
        fetch('http://localhost:7112/api/spotify/token', {
            method: 'DELETE'
        }).then(response => response.json())
          .then(result => {
              console.log('🗑️ 서버 토큰 삭제:', result.message);
          })
          .catch(error => {
              console.error('❌ 서버 토큰 삭제 오류:', error);
          });
        
        // 스포티파이 모듈 상태 초기화
        if (app.spotifyModule) {
            app.spotifyModule.accessToken = null;
            app.spotifyModule.refreshToken = null;
            app.spotifyModule.isAuthenticated = false;
        }
        
        // 버튼 상태 업데이트
        app.updateSpotifyAuthStatus('not_authenticated');
        
        console.log('✅ 모든 토큰이 삭제되었습니다');
        
        if (window.app && window.app.uiManager) {
            window.app.uiManager.showSuccess('모든 토큰이 삭제되었습니다.');
        } else {
            alert('모든 토큰이 삭제되었습니다.');
        }
    }
};

// 앱 인스턴스를 전역에서 접근 가능하도록
window.app = app; 