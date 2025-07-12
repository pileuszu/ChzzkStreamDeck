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
        
        let title = '모듈 설정';
        if (moduleName === 'spotify') title = 'Spotify 모듈 설정';
        else if (moduleName === 'chat') title = '채팅 모듈 설정';
        else if (moduleName === 'musicbot') title = '음악봇 모듈 설정';
        
        document.getElementById('modal-title').textContent = title;
        
        // 현재 설정 값 로드
        this.app.settingsManager.loadModalSettings(moduleName);
        
        // 음악봇 모듈인 경우 상태 업데이트
        if (moduleName === 'musicbot') {
            this.updateMusicBotStatus();
        }
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
        let module = null;
        if (this.currentModule === 'spotify') {
            module = this.app.spotifyModule;
        } else if (this.currentModule === 'chat') {
            module = this.app.chatModule;
        } else if (this.currentModule === 'musicbot') {
            module = this.app.musicBotModule;
        }
        
        if (module && module.isActive) {
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
    
    // 정보 메시지 표시
    showInfo(message) {
        console.log(message);
        
        // 멀티라인 메시지를 처리하기 위해 개행 문자를 <br>로 변환
        const formattedMessage = message.replace(/\n/g, '<br>');
        
        // 간단한 모달 다이얼로그로 표시
        const infoModal = document.createElement('div');
        infoModal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        
        infoModal.innerHTML = `
            <div style="
                background: white;
                padding: 30px;
                border-radius: 10px;
                max-width: 500px;
                max-height: 400px;
                overflow-y: auto;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            ">
                <h3 style="margin-top: 0; color: #333;">📋 정보</h3>
                <pre style="
                    white-space: pre-wrap;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    line-height: 1.4;
                    color: #666;
                    margin: 15px 0;
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                ">${message}</pre>
                <button style="
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    float: right;
                " onclick="this.parentElement.parentElement.remove()">
                    확인
                </button>
            </div>
        `;
        
        document.body.appendChild(infoModal);
        
        // 배경 클릭 시 닫기
        infoModal.addEventListener('click', (e) => {
            if (e.target === infoModal) {
                infoModal.remove();
            }
        });
        
        // 5초 후 자동 닫기
        setTimeout(() => {
            if (infoModal.parentElement) {
                infoModal.remove();
            }
        }, 10000);
    }
    
    // 음악봇 상태 업데이트
    updateMusicBotStatus() {
        const chatStatus = document.getElementById('musicbot-status-chat');
        const spotifyStatus = document.getElementById('musicbot-status-spotify');
        
        if (chatStatus) {
            if (this.app.chatModule && this.app.chatModule.isActive) {
                chatStatus.textContent = '활성화';
                chatStatus.className = 'status-value active';
            } else {
                chatStatus.textContent = '비활성화';
                chatStatus.className = 'status-value';
            }
        }
        
        if (spotifyStatus) {
            if (this.app.spotifyModule && this.app.spotifyModule.isActive) {
                spotifyStatus.textContent = '활성화';
                spotifyStatus.className = 'status-value active';
            } else {
                spotifyStatus.textContent = '비활성화';
                spotifyStatus.className = 'status-value';
            }
        }
    }
} 