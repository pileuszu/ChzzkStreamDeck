#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네온 오버레이 메인 실행 파일
통합된 시스템 시작
"""

import os
import sys

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    from unified_server import main
    main() 