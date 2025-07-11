#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChzzkStreamDeck 빌드 설정 관리
포트 선택 및 민감한 정보 제외한 빌드용 설정
"""

import json
import os
import sys
from pathlib import Path

# main 폴더를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'main'))

class BuildConfig:
    def __init__(self):
        self.default_port = 8080
        self.available_ports = [8080, 8081, 8082, 8083, 8084, 8085, 8090, 8091, 8092, 8093, 9000, 9001, 9090, 3000, 5000]
        
        # 동적으로 config 가져오기 (실행 시에만)
        try:
            from config import ConfigManager
            config = ConfigManager()
            self.current_port = config.get_server_port()
        except:
            # 빌드 시에는 기본값 사용
            self.current_port = self.default_port
        
        # config 속성 초기화
        self.config = self.get_build_config()
        
    def get_build_config(self):
        """빌드용 설정 반환"""
        return {
            "name": "ChzzkStreamDeck",
            "version": "2.0.0",
            "description": "치지직 스트림덱 - 채팅 오버레이 & 관리 패널",
            "main": "main/unified_server.py",
            "scripts": {
                "start": "python main/unified_server.py",
                "dev": "python main/unified_server.py --debug"
            },
            "dependencies": [
                "aiohttp>=3.8.0",
                "websockets>=10.0",
                "requests>=2.28.0",
                "pywebview>=4.0.0",
                "pythonnet>=3.0.0"
            ],
            "build": {
                "directories": {
                    "output": "dist"
                },
                "files": [
                    "main/**/*",
                    "neon/**/*",
                    "static/**/*",
                    "config.json",
                    "requirements.txt",
                    "README.md"
                ]
            },
            "server": {
                "port": self.current_port,
                "host": "localhost"
            },
            "modules": {
                "spotify": {
                    "client_id": "",
                    "client_secret": "",
                    "redirect_uri": f"http://localhost:{self.current_port}/spotify/callback",
                    "enabled": False
                }
            }
        }
    
    def select_port(self):
        """사용자에게 포트 선택하게 함"""
        print("🚀 ChzzkStreamDeck 빌드 설정")
        print("=" * 50)
        print("사용할 포트를 선택하세요:")
        print()
        
        for i, port in enumerate(self.available_ports, 1):
            print(f"{i:2d}. {port}")
        
        print()
        while True:
            try:
                choice = input(f"포트 번호 (1-{len(self.available_ports)}, 기본값: 1): ").strip()
                
                if not choice:
                    choice = "1"
                
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(self.available_ports):
                    selected_port = self.available_ports[choice_idx]
                    self.config["server"]["port"] = selected_port
                    
                    # Spotify redirect URI도 포트에 맞게 업데이트
                    self.config["modules"]["spotify"]["redirect_uri"] = f"http://localhost:{selected_port}/spotify/callback"
                    
                    print(f"✅ 포트 {selected_port} 선택됨")
                    return selected_port
                else:
                    print("❌ 잘못된 선택입니다. 다시 입력해주세요.")
                    
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
            except KeyboardInterrupt:
                print("\n❌ 빌드가 취소되었습니다.")
                sys.exit(1)
    
    def save_build_config(self, filename="config_build.json"):
        """빌드용 설정 파일 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"📁 빌드 설정이 {filename}에 저장되었습니다.")
    
    def create_port_launcher(self, port):
        """포트별 실행 스크립트 생성"""
        
        # Windows 배치 파일
        bat_content = f"""@echo off
chcp 65001 >nul
echo 🎮 ChzzkStreamDeck 시작 (포트: {port})
echo ====================================
python main.py --app --port {port}
pause
"""
        
        with open(f"start_port_{port}.bat", 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        # Linux/Mac 셸 스크립트
        sh_content = f"""#!/bin/bash
echo "🎮 ChzzkStreamDeck 시작 (포트: {port})"
echo "===================================="
python3 main.py --app --port {port}
read -p "Press Enter to exit..."
"""
        
        with open(f"start_port_{port}.sh", 'w', encoding='utf-8') as f:
            f.write(sh_content)
        
        # 실행 권한 부여 (Linux/Mac)
        try:
            os.chmod(f"start_port_{port}.sh", 0o755)
        except:
            pass
        
        print(f"🚀 포트별 실행 스크립트 생성됨:")
        print(f"   - Windows: start_port_{port}.bat")
        print(f"   - Linux/Mac: start_port_{port}.sh")

def main():
    """빌드 설정 메인 함수"""
    build_config = BuildConfig()
    
    print("🛠️  ChzzkStreamDeck 빌드 준비")
    print("=" * 50)
    print()
    print("⚠️  주의사항:")
    print("   - 채널 ID, Spotify 클라이언트 정보는 빌드에 포함되지 않습니다")
    print("   - 사용자가 직접 관리패널에서 설정해야 합니다")
    print("   - 이는 보안을 위한 조치입니다")
    print()
    
    # 포트 선택
    selected_port = build_config.select_port()
    
    # 설정 파일 저장
    build_config.save_build_config()
    
    # 포트별 실행 스크립트 생성
    build_config.create_port_launcher(selected_port)
    
    print()
    print("✅ 빌드 설정 완료!")
    print()
    print("📋 다음 단계:")
    print("1. 빌드 도구로 실행 파일 생성")
    print("2. 사용자는 첫 실행 시 관리패널에서 다음 정보 입력:")
    print("   - 치지직 채널 ID")
    print("   - Spotify 클라이언트 ID 및 Secret")
    print("3. 설정 저장 후 모듈 사용 가능")
    print()

if __name__ == "__main__":
    main() 