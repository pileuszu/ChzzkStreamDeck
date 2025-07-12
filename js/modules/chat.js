// CHZZK 채팅 모듈
class ChatModule {
    constructor(settingsManager) {
        this.settingsManager = settingsManager;
        this.isActive = false;
        this.isConnected = false;
        this.websocket = null;
        this.simulationInterval = null;
        this.heartbeatInterval = null;
        this.channelId = null;
        this.chatChannelId = null;
        this.accessToken = null;
        
        this.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Referer': 'https://chzzk.naver.com/',
            'Origin': 'https://chzzk.naver.com'
        };
    }
    
    // 모듈 시작
    async start() {
        console.log('🎛️ 채팅 모듈 시작 요청 중...');
        
        const settings = this.settingsManager.getModuleSettings('chat');
        
        // 채널 ID 확인
        if (!settings.channelId) {
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError('CHZZK 채널 ID를 먼저 설정해주세요.');
            } else {
                alert('CHZZK 채널 ID를 먼저 설정해주세요.');
            }
            return false;
        }
        
        this.channelId = settings.channelId;
        
        try {
            console.log('📡 백엔드 서버에 채팅 모듈 시작 요청...');
            
            // 백엔드 API 호출
            const response = await fetch('http://localhost:3000/api/chat/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    channelId: this.channelId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isActive = true;
                console.log('✅ 채팅 모듈이 터미널에서 시작되었습니다.');
                console.log(`📱 프로세스 ID: ${result.pid}`);
                
                // 상태 모니터링 시작
                this.startStatusMonitoring();
                
                if (window.app && window.app.uiManager) {
                    window.app.uiManager.showSuccess('채팅 모듈이 터미널에서 시작되었습니다.');
                }
                
                return true;
            } else {
                throw new Error(result.error || '백엔드 서버 연결 실패');
            }
            
        } catch (error) {
            console.error('❌ CHZZK 채팅 모듈 시작 실패:', error);
            
            let errorMsg = error.message;
            if (error.message.includes('fetch')) {
                errorMsg = '백엔드 서버가 실행되지 않았습니다. npm start로 서버를 먼저 시작해주세요.';
            }
            
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError(`채팅 모듈 시작 실패: ${errorMsg}`);
            } else {
                alert(`채팅 모듈 시작 실패: ${errorMsg}`);
            }
            return false;
        }
    }

    // 상태 모니터링 시작
    startStatusMonitoring() {
        console.log('📊 채팅 모듈 상태 모니터링 시작...');
        
        // 5초마다 백엔드 서버 상태 확인
        this.statusInterval = setInterval(async () => {
            try {
                const response = await fetch('http://localhost:3000/api/status');
                const result = await response.json();
                
                if (result.success) {
                    const chatStatus = result.status.chat;
                    
                    // 프로세스가 종료된 경우
                    if (!chatStatus.active && this.isActive) {
                        console.log('⚠️ 채팅 프로세스가 예상치 못하게 종료되었습니다.');
                        this.isActive = false;
                        this.isConnected = false;
                        
                        // UI 업데이트
                        if (window.app && window.app.uiManager) {
                            window.app.uiManager.updateModuleCard('chat', false);
                            window.app.uiManager.showError('채팅 프로세스가 종료되었습니다.');
                        }
                        
                        // 토글 스위치 업데이트
                        const toggle = document.getElementById('chat-toggle');
                        if (toggle) {
                            toggle.checked = false;
                        }
                        
                        // 모니터링 중지
                        clearInterval(this.statusInterval);
                        this.statusInterval = null;
                    }
                }
                
            } catch (error) {
                console.warn('🔄 상태 모니터링 오류:', error.message);
            }
        }, 5000);
    }
    
    // 모듈 중지
    async stop() {
        console.log('🛑 채팅 모듈 중지 요청 중...');
        
        try {
            // 백엔드 API 호출
            const response = await fetch('http://localhost:3000/api/chat/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isActive = false;
                this.isConnected = false;
                
                // 모니터링 중지
                if (this.statusInterval) {
                    clearInterval(this.statusInterval);
                    this.statusInterval = null;
                }
                
                console.log('✅ 채팅 모듈이 중지되었습니다.');
                
                if (window.app && window.app.uiManager) {
                    window.app.uiManager.showSuccess('채팅 모듈이 중지되었습니다.');
                }
            } else {
                console.warn('⚠️ 채팅 모듈 중지 요청 실패:', result.error);
            }
            
        } catch (error) {
            console.error('❌ 채팅 모듈 중지 실패:', error);
            // 강제로 상태 변경
            this.isActive = false;
            this.isConnected = false;
        }
    }
    
    // 모듈 재시작
    async restart() {
        console.log('CHZZK 채팅 모듈 재시작 중...');
        this.stop();
        await new Promise(resolve => setTimeout(resolve, 500));
        return await this.start();
    }
    
    // 채널 정보 가져오기
    async getChannelInfo() {
        try {
            const response = await fetch(`https://api.chzzk.naver.com/service/v1/channels/${this.channelId}`, {
                headers: this.headers
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.code === 200 && data.content) {
                    console.log(`CHZZK 채널 정보 획득: ${data.content.channelName || 'N/A'}`);
                    return data.content;
                }
            }
        } catch (error) {
            console.warn(`채널 정보 요청 실패: ${error.message}`);
        }
        return null;
    }
    
    // 라이브 상태 확인
    async getLiveStatus() {
        try {
            const response = await fetch(`https://api.chzzk.naver.com/polling/v2/channels/${this.channelId}/live-status`, {
                headers: this.headers
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.code === 200 && data.content) {
                    const content = data.content;
                    this.chatChannelId = content.chatChannelId;
                    console.log(`라이브 상태: ${content.status || content.liveStatus}`);
                    return content;
                }
            }
        } catch (error) {
            console.warn(`라이브 상태 확인 실패: ${error.message}`);
        }
        return null;
    }
    
    // 액세스 토큰 가져오기
    async getAccessToken() {
        if (!this.chatChannelId) {
            console.error('채팅 채널 ID가 없습니다.');
            return null;
        }
        
        try {
            const response = await fetch(`https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId=${this.chatChannelId}&chatType=STREAMING`, {
                headers: this.headers
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.code === 200 && data.content) {
                    this.accessToken = data.content.accessToken;
                    console.log(`액세스 토큰 획득 완료`);
                    return data.content;
                }
            }
        } catch (error) {
            console.warn(`액세스 토큰 요청 실패: ${error.message}`);
        }
        return null;
    }
    
    // CHZZK 웹소켓 연결
    async connectWebSocket() {
        console.log('CHZZK WebSocket 연결 시도...');
        
        if (!this.accessToken || !this.chatChannelId) {
            throw new Error('액세스 토큰 또는 채팅 채널 ID가 없습니다.');
        }
        
        // kr-ss1 ~ kr-ss10까지 시도
        for (let serverNum = 1; serverNum <= 10; serverNum++) {
            const wsUrl = `wss://kr-ss${serverNum}.chat.naver.com/chat?channelId=${this.chatChannelId}&accessToken=${this.accessToken}`;
            
            try {
                console.log(`WebSocket 연결 시도 ${serverNum}/10: kr-ss${serverNum}`);
                
                this.websocket = new WebSocket(wsUrl);
                
                // 연결 성공 처리
                this.websocket.onopen = () => {
                    console.log(`WebSocket 연결 성공! (kr-ss${serverNum})`);
                    this.isConnected = true;
                    
                    // 채팅 연결 메시지 전송
                    const connectMessage = {
                        ver: "2",
                        cmd: 100,
                        svcid: "game",
                        cid: this.chatChannelId,
                        bdy: {
                            uid: null,
                            devType: 2001,
                            accTkn: this.accessToken,
                            auth: "READ"
                        },
                        tid: 1
                    };
                    
                    this.websocket.send(JSON.stringify(connectMessage));
                    console.log('CHZZK 채팅 연결 완료');
                    
                    // 20초마다 heartbeat
                    this.startHeartbeat();
                };
                
                // 메시지 수신 처리
                this.websocket.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        this.handleWebSocketMessage(message);
                    } catch (error) {
                        console.warn(`메시지 파싱 실패: ${error.message}`);
                    }
                };
                
                // 에러 처리
                this.websocket.onerror = (error) => {
                    console.warn(`WebSocket 오류 (kr-ss${serverNum}): ${error.message}`);
                };
                
                // 연결 종료 처리
                this.websocket.onclose = (event) => {
                    if (this.isConnected) {
                        console.warn(`WebSocket 연결 종료: ${event.code} - ${event.reason}`);
                        this.isConnected = false;
                        this.stopHeartbeat();
                    }
                };
                
                // 연결 대기
                await new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => {
                        reject(new Error('WebSocket 연결 타임아웃'));
                    }, 3000);
                    
                    this.websocket.onopen = () => {
                        clearTimeout(timeout);
                        resolve();
                    };
                    
                    this.websocket.onerror = (error) => {
                        clearTimeout(timeout);
                        reject(error);
                    };
                });
                
                return true; // 연결 성공
                
            } catch (error) {
                console.warn(`kr-ss${serverNum} 연결 실패: ${error.message}`);
                
                if (this.websocket) {
                    this.websocket.close();
                    this.websocket = null;
                }
                
                if (serverNum < 10) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
            }
        }
        
        throw new Error('모든 WebSocket 연결 시도 실패');
    }
    
    // 하트비트 시작
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                const heartbeatMessage = { ver: "2", cmd: 0 };
                this.websocket.send(JSON.stringify(heartbeatMessage));
            }
        }, 20000);
    }
    
    // 하트비트 중지
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    // 웹소켓 메시지 처리
    handleWebSocketMessage(message) {
        if (message.cmd === 0) {
            // 서버 heartbeat 요청 - 응답 필요
            const response = { ver: "2", cmd: 10000 };
            this.websocket.send(JSON.stringify(response));
        } else if (message.cmd === 93101) {
            // 채팅 메시지
            this.handleChatMessage(message);
        }
    }
    
    // 채팅 메시지 처리
    handleChatMessage(message) {
        if (message.bdy && Array.isArray(message.bdy) && message.bdy.length > 0) {
            for (const chatData of message.bdy) {
                try {
                    // 프로필 정보 파싱
                    let profile = {};
                    if (typeof chatData.profile === 'string') {
                        profile = JSON.parse(chatData.profile);
                    } else {
                        profile = chatData.profile || {};
                    }
                    
                    const nickname = profile.nickname || '익명';
                    const content = chatData.msg || chatData.content || '';
                    
                    if (content) {
                        // 배지 처리
                        const badges = [];
                        if (profile.badge) {
                            badges.push(profile.badge);
                        }
                        if (profile.verifiedMark) {
                            badges.push('✓');
                        }
                        
                        // 이모티콘 정보 추출
                        const emoticons = this.extractEmoticons(chatData);
                        
                        // UI에 메시지 추가
                        this.addMessageToUI({
                            username: nickname,
                            message: content,
                            timestamp: new Date(),
                            badges: badges,
                            emoticons: emoticons
                        });
                    }
                } catch (error) {
                    console.warn(`채팅 메시지 처리 오류: ${error.message}`);
                }
            }
        }
    }
    
    // 이모티콘 정보 추출
    extractEmoticons(chatData) {
        const emoticons = [];
        
        if (chatData.extras) {
            try {
                const extras = typeof chatData.extras === 'string' ? JSON.parse(chatData.extras) : chatData.extras;
                if (extras.emojis && Object.keys(extras.emojis).length > 0) {
                    for (const [id, url] of Object.entries(extras.emojis)) {
                        emoticons.push({ id, url });
                    }
                }
            } catch (e) {
                // 이모티콘 파싱 실패 시 무시
            }
        }
        
        return emoticons;
    }
    
    // UI에 메시지 추가
    addMessageToUI(messageData) {
        const chatWidget = document.querySelector('.chat-widget');
        if (!chatWidget) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message';
        
        // 배지 표시
        let badgeHtml = '';
        if (messageData.badges && messageData.badges.length > 0) {
            badgeHtml = messageData.badges.map(badge => `<span class="badge">${badge}</span>`).join('');
        }
        
        // 이모티콘 치환
        let processedMessage = messageData.message;
        if (messageData.emoticons && messageData.emoticons.length > 0) {
            for (const emoticon of messageData.emoticons) {
                const emoticonPattern = new RegExp(`\\{:${emoticon.id}:\\}`, 'g');
                processedMessage = processedMessage.replace(emoticonPattern, 
                    `<img src="${emoticon.url}" alt="${emoticon.id}" class="emoticon" title="${emoticon.id}">`);
            }
        }
        
        messageElement.innerHTML = `
            ${badgeHtml}
            <span class="username">${messageData.username}:</span>
            <span class="message">${processedMessage}</span>
            <span class="timestamp">${messageData.timestamp.toLocaleTimeString()}</span>
        `;
        
        chatWidget.appendChild(messageElement);
        chatWidget.scrollTop = chatWidget.scrollHeight;
        
        // 설정에 따른 메시지 제한 및 페이드 아웃
        const settings = this.settingsManager.getModuleSettings('chat');
        this.limitMessages(settings.maxMessages || 50);
        
        if (settings.fadeTime && settings.fadeTime > 0) {
            this.scheduleMessageRemoval(settings.fadeTime * 1000);
        }
    }
    
    // 최대 메시지 수 제한
    limitMessages(maxMessages) {
        const chatWidget = document.querySelector('.chat-widget');
        if (!chatWidget) return;
        
        while (chatWidget.children.length > maxMessages) {
            chatWidget.removeChild(chatWidget.firstChild);
        }
    }
    
    // 메시지 제거 예약
    scheduleMessageRemoval(delay) {
        setTimeout(() => {
            const chatWidget = document.querySelector('.chat-widget');
            if (chatWidget && chatWidget.firstChild) {
                chatWidget.removeChild(chatWidget.firstChild);
            }
        }, delay);
    }
    
    // 테마 변경
    applyTheme(themeName) {
        if (window.app && window.app.uiManager) {
            window.app.uiManager.applyChatTheme(themeName);
        }
    }
} 