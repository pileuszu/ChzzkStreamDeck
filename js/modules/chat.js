// 채팅 모듈
export class ChatModule {
    constructor(settingsManager) {
        this.settingsManager = settingsManager;
        this.isActive = false;
        this.isConnected = false;
        this.websocket = null;
        this.simulationInterval = null;
    }
    
    // 모듈 시작
    async start() {
        console.log('채팅 모듈 시작 중...');
        
        const settings = this.settingsManager.getModuleSettings('chat');
        
        // 채널 ID 확인
        if (!settings.channelId) {
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError('Channel ID를 먼저 설정해주세요.');
            } else {
                alert('Channel ID를 먼저 설정해주세요.');
            }
            return false;
        }
        
        try {
            // 치지직 웹소켓 연결
            const connectSuccess = await this.connectWebSocket();
            if (!connectSuccess) {
                return false;
            }
            
            this.isActive = true;
            this.startSimulation(); // 데모용 시뮬레이션
            
            console.log('채팅 모듈이 시작되었습니다.');
            return true;
            
        } catch (error) {
            console.error('채팅 모듈 시작 실패:', error);
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError('채팅 모듈 시작에 실패했습니다.');
            } else {
                alert('채팅 모듈 시작에 실패했습니다.');
            }
            return false;
        }
    }
    
    // 모듈 중지
    stop() {
        console.log('채팅 모듈 중지 중...');
        
        this.isActive = false;
        this.isConnected = false;
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
            this.simulationInterval = null;
        }
        
        console.log('채팅 모듈이 중지되었습니다.');
    }
    
    // 모듈 재시작
    async restart() {
        console.log('채팅 모듈 재시작 중...');
        this.stop();
        await new Promise(resolve => setTimeout(resolve, 500));
        return await this.start();
    }
    
    // 치지직 웹소켓 연결
    async connectWebSocket() {
        const settings = this.settingsManager.getModuleSettings('chat');
        
        try {
            console.log(`치지직 채널 ${settings.channelId}에 연결 중...`);
            
            // 실제 치지직 웹소켓 연결 로직은 별도 테스트 폴더에서 구현 예정
            // 현재는 시뮬레이션
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            this.isConnected = true;
            console.log('치지직 웹소켓 연결 성공!');
            return true;
            
        } catch (error) {
            console.error('치지직 웹소켓 연결 실패:', error);
            if (window.app && window.app.uiManager) {
                window.app.uiManager.showError('채팅 연결에 실패했습니다. Channel ID를 확인해주세요.');
            } else {
                alert('채팅 연결에 실패했습니다. Channel ID를 확인해주세요.');
            }
            return false;
        }
    }
    
    // 채팅 메시지 처리
    handleMessage(messageData) {
        const settings = this.settingsManager.getModuleSettings('chat');
        
        // 메시지를 UI에 추가
        this.addMessageToUI({
            username: messageData.username || '익명',
            message: messageData.message || '',
            timestamp: new Date(),
            badges: messageData.badges || []
        });
        
        // 최대 메시지 수 제한
        this.limitMessages(settings.maxMessages);
        
        // 메시지 사라지는 시간 처리
        if (settings.fadeTime > 0) {
            this.scheduleMessageRemoval(settings.fadeTime * 1000);
        }
    }
    
    // UI에 메시지 추가
    addMessageToUI(messageData) {
        const chatWidget = document.querySelector('.chat-widget');
        if (!chatWidget) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message';
        messageElement.innerHTML = `
            <span class="username">${messageData.username}:</span>
            <span class="message">${messageData.message}</span>
        `;
        
        chatWidget.appendChild(messageElement);
        chatWidget.scrollTop = chatWidget.scrollHeight;
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
    
    // 데모용 메시지 시뮬레이션
    startSimulation() {
        const demoMessages = [
            { username: "스트리머팬", message: "오늘 방송 재밌네요!" },
            { username: "구독자123", message: "ㅋㅋㅋㅋㅋ 개웃겨" },
            { username: "뷰어456", message: "다음엔 뭐하실거에요?" },
            { username: "팔로워789", message: "화이팅!!" },
            { username: "새로운유저", message: "안녕하세요!" },
            { username: "랜덤시청자", message: "굿굿!" },
            { username: "팬클럽", message: "최고에요!" },
            { username: "구독자999", message: "ㅎㅎㅎ" }
        ];
        
        this.simulationInterval = setInterval(() => {
            if (Math.random() > 0.3) {
                const randomMessage = demoMessages[Math.floor(Math.random() * demoMessages.length)];
                this.handleMessage(randomMessage);
            }
        }, 2000);
    }
    
    // 테마 변경
    applyTheme(themeName) {
        if (window.app && window.app.uiManager) {
            window.app.uiManager.applyChatTheme(themeName);
        }
    }
} 