// 설정 관리자
class SettingsManager {
    constructor() {
        this.settings = {
            spotify: {
                port: 8001,
                theme: 'simple-purple',
                clientId: '',
                clientSecret: ''
            },
            chat: {
                port: 8002,
                theme: 'simple-purple',
                channelId: '',
                platform: 'chzzk',
                maxMessages: 10,
                alignment: 'default',
                fadeTime: 0
            }
        };
    }
    
    // 설정 로드
    loadSettings() {
        const saved = localStorage.getItem('moduleSettings');
        if (saved) {
            try {
                const savedSettings = JSON.parse(saved);
                this.settings = { ...this.settings, ...savedSettings };
                this.updateUI();
                console.log('설정이 로드되었습니다:', this.settings);
            } catch (error) {
                console.error('설정 로드 실패:', error);
            }
        }
    }
    
    // 설정 저장
    saveSettings() {
        try {
            localStorage.setItem('moduleSettings', JSON.stringify(this.settings));
            console.log('설정이 저장되었습니다:', this.settings);
        } catch (error) {
            console.error('설정 저장 실패:', error);
        }
    }
    
    // 특정 모듈 설정 가져오기
    getModuleSettings(moduleName) {
        return this.settings[moduleName] || {};
    }
    
    // 특정 모듈 설정 업데이트
    updateModuleSettings(moduleName, newSettings) {
        this.settings[moduleName] = { ...this.settings[moduleName], ...newSettings };
        this.saveSettings();
    }
    
    // UI 업데이트
    updateUI() {
        // 포트 정보 업데이트
        document.getElementById('spotify-port').textContent = this.settings.spotify.port;
        document.getElementById('chat-port').textContent = this.settings.chat.port;
        
        // 브라우저 소스 URL 업데이트
        document.getElementById('spotify-url').value = `http://localhost:${this.settings.spotify.port}/spotify`;
        document.getElementById('chat-url').value = `http://localhost:3000/chat-overlay.html`;
    }
    
    // 모달에서 설정 로드
    loadModalSettings(moduleName) {
        const settings = this.settings[moduleName];
        
        if (moduleName === 'spotify') {
            // 개별 localStorage 값들 우선 확인
            const theme = localStorage.getItem('spotify-theme') || settings.theme;
            const port = localStorage.getItem('spotify-port') || settings.port;
            const clientId = localStorage.getItem('spotify-client-id') || settings.clientId;
            const clientSecret = localStorage.getItem('spotify-client-secret') || settings.clientSecret;
            
            document.getElementById('spotify-port-input').value = port;
            document.getElementById('spotify-client-id').value = clientId;
            document.getElementById('spotify-client-secret').value = clientSecret;
            
            const themeRadio = document.querySelector(`input[name="spotify-theme"][value="${theme}"]`);
            if (themeRadio) themeRadio.checked = true;
            
        } else if (moduleName === 'chat') {
            // 개별 localStorage 값들 우선 확인 (chat-overlay.html 호환)
            const theme = localStorage.getItem('chat-theme') || settings.theme;
            const port = localStorage.getItem('chat-port') || settings.port;
            const channelId = localStorage.getItem('chat-channel-id') || settings.channelId;
            const platform = localStorage.getItem('chat-platform') || settings.platform;
            const maxMessages = localStorage.getItem('chat-max-messages') || settings.maxMessages;
            const alignment = localStorage.getItem('chat-alignment') || settings.alignment;
            const fadeTime = localStorage.getItem('chat-fade-time') || settings.fadeTime;
            
            document.getElementById('chat-port-input').value = port;
            document.getElementById('chat-channel-id').value = channelId;
            document.getElementById('chat-platform').value = platform;
            document.getElementById('chat-max-messages').value = maxMessages;
            document.getElementById('chat-alignment').value = alignment;
            document.getElementById('chat-fade-time').value = fadeTime;
            
            const themeRadio = document.querySelector(`input[name="chat-theme"][value="${theme}"]`);
            if (themeRadio) themeRadio.checked = true;
        }
    }
    
    // 모달에서 설정 저장
    saveModalSettings(moduleName) {
        if (moduleName === 'spotify') {
            const newSettings = {
                port: parseInt(document.getElementById('spotify-port-input').value),
                theme: document.querySelector('input[name="spotify-theme"]:checked').value,
                clientId: document.getElementById('spotify-client-id').value,
                clientSecret: document.getElementById('spotify-client-secret').value
            };
            
            this.updateModuleSettings('spotify', newSettings);
            
            // Spotify 개별 설정 저장
            localStorage.setItem('spotify-theme', newSettings.theme);
            localStorage.setItem('spotify-port', newSettings.port.toString());
            localStorage.setItem('spotify-client-id', newSettings.clientId);
            localStorage.setItem('spotify-client-secret', newSettings.clientSecret);
            
        } else if (moduleName === 'chat') {
            const newSettings = {
                port: parseInt(document.getElementById('chat-port-input').value),
                theme: document.querySelector('input[name="chat-theme"]:checked').value,
                channelId: document.getElementById('chat-channel-id').value,
                platform: document.getElementById('chat-platform').value,
                maxMessages: parseInt(document.getElementById('chat-max-messages').value),
                alignment: document.getElementById('chat-alignment').value,
                fadeTime: parseInt(document.getElementById('chat-fade-time').value)
            };
            
            this.updateModuleSettings('chat', newSettings);
            
            // 채팅 개별 설정 저장 (chat-overlay.html 호환)
            localStorage.setItem('chat-theme', newSettings.theme);
            localStorage.setItem('chat-max-messages', newSettings.maxMessages.toString());
            localStorage.setItem('chat-fade-time', newSettings.fadeTime.toString());
            localStorage.setItem('chat-alignment', newSettings.alignment);
            localStorage.setItem('chat-platform', newSettings.platform);
            localStorage.setItem('chat-channel-id', newSettings.channelId);
            
            // 채팅 설정 변경 이벤트 발생
            window.dispatchEvent(new CustomEvent('chatSettingsChanged', {
                detail: newSettings
            }));
            
            console.log('🎨 채팅 설정 저장 및 이벤트 발생:', newSettings);
        }
        
        this.updateUI();
    }
} 