// 설정 관리자
class SettingsManager {
    constructor() {
        this.settings = {
            spotify: {
                theme: 'simple-purple',
                clientId: '',
                clientSecret: ''
            },
            chat: {
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

            } catch (error) {
                console.error('설정 로드 실패:', error);
            }
        }
    }
    
    // 설정 저장
    saveSettings() {
        try {
            localStorage.setItem('moduleSettings', JSON.stringify(this.settings));

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
        // 브라우저 소스 URL 업데이트
        document.getElementById('spotify-url').value = `http://localhost:7112/spotify-widget.html`;
        document.getElementById('chat-url').value = `http://localhost:7112/chat-overlay.html`;
    }
    
    // 모달에서 설정 로드
    loadModalSettings(moduleName) {
        const settings = this.settings[moduleName];
        
        if (moduleName === 'spotify') {
            document.getElementById('spotify-client-id').value = settings.clientId;
            document.getElementById('spotify-client-secret').value = settings.clientSecret;
            document.getElementById('spotify-theme-select').value = settings.theme;
            
        } else if (moduleName === 'chat') {
            document.getElementById('chat-channel-id').value = settings.channelId;
            document.getElementById('chat-platform').value = settings.platform;
            document.getElementById('chat-max-messages').value = settings.maxMessages;
            document.getElementById('chat-alignment').value = settings.alignment;
            document.getElementById('chat-fade-time').value = settings.fadeTime;
            document.getElementById('chat-theme-select').value = settings.theme;
        }
    }
    
    // 모달에서 설정 저장
    saveModalSettings(moduleName) {
        if (moduleName === 'spotify') {
            const newSettings = {
                theme: document.getElementById('spotify-theme-select').value,
                clientId: document.getElementById('spotify-client-id').value,
                clientSecret: document.getElementById('spotify-client-secret').value
            };
            
            this.updateModuleSettings('spotify', newSettings);
            
            // 스포티파이 위젯에서 사용할 수 있도록 개별 localStorage 항목으로 저장
            localStorage.setItem('spotify-client-id', newSettings.clientId);
            localStorage.setItem('spotify-client-secret', newSettings.clientSecret);
            localStorage.setItem('spotify-theme', newSettings.theme);
            
        } else if (moduleName === 'chat') {
            const newSettings = {
                theme: document.getElementById('chat-theme-select').value,
                channelId: document.getElementById('chat-channel-id').value,
                platform: document.getElementById('chat-platform').value,
                maxMessages: parseInt(document.getElementById('chat-max-messages').value),
                alignment: document.getElementById('chat-alignment').value,
                fadeTime: parseInt(document.getElementById('chat-fade-time').value)
            };
            
            this.updateModuleSettings('chat', newSettings);
            
            // 채팅 오버레이에서 사용할 수 있도록 개별 localStorage 항목으로 저장
            localStorage.setItem('chat-theme', newSettings.theme);
            localStorage.setItem('chat-max-messages', newSettings.maxMessages);
            localStorage.setItem('chat-fade-time', newSettings.fadeTime);
            localStorage.setItem('chat-alignment', newSettings.alignment);
            localStorage.setItem('chat-platform', newSettings.platform);
            localStorage.setItem('chat-channel-id', newSettings.channelId);
        }
        
        this.updateUI();
    }
} 