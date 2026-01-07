#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统设置工具
负责处理系统配置的保存和读取
"""

import configparser
import os
from typing import Optional, Dict, Any, Union

class SettingsUtils:
    """系统设置工具类"""
    
    def __init__(self, settings_file: Optional[str] = None):
        """
        初始化系统设置工具
        :param settings_file: 配置文件路径，默认使用系统配置目录
        """
        # 确定配置文件路径
        if settings_file:
            self.settings_file: str = settings_file
        else:
            # 使用项目根目录下的config.ini
            self.settings_file: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.ini")
        
        # 禁用插值功能，避免%Y-%m-%d等格式被视为插值语法
        self.config: configparser.ConfigParser = configparser.ConfigParser(interpolation=None)
        
        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(self.settings_file):
            self._create_default_config()
        
        # 读取配置文件
        self.config.read(self.settings_file, encoding="utf-8")
    
    def _create_default_config(self) -> None:
        """
        创建默认配置文件
        """
        # 默认配置
        default_config: Dict[str, Dict[str, str]] = {
            "reading": {
                "default_reading_day": "25",  # 默认抄表日
                "reading_time_format": "%Y-%m-%d",  # 抄表日期格式
                "max_usage_difference": "200"  # 最大用量差值，用于校验
            },
            "system": {
                "auto_backup": "false",  # 是否自动备份
                "backup_interval_days": "7",  # 自动备份间隔（天）
                "last_backup_date": "",  # 上次备份日期
                "language": "zh_CN"  # 语言设置
            }
        }
        
        # 写入配置文件
        for section, options in default_config.items():
            self.config[section] = options
        
        # 确保配置目录存在
        config_dir: str = os.path.dirname(self.settings_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        with open(self.settings_file, "w", encoding="utf-8") as f:
            self.config.write(f)
    
    def get_setting(self, section: str, option: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取配置项值
        :param section: 配置节
        :param option: 配置项
        :param default: 默认值
        :return: 配置值
        """
        try:
            return self.config[section][option]
        except KeyError:
            return default
    
    def get_int_setting(self, section: str, option: str, default: int = 0) -> int:
        """
        获取整数类型配置项值
        :param section: 配置节
        :param option: 配置项
        :param default: 默认值
        :return: 配置值
        """
        try:
            return self.config.getint(section, option)
        except (KeyError, ValueError):
            return default
    
    def get_float_setting(self, section: str, option: str, default: float = 0.0) -> float:
        """
        获取浮点数类型配置项值
        :param section: 配置节
        :param option: 配置项
        :param default: 默认值
        :return: 配置值
        """
        try:
            return self.config.getfloat(section, option)
        except (KeyError, ValueError):
            return default
    
    def get_boolean_setting(self, section: str, option: str, default: bool = False) -> bool:
        """
        获取布尔类型配置项值
        :param section: 配置节
        :param option: 配置项
        :param default: 默认值
        :return: 配置值
        """
        try:
            return self.config.getboolean(section, option)
        except (KeyError, ValueError):
            return default
    
    def set_setting(self, section: str, option: str, value: Union[str, int, float, bool]) -> None:
        """
        设置配置项值
        :param section: 配置节
        :param option: 配置项
        :param value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        
        # 确保值是字符串类型
        self.config[section][option] = str(value)
        
        # 保存配置文件
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                self.config.write(f)
        except IOError as e:
            raise IOError(f"保存配置文件失败：{str(e)}")
    
    def set_int_setting(self, section: str, option: str, value: int) -> None:
        """
        设置整数类型配置项值
        :param section: 配置节
        :param option: 配置项
        :param value: 配置值
        """
        try:
            int_value = int(value)
            self.set_setting(section, option, str(int_value))
        except ValueError as e:
            raise ValueError(f"无效的整数值：{str(e)}")
    
    def set_float_setting(self, section: str, option: str, value: float) -> None:
        """
        设置浮点数类型配置项值
        :param section: 配置节
        :param option: 配置项
        :param value: 配置值
        """
        try:
            float_value = float(value)
            self.set_setting(section, option, str(float_value))
        except ValueError as e:
            raise ValueError(f"无效的浮点数值：{str(e)}")
    
    def set_boolean_setting(self, section: str, option: str, value: bool) -> None:
        """
        设置布尔类型配置项值
        :param section: 配置节
        :param option: 配置项
        :param value: 配置值
        """
        bool_value = str(value).lower()
        self.set_setting(section, option, bool_value)
    
    def delete_setting(self, section: str, option: str) -> None:
        """
        删除配置项
        :param section: 配置节
        :param option: 配置项
        """
        try:
            if section in self.config and option in self.config[section]:
                del self.config[section][option]
                
                # 保存配置文件
                with open(self.settings_file, "w", encoding="utf-8") as f:
                    self.config.write(f)
        except IOError as e:
            raise IOError(f"删除配置项失败：{str(e)}")
    
    def get_all_settings(self, section: Optional[str] = None) -> Dict[str, Any]:
        """
        获取所有配置项
        :param section: 配置节，None表示获取所有配置
        :return: 配置字典
        """
        if section:
            if section in self.config:
                return dict(self.config[section])
            else:
                return {}
        else:
            result: Dict[str, Any] = {}
            for sec in self.config.sections():
                result[sec] = dict(self.config[sec])
            return result
    
    def validate_config(self) -> bool:
        """
        验证配置的有效性
        :return: 配置是否有效
        """
        try:
            # 检查必要的配置节
            required_sections = ["reading", "system"]
            for section in required_sections:
                if section not in self.config:
                    return False
            
            # 检查必要的配置项
            required_options = {
                "reading": ["default_reading_day", "reading_time_format", "max_usage_difference"],
                "system": ["auto_backup", "backup_interval_days", "language"]
            }
            
            for section, options in required_options.items():
                for option in options:
                    if option not in self.config[section]:
                        return False
            
            return True
        except Exception:
            return False