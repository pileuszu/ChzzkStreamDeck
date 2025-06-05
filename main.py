#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
스트리밍 컨트롤 센터 메인 실행 파일
"""

import os
import sys

# main 디렉토리를 Python 경로에 추가
main_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main')
sys.path.insert(0, main_dir)

if __name__ == "__main__":
    from unified_server import main
    main() 