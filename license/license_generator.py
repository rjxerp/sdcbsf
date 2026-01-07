#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册码生成与验证模块
使用RSA非对称加密算法生成和验证注册码
"""

import rsa
import json
import base64
import hashlib
import time
from datetime import datetime, timedelta

class LicenseType:
    """授权类型枚举"""
    TRIAL = "trial"          # 试用版
    STANDARD = "standard"    # 标准版
    ENTERPRISE = "enterprise"  # 企业版

class LicenseGenerator:
    """注册码生成与验证类"""
    
    def __init__(self, private_key=None, public_key=None):
        """
        初始化注册码生成器
        :param private_key: RSA私钥，用于生成注册码
        :param public_key: RSA公钥，用于验证注册码
        """
        self.private_key = private_key
        self.public_key = public_key
    
    def generate_keypair(self, bits=2048):
        """
        生成RSA密钥对
        :param bits: 密钥长度，默认为2048位
        :return: (私钥, 公钥) 元组
        """
        self.public_key, self.private_key = rsa.newkeys(bits)
        return self.private_key, self.public_key
    
    def save_key_to_file(self, key, filename):
        """
        将密钥保存到文件
        :param key: 要保存的密钥
        :param filename: 文件名
        """
        with open(filename, 'wb') as f:
            f.write(key.save_pkcs1())
    
    def load_key_from_file(self, filename, is_private=True):
        """
        从文件加载密钥
        :param filename: 文件名
        :param is_private: 是否为私钥
        :return: 加载的密钥
        """
        with open(filename, 'rb') as f:
            key_data = f.read()
        
        if is_private:
            key = rsa.PrivateKey.load_pkcs1(key_data)
            self.private_key = key
        else:
            key = rsa.PublicKey.load_pkcs1(key_data)
            self.public_key = key
        
        return key
    
    def generate_license(self, license_type, machine_id, duration_days, features=None):
        """
        生成注册码
        :param license_type: 授权类型（trial, standard, enterprise）
        :param machine_id: 机器唯一标识
        :param duration_days: 有效期天数
        :param features: 功能权限列表，默认为空
        :return: 生成的注册码字符串
        """
        if not self.private_key:
            raise ValueError("私钥未设置，无法生成注册码")
        
        # 生成注册信息
        license_info = {
            "type": license_type,
            "machine_id": machine_id,
            "issued_at": int(time.time()),
            "expires_at": int(time.time()) + (duration_days * 86400),
            "features": features or [],
            "version": "1.0"
        }
        
        # 将注册信息转换为JSON字符串
        license_json = json.dumps(license_info, sort_keys=True)
        
        # 使用私钥签名
        signature = rsa.sign(license_json.encode('utf-8'), self.private_key, 'SHA-256')
        
        # 组合注册信息和签名
        license_data = {
            "info": license_info,
            "signature": base64.b64encode(signature).decode('utf-8')
        }
        
        # 将组合数据转换为JSON并进行Base64编码
        license_str = json.dumps(license_data, sort_keys=True)
        license_b64 = base64.b64encode(license_str.encode('utf-8')).decode('utf-8')
        
        # 格式化注册码，每8个字符一组
        formatted_license = '-'.join([license_b64[i:i+8] for i in range(0, len(license_b64), 8)])
        
        return formatted_license
    
    def validate_license(self, license_key, machine_id):
        """
        验证注册码
        :param license_key: 注册码字符串
        :param machine_id: 当前机器的唯一标识
        :return: (验证结果, 错误信息, 注册信息)
        """
        if not self.public_key:
            raise ValueError("公钥未设置，无法验证注册码")
        
        try:
            # 预处理注册码，处理复制粘贴可能出现的问题
            license_key = license_key.strip()  # 去除前后空格、换行符
            license_key = license_key.replace(' ', '')  # 去除空格
            license_key = license_key.replace('\n', '')  # 去除换行符
            license_key = license_key.replace('\r', '')  # 去除回车符
            license_key = license_key.replace('-', '')  # 去除连字符
            
            # Base64解码
            license_str = base64.b64decode(license_key).decode('utf-8')
            license_data = json.loads(license_str)
            
            # 提取注册信息和签名
            license_info = license_data["info"]
            signature = base64.b64decode(license_data["signature"])
            
            # 将注册信息转换为JSON字符串（用于验证签名）
            license_json = json.dumps(license_info, sort_keys=True)
            
            # 验证签名
            rsa.verify(license_json.encode('utf-8'), signature, self.public_key)
            
            # 检查机器ID是否匹配
            if license_info["machine_id"] != machine_id:
                return False, "注册码与当前设备不匹配", None
            
            # 检查是否过期
            current_time = int(time.time())
            if current_time > license_info["expires_at"]:
                return False, "注册码已过期", None
            
            # 检查授权类型是否有效
            valid_types = [LicenseType.TRIAL, LicenseType.STANDARD, LicenseType.ENTERPRISE]
            if license_info["type"] not in valid_types:
                return False, "无效的授权类型", None
            
            # 验证通过
            return True, "注册码验证成功", license_info
            
        except rsa.VerificationError:
            return False, "注册码无效或已被篡改", None
        except (base64.binascii.Error, json.JSONDecodeError):
            return False, "注册码格式错误", None
        except Exception as e:
            return False, f"验证过程发生错误: {str(e)}", None
    
    def parse_license(self, license_key):
        """
        解析注册码信息（不验证签名）
        :param license_key: 注册码字符串
        :return: 注册信息字典，解析失败返回None
        """
        try:
            # 预处理注册码，处理复制粘贴可能出现的问题
            license_key = license_key.strip()  # 去除前后空格、换行符
            license_key = license_key.replace(' ', '')  # 去除空格
            license_key = license_key.replace('\n', '')  # 去除换行符
            license_key = license_key.replace('\r', '')  # 去除回车符
            license_key = license_key.replace('-', '')  # 去除连字符
            
            # Base64解码
            license_str = base64.b64decode(license_key).decode('utf-8')
            license_data = json.loads(license_str)
            
            return license_data["info"]
        except Exception as e:
            print(f"解析注册码失败: {e}")
            return None
    
    def get_license_info(self, license_key):
        """
        获取注册码详细信息
        :param license_key: 注册码字符串
        :return: 格式化的注册信息
        """
        license_info = self.parse_license(license_key)
        if not license_info:
            return None
        
        # 格式化有效期
        issued_at = datetime.fromtimestamp(license_info["issued_at"])
        expires_at = datetime.fromtimestamp(license_info["expires_at"])
        
        info = {
            "授权类型": self._get_license_type_name(license_info["type"]),
            "颁发时间": issued_at.strftime("%Y-%m-%d %H:%M:%S"),
            "到期时间": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            "有效期": f"{(expires_at - issued_at).days} 天",
            "功能权限": ", ".join(license_info["features"]) if license_info["features"] else "无",
            "版本": license_info["version"]
        }
        
        return info
    
    def _get_license_type_name(self, license_type):
        """
        获取授权类型的中文名称
        :param license_type: 授权类型字符串
        :return: 中文名称
        """
        type_map = {
            LicenseType.TRIAL: "试用版",
            LicenseType.STANDARD: "标准版",
            LicenseType.ENTERPRISE: "企业版"
        }
        return type_map.get(license_type, "未知类型")
    
    def generate_trial_license(self, machine_id, days=30):
        """
        生成试用版注册码
        :param machine_id: 机器唯一标识
        :param days: 试用期天数，默认为30天
        :return: 注册码字符串
        """
        return self.generate_license(
            license_type=LicenseType.TRIAL,
            machine_id=machine_id,
            duration_days=days,
            features=["basic_function"]
        )
    
    def generate_standard_license(self, machine_id, days=365):
        """
        生成标准版注册码
        :param machine_id: 机器唯一标识
        :param days: 有效期天数，默认为365天
        :return: 注册码字符串
        """
        return self.generate_license(
            license_type=LicenseType.STANDARD,
            machine_id=machine_id,
            duration_days=days,
            features=["basic_function", "advanced_function", "report_function"]
        )
    
    def generate_enterprise_license(self, machine_id, days=365*3):
        """
        生成企业版注册码
        :param machine_id: 机器唯一标识
        :param days: 有效期天数，默认为3年
        :return: 注册码字符串
        """
        return self.generate_license(
            license_type=LicenseType.ENTERPRISE,
            machine_id=machine_id,
            duration_days=days,
            features=["basic_function", "advanced_function", "report_function", "admin_function", "api_access"]
        )

if __name__ == "__main__":
    # 测试注册码生成与验证
    generator = LicenseGenerator()
    
    # 生成密钥对
    private_key, public_key = generator.generate_keypair()
    print("密钥对生成成功")
    
    # 保存密钥到文件（实际使用时应该安全存储）
    # generator.save_key_to_file(private_key, 'private.pem')
    # generator.save_key_to_file(public_key, 'public.pem')
    
    # 模拟机器ID
    machine_id = "test_machine_id_123456"
    
    # 生成试用版注册码
    trial_license = generator.generate_trial_license(machine_id)
    print(f"试用版注册码: {trial_license}")
    
    # 生成标准版注册码
    standard_license = generator.generate_standard_license(machine_id)
    print(f"标准版注册码: {standard_license}")
    
    # 生成企业版注册码
    enterprise_license = generator.generate_enterprise_license(machine_id)
    print(f"企业版注册码: {enterprise_license}")
    
    # 验证注册码
    for license_key in [trial_license, standard_license, enterprise_license]:
        print(f"\n验证注册码: {license_key}")
        result, msg, info = generator.validate_license(license_key, machine_id)
        print(f"验证结果: {'成功' if result else '失败'}")
        print(f"消息: {msg}")
        if info:
            print(f"注册信息: {info}")
    
    # 测试无效注册码
    invalid_license = trial_license[:-1] + 'X'  # 篡改注册码
    print(f"\n验证无效注册码: {invalid_license}")
    result, msg, info = generator.validate_license(invalid_license, machine_id)
    print(f"验证结果: {'成功' if result else '失败'}")
    print(f"消息: {msg}")