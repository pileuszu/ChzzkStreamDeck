#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네온 오버레이 설정 관리 모듈
"""

import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# 기본 설정 파일 경로
CONFIG_FILE = "overlay_config.json"

# 기본 설정값
DEFAULT_CONFIG = {
    "server": {
        "port": 8080,
        "host": "localhost"
    },
    "modules": {
        "chat": {
            "enabled": False,
            "channel_id": "",
            "url_path": "/chat",
            "max_messages": 10,
            "show_recent_only": True
        },
        "spotify": {
            "enabled": False,
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "http://localhost:8080/spotify/callback",
            "url_path": "/spotify",
            "simplified_mode": False,
            "theme": "default",
            "available_themes": [
                {
                    "id": "default",
                    "name": "기본 네온 테마",
                    "description": "기본 네온 글로우 스타일"
                },
                {
                    "id": "minimal",
                    "name": "미니멀 테마",
                    "description": "깔끔한 미니멀 디자인"
                },
                {
                    "id": "retro",
                    "name": "레트로 테마",
                    "description": "80년대 신스웨이브 스타일"
                },
                {
                    "id": "glass",
                    "name": "글래스모피즘",
                    "description": "투명한 글래스 효과"
                }
            ]
        }
    },
    "ui": {
        "theme": "neon",
        "language": "ko",
        "chat_background": "transparent",
        "dark_mode": True
    }
}

class ConfigManager:
    """설정 관리 클래스"""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 기본값과 병합
                    return self._merge_with_defaults(config)
            else:
                logger.info("설정 파일이 없어 기본값을 사용합니다.")
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("설정이 저장되었습니다.")
            return True
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            return False
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """로드된 설정을 기본값과 병합"""
        merged = DEFAULT_CONFIG.copy()
        
        def deep_merge(base: dict, update: dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(merged, config)
        return merged
    
    def get(self, key_path: str, default=None):
        """설정값 가져오기 (예: "modules.chat.enabled")"""
        keys = key_path.split('.')
        current = self.config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value):
        """설정값 변경하기"""
        keys = key_path.split('.')
        current = self.config
        
        try:
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value
            return True
        except Exception as e:
            logger.error(f"설정 변경 실패: {e}")
            return False
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """특정 모듈의 설정 가져오기"""
        return self.config.get("modules", {}).get(module_name, {})
    
    def set_module_enabled(self, module_name: str, enabled: bool):
        """모듈 활성화/비활성화"""
        self.set(f"modules.{module_name}.enabled", enabled)
    
    def is_module_enabled(self, module_name: str) -> bool:
        """모듈 활성화 상태 확인"""
        return self.get(f"modules.{module_name}.enabled", False)
    
    def get_server_port(self) -> int:
        """서버 포트 가져오기"""
        return self.get("server.port", 8080)
    
    def get_server_host(self) -> str:
        """서버 호스트 가져오기"""
        return self.get("server.host", "localhost")
    
    def update_spotify_credentials(self, client_id: str, client_secret: str, redirect_uri: str = None):
        """Spotify 인증 정보 업데이트"""
        self.set("modules.spotify.client_id", client_id)
        self.set("modules.spotify.client_secret", client_secret)
        if redirect_uri:
            self.set("modules.spotify.redirect_uri", redirect_uri)
        else:
            # 기본 리다이렉트 URI 설정
            port = self.get_server_port()
            self.set("modules.spotify.redirect_uri", f"http://localhost:{port}/spotify/callback")
    
    def update_chat_channel(self, channel_id: str):
        """채팅 채널 ID 업데이트"""
        self.set("modules.chat.channel_id", channel_id)
    
    def get_spotify_theme(self) -> str:
        """현재 Spotify 테마 가져오기"""
        return self.get("modules.spotify.theme", "default")
    
    def set_spotify_theme(self, theme_id: str):
        """Spotify 테마 설정"""
        self.set("modules.spotify.theme", theme_id)
    
    def get_available_spotify_themes(self) -> list:
        """사용 가능한 Spotify 테마 목록 가져오기"""
        return self.get("modules.spotify.available_themes", [])

# 전역 설정 관리자 인스턴스
config_manager = ConfigManager() 