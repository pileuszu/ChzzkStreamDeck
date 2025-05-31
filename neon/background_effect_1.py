#!/usr/bin/env python3
"""
움직이는 파티클 배경 애니메이션 모듈
포트: 9090
URL: http://localhost:9090/background
"""

import http.server
import threading
import logging
from urllib.parse import urlparse

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ParticleBackgroundHandler(http.server.SimpleHTTPRequestHandler):
    """파티클 배경 HTTP 핸들러"""
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/' or parsed_path.path == '/background':
                # 파티클 배경만 제공
                self.send_particle_background()
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
    
    def send_particle_background(self):
        """파티클 배경 HTML 전송"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        
        html = self.get_particle_html()
        self.send_header('Content-Length', str(len(html.encode('utf-8'))))
        self.end_headers()
        
        try:
            self.wfile.write(html.encode('utf-8'))
            self.wfile.flush()
        except (ConnectionAbortedError, BrokenPipeError) as e:
            logger.debug(f"클라이언트 연결 끊어짐: {e}")
    
    def get_particle_html(self):
        """최적화된 파티클 배경 HTML"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>파티클 배경 애니메이션</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, 
                rgba(0, 0, 0, 0.05) 0%, 
                rgba(0, 50, 100, 0.08) 50%, 
                rgba(0, 0, 0, 0.05) 100%);
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            position: relative;
        }
        
        .particle-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        }
        
        .particle {
            position: absolute;
            border-radius: 50%;
            pointer-events: none;
            will-change: transform, opacity;
            backface-visibility: hidden;
        }
        
        .particle-type-1 {
            background: rgba(255, 255, 255, 0.4);
            animation: float1 8s ease-in-out infinite;
        }
        
        .particle-type-2 {
            background: rgba(0, 255, 175, 0.4);
            animation: float2 10s ease-in-out infinite;
        }
        
        .particle-type-3 {
            background: rgba(155, 77, 224, 0.3);
            animation: float3 12s ease-in-out infinite;
        }
        
        /* 부드러운 움직임을 위한 최적화된 애니메이션 */
        @keyframes float1 {
            0%, 100% { 
                transform: translate3d(0, 0, 0) rotate(0deg) scale(1); 
                opacity: 0.2; 
            }
            25% { 
                transform: translate3d(10px, -15px, 0) rotate(90deg) scale(1.1); 
                opacity: 0.6; 
            }
            50% { 
                transform: translate3d(-5px, -25px, 0) rotate(180deg) scale(1.2); 
                opacity: 0.8; 
            }
            75% { 
                transform: translate3d(-15px, -10px, 0) rotate(270deg) scale(1.1); 
                opacity: 0.6; 
            }
        }
        
        @keyframes float2 {
            0%, 100% { 
                transform: translate3d(0, 0, 0) rotate(0deg) scale(1); 
                opacity: 0.3; 
            }
            33% { 
                transform: translate3d(-12px, -20px, 0) rotate(120deg) scale(1.15); 
                opacity: 0.7; 
            }
            66% { 
                transform: translate3d(8px, -30px, 0) rotate(240deg) scale(1.25); 
                opacity: 0.9; 
            }
        }
        
        @keyframes float3 {
            0%, 100% { 
                transform: translate3d(0, 0, 0) rotate(0deg) scale(1); 
                opacity: 0.25; 
            }
            20% { 
                transform: translate3d(8px, -12px, 0) rotate(72deg) scale(1.08); 
                opacity: 0.5; 
            }
            40% { 
                transform: translate3d(-6px, -22px, 0) rotate(144deg) scale(1.18); 
                opacity: 0.7; 
            }
            60% { 
                transform: translate3d(12px, -18px, 0) rotate(216deg) scale(1.12); 
                opacity: 0.6; 
            }
            80% { 
                transform: translate3d(-8px, -8px, 0) rotate(288deg) scale(1.05); 
                opacity: 0.4; 
            }
        }
    </style>
</head>
<body>
    <div class="particle-container" id="particleContainer">
    </div>

    <script>
        class ParticleSystem {
            constructor() {
                this.container = document.getElementById('particleContainer');
                this.particles = new Set();
                this.maxParticles = 40; // 성능을 위해 파티클 수 제한
                this.animationId = null;
                
                this.init();
            }
            
            init() {
                // 초기 파티클 생성
                for (let i = 0; i < this.maxParticles; i++) {
                    setTimeout(() => this.createParticle(), i * 150);
                }
                
                // 정기적으로 파티클 갱신 (깜빡임 방지)
                this.startUpdateLoop();
            }
            
            createParticle() {
                if (this.particles.size >= this.maxParticles) return;
                
                const particle = document.createElement('div');
                particle.className = `particle particle-type-${Math.floor(Math.random() * 3) + 1}`;
                
                // 랜덤 위치
                particle.style.left = Math.random() * 95 + '%';
                particle.style.top = Math.random() * 95 + '%';
                
                // 랜덤 크기 (작은 범위로 제한)
                const size = Math.random() * 6 + 3; // 3-9px
                particle.style.width = size + 'px';
                particle.style.height = size + 'px';
                
                // 랜덤 애니메이션 지연
                particle.style.animationDelay = Math.random() * 8 + 's';
                
                this.container.appendChild(particle);
                this.particles.add(particle);
                
                // 생명주기 관리 (깜빡임 방지를 위해 순환 재생성)
                setTimeout(() => {
                    this.removeParticle(particle);
                    // 바로 새 파티클 생성하여 깜빡임 방지
                    setTimeout(() => this.createParticle(), 100);
                }, Math.random() * 15000 + 20000); // 20-35초 생명주기
            }
            
            removeParticle(particle) {
                if (particle && particle.parentNode) {
                    // 부드러운 페이드아웃
                    particle.style.transition = 'opacity 0.5s ease-out';
                    particle.style.opacity = '0';
                    
                    setTimeout(() => {
                        if (particle.parentNode) {
                            particle.parentNode.removeChild(particle);
                        }
                        this.particles.delete(particle);
                    }, 500);
                }
            }
            
            startUpdateLoop() {
                // 성능 최적화를 위한 requestAnimationFrame 사용
                const update = () => {
                    // 파티클 수 유지
                    if (this.particles.size < this.maxParticles) {
                        this.createParticle();
                    }
                    
                    this.animationId = requestAnimationFrame(update);
                };
                
                update();
            }
            
            destroy() {
                if (this.animationId) {
                    cancelAnimationFrame(this.animationId);
                }
                this.particles.forEach(particle => this.removeParticle(particle));
            }
        }
        
        // 페이지 로드 시 파티클 시스템 시작
        let particleSystem;
        
        document.addEventListener('DOMContentLoaded', () => {
            particleSystem = new ParticleSystem();
        });
        
        // 페이지 언로드 시 정리
        window.addEventListener('beforeunload', () => {
            if (particleSystem) {
                particleSystem.destroy();
            }
        });
        
        // 성능 모니터링 (선택사항)
        if (window.location.search.includes('debug=true')) {
            setInterval(() => {
                console.log(`파티클 수: ${particleSystem?.particles.size || 0}`);
            }, 5000);
        }
    </script>
</body>
</html>"""
    
    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

def start_background_server():
    """파티클 배경 HTTP 서버 시작"""
    try:
        server = http.server.ThreadingHTTPServer(("", 9090), ParticleBackgroundHandler)
        server.timeout = 10
        logger.info("🌟 파티클 배경 서버 시작: http://localhost:9090")
        server.serve_forever()
    except OSError as e:
        if e.errno == 10048:
            logger.error("❌ 포트 9090이 이미 사용 중입니다.")
        else:
            logger.error(f"❌ 배경 서버 시작 실패: {e}")
    except Exception as e:
        logger.error(f"❌ 배경 서버 오류: {e}")

def main():
    """메인 함수"""
    logger.info("🌟 파티클 배경 애니메이션 시작!")
    
    # HTTP 서버를 별도 스레드에서 실행
    server_thread = threading.Thread(target=start_background_server, daemon=True)
    server_thread.start()
    
    print("\n" + "="*60)
    print("🌟 파티클 배경 애니메이션 서버")
    print("="*60)
    print("🎨 파티클 배경: http://localhost:9090/background")
    print("\n🎯 OBS에서 브라우저 소스로 추가하세요!")
    print("   권장 크기: 1920x1080 (전체화면)")
    print("   레이어: 가장 아래쪽에 배치")
    print("⚠️  종료하려면 Ctrl+C를 누르세요")
    print("="*60)
    
    try:
        # 메인 스레드 유지
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 파티클 배경 서버를 종료합니다.")

if __name__ == "__main__":
    main() 