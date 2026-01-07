#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册系统核心管理类
用于统一管理注册流程、状态检查和验证
"""

import time
from datetime import datetime
from .hardware_info import HardwareInfo
from .license_generator import LicenseGenerator, LicenseType
from .license_store import LicenseStore

class LicenseManager:
    """注册系统核心管理类"""
    
    def __init__(self, public_key_path=None):
        """
        初始化注册管理器
        :param public_key_path: RSA公钥文件路径
        """
        # 初始化各模块
        self.hardware = HardwareInfo()
        self.generator = LicenseGenerator()
        self.store = LicenseStore()
        
        # 生成默认密钥对（用于测试和试用版生成）
        try:
            self.generator.generate_keypair()
        except Exception as e:
            print(f"生成默认密钥对失败: {e}")
        
        # 加载公钥（用于验证注册码）
        if public_key_path and public_key_path.exists():
            self.generator.load_key_from_file(public_key_path, is_private=False)
        
        # 生成机器唯一标识
        self.machine_id = self.hardware.get_unique_machine_id()
        
        # 加载注册信息
        self.license_info = self.store.load_license(self.machine_id)
        
        # 注册状态
        self.is_registered = self._check_registration_status()
    
    def _check_registration_status(self):
        """
        检查注册状态
        :return: 是否已注册
        """
        if not self.license_info:
            return False
        
        # 检查注册码是否过期
        current_time = int(time.time())
        if current_time > self.license_info.get("expires_at", 0):
            return False
        
        # 检查机器ID是否匹配
        if self.license_info.get("machine_id") != self.machine_id:
            return False
        
        return True
    
    def register_license(self, license_key):
        """
        注册新的注册码
        :param license_key: 注册码字符串
        :return: (注册结果, 消息, 注册信息)
        """
        try:
            # 验证注册码
            result, msg, info = self.generator.validate_license(license_key, self.machine_id)
            
            if result:
                # 保存注册信息
                save_result = self.store.save_license(info, self.machine_id)
                if save_result:
                    # 更新注册状态
                    self.license_info = info
                    self.is_registered = True
                    return True, "注册成功", info
                else:
                    return False, "保存注册信息失败", None
            else:
                return False, msg, None
        except Exception as e:
            return False, f"注册过程发生错误: {str(e)}", None
    
    def get_registration_status(self):
        """
        获取注册状态
        :return: 注册状态字典
        """
        status = {
            "is_registered": self.is_registered,
            "machine_id": self.machine_id,
            "license_info": self.license_info
        }
        
        if self.is_registered and self.license_info:
            # 计算剩余天数
            current_time = int(time.time())
            expires_at = self.license_info.get("expires_at", 0)
            remaining_days = max(0, (expires_at - current_time) // 86400)
            
            status.update({
                "license_type": self.license_info.get("type"),
                "license_type_name": self.generator._get_license_type_name(self.license_info.get("type")),
                "issued_at": self.license_info.get("issued_at"),
                "expires_at": expires_at,
                "remaining_days": remaining_days,
                "features": self.license_info.get("features", [])
            })
        
        return status
    
    def get_license_display_info(self):
        """
        获取用于显示的注册信息
        :return: 格式化的注册信息字符串
        """
        status = self.get_registration_status()
        
        if not status["is_registered"]:
            return "[未注册]"
        
        license_type = status["license_type_name"]
        expires_at = datetime.fromtimestamp(status["expires_at"])
        expires_str = expires_at.strftime("%Y-%m-%d")
        
        return f"[{license_type} - 有效期至 {expires_str}]"
    
    def unregister(self):
        """
        注销注册
        :return: 注销结果
        """
        result = self.store.delete_license()
        if result:
            self.license_info = None
            self.is_registered = False
        return result
    
    def check_feature_access(self, feature_name):
        """
        检查是否有权限访问特定功能
        :param feature_name: 功能名称
        :return: 是否有权限
        """
        if not self.is_registered or not self.license_info:
            return False
        
        features = self.license_info.get("features", [])
        return feature_name in features
    
    def get_remaining_days(self):
        """
        获取剩余有效期天数
        :return: 剩余天数，如果未注册返回0
        """
        if not self.is_registered or not self.license_info:
            return 0
        
        current_time = int(time.time())
        expires_at = self.license_info.get("expires_at", 0)
        remaining_days = max(0, (expires_at - current_time) // 86400)
        
        return remaining_days
    
    def is_license_expired(self):
        """
        检查注册码是否过期
        :return: 是否过期
        """
        if not self.license_info:
            return True
        
        current_time = int(time.time())
        expires_at = self.license_info.get("expires_at", 0)
        return current_time > expires_at
    
    def refresh_license(self):
        """
        刷新注册信息
        :return: 刷新后的注册状态
        """
        self.license_info = self.store.load_license(self.machine_id)
        self.is_registered = self._check_registration_status()
        return self.is_registered
    
    def get_machine_info(self):
        """
        获取机器信息
        :return: 机器信息字典
        """
        return {
            "machine_id": self.machine_id,
            "motherboard_serial": self.hardware.get_motherboard_serial(),
            "mac_address": self.hardware.get_mac_address(),
            "cpu_info": self.hardware.get_cpu_info(),
            "disk_serial": self.hardware.get_disk_serial()
        }
    
    def generate_trial_license(self, days=30):
        """
        生成试用版注册码（仅用于测试）
        :param days: 试用期天数
        :return: 试用版注册码
        """
        # 注意：实际使用时应移除此方法或添加严格的权限控制
        return self.generator.generate_trial_license(self.machine_id, days)
    
    def get_license_path(self):
        """
        获取注册信息存储路径
        :return: 存储路径字符串
        """
        return self.store.get_store_path()