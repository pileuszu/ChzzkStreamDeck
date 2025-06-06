import json
import logging
import http.server
import threading
from urllib.parse import urlparse

# 로깅 설정
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 글로벌 메시지 저장소
chat_messages = []
MAX_MESSAGES = 50
# 중복 방지를 위한 메시지 ID 저장소
processed_message_ids = set()
MAX_PROCESSED_IDS = 10  # 최근 10개 메시지 ID 유지

def add_chat_message(message_data):
    """새 채팅 메시지 추가 - 중복 방지 로직 포함"""
    global chat_messages, processed_message_ids
    
    # 메시지 ID 확인
    message_id = message_data.get('id', '')
    if not message_id:
        return  # ID가 없으면 무시
    
    # 중복 메시지 체크
    if message_id in processed_message_ids:
        logger.debug(f"중복 메시지 무시: {message_id}")
        return
    
    # 새 메시지 추가
    chat_messages.append(message_data)
    processed_message_ids.add(message_id)
    
    # 최대 메시지 수 제한
    if len(chat_messages) > MAX_MESSAGES:
        removed_message = chat_messages.pop(0)
        # 제거된 메시지의 ID도 정리 (오래된 ID 관리)
        if len(processed_message_ids) > MAX_PROCESSED_IDS:
            # 가장 오래된 ID들 일부 제거 (실제로는 LRU 캐시가 더 좋지만 간단히 처리)
            oldest_ids = list(processed_message_ids)[:50]  # 오래된 50개 제거
            processed_message_ids -= set(oldest_ids)
    
    logger.debug(f"새 채팅 메시지 추가: {message_data.get('nickname', '익명')}: {message_data.get('message', '')[:20]}...")

class OverlayHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """오버레이용 HTTP 핸들러"""
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/' or parsed_path.path == '/obs':
                # 채팅 오버레이 HTML 제공
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                html = self.get_overlay_html()
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                
                # 연결 상태 확인 후 전송
                try:
                    self.wfile.write(html.encode('utf-8'))
                    self.wfile.flush()
                except (ConnectionAbortedError, BrokenPipeError) as e:
                    logger.debug(f"클라이언트 연결 끊어짐: {e}")
                    return
            
            elif parsed_path.path == '/chat/api/messages':
                # 메시지 API
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                messages_json = json.dumps(chat_messages, ensure_ascii=False)
                self.send_header('Content-Length', str(len(messages_json.encode('utf-8'))))
                self.end_headers()
                
                try:
                    self.wfile.write(messages_json.encode('utf-8'))
                    self.wfile.flush()
                except (ConnectionAbortedError, BrokenPipeError) as e:
                    logger.debug(f"클라이언트 연결 끊어짐: {e}")
                    return
            
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
    
    def get_overlay_html(self):
        """OBS용 채팅 오버레이 HTML"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>치지직 채팅 오버레이</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: transparent;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            position: relative;
        }

        /* 사이버펑크 배경 - 데이터 스트림과 네온 그리드 */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                /* 네온 그리드 */
                linear-gradient(90deg, rgba(0,255,175,0.03) 1px, transparent 1px),
                linear-gradient(180deg, rgba(155,77,224,0.03) 1px, transparent 1px),
                /* 데이터 스트림 파티클 */
                radial-gradient(2px 2px at 20% 30%, rgba(0,255,175,0.8), transparent),
                radial-gradient(1px 1px at 80% 20%, rgba(155,77,224,0.6), transparent),
                radial-gradient(3px 3px at 45% 70%, rgba(255,215,0,0.4), transparent),
                radial-gradient(2px 2px at 90% 80%, rgba(255,255,255,0.3), transparent);
            background-size: 50px 50px, 50px 50px, 300px 300px, 250px 250px, 400px 400px, 200px 200px;
            animation: dataStreamFlow 15s linear infinite, cyberGrid 8s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }

        /* 추가 홀로그램 레이어 */
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                /* 스캔라인 효과 */
                repeating-linear-gradient(
                    0deg,
                    transparent 0px,
                    rgba(0,255,175,0.03) 1px,
                    transparent 2px,
                    transparent 4px
                );
            animation: scanlines 2s linear infinite;
            pointer-events: none;
            z-index: 1;
        }
        
        .chat_wrap {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 520px;
            height: 600px;
            background: transparent;
            z-index: 1000;
            font-family: 'Noto Sans KR', sans-serif;
            overflow: hidden;
            padding: 20px;
        }

        .chat_list {
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            gap: 15px;
            height: 100%;
            overflow: hidden;
            position: relative;
            z-index: 2;
            /* 위쪽 자연스러운 페이드아웃 마스크 */
            mask: linear-gradient(to bottom, 
                transparent 0%, 
                rgba(0,0,0,0.05) 5%, 
                rgba(0,0,0,0.2) 15%, 
                rgba(0,0,0,0.6) 30%, 
                black 45%, 
                black 100%);
            -webkit-mask: linear-gradient(to bottom, 
                transparent 0%, 
                rgba(0,0,0,0.05) 5%, 
                rgba(0,0,0,0.2) 15%, 
                rgba(0,0,0,0.6) 30%, 
                black 45%, 
                black 100%);
        }

        .chat_box.naver.chat {
            padding: 18px 25px;
            margin: 20px 40px;
            position: relative;
            z-index: 2;
            animation: messageEntrance 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            transform: translateX(-120px) rotateY(-15deg) scale(0.8);
            opacity: 0;
            max-width: calc(100% - 80px);
            filter: drop-shadow(0 0 0 transparent);
            overflow: hidden;
        }

        /* 홀로그램 글리치 효과 레이어 */
        .chat_box.naver.chat:before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(255,255,255,0.03) 25%,
                transparent 26%,
                transparent 74%,
                rgba(0,255,175,0.05) 75%,
                transparent 100%
            );
            animation: hologramScan 3s ease-in-out infinite;
            z-index: -1;
            pointer-events: none;
        }

        /* 네온 파티클 트레일 */
        .chat_box.naver.chat:after {
            content: '';
            position: absolute;
            top: -5px;
            left: -5px;
            right: -5px;
            bottom: -5px;
            background: 
                radial-gradient(circle at 10% 20%, rgba(0,255,175,0.1) 0%, transparent 50%),
                radial-gradient(circle at 90% 80%, rgba(155,77,224,0.1) 0%, transparent 50%),
                radial-gradient(circle at 50% 10%, rgba(255,215,0,0.08) 0%, transparent 50%);
            animation: particleFlow 4s ease-in-out infinite;
            z-index: -2;
            pointer-events: none;
            filter: blur(1px);
        }

        /* 스트리머용 왼쪽 상단 별 */
        .chat_box.naver.chat.streamer::before {
            content: '⭐';
            position: absolute;
            top: -8px;
            left: -8px;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            background: transparent;
            border-radius: 50%;
            animation: starTwinkle 1.5s ease-in-out infinite alternate;
            z-index: 10;
            filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.9));
        }

        .chat_box.naver.chat p.name {
            display: block;
            font-weight: 900;
            font-size: 15px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 2px;
            position: relative;
            overflow: hidden;
        }

        .chat_box.naver.chat.streamer p.name {
            color: #9b4de0;
            text-shadow: 
                0 0 15px rgba(155, 77, 224, 0.9),
                0 0 30px rgba(155, 77, 224, 0.5),
                0 0 45px rgba(155, 77, 224, 0.3);
            animation: royalGlow 3s ease-in-out infinite alternate;
        }

        .chat_box.naver.chat:not(.streamer) p.name {
            color: #00FFAF;
            text-shadow: 
                0 0 15px rgba(0, 255, 175, 0.9),
                0 0 30px rgba(0, 255, 175, 0.5),
                0 0 45px rgba(0, 255, 175, 0.3);
            animation: emeraldGlow 3s ease-in-out infinite alternate;
        }

        /* 타이핑 효과용 애니메이션 */
        .chat_box.naver.chat p.name::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transform: translateX(-100%);
            animation: shimmer 2s ease-in-out 0.5s;
        }

        .chat_box.naver.chat p.name::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 100%;
            height: 3px;
            background: currentColor;
            transform: scaleX(0);
            animation: underlineExpand 1.2s ease-out 0.4s forwards;
            border-radius: 2px;
        }

        /* 이름과 텍스트 사이 구분선 */
        .chat_box.naver.chat::after {
            content: '';
            position: absolute;
            left: 25px;
            right: 25px;
            top: calc(15px + 8px + 15px + 3px);
            height: 4px;
            background: linear-gradient(90deg, 
                transparent 0%,
                currentColor 20%,
                currentColor 80%,
                transparent 100%);
            opacity: 0.3;
            transform: scaleX(0);
            animation: separatorExpand 1.5s ease-out 0.8s forwards;
            z-index: 1;
        }

        .chat_box.naver.chat.streamer::after {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(155, 77, 224, 0.8) 20%,
                rgba(155, 77, 224, 0.8) 80%,
                transparent 100%);
            opacity: 0.6;
        }

        .chat_box.naver.chat:not(.streamer)::after {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(0, 255, 175, 0.8) 20%,
                rgba(0, 255, 175, 0.8) 80%,
                transparent 100%);
            opacity: 0.6;
        }

        .chat_box.naver.chat.donation::after {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(255, 215, 0, 0.8) 20%,
                rgba(255, 215, 0, 0.8) 80%,
                transparent 100%);
            opacity: 0.6;
        }

        .chat_box.naver.chat p.text {
            color: #ffffff;
            font-size: 17px;
            line-height: 1.5;
            font-weight: 400;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
            animation: typeWriter 1.5s ease-out 0.3s forwards;
            opacity: 0;
            position: relative;
        }

        .chat_box.naver.chat.donation {
            background: linear-gradient(135deg, 
                rgba(255, 215, 0, 0.05) 0%, 
                rgba(255, 140, 0, 0.08) 30%,
                rgba(255, 69, 0, 0.10) 70%,
                rgba(255, 215, 0, 0.05) 100%);
            border: 1px solid rgba(255, 215, 0, 0.4);
            box-shadow: 
                0 15px 50px rgba(255, 215, 0, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.15),
                0 0 40px rgba(255, 215, 0, 0.15);
            animation: goldenEntrance 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
        }

        .chat_box.naver.chat.donation p.name {
            color: #FFD700;
            text-shadow: 
                0 0 20px rgba(255, 215, 0, 0.9),
                0 0 40px rgba(255, 215, 0, 0.6),
                0 0 60px rgba(255, 140, 0, 0.4);
            animation: goldenPulse 2s ease-in-out infinite;
        }

        .donation-amount {
            display: inline-block;
            background: linear-gradient(45deg, #FFD700, #FFA500, #FF8C00);
            color: #000;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 13px;
            font-weight: bold;
            margin-left: 10px;
            box-shadow: 
                0 4px 15px rgba(255, 215, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
            animation: coinFlip 1s ease-in-out 0.8s;
            transform: rotateY(90deg);
        }

        .waiting-message {
            text-align: center;
            color: rgba(255,255,255,0.8);
            padding: 25px;
            background: linear-gradient(135deg, 
                rgba(0,0,0,0.2) 0%, 
                rgba(50,50,50,0.3) 50%, 
                rgba(0,0,0,0.2) 100%);
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            animation: breathe 3s ease-in-out infinite;
            position: relative;
            overflow: hidden;
        }

        .waiting-message::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, 
                transparent 30%, 
                rgba(255,255,255,0.1) 50%, 
                transparent 70%);
            animation: scan 4s ease-in-out infinite;
        }

        /* 애니메이션 정의 */
        @keyframes messageEntrance {
            0% {
                transform: translateX(-120px) rotateY(-15deg) scale(0.8);
                opacity: 0;
                filter: blur(10px);
            }
            50% {
                transform: translateX(15px) rotateY(-5deg) scale(1.05);
                opacity: 0.8;
                filter: blur(2px);
            }
            80% {
                transform: translateX(-5px) rotateY(2deg) scale(1.02);
                opacity: 0.95;
                filter: blur(0px);
            }
            100% {
                transform: translateX(0) rotateY(0deg) scale(1);
                opacity: 1;
                filter: blur(0px);
            }
        }

        @keyframes messageEntranceRight {
            0% {
                transform: translateX(120px) rotateY(15deg) scale(0.8);
                opacity: 0;
                filter: blur(10px);
            }
            50% {
                transform: translateX(-15px) rotateY(5deg) scale(1.05);
                opacity: 0.8;
                filter: blur(2px);
            }
            80% {
                transform: translateX(5px) rotateY(-2deg) scale(1.02);
                opacity: 0.95;
                filter: blur(0px);
            }
            100% {
                transform: translateX(0) rotateY(0deg) scale(1);
                opacity: 1;
                filter: blur(0px);
            }
        }

        @keyframes royalGlow {
            0% {
                text-shadow: 
                    0 0 15px rgba(155, 77, 224, 0.9),
                    0 0 30px rgba(155, 77, 224, 0.5),
                    0 0 45px rgba(155, 77, 224, 0.3);
            }
            100% {
                text-shadow: 
                    0 0 25px rgba(155, 77, 224, 1),
                    0 0 40px rgba(155, 77, 224, 0.8),
                    0 0 60px rgba(155, 77, 224, 0.5),
                    0 0 80px rgba(155, 77, 224, 0.3);
            }
        }

        @keyframes emeraldGlow {
            0% {
                text-shadow: 
                    0 0 15px rgba(0, 255, 175, 0.9),
                    0 0 30px rgba(0, 255, 175, 0.5),
                    0 0 45px rgba(0, 255, 175, 0.3);
            }
            100% {
                text-shadow: 
                    0 0 25px rgba(0, 255, 175, 1),
                    0 0 40px rgba(0, 255, 175, 0.8),
                    0 0 60px rgba(0, 255, 175, 0.5),
                    0 0 80px rgba(0, 255, 175, 0.3);
            }
        }

        @keyframes shimmer {
            0% {
                transform: translateX(-100%);
            }
            100% {
                transform: translateX(100%);
            }
        }

        @keyframes underlineExpand {
            0% {
                transform: scaleX(0);
            }
            100% {
                transform: scaleX(1);
            }
        }

        @keyframes typeWriter {
            0% {
                opacity: 0;
                transform: translateY(20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes goldenEntrance {
            0% {
                transform: translateY(50px) scale(0.5) rotateZ(-10deg);
                opacity: 0;
                filter: brightness(0.5);
            }
            50% {
                transform: translateY(-10px) scale(1.1) rotateZ(2deg);
                opacity: 0.8;
                filter: brightness(1.2);
            }
            100% {
                transform: translateY(0) scale(1) rotateZ(0deg);
                opacity: 1;
                filter: brightness(1);
            }
        }

        @keyframes goldenPulse {
            0%, 100% {
                transform: scale(1);
                filter: brightness(1);
            }
            50% {
                transform: scale(1.05);
                filter: brightness(1.3);
            }
        }

        @keyframes coinFlip {
            0% {
                transform: rotateY(90deg) scale(0.8);
                opacity: 0;
            }
            50% {
                transform: rotateY(0deg) scale(1.1);
                opacity: 0.8;
            }
            100% {
                transform: rotateY(0deg) scale(1);
                opacity: 1;
            }
        }

        @keyframes breathe {
            0%, 100% {
                transform: scale(1);
                opacity: 0.7;
            }
            50% {
                transform: scale(1.02);
                opacity: 0.9;
            }
        }

        @keyframes scan {
            0% {
                transform: translate(-50%, -50%) rotate(0deg);
            }
            100% {
                transform: translate(-50%, -50%) rotate(360deg);
            }
        }

        @keyframes fadeOut {
            0% {
                opacity: 1;
                transform: scale(1) translateY(0);
                filter: blur(0px);
            }
            50% {
                opacity: 0.5;
                transform: scale(0.95) translateY(-10px);
                filter: blur(2px);
            }
            100% {
                opacity: 0;
                transform: scale(0.8) translateY(-30px);
                filter: blur(8px);
            }
        }

        @keyframes separatorExpand {
            0% {
                transform: scaleX(0);
            }
            100% {
                transform: scaleX(1);
            }
        }

        /* 새로운 사이버펑크 애니메이션들 */
        @keyframes dataStreamFlow {
            0% {
                transform: translateY(0) translateX(0);
                opacity: 0.4;
            }
            50% {
                transform: translateY(-50px) translateX(25px);
                opacity: 0.8;
            }
            100% {
                transform: translateY(-100px) translateX(50px);
                opacity: 0.2;
            }
        }

        @keyframes cyberGrid {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1);
            }
            50% {
                opacity: 0.6;
                transform: scale(1.02);
            }
        }

        @keyframes scanlines {
            0% {
                transform: translateY(0);
            }
            100% {
                transform: translateY(4px);
            }
        }

        @keyframes hologramScan {
            0% {
                transform: translateX(-100%);
                opacity: 0;
            }
            10% {
                opacity: 0.8;
            }
            90% {
                opacity: 0.8;
            }
            100% {
                transform: translateX(100%);
                opacity: 0;
            }
        }

        @keyframes particleFlow {
            0%, 100% {
                transform: rotate(0deg) scale(1);
                opacity: 0.3;
            }
            25% {
                transform: rotate(90deg) scale(1.2);
                opacity: 0.7;
            }
            50% {
                transform: rotate(180deg) scale(0.8);
                opacity: 0.5;
            }
            75% {
                transform: rotate(270deg) scale(1.1);
                opacity: 0.6;
            }
        }

        @keyframes hologramGlitch {
            0%, 90%, 100% {
                transform: translate(0);
                filter: hue-rotate(0deg);
            }
            10% {
                transform: translate(-2px, 2px);
                filter: hue-rotate(90deg);
            }
            20% {
                transform: translate(2px, -2px);
                filter: hue-rotate(180deg);
            }
            30% {
                transform: translate(-1px, 1px);
                filter: hue-rotate(270deg);
            }
        }

        .chat_box.naver.chat:not(.streamer) {
            align-self: flex-start;
            background: linear-gradient(135deg, 
                rgba(0, 255, 175, 0.03) 0%, 
                rgba(0, 255, 175, 0.08) 30%,
                rgba(0, 255, 175, 0.12) 50%, 
                rgba(0, 255, 175, 0.08) 70%,
                rgba(0, 255, 175, 0.03) 100%);
            border: 1px solid rgba(0, 255, 175, 0.25);
            border-radius: 25px 25px 25px 8px;
            backdrop-filter: blur(20px);
            box-shadow: 
                0 12px 40px rgba(0, 255, 175, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.06),
                0 0 30px rgba(0, 255, 175, 0.1);
        }

        .chat_box.naver.chat.streamer {
            align-self: flex-end;
            background: linear-gradient(135deg, 
                rgba(155, 77, 224, 0.03) 0%, 
                rgba(155, 77, 224, 0.08) 30%,
                rgba(155, 77, 224, 0.12) 50%, 
                rgba(155, 77, 224, 0.08) 70%,
                rgba(155, 77, 224, 0.03) 100%);
            border: 1px solid rgba(155, 77, 224, 0.25);
            border-radius: 25px 25px 8px 25px;
            backdrop-filter: blur(20px);
            box-shadow: 
                0 12px 40px rgba(155, 77, 224, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.06),
                0 0 30px rgba(155, 77, 224, 0.1);
            animation: messageEntranceRight 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            transform: translateX(120px) rotateY(15deg) scale(0.8);
        }

        @keyframes starTwinkle {
            0% {
                filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.8));
                opacity: 1;
            }
            100% {
                filter: drop-shadow(0 0 15px rgba(255, 215, 0, 1)) drop-shadow(0 0 25px rgba(255, 215, 0, 0.5));
                opacity: 0.8;
            }
        }

        /* 반응형 */
        @media (max-width: 768px) {
            .chat_wrap {
                width: 90vw;
                left: 5vw;
                padding: 15px;
            }
            
            .chat_box.naver.chat {
                margin: 15px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="chat_wrap">
        <div class="chat_list">
        </div>
    </div>

    <script>
        let lastMessageCount = 0;
        
        async function updateMessages() {
            try {
                const response = await fetch('/chat/api/messages');
                const messages = await response.json();
                
                if (messages.length > lastMessageCount) {
                    const container = document.querySelector('.chat_list');
                    
                    // 대기 메시지 제거
                    const waitingMsg = container.querySelector('.waiting-message');
                    if (waitingMsg) {
                        waitingMsg.style.animation = 'fadeOut 1s ease-out forwards';
                        setTimeout(() => {
                            if (waitingMsg.parentNode) {
                                waitingMsg.remove();
                            }
                        }, 1000);
                    }
                    
                    const newMessages = messages.slice(lastMessageCount);
                    
                    newMessages.forEach((data, index) => {
                        setTimeout(() => {
                            const messageDiv = document.createElement('div');
                            
                            // 클래스 설정
                            let className = 'chat_box naver chat';
                            if (data.is_streamer) {
                                className += ' streamer';
                            } else if (data.type === 'donation') {
                                className += ' donation';
                            }
                            messageDiv.className = className;
                            
                            // 후원 금액 표시
                            const donationAmount = data.type === 'donation' ? 
                                `<span class="donation-amount">💰 ${data.amount ? data.amount.toLocaleString() : 0}원</span>` : '';
                            
                            messageDiv.innerHTML = `
                                <p class="name">${escapeHtml(data.nickname)}${donationAmount}</p>
                                <p class="text">${escapeHtml(data.message)}</p>
                            `;
                            
                            container.appendChild(messageDiv);
                            
                            // 최대 15개 메시지 유지 - 오래된 것부터 제거
                            while (container.children.length > 15) {
                                const firstChild = container.firstChild;
                                if (firstChild && !firstChild.classList.contains('waiting-message')) {
                                    firstChild.style.animation = 'fadeOut 1s ease-out forwards';
                                    setTimeout(() => {
                                        if (firstChild.parentNode) {
                                            firstChild.remove();
                                        }
                                    }, 1000);
                                    break;
                                }
                            }
                        }, index * 200);
                    });
                    
                    lastMessageCount = messages.length;
                }
            } catch (e) {
                console.error('메시지 업데이트 실패:', e);
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // 2초마다 새 메시지 체크
        setInterval(updateMessages, 2000);
        
        // 초기 로드
        updateMessages();
    </script>
</body>
</html>"""
    
    def log_message(self, format, *args):
        # 로그 메시지 비활성화
        pass

def start_http_server(port=None):
    """HTTP 서버 시작"""
    if port is None:
        from config import AppConfig
        config = AppConfig()
        port = config.get_server_port()
        
    try:
        server = http.server.ThreadingHTTPServer(("", port), OverlayHTTPHandler)
        server.timeout = 10
        logger.info(f"🌐 HTTP 서버 시작: http://localhost:{port}")
        server.serve_forever()
    except OSError as e:
        if e.errno == 10048:
            logger.error(f"❌ 포트 {port}가 이미 사용 중입니다.")
        else:
            logger.error(f"❌ HTTP 서버 시작 실패: {e}")
    except Exception as e:
        logger.error(f"❌ HTTP 서버 오류: {e}")

def run_server_thread(port=None):
    """HTTP 서버를 별도 스레드에서 실행"""
    if port is None:
        from config import AppConfig
        config = AppConfig()
        port = config.get_server_port()
        
    server_thread = threading.Thread(target=start_http_server, args=(port,), daemon=True)
    server_thread.start()
    return server_thread 