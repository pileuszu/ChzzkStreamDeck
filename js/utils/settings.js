// 설정 관리자
export class SettingsManager {
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
        document.getElementById('chat-url').value = `http://localhost:${this.settings.chat.port}/chat`;
    }
    
    // 모달에서 설정 로드
    loadModalSettings(moduleName) {
        const settings = this.settings[moduleName];
        
        if (moduleName === 'spotify') {
            document.getElementById('spotify-port-input').value = settings.port;
            document.getElementById('spotify-client-id').value = settings.clientId;
            document.getElementById('spotify-client-secret').value = settings.clientSecret;
            
            const themeRadio = document.querySelector(`input[name="spotify-theme"][value="${settings.theme}"]`);
            if (themeRadio) themeRadio.checked = true;
            
        } else if (moduleName === 'chat') {
            document.getElementById('chat-port-input').value = settings.port;
            document.getElementById('chat-channel-id').value = settings.channelId;
            document.getElementById('chat-platform').value = settings.platform;
            document.getElementById('chat-max-messages').value = settings.maxMessages;
            document.getElementById('chat-alignment').value = settings.alignment;
            document.getElementById('chat-fade-time').value = settings.fadeTime;
            
            const themeRadio = document.querySelector(`input[name="chat-theme"][value="${settings.theme}"]`);
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
        }
        
        this.updateUI();
    }
} 