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
            "show_recent_only": True,
            "single_chat_mode": False,
            "streamer_align_left": False,
            "background_enabled": True,
            "background_opacity": 0.3,
            "remove_outer_effects": False
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
                    "id": "purple",
                    "name": "퍼플 테마",
                    "description": "보라색 그라데이션 스타일"
                },
                {
                    "id": "purple_compact",
                    "name": "퍼플 컴팩트",
                    "description": "보라색 한 줄 컴팩트 스타일"
                }
            ]
        }
    },
    "ui": {
        "theme": "neon",
        "admin_theme": "neon",
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
    
    def get_config(self) -> Dict[str, Any]:
        """현재 설정 전체 반환"""
        return self.config
    
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
    
    def save_config(self, config_data: Dict[str, Any] = None) -> bool:
        """설정 파일 저장"""
        try:
            # 설정 데이터가 제공되면 현재 설정을 업데이트
            if config_data is not None:
                self.config = config_data
            
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
CONFIG_MANAGER = ConfigManager()
config_manager = CONFIG_MANAGER  # 이전 버전 호환성 