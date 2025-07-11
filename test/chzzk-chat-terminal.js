#!/usr/bin/env node

/**
 * 치지직 채팅 웹소켓 터미널 테스트
 * 
 * 사용법:
 * node chzzk-chat-terminal.js [채널ID]
 * 
 * 예시:
 * node chzzk-chat-terminal.js abc123def456
 */

const WebSocket = require('ws');
const https = require('https');
const readline = require('readline');
const { URL } = require('url');

class ChzzkChatTerminal {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.channelId = null;
        this.chatChannelId = null;
        this.accessToken = null;
        this.messageCount = 0;
        this.pingInterval = null;
        this.lastMessageTime = Date.now();
        this.wsServers = [
            'wss://kr-ss1.chat.naver.com/chat',
            'wss://kr-ss2.chat.naver.com/chat',
            'wss://kr-ss3.chat.naver.com/chat'
        ];
        this.currentServerIndex = 0;
        this.maxRetries = 3;
    }

    // HTTP 요청 유틸리티
    makeRequest(url) {
        return new Promise((resolve, reject) => {
            const parsedUrl = new URL(url);
            
            const options = {
                hostname: parsedUrl.hostname,
                port: parsedUrl.port || 443,
                path: parsedUrl.pathname + parsedUrl.search,
                method: 'GET',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': 'https://chzzk.naver.com/',
                    'Origin': 'https://chzzk.naver.com',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"'
                }
            };
            
            const req = https.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    if (res.statusCode !== 200) {
                        reject(new Error(`HTTP ${res.statusCode}: ${data}`));
                        return;
                    }
                    try {
                        const jsonData = JSON.parse(data);
                        resolve(jsonData);
                    } catch (error) {
                        reject(new Error(`JSON 파싱 오류: ${error.message}. 응답 데이터: ${data}`));
                    }
                });
            });
            
            req.on('error', (error) => {
                reject(error);
            });
            
            req.setTimeout(10000, () => {
                req.destroy();
                reject(new Error('요청 타임아웃'));
            });
            
            req.end();
        });
    }

    // 치지직 채널 정보 가져오기
    async getChannelInfo(channelId) {
        try {
            console.log(`📡 채널 정보 가져오는 중: ${channelId}`);
            const url = `https://api.chzzk.naver.com/polling/v1/channels/${channelId}/live-status`;
            const data = await this.makeRequest(url);
            console.log(`✅ 채널 정보 수신 완료`);
            console.log(`🔍 채널 상태:`, data.content?.status || 'Unknown');
            return data;
        } catch (error) {
            console.error('❌ 채널 정보 가져오기 실패:', error.message);
            
            // 대안 시도: 서비스 API 사용
            try {
                console.log('🔄 대안 API 시도 중...');
                const alternativeUrl = `https://api.chzzk.naver.com/service/v1/channels/${channelId}`;
                const alternativeData = await this.makeRequest(alternativeUrl);
                console.log('✅ 대안 API 성공');
                return alternativeData;
            } catch (alternativeError) {
                console.error('❌ 대안 API도 실패:', alternativeError.message);
                throw error;
            }
        }
    }

    // 채팅 채널 ID 가져오기
    async getChatChannelId(channelId) {
        try {
            console.log(`💬 채팅 채널 ID 가져오는 중...`);
            const url = `https://api.chzzk.naver.com/service/v1/channels/${channelId}/live-detail`;
            const data = await this.makeRequest(url);
            const chatChannelId = data.content?.chatChannelId;
            
            if (chatChannelId) {
                console.log(`✅ 채팅 채널 ID: ${chatChannelId}`);
                return chatChannelId;
            } else {
                throw new Error('채팅 채널 ID를 찾을 수 없습니다');
            }
        } catch (error) {
            console.error('❌ 채팅 채널 ID 가져오기 실패:', error.message);
            throw error;
        }
    }

    // 액세스 토큰 가져오기
    async getAccessToken(chatChannelId) {
        try {
            console.log(`🔑 액세스 토큰 가져오는 중...`);
            const url = `https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId=${chatChannelId}&chatType=STREAMING`;
            const data = await this.makeRequest(url);
            const accessToken = data.content?.accessToken;
            
            if (accessToken) {
                console.log(`✅ 액세스 토큰 획득 완료`);
                return accessToken;
            } else {
                throw new Error('액세스 토큰을 받을 수 없습니다');
            }
        } catch (error) {
            console.error('❌ 액세스 토큰 가져오기 실패:', error.message);
            throw error;
        }
    }

    // 채널 ID 유효성 검사
    validateChannelId(channelId) {
        if (!channelId || typeof channelId !== 'string') {
            throw new Error('채널 ID가 제공되지 않았습니다.');
        }
        
        if (channelId.length !== 32) {
            throw new Error(`채널 ID는 32자리여야 합니다. 현재 길이: ${channelId.length}`);
        }
        
        if (!/^[a-zA-Z0-9]+$/.test(channelId)) {
            throw new Error('채널 ID는 영문자와 숫자만 포함해야 합니다.');
        }
        
        console.log(`✅ 채널 ID 유효성 검사 통과: ${channelId}`);
    }

    // 웹소켓 연결
    async connect(channelId) {
        try {
            // 채널 ID 유효성 검사
            this.validateChannelId(channelId);
            this.channelId = channelId;
            
            console.log(`\n🚀 치지직 채팅 연결 시작: ${channelId}`);
            console.log('='.repeat(50));
            
            // 1. 채널 정보 확인
            await this.getChannelInfo(channelId);
            
            // 2. 채팅 채널 ID 가져오기
            this.chatChannelId = await this.getChatChannelId(channelId);
            
            // 3. 액세스 토큰 가져오기
            this.accessToken = await this.getAccessToken(this.chatChannelId);
            
            // 4. 웹소켓 연결
            const connectSuccess = await this.connectWebSocket();
            if (!connectSuccess) {
                throw new Error('모든 웹소켓 서버 연결 실패');
            }
            
        } catch (error) {
            console.error(`\n❌ 연결 실패: ${error.message}`);
            
            // 문제 해결 가이드 제공
            this.printTroubleshootingGuide(error);
            
            process.exit(1);
        }
    }
    
    // 문제 해결 가이드
    printTroubleshootingGuide(error) {
        console.log('\n🔧 문제 해결 가이드:');
        console.log('='.repeat(50));
        
        if (error.message.includes('9004')) {
            console.log('❌ 치지직 API 접근 제한 오류');
            console.log('📝 해결 방법:');
            console.log('   1. 다른 채널 ID로 시도해보세요');
            console.log('   2. 라이브 방송 중인 채널을 사용하세요');
            console.log('   3. 잠시 후 다시 시도해보세요');
        } else if (error.message.includes('32자리')) {
            console.log('❌ 채널 ID 형식 오류');
            console.log('📝 올바른 채널 ID 찾기:');
            console.log('   1. 치지직 방송 페이지로 이동');
            console.log('   2. URL에서 /live/ 뒤의 32자리 복사');
            console.log('   3. 예: https://chzzk.naver.com/live/9ae7d38b629b78f48e49fb3106218ff5');
        } else if (error.message.includes('timeout') || error.message.includes('ENOTFOUND')) {
            console.log('❌ 네트워크 연결 오류');
            console.log('📝 해결 방법:');
            console.log('   1. 인터넷 연결 상태 확인');
            console.log('   2. 방화벽 설정 확인');
            console.log('   3. DNS 설정 확인');
        }
        
        console.log('\n💡 추가 도움말:');
        console.log('   - 실제 라이브 방송 중인 채널만 연결 가능');
        console.log('   - 치지직 API 상태에 따라 일시적 접근 제한 가능');
        console.log('   - 문제가 계속되면 다른 채널로 테스트 해보세요');
    }

    // 치지직 웹소켓 연결 (자동 서버 전환)
    async connectWebSocket() {
        for (let i = 0; i < this.wsServers.length; i++) {
            const serverUrl = this.wsServers[i];
            console.log(`🌐 웹소켓 서버 ${i + 1}/${this.wsServers.length} 연결 시도: ${serverUrl}`);
            
            try {
                const success = await this.tryConnectToServer(serverUrl);
                if (success) {
                    console.log(`✅ 웹소켓 서버 ${i + 1} 연결 성공!`);
                    this.currentServerIndex = i;
                    return true;
                }
            } catch (error) {
                console.log(`❌ 웹소켓 서버 ${i + 1} 연결 실패: ${error.message}`);
            }
        }
        
        console.error('❌ 모든 웹소켓 서버 연결 실패');
        return false;
    }
    
    // 특정 서버에 연결 시도
    async tryConnectToServer(serverUrl) {
        return new Promise((resolve, reject) => {
            const ws = new WebSocket(serverUrl);
            let connectionTimeout;
            
            // 연결 타임아웃 설정 (10초)
            connectionTimeout = setTimeout(() => {
                ws.close();
                reject(new Error('연결 타임아웃'));
            }, 10000);
            
            ws.on('open', () => {
                clearTimeout(connectionTimeout);
                console.log(`📡 웹소켓 연결 성공: ${serverUrl}`);
                
                // 기존 연결이 있으면 정리
                if (this.websocket) {
                    this.websocket.close();
                }
                
                this.websocket = ws;
                this.setupWebSocketHandlers();
                this.sendConnectionRequest();
                this.startPingInterval();
                
                resolve(true);
            });
            
            ws.on('error', (error) => {
                clearTimeout(connectionTimeout);
                reject(error);
            });
            
            ws.on('close', (code, reason) => {
                clearTimeout(connectionTimeout);
                if (!this.isConnected) {
                    reject(new Error(`연결 종료 (코드: ${code})`));
                }
            });
        });
    }
    
    // 웹소켓 이벤트 핸들러 설정
    setupWebSocketHandlers() {
        this.websocket.on('message', (data) => {
            this.handleMessage(data.toString());
        });
        
        this.websocket.on('close', (code, reason) => {
            this.isConnected = false;
            this.stopPingInterval();
            console.log(`\n❌ 웹소켓 연결 종료 (코드: ${code}, 이유: ${reason})`);
            
            // 연결이 끊어지면 다음 서버로 자동 재연결 시도
            if (this.currentServerIndex < this.wsServers.length - 1) {
                console.log('🔄 다음 서버로 자동 재연결 시도...');
                setTimeout(() => {
                    this.connectWebSocket();
                }, 3000);
            }
        });
        
        this.websocket.on('error', (error) => {
            console.error('❌ 웹소켓 에러:', error.message);
        });
    }

    // 연결 요청 전송
    sendConnectionRequest() {
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
        console.log(`📤 연결 요청 전송...`);
    }

    // 핑 인터벌 시작
    startPingInterval() {
        this.pingInterval = setInterval(() => {
            const now = Date.now();
            if (now - this.lastMessageTime > 20000) { // 20초 이상 메시지가 없으면
                console.log('💓 클라이언트에서 PING 전송');
                this.websocket.send(JSON.stringify({ ver: "2", cmd: 0 }));
            }
        }, 20000);
    }

    // 핑 인터벌 정지
    stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    // 메시지 처리
    handleMessage(data) {
        try {
            this.lastMessageTime = Date.now(); // 메시지 수신 시간 업데이트
            const message = JSON.parse(data);
            
            switch (message.cmd) {
                case 0: // PING
                    console.log('💓 PING 수신 - PONG 응답');
                    this.websocket.send(JSON.stringify({ ver: "2", cmd: 10000 }));
                    break;
                    
                case 101: // 연결 응답
                    if (message.retCode === 0) {
                        this.isConnected = true;
                        console.log('🎉 채팅 채널 연결 완료!');
                        console.log('\n📢 실시간 채팅 메시지:');
                        console.log('-'.repeat(50));
                    } else {
                        console.error(`❌ 연결 실패 (코드: ${message.retCode}): ${message.retMsg || '알 수 없는 오류'}`);
                    }
                    break;
                    
                case 93101: // 채팅 메시지
                    if (message.bdy && message.bdy.length > 0) {
                        message.bdy.forEach(chatMsg => {
                            this.messageCount++;
                            const profile = chatMsg.profile || {};
                            const nickname = profile.nickname || '익명';
                            const content = chatMsg.msg || '';
                            const time = new Date(chatMsg.msgTime).toLocaleTimeString('ko-KR');
                            
                            console.log(`[${this.messageCount.toString().padStart(3, '0')}] ${time} | ${nickname}: ${content}`);
                        });
                    }
                    break;
                    
                default:
                    console.log(`🔍 기타 메시지 (CMD: ${message.cmd})`);
                    break;
            }
            
        } catch (error) {
            console.error('❌ 메시지 파싱 오류:', error.message);
            console.log('원본 데이터:', data);
        }
    }

    // 연결 해제
    disconnect() {
        this.stopPingInterval();
        if (this.websocket) {
            this.websocket.close();
        }
        console.log('\n👋 연결을 종료합니다.');
    }
}

// 메인 실행
async function main() {
    console.log('🎮 치지직 채팅 웹소켓 터미널 테스터');
    console.log('=====================================\n');
    
    // 채널 ID 확인
    const channelId = process.argv[2];
    if (!channelId) {
        console.log('사용법: node chzzk-chat-terminal.js [채널ID]');
        console.log('예시: node chzzk-chat-terminal.js 9ae7d38b629b78f48e49fb3106218ff5');
        console.log('');
        console.log('💡 채널 ID 찾는 방법:');
        console.log('   1. 치지직 방송 페이지 접속');
        console.log('   2. URL에서 /live/ 뒤의 32자리 ID 복사');
        console.log('   3. 예: https://chzzk.naver.com/live/9ae7d38b629b78f48e49fb3106218ff5');
        process.exit(1);
    }
    
    const chatTest = new ChzzkChatTerminal();
    
    // 프로그램 종료 처리
    process.on('SIGINT', () => {
        chatTest.disconnect();
        process.exit(0);
    });
    
    process.on('SIGTERM', () => {
        chatTest.disconnect();
        process.exit(0);
    });
    
    // 연결 시작
    await chatTest.connect(channelId);
    
    // 사용자 입력 대기 (종료를 위해)
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    console.log('\n⌨️  종료하려면 Ctrl+C 또는 "quit"을 입력하세요.\n');
    
    rl.on('line', (input) => {
        if (input.toLowerCase().trim() === 'quit') {
            rl.close();
            chatTest.disconnect();
            process.exit(0);
        }
    });
}

// 프로그램 시작
if (require.main === module) {
    main().catch(error => {
        console.error('프로그램 실행 오류:', error.message);
        process.exit(1);
    });
} 