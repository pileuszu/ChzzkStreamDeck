// 메인 애플리케이션 초기화

class App {
    constructor() {
        this.settingsManager = new SettingsManager();
        this.uiManager = new UIManager(this);
        this.spotifyModule = new SpotifyModule(this.settingsManager);
        this.chatModule = new ChatModule(this.settingsManager);
        
        this.init();
    }
    
    init() {
        console.log('OBS 위젯 대시보드 초기화 중...');
        
        // 설정 로드
        this.settingsManager.loadSettings();
        
        // UI 이벤트 리스너 설정
        this.setupEventListeners();
        
        // 모듈 상태 업데이트
        this.updateModuleStates();
        
        // 테마 적용
        this.uiManager.applyTheme('spotify', this.settingsManager.getModuleSettings('spotify').theme);
        this.uiManager.applyTheme('chat', this.settingsManager.getModuleSettings('chat').theme);
        
        console.log('OBS 위젯 대시보드 초기화 완료!');
    }
    
    setupEventListeners() {
        // Spotify 토글
        document.getElementById('spotify-toggle').addEventListener('change', async (e) => {
            if (e.target.checked) {
                const success = await this.spotifyModule.start();
                if (!success) {
                    e.target.checked = false;
                }
            } else {
                this.spotifyModule.stop();
            }
            this.uiManager.updateModuleCard('spotify', this.spotifyModule.isActive);
        });
        
        // 채팅 토글
        document.getElementById('chat-toggle').addEventListener('change', async (e) => {
            if (e.target.checked) {
                const success = await this.chatModule.start();
                if (!success) {
                    e.target.checked = false;
                }
            } else {
                await this.chatModule.stop();
            }
            this.uiManager.updateModuleCard('chat', this.chatModule.isActive);
        });
        
        // 모달 외부 클릭시 닫기
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('settings-modal');
            if (e.target === modal) {
                this.uiManager.closeSettings();
            }
        });
    }
    
    updateModuleStates() {
        this.uiManager.updateModuleCard('spotify', this.spotifyModule.isActive);
        this.uiManager.updateModuleCard('chat', this.chatModule.isActive);
    }
}

// 애플리케이션 시작
const app = new App();

// 전역 함수들 (HTML에서 호출)
window.openSettings = (moduleName) => {
    app.uiManager.openSettings(moduleName);
};

window.closeSettings = () => {
    app.uiManager.closeSettings();
};

window.saveSettings = () => {
    app.uiManager.saveSettings();
};

window.copyToClipboard = (elementId) => {
    app.uiManager.copyToClipboard(elementId);
};

// 앱 인스턴스를 전역에서 접근 가능하도록
window.app = app; 