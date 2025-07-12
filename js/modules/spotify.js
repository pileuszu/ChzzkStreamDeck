// Spotify 모듈
class SpotifyModule {
    constructor(settingsManager) {
        this.settingsManager = settingsManager;
        this.isActive = false;
        this.isAuthenticated = false;
        this.accessToken = null;
        this.refreshToken = null;
        this.updateInterval = null;
        this.currentTrack = null;
    }
    
    // 모듈 시작
    async start() {
        console.log('Spotify 모듈 시작 중...');
        
        const settings = this.settingsManager.getModuleSettings('spotify');
        
        // 인증 정보 확인
        if (!settings.clientId || !settings.clientSecret) {
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError('Spotify Client ID와 Client Secret을 먼저 설정해주세요.');
            } else {
                alert('Spotify Client ID와 Client Secret을 먼저 설정해주세요.');
            }
            return false;
        }
        
        try {
            // Spotify 인증
            const authSuccess = await this.authenticate();
            if (!authSuccess) {
                return false;
            }
            
            this.isActive = true;
            this.startTracking();
            
            console.log('Spotify 모듈이 시작되었습니다.');
            return true;
            
        } catch (error) {
            console.error('Spotify 모듈 시작 실패:', error);
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError('Spotify 모듈 시작에 실패했습니다.');
            } else {
                alert('Spotify 모듈 시작에 실패했습니다.');
            }
            return false;
        }
    }
    
    // 모듈 중지
    stop() {
        console.log('Spotify 모듈 중지 중...');
        
        this.isActive = false;
        this.isAuthenticated = false;
        this.accessToken = null;
        this.refreshToken = null;
        
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        console.log('Spotify 모듈이 중지되었습니다.');
    }
    
    // 모듈 재시작
    async restart() {
        console.log('Spotify 모듈 재시작 중...');
        this.stop();
        await new Promise(resolve => setTimeout(resolve, 500));
        return await this.start();
    }
    
    // Spotify 인증
    async authenticate() {
        const settings = this.settingsManager.getModuleSettings('spotify');
        
        try {
            console.log('Spotify 인증 시도 중...');
            
            // Client Credentials Flow 사용 (사용자 인증 필요 없음)
            const response = await fetch('https://accounts.spotify.com/api/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Basic ' + btoa(settings.clientId + ':' + settings.clientSecret)
                },
                body: 'grant_type=client_credentials'
            });
            
            if (!response.ok) {
                throw new Error('인증 요청 실패');
            }
            
            const data = await response.json();
            this.accessToken = data.access_token;
            this.isAuthenticated = true;
            
            console.log('Spotify 인증 성공!');
            return true;
            
        } catch (error) {
            console.error('Spotify 인증 실패:', error);
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError('Spotify 인증에 실패했습니다. Client ID와 Client Secret을 확인해주세요.');
            } else {
                alert('Spotify 인증에 실패했습니다. Client ID와 Client Secret을 확인해주세요.');
            }
            return false;
        }
    }
    
    // 현재 재생 중인 트랙 가져오기
    async getCurrentTrack() {
        if (!this.isAuthenticated) return null;
        
        try {
            // 실제로는 사용자의 현재 재생 중인 트랙을 가져오려면 
            // Authorization Code Flow가 필요합니다.
            // 여기서는 데모용으로 인기 트랙을 가져옵니다.
            const response = await fetch('https://api.spotify.com/v1/browse/featured-playlists?limit=1', {
                headers: {
                    'Authorization': 'Bearer ' + this.accessToken
                }
            });
            
            if (!response.ok) {
                throw new Error('트랙 정보 가져오기 실패');
            }
            
            const data = await response.json();
            
            // 데모용 더미 데이터
            return {
                name: 'Shape of You',
                artist: 'Ed Sheeran',
                album: '÷ (Divide)',
                progress: Math.floor(Math.random() * 100),
                duration: 233000,
                isPlaying: true
            };
            
        } catch (error) {
            console.error('현재 트랙 가져오기 실패:', error);
            return null;
        }
    }
    
    // 트랙 정보 추적 시작
    startTracking() {
        this.updateInterval = setInterval(async () => {
            const track = await this.getCurrentTrack();
            if (track) {
                this.updateUI(track);
                this.currentTrack = track;
            }
        }, 1000);
    }
    
    // UI 업데이트
    updateUI(track) {
        const songTitle = document.querySelector('.spotify-widget .song-title');
        const songArtist = document.querySelector('.spotify-widget .song-artist');
        const progress = document.querySelector('.spotify-widget .progress');
        
        if (songTitle) songTitle.textContent = track.name;
        if (songArtist) songArtist.textContent = track.artist;
        if (progress) {
            progress.style.width = track.progress + '%';
        }
    }
    
    // 테마 변경
    applyTheme(themeName) {
        if (window.app && window.app.uiManager) {
            window.app.uiManager.applySpotifyTheme(themeName);
        }
    }
} 