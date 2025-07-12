// 음악봇 모듈 - 채팅 명령을 통한 Spotify 대기열 관리
class MusicBotModule {
    constructor(settingsManager) {
        this.settingsManager = settingsManager;
        this.isActive = false;
        this.chatModule = null;
        this.spotifyModule = null;
        this.eventSource = null;
        this.isListening = false;
        this.lastError = null;
        
        // 명령어 설정
        this.commands = {
            addSong: '!노래추가',
            skipSong: '!건너뛰기',
            currentSong: '!현재곡',
            queue: '!대기열'
        };
        
        // 설정에서 명령어 로드
        this.loadCommands();
        
        // 상태 관리
        this.commandQueue = [];
        this.isProcessing = false;
        
        // 페이지 로드 시 상태 확인
        this.checkInitialStatus();
    }

    // 초기 상태 확인
    async checkInitialStatus() {
        try {
            const response = await fetch(`http://localhost:7112/api/status`);
            const result = await response.json();
            
            if (result.success) {
                const chatActive = result.status.chat && result.status.chat.active;
                const spotifyActive = result.status.spotify && result.status.spotify.active;
                
                if (chatActive && spotifyActive && this.canStart()) {
                    this.isActive = true;
                    this.startListening();
                    
                    // 토글 스위치 활성화
                    const toggle = document.getElementById('musicbot-toggle');
                    if (toggle) {
                        toggle.checked = true;
                    }
                    
                    // 모듈 카드 업데이트
                    if (window.app && window.app.uiManager) {
                        window.app.uiManager.updateModuleCard('musicbot', true);
                    }
                    
                    console.log('✅ 음악봇 모듈이 이미 실행 중입니다.');
                }
            }
        } catch (error) {
            // 서버가 실행되지 않은 경우 무시
        }
    }

    // 모듈 시작 가능 여부 확인
    canStart() {
        // 메인 앱에서 참조 가져오기
        if (window.app) {
            this.chatModule = window.app.chatModule;
            this.spotifyModule = window.app.spotifyModule;
            
            return this.chatModule && this.chatModule.isActive && 
                   this.spotifyModule && this.spotifyModule.isActive;
        }
        return false;
    }

    // 모듈 시작
    async start() {
        if (!this.canStart()) {
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError('채팅 모듈과 Spotify 모듈이 먼저 실행되어야 합니다.');
            } else {
                alert('채팅 모듈과 Spotify 모듈이 먼저 실행되어야 합니다.');
            }
            return false;
        }

        try {
            this.isActive = true;
            this.startListening();
            
            console.log('✅ 음악봇 모듈 시작');
            
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showSuccess('음악봇 모듈이 시작되었습니다.');
            }
            
            return true;
            
        } catch (error) {
            console.error('❌ 음악봇 모듈 시작 실패:', error);
            
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError(`음악봇 모듈 시작 실패: ${error.message}`);
            } else {
                alert(`음악봇 모듈 시작 실패: ${error.message}`);
            }
            return false;
        }
    }

    // 모듈 중지
    stop() {
        this.isActive = false;
        this.stopListening();
        
        console.log('✅ 음악봇 모듈 중지');
        
        if (window.app && window.app.uiManager) {
            window.app.uiManager.showSuccess('음악봇 모듈이 중지되었습니다.');
        }
    }

    // 모듈 재시작
    async restart() {
        console.log('🔄 음악봇 모듈 재시작');
        this.stop();
        await new Promise(resolve => setTimeout(resolve, 500));
        return await this.start();
    }

    // 채팅 메시지 리스닝 시작
    startListening() {
        if (this.isListening) return;
        
        try {
            this.eventSource = new EventSource('http://localhost:7112/api/chat/stream');
            this.isListening = true;
            
            this.eventSource.onmessage = (event) => {
                try {
                    const messageData = JSON.parse(event.data);
                    if (messageData.type === 'chat') {
                        this.handleChatMessage(messageData);
                    }
                } catch (error) {
                    console.error('음악봇 메시지 파싱 오류:', error);
                }
            };
            
            this.eventSource.onerror = (error) => {
                console.error('음악봇 SSE 연결 오류:', error);
                this.stopListening();
                
                // 재연결 시도
                setTimeout(() => {
                    if (this.isActive) {
                        this.startListening();
                    }
                }, 5000);
            };
            
            console.log('🎵 음악봇 채팅 리스닝 시작');
            
        } catch (error) {
            console.error('음악봇 리스닝 시작 실패:', error);
        }
    }

    // 채팅 메시지 리스닝 중지
    stopListening() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        this.isListening = false;
        
        console.log('🎵 음악봇 채팅 리스닝 중지');
    }

    // 채팅 메시지 처리
    async handleChatMessage(messageData) {
        if (!this.isActive || !messageData.message) return;
        
        const message = messageData.message.trim();
        const username = messageData.username || '익명';
        
        // 노래 추가 명령 처리
        if (message.startsWith(this.commands.addSong)) {
            const keyword = message.substring(this.commands.addSong.length).trim();
            if (keyword) {
                await this.handleAddSongCommand(username, keyword);
            } else {
                this.sendChatResponse(`@${username} 사용법: ${this.commands.addSong} [검색 키워드]`);
            }
        }
        // 건너뛰기 명령 처리
        else if (message.startsWith(this.commands.skipSong)) {
            await this.handleSkipSongCommand(username);
        }
        // 현재곡 명령 처리
        else if (message.startsWith(this.commands.currentSong)) {
            await this.handleCurrentSongCommand(username);
        }
        // 대기열 명령 처리
        else if (message.startsWith(this.commands.queue)) {
            await this.handleQueueCommand(username);
        }
    }

    // 노래 추가 명령 처리
    async handleAddSongCommand(username, keyword) {
        try {
            console.log(`🎵 음악 검색 요청: "${keyword}" by ${username}`);
            
            // 검색 실행
            const searchResult = await this.searchSpotifyTrack(keyword);
            
            if (searchResult) {
                // 대기열에 추가
                const addResult = await this.addToQueue(searchResult.uri);
                
                if (addResult) {
                    this.sendChatResponse(`@${username} 🎵 "${searchResult.name}" by ${searchResult.artists[0].name} 곡이 대기열에 추가되었습니다!`);
                } else {
                    // 구체적인 오류 메시지 표시
                    const errorMessage = this.lastError || '대기열 추가에 실패했습니다.';
                    this.sendChatResponse(`@${username} ❌ ${errorMessage}`);
                }
            } else {
                this.sendChatResponse(`@${username} ❌ "${keyword}" 검색 결과를 찾을 수 없습니다.`);
            }
            
        } catch (error) {
            console.error('노래 추가 명령 처리 오류:', error);
            this.sendChatResponse(`@${username} ❌ 노래 추가 중 오류가 발생했습니다.`);
        }
    }

    // 건너뛰기 명령 처리
    async handleSkipSongCommand(username) {
        try {
            const skipResult = await this.skipCurrentTrack();
            
            if (skipResult) {
                this.sendChatResponse(`@${username} ⏭️ 현재 곡을 건너뛰었습니다.`);
            } else {
                this.sendChatResponse(`@${username} ❌ 건너뛰기에 실패했습니다.`);
            }
            
        } catch (error) {
            console.error('건너뛰기 명령 처리 오류:', error);
            this.sendChatResponse(`@${username} ❌ 건너뛰기 중 오류가 발생했습니다.`);
        }
    }

    // 현재곡 명령 처리
    async handleCurrentSongCommand(username) {
        try {
            const currentTrack = await this.getCurrentTrack();
            
            if (currentTrack && currentTrack.item) {
                const track = currentTrack.item;
                const artists = track.artists.map(artist => artist.name).join(', ');
                const progressMs = currentTrack.progress_ms || 0;
                const durationMs = track.duration_ms;
                
                const progress = this.formatTime(progressMs);
                const duration = this.formatTime(durationMs);
                
                this.sendChatResponse(`@${username} 🎵 현재 재생 중: "${track.name}" by ${artists} [${progress}/${duration}]`);
            } else {
                this.sendChatResponse(`@${username} ❌ 현재 재생 중인 곡이 없습니다.`);
            }
            
        } catch (error) {
            console.error('현재곡 명령 처리 오류:', error);
            this.sendChatResponse(`@${username} ❌ 현재곡 정보를 가져올 수 없습니다.`);
        }
    }

    // 대기열 명령 처리
    async handleQueueCommand(username) {
        try {
            const queue = await this.getQueue();
            
            if (queue && queue.queue && queue.queue.length > 0) {
                const nextTracks = queue.queue.slice(0, 3); // 다음 3곡만 표시
                const queueText = nextTracks.map((track, index) => 
                    `${index + 1}. ${track.name} by ${track.artists[0].name}`
                ).join(' | ');
                
                this.sendChatResponse(`@${username} 📋 대기열 (다음 ${nextTracks.length}곡): ${queueText}`);
            } else {
                this.sendChatResponse(`@${username} ❌ 대기열이 비어있습니다.`);
            }
            
        } catch (error) {
            console.error('대기열 명령 처리 오류:', error);
            this.sendChatResponse(`@${username} ❌ 대기열 정보를 가져올 수 없습니다.`);
        }
    }

    // Spotify 트랙 검색
    async searchSpotifyTrack(keyword) {
        try {
            const settings = this.settingsManager.getModuleSettings('spotify');
            const accessToken = await this.getSpotifyAccessToken();
            
            if (!accessToken) {
                throw new Error('Spotify 액세스 토큰이 없습니다.');
            }
            
            const response = await fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(keyword)}&type=track&limit=1`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`Spotify 검색 실패: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.tracks && data.tracks.items && data.tracks.items.length > 0) {
                return data.tracks.items[0];
            }
            
            return null;
            
        } catch (error) {
            console.error('Spotify 검색 오류:', error);
            return null;
        }
    }

    // 대기열에 추가
    async addToQueue(uri) {
        try {
            const accessToken = await this.getSpotifyAccessToken();
            
            if (!accessToken) {
                throw new Error('Spotify 액세스 토큰이 없습니다.');
            }
            
            // 먼저 활성 장치 확인
            const deviceCheck = await this.checkActiveDevice(accessToken);
            if (!deviceCheck.success) {
                throw new Error(deviceCheck.message);
            }
            
            const response = await fetch(`https://api.spotify.com/v1/me/player/queue?uri=${encodeURIComponent(uri)}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            
            if (!response.ok) {
                // 구체적인 오류 메시지 처리
                if (response.status === 403) {
                    const errorData = await response.json().catch(() => null);
                    if (errorData && errorData.error) {
                        if (errorData.error.reason === 'PREMIUM_REQUIRED') {
                            throw new Error('Spotify Premium 계정이 필요합니다.');
                        } else if (errorData.error.reason === 'NO_ACTIVE_DEVICE') {
                            throw new Error('활성 Spotify 장치가 없습니다. Spotify 앱에서 음악을 재생해주세요.');
                        }
                    }
                    throw new Error('Spotify에서 요청을 거부했습니다. Premium 계정 또는 활성 장치가 필요할 수 있습니다.');
                } else if (response.status === 401) {
                    throw new Error('Spotify 인증이 만료되었습니다. 다시 로그인해주세요.');
                } else {
                    throw new Error(`Spotify API 오류: ${response.status}`);
                }
            }
            
            return true;
            
        } catch (error) {
            console.error('대기열 추가 오류:', error);
            // 사용자에게 구체적인 오류 메시지 전달
            this.lastError = error.message;
            return false;
        }
    }

    // 현재 트랙 건너뛰기
    async skipCurrentTrack() {
        try {
            const accessToken = await this.getSpotifyAccessToken();
            
            if (!accessToken) {
                throw new Error('Spotify 액세스 토큰이 없습니다.');
            }
            
            const response = await fetch('https://api.spotify.com/v1/me/player/next', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            
            return response.ok;
            
        } catch (error) {
            console.error('건너뛰기 오류:', error);
            return false;
        }
    }

    // 현재 재생 중인 트랙 가져오기
    async getCurrentTrack() {
        try {
            const accessToken = await this.getSpotifyAccessToken();
            
            if (!accessToken) {
                throw new Error('Spotify 액세스 토큰이 없습니다.');
            }
            
            const response = await fetch('https://api.spotify.com/v1/me/player/currently-playing', {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            
            if (response.ok && response.status !== 204) {
                return await response.json();
            }
            
            return null;
            
        } catch (error) {
            console.error('현재 트랙 가져오기 오류:', error);
            return null;
        }
    }

    // 대기열 가져오기
    async getQueue() {
        try {
            const accessToken = await this.getSpotifyAccessToken();
            
            if (!accessToken) {
                throw new Error('Spotify 액세스 토큰이 없습니다.');
            }
            
            const response = await fetch('https://api.spotify.com/v1/me/player/queue', {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            
            if (response.ok) {
                return await response.json();
            }
            
            return null;
            
        } catch (error) {
            console.error('대기열 가져오기 오류:', error);
            return null;
        }
    }

    // 활성 장치 확인
    async checkActiveDevice(accessToken) {
        try {
            const response = await fetch('https://api.spotify.com/v1/me/player', {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            
            if (response.status === 204) {
                // 활성 장치 없음
                return {
                    success: false,
                    message: '활성 Spotify 장치가 없습니다. Spotify 앱에서 음악을 재생해주세요.'
                };
            }
            
            if (!response.ok) {
                if (response.status === 403) {
                    return {
                        success: false,
                        message: 'Spotify Premium 계정이 필요합니다.'
                    };
                }
                return {
                    success: false,
                    message: `장치 확인 실패: ${response.status}`
                };
            }
            
            const playerData = await response.json();
            
            if (!playerData.device || !playerData.device.is_active) {
                return {
                    success: false,
                    message: '활성 Spotify 장치가 없습니다. Spotify 앱에서 음악을 재생해주세요.'
                };
            }
            
            return {
                success: true,
                device: playerData.device
            };
            
        } catch (error) {
            console.error('활성 장치 확인 오류:', error);
            return {
                success: false,
                message: '장치 확인 중 오류가 발생했습니다.'
            };
        }
    }

    // Spotify 액세스 토큰 가져오기 (서버 기반)
    async getSpotifyAccessToken() {
        try {
            // 서버에서 토큰 조회
            const response = await fetch('http://localhost:7112/api/spotify/token');
            const result = await response.json();
            
            if (result.success && result.hasToken && !result.isExpired) {
                console.log('🔑 서버에서 유효한 토큰 조회됨');
                return result.token;
            } else {
                console.log('❌ 서버에 유효한 토큰이 없음');
                return null;
            }
            
        } catch (error) {
            console.error('❌ 서버 토큰 조회 오류:', error);
            
            // 폴백: 기존 방식 시도
            if (this.spotifyModule && this.spotifyModule.accessToken) {
                return this.spotifyModule.accessToken;
            }
            
            return null;
        }
    }

    // 시간 포맷팅 (ms -> mm:ss)
    formatTime(ms) {
        const totalSeconds = Math.floor(ms / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    // 채팅 응답 전송 (콘솔 출력)
    sendChatResponse(message) {
        console.log(`🤖 음악봇: ${message}`);
        
        // UI에 알림 표시
        if (window.app && window.app.uiManager) {
            window.app.uiManager.showInfo(message);
        }
    }

    // 설정에서 명령어 로드
    loadCommands() {
        const settings = this.settingsManager.getModuleSettings('musicbot');
        if (settings.commands) {
            this.commands = { ...this.commands, ...settings.commands };
        }
    }
} 