#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册信息加密存储模块
用于安全地存储和读取注册信息
"""

import os
import json
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import platform

class LicenseStore:
    """注册信息加密存储类"""
    
    def __init__(self, store_path=None):
        """
        初始化注册信息存储类
        :param store_path: 注册信息存储路径，默认为空
        """
        self.system = platform.system()
        self.store_path = store_path or self._get_default_store_path()
        self._backend = default_backend()
    
    def _get_default_store_path(self):
        """
        获取默认的注册信息存储路径
        :return: 默认存储路径
        """
        if self.system == "Windows":
            # Windows系统存储在AppData目录
            appdata = os.environ.get("APPDATA")
            return os.path.join(appdata, "WaterElectricityMeter", "license.dat")
        elif self.system == "Linux":
            # Linux系统存储在用户主目录的隐藏文件夹
            home = os.path.expanduser("~")
            return os.path.join(home, ".water_electricity_meter", "license.dat")
        elif self.system == "Darwin":
            # macOS系统存储在Library/Application Support目录
            home = os.path.expanduser("~")
            return os.path.join(home, "Library", "Application Support", "WaterElectricityMeter", "license.dat")
        else:
            # 其他系统存储在当前目录
            return os.path.join(os.getcwd(), ".license.dat")
    
    def _generate_key(self, passphrase, salt):
        """
        使用密码和盐生成加密密钥
        :param passphrase: 密码短语
        :param salt: 盐值
        :return: 生成的密钥
        """
        # 使用SHA256哈希算法生成32字节的密钥
        key_material = passphrase + salt
        key = hashlib.sha256(key_material.encode('utf-8')).digest()
        return key
    
    def _encrypt_data(self, data, passphrase):
        """
        加密数据
        :param data: 要加密的数据
        :param passphrase: 加密密码
        :return: 加密后的数据（盐值 + IV + 密文）
        """
        # 生成随机盐值
        salt = os.urandom(16)
        
        # 生成密钥
        key = self._generate_key(passphrase, salt.decode('latin-1'))
        
        # 生成随机IV
        iv = os.urandom(16)
        
        # 创建AES密码器
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self._backend)
        encryptor = cipher.encryptor()
        
        # 对数据进行填充
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data.encode('utf-8')) + padder.finalize()
        
        # 加密数据
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # 组合盐值、IV和密文
        encrypted_data = salt + iv + ciphertext
        
        # Base64编码
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def _decrypt_data(self, encrypted_data, passphrase):
        """
        解密数据
        :param encrypted_data: 加密的数据
        :param passphrase: 解密密码
        :return: 解密后的数据
        """
        # Base64解码
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # 提取盐值、IV和密文
        salt = encrypted_bytes[:16]
        iv = encrypted_bytes[16:32]
        ciphertext = encrypted_bytes[32:]
        
        # 生成密钥
        key = self._generate_key(passphrase, salt.decode('latin-1'))
        
        # 创建AES密码器
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self._backend)
        decryptor = cipher.decryptor()
        
        # 解密数据
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 去除填充
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data.decode('utf-8')
    
    def save_license(self, license_info, machine_id):
        """
        保存注册信息
        :param license_info: 注册信息字典
        :param machine_id: 机器唯一标识（用于生成加密密码）
        :return: 保存是否成功
        """
        try:
            # 确保存储目录存在
            store_dir = os.path.dirname(self.store_path)
            if not os.path.exists(store_dir):
                os.makedirs(store_dir, exist_ok=True)
            
            # 使用机器ID作为加密密码
            passphrase = machine_id[:16]  # 取前16个字符作为密码
            
            # 将注册信息转换为JSON字符串
            license_json = json.dumps(license_info, ensure_ascii=False, indent=2)
            
            # 加密注册信息
            encrypted_license = self._encrypt_data(license_json, passphrase)
            
            # 保存到文件
            with open(self.store_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_license)
            
            return True
        except Exception as e:
            print(f"保存注册信息失败: {e}")
            return False
    
    def load_license(self, machine_id):
        """
        加载注册信息
        :param machine_id: 机器唯一标识（用于生成解密密码）
        :return: 解密后的注册信息字典，加载失败返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(self.store_path):
                return None
            
            # 使用机器ID作为解密密码
            passphrase = machine_id[:16]  # 取前16个字符作为密码
            
            # 读取加密数据
            with open(self.store_path, 'r', encoding='utf-8') as f:
                encrypted_license = f.read()
            
            # 解密注册信息
            license_json = self._decrypt_data(encrypted_license, passphrase)
            
            # 解析JSON数据
            license_info = json.loads(license_json)
            
            return license_info
        except Exception as e:
            print(f"加载注册信息失败: {e}")
            return None
    
    def delete_license(self):
        """
        删除注册信息
        :return: 删除是否成功
        """
        try:
            # 检查文件是否存在
            if os.path.exists(self.store_path):
                os.remove(self.store_path)
            return True
        except Exception as e:
            print(f"删除注册信息失败: {e}")
            return False
    
    def is_license_exists(self):
        """
        检查注册信息是否存在
        :return: 存在返回True，否则返回False
        """
        return os.path.exists(self.store_path)
    
    def get_store_path(self):
        """
        获取注册信息存储路径
        :return: 存储路径字符串
        """
        return self.store_path

if __name__ == "__main__":
    # 测试注册信息存储
    license_store = LicenseStore()
    
    # 测试数据
    test_license = {
        "type": "enterprise",
        "machine_id": "test_machine_id_123456",
        "issued_at": 1609459200,
        "expires_at": 1640995200,
        "features": ["basic_function", "advanced_function"],
        "version": "1.0"
    }
    
    machine_id = "test_machine_id_123456"
    
    # 保存注册信息
    print(f"保存注册信息到: {license_store.get_store_path()}")
    result = license_store.save_license(test_license, machine_id)
    print(f"保存结果: {'成功' if result else '失败'}")
    
    # 加载注册信息
    loaded_license = license_store.load_license(machine_id)
    print(f"\n加载的注册信息: {loaded_license}")
    
    # 验证加载的数据是否与原数据一致
    if loaded_license == test_license:
        print("\n验证通过: 加载的数据与原数据一致")
    else:
        print("\n验证失败: 加载的数据与原数据不一致")
    
    # 删除注册信息
    delete_result = license_store.delete_license()
    print(f"\n删除注册信息: {'成功' if delete_result else '失败'}")
    
    # 再次加载，验证是否已删除
    loaded_license_after_delete = license_store.load_license(machine_id)
    print(f"删除后加载注册信息: {loaded_license_after_delete}")