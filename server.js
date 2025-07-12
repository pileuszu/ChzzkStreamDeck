/**
 * ChzzkStreamDeck OBS 위젯 서버
 * 
 * @description 채팅 및 Spotify 위젯을 위한 백엔드 서버
 * @author ChzzkStreamDeck
 * @version 2.0.0
 */

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const cors = require('cors');

class ChzzkStreamDeckServer {
    constructor() {
        this.app = express();
        this.port = 7112;
        
        // 프로세스 관리
        this.processes = {
            spotify: null,
            chat: null
        };
        
        // 상태 관리
        this.status = {
            spotify: { active: false, port: 8001, pid: null },
            chat: { active: false, port: 8002, pid: null }
        };
        
        // 채팅 메시지 저장소
        this.chatMessages = [];
        this.maxMessages = 50;
        
        // SSE 연결 관리
        this.sseConnections = new Set();
        
        // Spotify 토큰 관리
        this.spotifyTokens = {
            accessToken: null,
            refreshToken: null,
            expiryTime: null,
            clientId: null,
            clientSecret: null
        };
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupProcessHandlers();
    }

    /**
     * 미들웨어 설정
     */
    setupMiddleware() {
        this.app.use(cors());
        this.app.use(express.json());
        this.app.use(express.static('.'));
    }

    /**
     * 라우트 설정
     */
    setupRoutes() {
        // 홈 페이지
        this.app.get('/', (req, res) => {
            res.sendFile(path.join(__dirname, 'index.html'));
        });



        // 채팅 오버레이 페이지
        this.app.get('/chat-overlay.html', (req, res) => {
            res.sendFile(path.join(__dirname, 'src/chat-overlay.html'));
        });

        // 스포티파이 위젯 페이지
        this.app.get('/spotify-widget.html', (req, res) => {
            res.sendFile(path.join(__dirname, 'src/spotify-widget.html'));
        });



        // SSE 스트림 엔드포인트
        this.app.get('/api/chat/stream', (req, res) => this.handleChatStream(req, res));
        
        // 채팅 메시지 조회
        this.app.get('/api/chat/messages', (req, res) => this.getChatMessages(req, res));
        
        // 채팅 모듈 제어
        this.app.post('/api/chat/:action', (req, res) => this.handleChatAction(req, res));
        
        // Spotify 토큰 관리 (더 구체적인 라우트를 먼저 설정)
        this.app.get('/api/spotify/token', (req, res) => this.getSpotifyToken(req, res));
        this.app.post('/api/spotify/token', (req, res) => this.saveSpotifyToken(req, res));
        this.app.delete('/api/spotify/token', (req, res) => this.clearSpotifyToken(req, res));
        this.app.post('/api/spotify/refresh', (req, res) => this.refreshSpotifyToken(req, res));
        
        // Spotify API 프록시
        this.app.get('/api/spotify/current-track', (req, res) => this.getCurrentTrack(req, res));
        this.app.post('/api/spotify/next', (req, res) => this.nextTrack(req, res));
        this.app.post('/api/spotify/previous', (req, res) => this.previousTrack(req, res));
        this.app.post('/api/spotify/play', (req, res) => this.playPause(req, res));
        
        // Spotify 모듈 제어 (일반적인 패턴을 마지막에 설정)
        this.app.post('/api/spotify/:action', (req, res) => this.handleSpotifyAction(req, res));
        
        // Spotify 인증 콜백
        this.app.get('/spotify/callback', (req, res) => this.handleSpotifyCallback(req, res));
        
        // 상태 조회
        this.app.get('/api/status', (req, res) => this.getStatus(req, res));
    }

    /**
     * 채팅 스트림 처리 (SSE)
     */
    handleChatStream(req, res) {
        // SSE 헤더 설정
        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        });
        
        // 연결 추가
        this.sseConnections.add(res);
        
        // 기존 메시지 전송 (최근 10개)
        const recentMessages = this.chatMessages.slice(-10);
        recentMessages.forEach(message => {
            this.sendSSEMessage(res, message);
        });
        
        // 연결 종료 시 정리
        req.on('close', () => {
            this.sseConnections.delete(res);
        });
        
        req.on('aborted', () => {
            this.sseConnections.delete(res);
        });
    }

    /**
     * 채팅 메시지 조회
     */
    getChatMessages(req, res) {
        const limit = parseInt(req.query.limit) || 20;
        const messages = this.chatMessages.slice(-limit);
        
        res.json({ 
            success: true, 
            messages,
            total: this.chatMessages.length
        });
    }

    /**
     * 채팅 액션 처리
     */
    async handleChatAction(req, res) {
        const action = req.params.action;
        const { channelId } = req.body;
        
        try {
            if (action === 'start') {
                await this.startChatModule(channelId);
                res.json({ 
                    success: true, 
                    message: '채팅 모듈이 시작되었습니다.',
                    pid: this.processes.chat?.pid
                });
                
            } else if (action === 'stop') {
                this.stopChatModule();
                res.json({ 
                    success: true, 
                    message: '채팅 모듈이 중지되었습니다.' 
                });
                
            } else {
                res.json({ 
                    success: false, 
                    error: '지원하지 않는 액션입니다.' 
                });
            }
            
        } catch (error) {
            console.error('💥 채팅 액션 오류:', error);
            res.json({ 
                success: false, 
                error: error.message 
            });
        }
    }

    /**
     * 채팅 모듈 시작
     */
    async startChatModule(channelId) {
        if (this.processes.chat) {
            throw new Error('채팅 모듈이 이미 실행 중입니다.');
        }
        
        if (!channelId) {
            throw new Error('채널 ID가 필요합니다.');
        }
        
        console.log(`🚀 채팅 모듈 시작 - 채널: ${channelId.substring(0, 8)}...`);
        
        // 채팅 클라이언트 실행
        const chatProcess = spawn('node', ['src/chat-client.js', channelId], {
            stdio: ['pipe', 'pipe', 'pipe'],
            cwd: process.cwd()
        });
        
        this.processes.chat = chatProcess;
        this.status.chat.active = true;
        this.status.chat.pid = chatProcess.pid;
        
        // 프로세스 출력 처리
        chatProcess.stdout.on('data', (data) => {
            const output = data.toString().trim();
            
            // 채팅 메시지 파싱 및 브로드캐스트
            this.parseChatMessage(output);
        });
        
        chatProcess.stderr.on('data', (data) => {
            console.error(`❌ 채팅 오류: ${data.toString().trim()}`);
        });
        
        chatProcess.on('close', (code) => {
            if (code !== 0) {
                console.log(`⚠️ 채팅 모듈 종료 - 코드: ${code}`);
            }
            this.processes.chat = null;
            this.status.chat.active = false;
            this.status.chat.pid = null;
        });
        
        // 프로세스 시작 확인
        await this.sleep(2000);
        
        if (!this.processes.chat || this.processes.chat.killed) {
            throw new Error('채팅 모듈 시작에 실패했습니다.');
        }
    }

    /**
     * 채팅 모듈 중지
     */
    stopChatModule() {
        if (!this.processes.chat) {
            throw new Error('실행 중인 채팅 모듈이 없습니다.');
        }
        
        console.log('🛑 채팅 모듈 중지');
        
        this.processes.chat.kill('SIGTERM');
        this.processes.chat = null;
        this.status.chat.active = false;
        this.status.chat.pid = null;
    }

    /**
     * 채팅 메시지 파싱
     */
    parseChatMessage(output) {
        try {
            // JSON 형태의 메시지 (이모티콘 포함) 확인
            if (output.startsWith('CHAT_JSON:')) {
                const jsonData = output.substring(10); // 'CHAT_JSON:' 제거
                const chatData = JSON.parse(jsonData);
                
                const message = {
                    id: Date.now() + Math.random(),
                    timestamp: new Date().toISOString(),
                    username: chatData.username,
                    message: chatData.message,
                    extras: chatData.extras,
                    type: 'chat'
                };
                
                // 메시지 저장
                this.addChatMessage(message);
                
                // SSE로 실시간 전송
                this.broadcastMessage(message);
                return;
            }
            
            // 기존 형태: [닉네임]: 메시지 내용
            const chatMatch = output.match(/\[([^\]]+)\]: (.+)/);
            
            if (chatMatch) {
                const message = {
                    id: Date.now() + Math.random(),
                    timestamp: new Date().toISOString(),
                    username: chatMatch[1],
                    message: chatMatch[2],
                    type: 'chat'
                };
                
                // 메시지 저장
                this.addChatMessage(message);
                
                // SSE로 실시간 전송
                this.broadcastMessage(message);
            }
        } catch (error) {
            console.error('💥 채팅 메시지 파싱 오류:', error);
        }
    }

    /**
     * 채팅 메시지 추가
     */
    addChatMessage(message) {
        this.chatMessages.push(message);
        
        // 최대 메시지 수 유지
        if (this.chatMessages.length > this.maxMessages) {
            this.chatMessages.shift();
        }
    }

    /**
     * 모든 SSE 연결에 메시지 브로드캐스트
     */
    broadcastMessage(message) {
        const data = JSON.stringify(message);
        
        this.sseConnections.forEach(connection => {
            this.sendSSEMessage(connection, message);
        });
    }

    /**
     * SSE 메시지 전송
     */
    sendSSEMessage(connection, message) {
        try {
            const data = JSON.stringify(message);
            connection.write(`data: ${data}\n\n`);
        } catch (error) {
            console.error('💥 SSE 전송 오류:', error);
            this.sseConnections.delete(connection);
        }
    }

    /**
     * Spotify 액션 처리
     */
    handleSpotifyAction(req, res) {
        const action = req.params.action;
        
        if (action === 'start') {
            res.json({ 
                success: false, 
                error: 'Spotify 모듈은 아직 구현되지 않았습니다.' 
            });
        } else if (action === 'stop') {
            res.json({ 
                success: true, 
                message: 'Spotify 모듈이 중지되었습니다.' 
            });
        } else {
            res.json({ 
                success: false, 
                error: '지원하지 않는 액션입니다.' 
            });
        }
    }

    /**
     * Spotify 인증 콜백 처리
     */
    handleSpotifyCallback(req, res) {
        const { code, state, error, error_description } = req.query;
        
        console.log('🔐 Spotify 콜백 수신:', { 
            hasCode: !!code,
            state: state,
            error: error,
            error_description: error_description
        });
        
        // 에러가 있는 경우
        if (error) {
            console.error('❌ Spotify 인증 오류:', error, error_description);
            
            res.send(`
                <html>
                    <head>
                        <title>Spotify 인증 실패</title>
                        <style>
                            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                            .error { color: #e74c3c; }
                            .code { background: #f8f9fa; padding: 10px; border-radius: 5px; display: inline-block; }
                        </style>
                    </head>
                    <body>
                        <h1 class="error">🚫 인증 실패</h1>
                        <p><strong>오류:</strong> ${error}</p>
                        ${error_description ? `<p><strong>설명:</strong> ${error_description}</p>` : ''}
                        <p>이 창을 닫고 다시 시도해주세요.</p>
                        <script>
                            // 오류를 부모 창으로 전달
                            if (window.opener) {
                                window.opener.postMessage({
                                    type: 'spotify_auth',
                                    error: '${error}',
                                    error_description: '${error_description || ''}'
                                }, '*');
                            }
                            setTimeout(() => window.close(), 3000);
                        </script>
                    </body>
                </html>
            `);
            return;
        }
        
        // 코드나 state가 없는 경우
        if (!code) {
            console.error('❌ 인증 코드가 없습니다.');
            
            res.send(`
                <html>
                    <head>
                        <title>Spotify 인증 실패</title>
                        <style>
                            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                            .error { color: #e74c3c; }
                        </style>
                    </head>
                    <body>
                        <h1 class="error">🚫 인증 실패</h1>
                        <p>인증 코드를 받지 못했습니다.</p>
                        <p>이 창을 닫고 다시 시도해주세요.</p>
                        <script>
                            if (window.opener) {
                                window.opener.postMessage({
                                    type: 'spotify_auth',
                                    error: 'no_code',
                                    error_description: '인증 코드를 받지 못했습니다.'
                                }, '*');
                            }
                            setTimeout(() => window.close(), 3000);
                        </script>
                    </body>
                </html>
            `);
            return;
        }
        
        // state 검증 (spotify_auth로 시작하는지 확인)
        if (!state || !state.startsWith('spotify_auth')) {
            console.error('❌ 잘못된 state 값:', state);
            
            res.send(`
                <html>
                    <head>
                        <title>Spotify 인증 실패</title>
                        <style>
                            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                            .error { color: #e74c3c; }
                        </style>
                    </head>
                    <body>
                        <h1 class="error">🚫 인증 실패</h1>
                        <p>잘못된 인증 요청입니다. (State 불일치)</p>
                        <p>이 창을 닫고 다시 시도해주세요.</p>
                        <script>
                            if (window.opener) {
                                window.opener.postMessage({
                                    type: 'spotify_auth',
                                    error: 'invalid_state',
                                    error_description: '잘못된 인증 요청입니다.'
                                }, '*');
                            }
                            setTimeout(() => window.close(), 3000);
                        </script>
                    </body>
                </html>
            `);
            return;
        }
        
        // 성공적으로 인증 코드 수신
        console.log('✅ Spotify 인증 코드 수신 성공');
        
        res.send(`
            <html>
                <head>
                    <title>Spotify 인증 성공</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .success { color: #27ae60; }
                        .loading { color: #3498db; }
                        .spinner { 
                            border: 4px solid #f3f3f3;
                            border-top: 4px solid #3498db;
                            border-radius: 50%;
                            width: 40px;
                            height: 40px;
                            animation: spin 1s linear infinite;
                            margin: 20px auto;
                        }
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                    </style>
                </head>
                <body>
                    <h1 class="success">🎉 인증 성공!</h1>
                    <div class="spinner"></div>
                    <p class="loading">토큰을 교환하는 중입니다...</p>
                    <p>잠시만 기다려주세요.</p>
                    <script>
                        console.log('🔐 인증 성공 - 코드를 부모 창으로 전달');
                        
                        // 인증 코드를 부모 창으로 전달
                        if (window.opener && !window.opener.closed) {
                            window.opener.postMessage({
                                type: 'spotify_auth',
                                code: '${code}',
                                state: '${state}'
                            }, '*');
                            
                            // 메시지 전송 후 잠시 후 창 닫기
                            setTimeout(() => {
                                window.close();
                            }, 2000);
                        } else {
                            console.error('❌ 부모 창을 찾을 수 없습니다.');
                            document.body.innerHTML = '<h1>오류</h1><p>부모 창을 찾을 수 없습니다. 수동으로 창을 닫아주세요.</p>';
                        }
                    </script>
                </body>
            </html>
        `);
    }

    /**
     * Spotify 토큰 조회
     */
    getSpotifyToken(req, res) {
        const hasToken = !!this.spotifyTokens.accessToken;
        const isExpired = this.spotifyTokens.expiryTime ? Date.now() > this.spotifyTokens.expiryTime : true;
        
        res.json({
            success: true,
            hasToken: hasToken,
            isExpired: isExpired,
            expiryTime: this.spotifyTokens.expiryTime,
            token: hasToken && !isExpired ? this.spotifyTokens.accessToken : null
        });
    }

    /**
     * Spotify 토큰 저장
     */
    saveSpotifyToken(req, res) {
        const { accessToken, refreshToken, expiryTime, clientId, clientSecret } = req.body;
        
        console.log('💾 Spotify 토큰 서버에 저장');
        
        this.spotifyTokens.accessToken = accessToken;
        this.spotifyTokens.refreshToken = refreshToken;
        this.spotifyTokens.expiryTime = expiryTime;
        
        if (clientId) this.spotifyTokens.clientId = clientId;
        if (clientSecret) this.spotifyTokens.clientSecret = clientSecret;
        
        res.json({
            success: true,
            message: '토큰이 저장되었습니다.'
        });
    }

    /**
     * Spotify 토큰 삭제
     */
    clearSpotifyToken(req, res) {
        console.log('🗑️ Spotify 토큰 서버에서 삭제');
        
        this.spotifyTokens.accessToken = null;
        this.spotifyTokens.refreshToken = null;
        this.spotifyTokens.expiryTime = null;
        
        res.json({
            success: true,
            message: '토큰이 삭제되었습니다.'
        });
    }

    /**
     * Spotify 토큰 갱신
     */
    async refreshSpotifyToken(req, res) {
        if (!this.spotifyTokens.refreshToken || !this.spotifyTokens.clientId || !this.spotifyTokens.clientSecret) {
            return res.json({
                success: false,
                error: '토큰 갱신에 필요한 정보가 없습니다.'
            });
        }

        try {
            const response = await fetch('https://accounts.spotify.com/api/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Basic ' + Buffer.from(this.spotifyTokens.clientId + ':' + this.spotifyTokens.clientSecret).toString('base64')
                },
                body: `grant_type=refresh_token&refresh_token=${this.spotifyTokens.refreshToken}`
            });

            if (!response.ok) {
                throw new Error('토큰 갱신 실패');
            }

            const data = await response.json();
            
            this.spotifyTokens.accessToken = data.access_token;
            this.spotifyTokens.expiryTime = Date.now() + (data.expires_in * 1000);
            
            if (data.refresh_token) {
                this.spotifyTokens.refreshToken = data.refresh_token;
            }

            console.log('✅ Spotify 토큰 갱신 완료');

            res.json({
                success: true,
                accessToken: this.spotifyTokens.accessToken,
                expiryTime: this.spotifyTokens.expiryTime
            });

        } catch (error) {
            console.error('❌ 토큰 갱신 실패:', error);
            res.json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 현재 재생 중인 트랙 조회
     */
    async getCurrentTrack(req, res) {
        if (!this.spotifyTokens.accessToken) {
            return res.json({
                success: false,
                error: '인증 토큰이 없습니다.'
            });
        }

        // 토큰 만료 확인 및 갱신
        if (this.spotifyTokens.expiryTime && Date.now() > this.spotifyTokens.expiryTime) {
            console.log('🔄 토큰 만료됨, 자동 갱신 시도');
            try {
                await this.refreshSpotifyTokenInternal();
            } catch (error) {
                return res.json({
                    success: false,
                    error: '토큰 갱신 실패'
                });
            }
        }

        try {
            const response = await fetch('https://api.spotify.com/v1/me/player/currently-playing', {
                headers: {
                    'Authorization': 'Bearer ' + this.spotifyTokens.accessToken
                }
            });

            if (response.status === 204) {
                return res.json({
                    success: true,
                    isPlaying: false,
                    track: null
                });
            }

            if (!response.ok) {
                throw new Error('Spotify API 오류');
            }

            const data = await response.json();

            res.json({
                success: true,
                isPlaying: data.is_playing,
                track: data.item ? {
                    name: data.item.name,
                    artist: data.item.artists[0].name,
                    album: data.item.album.name,
                    duration: data.item.duration_ms,
                    progress: data.progress_ms,
                    image: data.item.album.images[0]?.url
                } : null
            });

        } catch (error) {
            console.error('❌ 현재 트랙 조회 실패:', error);
            res.json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 다음 트랙 재생
     */
    async nextTrack(req, res) {
        if (!this.spotifyTokens.accessToken) {
            return res.json({
                success: false,
                error: '인증 토큰이 없습니다.'
            });
        }

        try {
            const response = await fetch('https://api.spotify.com/v1/me/player/next', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + this.spotifyTokens.accessToken
                }
            });

            if (response.status === 204) {
                res.json({
                    success: true,
                    message: '다음 트랙으로 이동했습니다.'
                });
            } else {
                throw new Error('Spotify API 오류');
            }

        } catch (error) {
            console.error('❌ 다음 트랙 재생 실패:', error);
            res.json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 이전 트랙 재생
     */
    async previousTrack(req, res) {
        if (!this.spotifyTokens.accessToken) {
            return res.json({
                success: false,
                error: '인증 토큰이 없습니다.'
            });
        }

        try {
            const response = await fetch('https://api.spotify.com/v1/me/player/previous', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + this.spotifyTokens.accessToken
                }
            });

            if (response.status === 204) {
                res.json({
                    success: true,
                    message: '이전 트랙으로 이동했습니다.'
                });
            } else {
                throw new Error('Spotify API 오류');
            }

        } catch (error) {
            console.error('❌ 이전 트랙 재생 실패:', error);
            res.json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 재생/일시정지 토글
     */
    async playPause(req, res) {
        if (!this.spotifyTokens.accessToken) {
            return res.json({
                success: false,
                error: '인증 토큰이 없습니다.'
            });
        }

        try {
            // 현재 재생 상태 확인
            const statusResponse = await fetch('https://api.spotify.com/v1/me/player/currently-playing', {
                headers: {
                    'Authorization': 'Bearer ' + this.spotifyTokens.accessToken
                }
            });

            let isPlaying = false;
            if (statusResponse.status === 200) {
                const statusData = await statusResponse.json();
                isPlaying = statusData.is_playing;
            }

            // 재생/일시정지 토글
            const action = isPlaying ? 'pause' : 'play';
            const response = await fetch(`https://api.spotify.com/v1/me/player/${action}`, {
                method: 'PUT',
                headers: {
                    'Authorization': 'Bearer ' + this.spotifyTokens.accessToken
                }
            });

            if (response.status === 204) {
                res.json({
                    success: true,
                    message: isPlaying ? '재생이 일시정지되었습니다.' : '재생이 시작되었습니다.',
                    isPlaying: !isPlaying
                });
            } else {
                throw new Error('Spotify API 오류');
            }

        } catch (error) {
            console.error('❌ 재생/일시정지 토글 실패:', error);
            res.json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 내부 토큰 갱신 (await 가능)
     */
    async refreshSpotifyTokenInternal() {
        const response = await fetch('https://accounts.spotify.com/api/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + Buffer.from(this.spotifyTokens.clientId + ':' + this.spotifyTokens.clientSecret).toString('base64')
            },
            body: `grant_type=refresh_token&refresh_token=${this.spotifyTokens.refreshToken}`
        });

        if (!response.ok) {
            throw new Error('토큰 갱신 실패');
        }

        const data = await response.json();
        
        this.spotifyTokens.accessToken = data.access_token;
        this.spotifyTokens.expiryTime = Date.now() + (data.expires_in * 1000);
        
        if (data.refresh_token) {
            this.spotifyTokens.refreshToken = data.refresh_token;
        }
    }

    /**
     * 상태 조회
     */
    getStatus(req, res) {
        res.json({ 
            success: true, 
            status: {
                chat: {
                    active: this.status.chat.active,
                    pid: this.status.chat.pid,
                    port: this.status.chat.port,
                    messageCount: this.chatMessages.length
                },
                spotify: {
                    active: this.status.spotify.active,
                    pid: this.status.spotify.pid,
                    port: this.status.spotify.port,
                    hasToken: !!this.spotifyTokens.accessToken,
                    tokenExpired: this.spotifyTokens.expiryTime ? Date.now() > this.spotifyTokens.expiryTime : true
                },
                server: {
                    port: this.port,
                    sseConnections: this.sseConnections.size
                }
            }
        });
    }

    /**
     * 프로세스 핸들러 설정
     */
    setupProcessHandlers() {
        // 서버 종료 시 정리
        process.on('SIGINT', () => {
            this.shutdown();
        });

        process.on('SIGTERM', () => {
            this.shutdown();
        });
    }

    /**
     * 서버 시작
     */
    start() {
        this.app.listen(this.port, () => {
            this.printStartupInfo();
        });
    }

    /**
     * 시작 정보 출력
     */
    printStartupInfo() {
        console.log('🎮 ChzzkStreamDeck 서버 시작 (포트: 7112)');
        console.log(`📊 대시보드: http://localhost:7112`);
        console.log(`💬 채팅 오버레이: http://localhost:7112/chat-overlay.html`);
        console.log(`🎵 스포티파이 위젯: http://localhost:7112/spotify-widget.html`);
    }

    /**
     * 서버 종료
     */
    shutdown() {
        console.log('🛑 서버 종료');
        
        // 모든 프로세스 정리
        if (this.processes.chat) {
            this.processes.chat.kill('SIGTERM');
        }
        
        if (this.processes.spotify) {
            this.processes.spotify.kill('SIGTERM');
        }
        
        // SSE 연결 정리
        this.sseConnections.forEach(connection => {
            try {
                connection.end();
            } catch (error) {
                // 무시
            }
        });
        
        process.exit(0);
    }

    // 유틸리티 메서드
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 서버 인스턴스 생성 및 시작
const server = new ChzzkStreamDeckServer();
server.start(); 