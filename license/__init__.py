#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册系统包初始化文件
"""

from .license_manager import LicenseManager
from .license_generator import LicenseType

__all__ = ['LicenseManager', 'LicenseType']
__version__ = '1.0.0'