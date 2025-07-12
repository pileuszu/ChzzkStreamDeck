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

        
        this.isActive = false;
        this.isAuthenticated = false;
        this.accessToken = null;
        this.refreshToken = null;
        
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        

    }
    
    // 모듈 재시작
    async restart() {

        this.stop();
        await new Promise(resolve => setTimeout(resolve, 500));
        return await this.start();
    }
    
    // Spotify 인증
    async authenticate() {
        const settings = this.settingsManager.getModuleSettings('spotify');
        
        console.log('🎵 Spotify 인증 시작');
        console.log('Settings:', { 
            hasClientId: !!settings.clientId, 
            hasClientSecret: !!settings.clientSecret, 
            redirectUri: settings.redirectUri 
        });
        
        // 설정 확인
        if (!settings.clientId || !settings.clientSecret) {
            const errorMsg = 'Spotify Client ID와 Client Secret을 먼저 설정해주세요.';
            console.error('❌', errorMsg);
            
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError(errorMsg);
            } else {
                alert(errorMsg);
            }
            
            return false;
        }
        
        try {
            // 서버에서 토큰 먼저 확인
            const serverTokenValid = await this.getTokenFromServer();
            if (serverTokenValid) {
                console.log('✅ 서버 토큰 사용');
                return true;
            }
            
            // 로컬 저장된 토큰 확인
            const savedToken = localStorage.getItem('spotify-access-token');
            const savedRefreshToken = localStorage.getItem('spotify-refresh-token');
            const tokenExpiry = localStorage.getItem('spotify-token-expiry');
            
            console.log('💾 저장된 토큰 상태:', {
                hasToken: !!savedToken,
                hasRefreshToken: !!savedRefreshToken,
                tokenExpiry: tokenExpiry ? new Date(parseInt(tokenExpiry)).toLocaleString() : 'N/A',
                isExpired: tokenExpiry ? Date.now() >= parseInt(tokenExpiry) : 'N/A'
            });
            
            if (savedToken && tokenExpiry && Date.now() < parseInt(tokenExpiry)) {
                this.accessToken = savedToken;
                this.refreshToken = savedRefreshToken;
                this.isAuthenticated = true;
                
                // 로컬 토큰을 서버에도 저장
                await this.saveTokenToServer(this.accessToken, this.refreshToken, parseInt(tokenExpiry));
                
                console.log('✅ 저장된 Spotify 토큰 사용');
                return true;
            }
            
            // 리프레시 토큰이 있으면 토큰 갱신 시도
            if (savedRefreshToken) {
                console.log('🔄 리프레시 토큰으로 갱신 시도');
                const refreshResult = await this.refreshAccessToken(savedRefreshToken);
                if (refreshResult) {
                    return true;
                }
            }
            
            // 새로운 인증 필요
            console.log('🆕 새로운 인증 필요 - 팝업 창 열기');
            await this.authorizeUser();
            return true;
            
        } catch (error) {
            console.error('❌ Spotify 인증 실패:', error);
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError(`Spotify 인증에 실패했습니다: ${error.message}`);
            } else {
                alert(`Spotify 인증에 실패했습니다: ${error.message}`);
            }
            return false;
        }
    }

    // 사용자 인증 (Authorization Code Flow)
    async authorizeUser() {
        const settings = this.settingsManager.getModuleSettings('spotify');
        
        if (!settings.clientId || !settings.clientSecret) {
            throw new Error('Client ID와 Client Secret이 설정되지 않았습니다.');
        }
        
        const redirectUri = settings.redirectUri || 'http://localhost:7112/spotify/callback';
        
        // Spotify 문서에 따른 필수 스코프들
        const scopes = [
            'user-read-currently-playing',
            'user-read-playback-state',
            'user-modify-playback-state',
            'user-read-recently-played',
            'user-read-playback-position',
            'user-top-read',
            'playlist-read-private',
            'playlist-read-collaborative',
            'playlist-modify-public',
            'playlist-modify-private'
        ].join(' ');
        
        // CSRF 보호를 위한 고유 state 생성
        const state = 'spotify_auth_' + Math.random().toString(36).substring(2, 15);
        
        // Spotify 인증 URL 생성 (문서 기준)
        const authUrl = new URL('https://accounts.spotify.com/authorize');
        authUrl.searchParams.set('response_type', 'code');
        authUrl.searchParams.set('client_id', settings.clientId);
        authUrl.searchParams.set('scope', scopes);
        authUrl.searchParams.set('redirect_uri', redirectUri);
        authUrl.searchParams.set('state', state);
        
        console.log('🔐 인증 URL 생성:', authUrl.toString());
        console.log('🔐 사용할 Redirect URI:', redirectUri);
        console.log('🔐 사용할 State:', state);
        
        // 팝업 창 열기
        const popup = window.open(
            authUrl.toString(),
            'spotify_auth',
            'width=500,height=700,scrollbars=yes,resizable=yes'
        );
        
        if (!popup) {
            throw new Error('팝업이 차단되었습니다. 브라우저에서 팝업을 허용해주세요.');
        }
        
        // 팝업 창이 열렸는지 확인
        if (popup.closed) {
            throw new Error('팝업 창을 열 수 없습니다.');
        }
        
        console.log('🪟 인증 팝업 창이 열렸습니다.');
        
        return new Promise((resolve, reject) => {
            let resolved = false;
            
            // 메시지 리스너 등록
            const messageListener = async (event) => {
                // 보안을 위해 origin 확인
                if (event.origin !== window.location.origin) {
                    console.warn('⚠️ 잘못된 origin에서 메시지 수신:', event.origin);
                    return;
                }
                
                console.log('📨 메시지 수신:', event.data);
                
                if (event.data.type === 'spotify_auth') {
                    if (resolved) return;
                    resolved = true;
                    
                    // 리스너 정리
                    window.removeEventListener('message', messageListener);
                    clearInterval(popupChecker);
                    
                    if (event.data.error) {
                        console.error('❌ 인증 오류:', event.data.error);
                        reject(new Error(`인증 실패: ${event.data.error}`));
                        return;
                    }
                    
                    if (!event.data.code) {
                        console.error('❌ 인증 코드가 없습니다.');
                        reject(new Error('인증 코드를 받지 못했습니다.'));
                        return;
                    }
                    
                    console.log('✅ 인증 코드 수신:', event.data.code.substring(0, 20) + '...');
                    
                    try {
                        // 토큰 교환 시도
                        await this.exchangeCodeForToken(event.data.code);
                        console.log('🎉 인증 완료!');
                        resolve(true);
                    } catch (error) {
                        console.error('❌ 토큰 교환 실패:', error);
                        reject(error);
                    }
                }
            };
            
            // 팝업 상태 확인 타이머
            const popupChecker = setInterval(() => {
                if (popup.closed) {
                    if (resolved) return;
                    resolved = true;
                    
                    console.log('🚪 팝업 창이 닫혔습니다.');
                    window.removeEventListener('message', messageListener);
                    clearInterval(popupChecker);
                    
                    // 인증이 완료되었는지 확인
                    if (this.isAuthenticated) {
                        console.log('✅ 인증이 완료되었습니다.');
                        resolve(true);
                    } else {
                        console.log('❌ 인증이 취소되었습니다.');
                        reject(new Error('사용자가 인증을 취소했습니다.'));
                    }
                }
            }, 1000);
            
            // 메시지 리스너 등록
            window.addEventListener('message', messageListener);
            
            // 타임아웃 설정 (5분)
            setTimeout(() => {
                if (resolved) return;
                resolved = true;
                
                console.log('⏰ 인증 타임아웃');
                window.removeEventListener('message', messageListener);
                clearInterval(popupChecker);
                
                if (!popup.closed) {
                    popup.close();
                }
                
                reject(new Error('인증 시간이 초과되었습니다.'));
            }, 5 * 60 * 1000); // 5분
        });
    }

    // 인증 코드를 액세스 토큰으로 교환
    async exchangeCodeForToken(code) {
        const settings = this.settingsManager.getModuleSettings('spotify');
        const redirectUri = settings.redirectUri || 'http://localhost:7112/spotify/callback';
        
        console.log('🔄 토큰 교환 시작');
        console.log('🔄 사용할 코드:', code.substring(0, 20) + '...');
        console.log('🔄 사용할 Redirect URI:', redirectUri);
        
        // Authorization 헤더 생성 (Basic Auth)
        const authString = btoa(`${settings.clientId}:${settings.clientSecret}`);
        
        // 요청 본문 생성
        const requestBody = new URLSearchParams({
            grant_type: 'authorization_code',
            code: code,
            redirect_uri: redirectUri
        });
        
        console.log('📤 토큰 요청 본문:', requestBody.toString());
        
        try {
            const response = await fetch('https://accounts.spotify.com/api/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': `Basic ${authString}`
                },
                body: requestBody.toString()
            });
            
            console.log('📥 토큰 응답 상태:', response.status, response.statusText);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ 토큰 교환 오류 응답:', errorData);
                throw new Error(`토큰 교환 실패: ${errorData.error_description || errorData.error || response.statusText}`);
            }
            
            const tokenData = await response.json();
            console.log('🎫 토큰 데이터 수신:', { 
                hasAccessToken: !!tokenData.access_token, 
                hasRefreshToken: !!tokenData.refresh_token,
                expiresIn: tokenData.expires_in,
                tokenType: tokenData.token_type,
                scope: tokenData.scope
            });
            
            // 토큰 저장
            this.accessToken = tokenData.access_token;
            this.refreshToken = tokenData.refresh_token;
            this.isAuthenticated = true;
            
            // localStorage에 저장
            const expiryTime = Date.now() + (tokenData.expires_in * 1000);
            localStorage.setItem('spotify-access-token', this.accessToken);
            localStorage.setItem('spotify-refresh-token', this.refreshToken);
            localStorage.setItem('spotify-token-expiry', expiryTime.toString());
            
            console.log('💾 토큰 localStorage 저장 완료');
            
            // 서버에도 토큰 저장
            await this.saveTokenToServer(this.accessToken, this.refreshToken, expiryTime);
            
            console.log('⏰ 토큰 만료 시간:', new Date(expiryTime).toLocaleString());
            
            return true;
            
        } catch (error) {
            console.error('❌ 토큰 교환 중 오류:', error);
            throw error;
        }
    }

    // 액세스 토큰 갱신
    async refreshAccessToken(refreshToken) {
        const settings = this.settingsManager.getModuleSettings('spotify');
        
        console.log('🔄 토큰 갱신 시도');
        console.log('🔄 사용할 리프레시 토큰:', refreshToken.substring(0, 20) + '...');
        
        const authString = btoa(`${settings.clientId}:${settings.clientSecret}`);
        
        const requestBody = new URLSearchParams({
            grant_type: 'refresh_token',
            refresh_token: refreshToken
        });
        
        try {
            const response = await fetch('https://accounts.spotify.com/api/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': `Basic ${authString}`
                },
                body: requestBody.toString()
            });
            
            console.log('📥 토큰 갱신 응답:', response.status, response.statusText);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ 토큰 갱신 오류:', errorData);
                
                // 리프레시 토큰이 만료되었거나 유효하지 않은 경우
                if (errorData.error === 'invalid_grant') {
                    console.log('🗑️ 만료된 토큰 삭제');
                    localStorage.removeItem('spotify-access-token');
                    localStorage.removeItem('spotify-refresh-token');
                    localStorage.removeItem('spotify-token-expiry');
                    this.accessToken = null;
                    this.refreshToken = null;
                    this.isAuthenticated = false;
                }
                
                throw new Error(`토큰 갱신 실패: ${errorData.error_description || errorData.error}`);
            }
            
            const tokenData = await response.json();
            console.log('🎫 갱신된 토큰 데이터:', { 
                hasAccessToken: !!tokenData.access_token, 
                hasRefreshToken: !!tokenData.refresh_token,
                expiresIn: tokenData.expires_in
            });
            
            // 새로운 토큰 저장
            this.accessToken = tokenData.access_token;
            
            // 새로운 리프레시 토큰이 있으면 업데이트
            if (tokenData.refresh_token) {
                this.refreshToken = tokenData.refresh_token;
                localStorage.setItem('spotify-refresh-token', tokenData.refresh_token);
            }
            
            // 액세스 토큰과 만료 시간 업데이트
            const expiryTime = Date.now() + (tokenData.expires_in * 1000);
            localStorage.setItem('spotify-access-token', this.accessToken);
            localStorage.setItem('spotify-token-expiry', expiryTime.toString());
            
            // 서버에도 토큰 저장
            await this.saveTokenToServer(this.accessToken, this.refreshToken, expiryTime);
            
            this.isAuthenticated = true;
            console.log('✅ 토큰 갱신 완료');
            
            return true;
            
        } catch (error) {
            console.error('❌ 토큰 갱신 실패:', error);
            return false;
        }
    }
    
    // 현재 재생 중인 트랙 가져오기
    async getCurrentTrack() {
        if (!this.isAuthenticated) return null;
        
        try {
            const response = await fetch('https://api.spotify.com/v1/me/player/currently-playing', {
                headers: {
                    'Authorization': 'Bearer ' + this.accessToken
                }
            });
            
            if (response.status === 204) {
                // 재생 중인 트랙이 없음
                return null;
            }
            
            if (!response.ok) {
                throw new Error('트랙 정보 가져오기 실패');
            }
            
            const data = await response.json();
            
            if (data.item) {
                return {
                    name: data.item.name,
                    artist: data.item.artists[0].name,
                    album: data.item.album.name,
                    progress: Math.floor((data.progress_ms / data.item.duration_ms) * 100),
                    duration: data.item.duration_ms,
                    isPlaying: data.is_playing
                };
            }
            
            return null;
            
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
    
    // 서버에 토큰 저장
    async saveTokenToServer(accessToken, refreshToken, expiryTime) {
        try {
            const settings = this.settingsManager.getModuleSettings('spotify');
            
            const response = await fetch('http://localhost:7112/api/spotify/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    accessToken,
                    refreshToken,
                    expiryTime,
                    clientId: settings.clientId,
                    clientSecret: settings.clientSecret
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('💾 토큰 서버 저장 완료');
            } else {
                console.error('❌ 토큰 서버 저장 실패:', result.error);
            }
            
        } catch (error) {
            console.error('❌ 토큰 서버 저장 오류:', error);
        }
    }
    
    // 서버에서 토큰 조회
    async getTokenFromServer() {
        try {
            const response = await fetch('http://localhost:7112/api/spotify/token');
            const result = await response.json();
            
            if (result.success && result.hasToken && !result.isExpired) {
                console.log('🔄 서버에서 토큰 조회 성공');
                this.accessToken = result.token;
                this.isAuthenticated = true;
                return true;
            } else {
                console.log('🔄 서버에 유효한 토큰 없음');
                return false;
            }
            
        } catch (error) {
            console.error('❌ 서버 토큰 조회 오류:', error);
            return false;
        }
    }

    // 테마 변경
    applyTheme(themeName) {
        if (window.app && window.app.uiManager) {
            window.app.uiManager.applySpotifyTheme(themeName);
        }
    }
} 