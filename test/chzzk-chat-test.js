// 치지직 채팅 웹소켓 테스트
class ChzzkChatTest {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.channelId = null;
        this.chatChannelId = null;
        this.accessToken = null;
    }
    
    // 치지직 채널 정보 가져오기
    async getChannelInfo(channelId) {
        try {
            const response = await fetch(`https://api.chzzk.naver.com/polling/v2/channels/${channelId}/live-status`);
            if (!response.ok) {
                throw new Error('채널 정보를 가져올 수 없습니다');
            }
            return await response.json();
        } catch (error) {
            console.error('채널 정보 가져오기 실패:', error);
            throw error;
        }
    }
    
    // 채팅 채널 ID 가져오기
    async getChatChannelId(channelId) {
        try {
            const response = await fetch(`https://api.chzzk.naver.com/polling/v1/channels/${channelId}/live-detail`);
            if (!response.ok) {
                throw new Error('채팅 채널 정보를 가져올 수 없습니다');
            }
            const data = await response.json();
            return data.content?.chatChannelId;
        } catch (error) {
            console.error('채팅 채널 ID 가져오기 실패:', error);
            throw error;
        }
    }
    
    // 액세스 토큰 가져오기
    async getAccessToken(chatChannelId) {
        try {
            const response = await fetch(`https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId=${chatChannelId}&chatType=STREAMING`);
            if (!response.ok) {
                throw new Error('액세스 토큰을 가져올 수 없습니다');
            }
            const data = await response.json();
            return data.content?.accessToken;
        } catch (error) {
            console.error('액세스 토큰 가져오기 실패:', error);
            throw error;
        }
    }
    
    // 웹소켓 연결
    async connect(channelId, customChatChannelId = null) {
        try {
            updateStatus('연결 중...', 'connecting');
            addMessage('시스템', '연결을 시도하고 있습니다...');
            
            this.channelId = channelId;
            
            // 채널 정보 확인
            addMessage('시스템', '채널 정보를 확인하고 있습니다...');
            const channelInfo = await this.getChannelInfo(channelId);
            addMessage('시스템', `채널 정보: ${JSON.stringify(channelInfo)}`, channelInfo);
            
            // 채팅 채널 ID 가져오기
            this.chatChannelId = customChatChannelId || await this.getChatChannelId(channelId);
            if (!this.chatChannelId) {
                throw new Error('채팅 채널 ID를 찾을 수 없습니다');
            }
            
            document.getElementById('chat-channel-id').value = this.chatChannelId;
            addMessage('시스템', `채팅 채널 ID: ${this.chatChannelId}`);
            
            // 액세스 토큰 가져오기
            addMessage('시스템', '액세스 토큰을 가져오고 있습니다...');
            this.accessToken = await this.getAccessToken(this.chatChannelId);
            if (!this.accessToken) {
                throw new Error('액세스 토큰을 받을 수 없습니다');
            }
            addMessage('시스템', '액세스 토큰을 성공적으로 받았습니다');
            
            // 웹소켓 연결
            addMessage('시스템', '웹소켓에 연결하고 있습니다...');
            const wsUrl = `wss://kr-ss.chat.naver.com/chat`;
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                addMessage('시스템', '웹소켓 연결 성공!');
                this.sendConnectionRequest();
            };
            
            this.websocket.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.websocket.onclose = (event) => {
                this.isConnected = false;
                updateStatus(`연결 종료 (코드: ${event.code})`, 'disconnected');
                addMessage('시스템', `웹소켓 연결이 종료되었습니다. 코드: ${event.code}, 이유: ${event.reason}`);
                document.getElementById('connect-btn').disabled = false;
                document.getElementById('disconnect-btn').disabled = true;
            };
            
            this.websocket.onerror = (error) => {
                console.error('웹소켓 에러:', error);
                updateStatus('연결 오류', 'error');
                addMessage('시스템', '웹소켓 연결 중 오류가 발생했습니다', error);
            };
            
        } catch (error) {
            console.error('연결 실패:', error);
            updateStatus(`연결 실패: ${error.message}`, 'error');
            addMessage('시스템', `연결 실패: ${error.message}`, error);
            document.getElementById('connect-btn').disabled = false;
        }
    }
    
    // 연결 요청 전송
    sendConnectionRequest() {
        const connectMessage = {
            ver: "3",
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
        addMessage('시스템', '연결 요청을 전송했습니다', connectMessage);
    }
    
    // 메시지 처리
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('받은 메시지:', message);
            
            // 메시지 타입별 처리
            switch (message.cmd) {
                case 0: // PING
                    addMessage('시스템', 'PING 받음');
                    // PONG 응답
                    this.websocket.send(JSON.stringify({ ver: "3", cmd: 10000 }));
                    break;
                    
                case 101: // 연결 응답
                    if (message.retCode === 0) {
                        this.isConnected = true;
                        updateStatus('연결됨', 'connected');
                        addMessage('시스템', '채팅 채널에 성공적으로 연결되었습니다!');
                        document.getElementById('connect-btn').disabled = true;
                        document.getElementById('disconnect-btn').disabled = false;
                    } else {
                        updateStatus(`연결 실패 (코드: ${message.retCode})`, 'error');
                        addMessage('시스템', `연결 실패: ${message.retMsg || '알 수 없는 오류'}`);
                    }
                    addMessage('연결 응답', JSON.stringify(message), message);
                    break;
                    
                case 93101: // 채팅 메시지
                    if (message.bdy && message.bdy.length > 0) {
                        message.bdy.forEach(chatMsg => {
                            const profile = chatMsg.profile || {};
                            const nickname = profile.nickname || '익명';
                            const content = chatMsg.msg || '';
                            const messageTime = new Date(chatMsg.msgTime).toLocaleTimeString();
                            
                            addMessage(`${nickname} (${messageTime})`, content, chatMsg);
                        });
                    }
                    break;
                    
                default:
                    addMessage('기타 메시지', `CMD: ${message.cmd}`, message);
                    break;
            }
            
        } catch (error) {
            console.error('메시지 파싱 오류:', error);
            addMessage('오류', `메시지 파싱 실패: ${data}`, error);
        }
    }
    
    // 연결 해제
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this.isConnected = false;
        updateStatus('연결 해제됨', 'disconnected');
        addMessage('시스템', '연결을 해제했습니다');
        document.getElementById('connect-btn').disabled = false;
        document.getElementById('disconnect-btn').disabled = true;
    }
}

// 전역 변수
const chatTest = new ChzzkChatTest();

// UI 함수들
function connectToChzzk() {
    const channelId = document.getElementById('channel-id').value.trim();
    const customChatChannelId = document.getElementById('chat-channel-id').value.trim() || null;
    
    if (!channelId) {
        alert('채널 ID를 입력해주세요');
        return;
    }
    
    document.getElementById('connect-btn').disabled = true;
    chatTest.connect(channelId, customChatChannelId);
}

function disconnectFromChzzk() {
    chatTest.disconnect();
}

function updateStatus(message, className = '') {
    const statusElement = document.getElementById('status');
    statusElement.innerHTML = `<strong>상태:</strong> ${message}`;
    statusElement.className = `status ${className}`;
}

function addMessage(sender, content, rawData = null) {
    const container = document.getElementById('messages-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const now = new Date().toLocaleTimeString();
    let html = `
        <div><strong>${sender}:</strong> ${content}</div>
        <div class="message-time">${now}</div>
    `;
    
    if (rawData) {
        html += `<div class="message-raw">${JSON.stringify(rawData, null, 2)}</div>`;
    }
    
    messageDiv.innerHTML = html;
    container.appendChild(messageDiv);
    
    // 스크롤을 아래로
    container.scrollTop = container.scrollHeight;
}

function clearMessages() {
    const container = document.getElementById('messages-container');
    container.innerHTML = '<div class="message"><div><strong>시스템:</strong> 메시지를 모두 지웠습니다.</div><div class="message-time">' + new Date().toLocaleTimeString() + '</div></div>';
} 