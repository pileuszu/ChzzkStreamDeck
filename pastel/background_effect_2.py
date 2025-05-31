#!/usr/bin/env python3
"""
파스텔 꽃잎 배경 애니메이션 모듈
포트: 9091
URL: http://localhost:9091/background
"""

import http.server
import threading
import logging
from urllib.parse import urlparse
import socketserver

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PastelBackgroundHandler(http.server.SimpleHTTPRequestHandler):
    """파스텔 꽃잎 배경 HTTP 핸들러"""
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/' or parsed_path.path == '/background':
                # 파스텔 배경만 제공
                self.send_pastel_background()
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"HTTP 요청 처리 오류: {e}")
            try:
                self.send_response(500)
                self.end_headers()
            except:
                pass
    
    def send_pastel_background(self):
        """파스텔 배경 HTML 전송"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        
        html = self.get_pastel_html()
        self.send_header('Content-Length', str(len(html.encode('utf-8'))))
        self.end_headers()
        
        try:
            self.wfile.write(html.encode('utf-8'))
            self.wfile.flush()
        except (ConnectionAbortedError, BrokenPipeError) as e:
            logger.debug(f"클라이언트 연결 끊어짐: {e}")
    
    def get_pastel_html(self):
        """파스텔 꽃잎 배경 HTML"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌸 파스텔 꽃잎 배경 애니메이션 🌸</title>
    <link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, 
                rgba(255, 240, 245, 0.05) 0%, 
                rgba(255, 218, 185, 0.08) 25%,
                rgba(221, 160, 221, 0.06) 50%, 
                rgba(176, 224, 230, 0.08) 75%,
                rgba(255, 182, 193, 0.05) 100%);
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            position: relative;
            font-family: 'Comfortaa', sans-serif;
        }
        
        .pastel-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        }
        
        .petal {
            position: absolute;
            border-radius: 50%;
            pointer-events: none;
            will-change: transform, opacity;
            backface-visibility: hidden;
        }
        
        .petal-pink {
            background: radial-gradient(circle, 
                rgba(255, 182, 193, 0.6) 0%,
                rgba(255, 182, 193, 0.3) 50%,
                rgba(255, 182, 193, 0.1) 100%);
            animation: floatPetal1 12s ease-in-out infinite;
            box-shadow: 0 0 20px rgba(255, 182, 193, 0.4);
        }
        
        .petal-lavender {
            background: radial-gradient(circle, 
                rgba(221, 160, 221, 0.5) 0%,
                rgba(221, 160, 221, 0.25) 50%,
                rgba(221, 160, 221, 0.1) 100%);
            animation: floatPetal2 15s ease-in-out infinite;
            box-shadow: 0 0 25px rgba(221, 160, 221, 0.3);
        }
        
        .petal-sky {
            background: radial-gradient(circle, 
                rgba(176, 224, 230, 0.6) 0%,
                rgba(176, 224, 230, 0.3) 50%,
                rgba(176, 224, 230, 0.1) 100%);
            animation: floatPetal3 18s ease-in-out infinite;
            box-shadow: 0 0 18px rgba(176, 224, 230, 0.4);
        }
        
        .petal-peach {
            background: radial-gradient(circle, 
                rgba(255, 218, 185, 0.5) 0%,
                rgba(255, 218, 185, 0.25) 50%,
                rgba(255, 218, 185, 0.1) 100%);
            animation: floatPetal4 20s ease-in-out infinite;
            box-shadow: 0 0 22px rgba(255, 218, 185, 0.3);
        }
        
        .petal-cream {
            background: radial-gradient(circle, 
                rgba(255, 240, 245, 0.7) 0%,
                rgba(255, 240, 245, 0.4) 50%,
                rgba(255, 240, 245, 0.1) 100%);
            animation: floatPetal5 14s ease-in-out infinite;
            box-shadow: 0 0 15px rgba(255, 240, 245, 0.5);
        }
        
        /* 부드러운 꽃잎 움직임 애니메이션 */
        @keyframes floatPetal1 {
            0%, 100% { 
                transform: translate3d(0, 0, 0) rotate(0deg) scale(1); 
                opacity: 0.3; 
            }
            25% { 
                transform: translate3d(15px, -20px, 0) rotate(90deg) scale(1.2); 
                opacity: 0.7; 
            }
            50% { 
                transform: translate3d(-8px, -35px, 0) rotate(180deg) scale(1.4); 
                opacity: 0.9; 
            }
            75% { 
                transform: translate3d(-20px, -15px, 0) rotate(270deg) scale(1.1); 
                opacity: 0.6; 
            }
        }
        
        @keyframes floatPetal2 {
            0%, 100% { 
                transform: translate3d(0, 0, 0) rotate(0deg) scale(1); 
                opacity: 0.25; 
            }
            33% { 
                transform: translate3d(-18px, -25px, 0) rotate(120deg) scale(1.3); 
                opacity: 0.8; 
            }
            66% { 
                transform: translate3d(12px, -40px, 0) rotate(240deg) scale(1.5); 
                opacity: 1; 
            }
        }
        
        @keyframes floatPetal3 {
            0%, 100% { 
                transform: translate3d(0, 0, 0) rotate(0deg) scale(1); 
                opacity: 0.35; 
            }
            20% { 
                transform: translate3d(10px, -15px, 0) rotate(72deg) scale(1.1); 
                opacity: 0.6; 
            }
            40% { 
                transform: translate3d(-10px, -30px, 0) rotate(144deg) scale(1.25); 
                opacity: 0.8; 
            }
            60% { 
                transform: translate3d(18px, -25px, 0) rotate(216deg) scale(1.15); 
                opacity: 0.7; 
            }
            80% { 
                transform: translate3d(-12px, -10px, 0) rotate(288deg) scale(1.05); 
                opacity: 0.5; 
            }
        }
        
        @keyframes floatPetal4 {
            0%, 100% { 
                transform: translate3d(0, 0, 0) rotate(0deg) scale(1); 
                opacity: 0.2; 
            }
            16% { 
                transform: translate3d(8px, -12px, 0) rotate(60deg) scale(1.08); 
                opacity: 0.5; 
            }
            32% { 
                transform: translate3d(-6px, -22px, 0) rotate(120deg) scale(1.18); 
                opacity: 0.7; 
            }
            48% { 
                transform: translate3d(14px, -28px, 0) rotate(180deg) scale(1.3); 
                opacity: 0.9; 
            }
            64% { 
                transform: translate3d(-10px, -18px, 0) rotate(240deg) scale(1.12); 
                opacity: 0.6; 
            }
            80% { 
                transform: translate3d(5px, -8px, 0) rotate(300deg) scale(1.02); 
                opacity: 0.4; 
            }
        }
        
        @keyframes floatPetal5 {
            0%, 100% { 
                transform: translate3d(0, 0, 0) rotate(0deg) scale(1); 
                opacity: 0.4; 
            }
            30% { 
                transform: translate3d(-15px, -18px, 0) rotate(108deg) scale(1.2); 
                opacity: 0.8; 
            }
            60% { 
                transform: translate3d(10px, -32px, 0) rotate(216deg) scale(1.35); 
                opacity: 1; 
            }
            90% { 
                transform: translate3d(-8px, -12px, 0) rotate(324deg) scale(1.1); 
                opacity: 0.5; 
            }
        }
        
        /* 스타더스트 효과 */
        .stardust {
            position: absolute;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 50%;
            animation: twinkle 3s ease-in-out infinite;
            pointer-events: none;
        }
        
        @keyframes twinkle {
            0%, 100% { 
                opacity: 0.2; 
                transform: scale(0.8); 
            }
            50% { 
                opacity: 1; 
                transform: scale(1.2); 
            }
        }
        
        /* 그라데이션 오버레이 */
        .gradient-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(
                ellipse at center,
                transparent 30%,
                rgba(255, 182, 193, 0.02) 60%,
                rgba(221, 160, 221, 0.03) 80%,
                rgba(176, 224, 230, 0.02) 100%
            );
            animation: breathe 8s ease-in-out infinite;
        }
        
        @keyframes breathe {
            0%, 100% { 
                opacity: 0.5; 
                transform: scale(1);
            }
            50% { 
                opacity: 0.8; 
                transform: scale(1.05);
            }
        }
        
        /* 부드러운 빛 번짐 */
        .soft-glow {
            position: absolute;
            border-radius: 50%;
            filter: blur(20px);
            animation: gentleGlow 10s ease-in-out infinite;
            pointer-events: none;
        }
        
        .glow-pink {
            background: rgba(255, 182, 193, 0.15);
            animation-delay: 0s;
        }
        
        .glow-lavender {
            background: rgba(221, 160, 221, 0.12);
            animation-delay: 2s;
        }
        
        .glow-sky {
            background: rgba(176, 224, 230, 0.18);
            animation-delay: 4s;
        }
        
        .glow-peach {
            background: rgba(255, 218, 185, 0.14);
            animation-delay: 6s;
        }
        
        .glow-cream {
            background: rgba(255, 240, 245, 0.16);
            animation-delay: 8s;
        }
        
        @keyframes gentleGlow {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1) rotate(0deg);
            }
            50% {
                opacity: 0.7;
                transform: scale(1.5) rotate(180deg);
            }
        }
    </style>
</head>
<body>
    <div class="pastel-container" id="pastelContainer">
        <div class="gradient-overlay"></div>
    </div>

    <script>
        class PastelEffectSystem {
            constructor() {
                this.container = document.getElementById('pastelContainer');
                this.petals = new Set();
                this.stardusts = new Set();
                this.glows = new Set();
                this.maxPetals = 50;
                this.maxStardusts = 30;
                this.maxGlows = 8;
                this.animationId = null;
                
                this.init();
            }
            
            init() {
                // 초기 꽃잎 생성
                for (let i = 0; i < this.maxPetals; i++) {
                    setTimeout(() => this.createPetal(), i * 200);
                }
                
                // 초기 스타더스트 생성
                for (let i = 0; i < this.maxStardusts; i++) {
                    setTimeout(() => this.createStardust(), i * 300);
                }
                
                // 초기 글로우 생성
                for (let i = 0; i < this.maxGlows; i++) {
                    setTimeout(() => this.createGlow(), i * 800);
                }
                
                // 정기적으로 업데이트
                this.startUpdateLoop();
            }
            
            createPetal() {
                if (this.petals.size >= this.maxPetals) return;
                
                const petal = document.createElement('div');
                petal.className = 'petal ' + this.getRandomPetalType();
                
                // 랜덤 크기 (8px ~ 25px)
                const size = Math.random() * 17 + 8;
                petal.style.width = size + 'px';
                petal.style.height = size + 'px';
                
                // 랜덤 위치
                petal.style.left = Math.random() * window.innerWidth + 'px';
                petal.style.top = Math.random() * window.innerHeight + 'px';
                
                // 랜덤 애니메이션 딜레이
                petal.style.animationDelay = Math.random() * 10 + 's';
                
                this.container.appendChild(petal);
                this.petals.add(petal);
                
                // 15-25초 후 제거
                setTimeout(() => {
                    this.removePetal(petal);
                }, Math.random() * 10000 + 15000);
            }
            
            createStardust() {
                if (this.stardusts.size >= this.maxStardusts) return;
                
                const star = document.createElement('div');
                star.className = 'stardust';
                
                // 작은 크기 (1px ~ 4px)
                const size = Math.random() * 3 + 1;
                star.style.width = size + 'px';
                star.style.height = size + 'px';
                
                // 랜덤 위치
                star.style.left = Math.random() * window.innerWidth + 'px';
                star.style.top = Math.random() * window.innerHeight + 'px';
                
                // 랜덤 애니메이션 딜레이
                star.style.animationDelay = Math.random() * 3 + 's';
                
                this.container.appendChild(star);
                this.stardusts.add(star);
                
                // 5-8초 후 제거
                setTimeout(() => {
                    this.removeStardust(star);
                }, Math.random() * 3000 + 5000);
            }
            
            createGlow() {
                if (this.glows.size >= this.maxGlows) return;
                
                const glow = document.createElement('div');
                glow.className = 'soft-glow ' + this.getRandomGlowType();
                
                // 큰 크기 (100px ~ 300px)
                const size = Math.random() * 200 + 100;
                glow.style.width = size + 'px';
                glow.style.height = size + 'px';
                
                // 랜덤 위치
                glow.style.left = Math.random() * (window.innerWidth - size) + 'px';
                glow.style.top = Math.random() * (window.innerHeight - size) + 'px';
                
                this.container.appendChild(glow);
                this.glows.add(glow);
                
                // 20-30초 후 제거
                setTimeout(() => {
                    this.removeGlow(glow);
                }, Math.random() * 10000 + 20000);
            }
            
            getRandomPetalType() {
                const types = ['petal-pink', 'petal-lavender', 'petal-sky', 'petal-peach', 'petal-cream'];
                return types[Math.floor(Math.random() * types.length)];
            }
            
            getRandomGlowType() {
                const types = ['glow-pink', 'glow-lavender', 'glow-sky', 'glow-peach', 'glow-cream'];
                return types[Math.floor(Math.random() * types.length)];
            }
            
            removePetal(petal) {
                if (this.petals.has(petal)) {
                    petal.style.opacity = '0';
                    petal.style.transform = 'scale(0)';
                    setTimeout(() => {
                        if (petal.parentNode) {
                            petal.parentNode.removeChild(petal);
                        }
                        this.petals.delete(petal);
                    }, 1000);
                }
            }
            
            removeStardust(star) {
                if (this.stardusts.has(star)) {
                    star.style.opacity = '0';
                    setTimeout(() => {
                        if (star.parentNode) {
                            star.parentNode.removeChild(star);
                        }
                        this.stardusts.delete(star);
                    }, 500);
                }
            }
            
            removeGlow(glow) {
                if (this.glows.has(glow)) {
                    glow.style.opacity = '0';
                    setTimeout(() => {
                        if (glow.parentNode) {
                            glow.parentNode.removeChild(glow);
                        }
                        this.glows.delete(glow);
                    }, 2000);
                }
            }
            
            startUpdateLoop() {
                const update = () => {
                    // 필요에 따라 새로운 요소들 생성
                    if (Math.random() < 0.1 && this.petals.size < this.maxPetals) {
                        this.createPetal();
                    }
                    
                    if (Math.random() < 0.05 && this.stardusts.size < this.maxStardusts) {
                        this.createStardust();
                    }
                    
                    if (Math.random() < 0.02 && this.glows.size < this.maxGlows) {
                        this.createGlow();
                    }
                    
                    this.animationId = requestAnimationFrame(update);
                };
                
                update();
            }
            
            destroy() {
                if (this.animationId) {
                    cancelAnimationFrame(this.animationId);
                }
                
                // 모든 요소 제거
                this.petals.forEach(petal => this.removePetal(petal));
                this.stardusts.forEach(star => this.removeStardust(star));
                this.glows.forEach(glow => this.removeGlow(glow));
            }
        }
        
        // 페이지 로드 시 시스템 시작
        document.addEventListener('DOMContentLoaded', () => {
            const effectSystem = new PastelEffectSystem();
            
            // 페이지 언로드 시 정리
            window.addEventListener('beforeunload', () => {
                effectSystem.destroy();
            });
        });
    </script>
</body>
</html>"""

    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

def start_pastel_background_server():
    """파스텔 배경 서버 시작"""
    try:
        port = 9091
        with socketserver.TCPServer(("", port), PastelBackgroundHandler) as httpd:
            httpd.allow_reuse_address = True
            logger.info(f"🌸 파스텔 꽃잎 배경 서버 시작: http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            logger.error(f"❌ 포트 {port}가 이미 사용 중입니다. 다른 포트를 사용하거나 기존 프로세스를 종료하세요.")
        else:
            logger.error(f"❌ 서버 시작 실패: {e}")
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")

def main():
    """메인 함수"""
    print("🌸✨ 파스텔 꽃잎 배경 이펙트 ✨🌸")
    print("=" * 50)
    
    # 서버를 별도 스레드에서 시작
    server_thread = threading.Thread(target=start_pastel_background_server, daemon=True)
    server_thread.start()
    
    print(f"🌸 파스텔 배경 이펙트: http://localhost:9091")
    print("🌺 OBS에서 브라우저 소스로 추가하세요!")
    print("⏹️  종료하려면 Ctrl+C를 누르세요.")
    
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🌸 사용자에 의해 중단됨")

if __name__ == "__main__":
    main() 