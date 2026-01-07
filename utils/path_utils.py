#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径处理工具模块
负责统一处理项目中的路径问题，避免重复代码
"""

import sys
import os
from typing import List

# 项目根目录
ROOT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录添加到系统路径
def add_project_root_to_path() -> None:
    """
    将项目根目录添加到系统路径，解决模块导入问题
    """
    if ROOT_DIR not in sys.path:
        sys.path.append(ROOT_DIR)

# 初始化时自动添加项目根目录到系统路径
add_project_root_to_path()
