// UI 관리자
class UIManager {
    constructor(app) {
        this.app = app;
        this.currentModule = null;
        this.settingsModal = document.getElementById('settings-modal');
    }
    
    // 모듈 카드 상태 업데이트
    updateModuleCard(moduleName, isActive) {
        const moduleCard = document.getElementById(`${moduleName}-module`);
        if (isActive) {
            moduleCard.classList.add('active');
        } else {
            moduleCard.classList.remove('active');
        }
    }
    
    // 설정 모달 열기
    openSettings(moduleName) {
        this.currentModule = moduleName;
        this.settingsModal.style.display = 'block';
        
        // 모든 설정 패널 숨기기
        document.querySelectorAll('.settings-panel').forEach(panel => {
            panel.style.display = 'none';
        });
        
        // 해당 모듈의 설정 패널 표시
        document.getElementById(`${moduleName}-settings`).style.display = 'block';
        document.getElementById('modal-title').textContent = `${moduleName === 'spotify' ? 'Spotify' : '채팅'} 모듈 설정`;
        
        // 현재 설정 값 로드
        this.app.settingsManager.loadModalSettings(moduleName);
    }
    
    // 설정 모달 닫기
    closeSettings() {
        this.settingsModal.style.display = 'none';
        this.currentModule = null;
    }
    
    // 설정 저장
    saveSettings() {
        if (!this.currentModule) return;
        
        // 설정 저장
        this.app.settingsManager.saveModalSettings(this.currentModule);
        
        // 테마 적용
        this.applyTheme(this.currentModule, this.app.settingsManager.getModuleSettings(this.currentModule).theme);
        
        // 모듈이 실행 중이면 재시작
        const module = this.currentModule === 'spotify' ? this.app.spotifyModule : this.app.chatModule;
        if (module.isActive) {
            module.restart();
        }
        
        this.closeSettings();
    }
    
    // 테마 적용
    applyTheme(moduleName, themeName) {
        if (moduleName === 'spotify') {
            this.applySpotifyTheme(themeName);
        } else if (moduleName === 'chat') {
            this.applyChatTheme(themeName);
        }
    }
    
    // Spotify 테마 적용
    applySpotifyTheme(themeName) {
        const spotifyWidget = document.querySelector('.spotify-widget');
        if (!spotifyWidget) return;
        
        // 기존 테마 클래스 제거
        spotifyWidget.classList.remove('theme-simple-purple', 'theme-neon-green');
        
        // 새 테마 클래스 추가
        spotifyWidget.classList.add(`theme-${themeName}`);
    }
    
    // 채팅 테마 적용
    applyChatTheme(themeName) {
        const chatWidget = document.querySelector('.chat-widget');
        if (!chatWidget) return;
        
        // 기존 테마 클래스 제거
        chatWidget.classList.remove('theme-simple-purple', 'theme-neon-green');
        
        // 새 테마 클래스 추가
        chatWidget.classList.add(`theme-${themeName}`);
    }
    
    // 브라우저 소스 URL 복사
    copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        const copyBtn = element.nextElementSibling;
        
        // 텍스트 선택 및 복사
        element.select();
        element.setSelectionRange(0, 99999); // 모바일 브라우저용
        
        try {
            document.execCommand('copy');
            this.showCopyFeedback(copyBtn);
        } catch (err) {
            console.error('복사 실패:', err);
            // 대체 방법으로 navigator.clipboard API 사용
            navigator.clipboard.writeText(element.value).then(() => {
                this.showCopyFeedback(copyBtn);
            }).catch(err => {
                console.error('복사 실패:', err);
                alert('복사에 실패했습니다. 수동으로 복사해주세요.');
            });
        }
    }
    
    // 복사 성공 피드백
    showCopyFeedback(copyBtn) {
        copyBtn.classList.add('copied');
        const originalHTML = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fas fa-check"></i>';
        
        setTimeout(() => {
            copyBtn.classList.remove('copied');
            copyBtn.innerHTML = originalHTML;
        }, 2000);
    }
    
    // 에러 메시지 표시
    showError(message) {
        alert(message); // 추후 더 나은 토스트 알림으로 교체 가능
    }
    
    // 성공 메시지 표시
    showSuccess(message) {
// 성공 메시지 (로그 제거)
    }
} 