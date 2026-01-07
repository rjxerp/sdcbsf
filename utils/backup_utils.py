#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据备份与恢复工具
负责处理数据库的备份和恢复操作
"""

import os
import shutil
import datetime

class BackupUtils:
    """数据备份与恢复工具类"""
    
    @staticmethod
    def backup_database(db_path, backup_dir=None):
        """
        备份数据库
        :param db_path: 数据库文件路径
        :param backup_dir: 备份目录，默认为当前目录下的backup文件夹
        :return: 备份文件路径或None
        """
        if not os.path.exists(db_path):
            return None
        
        # 设置默认备份目录
        if not backup_dir:
            backup_dir = os.path.join(os.path.dirname(db_path), "backup")
        
        # 创建备份目录
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # 生成备份文件名
        backup_filename = f"water_electricity_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            # 复制数据库文件到备份目录
            shutil.copy2(db_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"备份数据库失败: {str(e)}")
            return None
    
    @staticmethod
    def restore_database(backup_path, target_db_path):
        """
        从备份恢复数据库
        :param backup_path: 备份文件路径
        :param target_db_path: 目标数据库路径
        :return: 是否恢复成功
        """
        if not os.path.exists(backup_path):
            return False
        
        try:
            # 复制备份文件到目标路径
            shutil.copy2(backup_path, target_db_path)
            return True
        except Exception as e:
            print(f"恢复数据库失败: {str(e)}")
            return False
    
    @staticmethod
    def get_backup_list(backup_dir):
        """
        获取备份文件列表
        :param backup_dir: 备份目录
        :return: 备份文件列表，按日期倒序排列
        """
        if not os.path.exists(backup_dir):
            return []
        
        # 获取所有备份文件
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith(".db") and f.startswith("water_electricity_")]
        
        # 按日期倒序排列
        backup_files.sort(reverse=True, key=lambda x: x.replace("water_electricity_", "").replace(".db", ""))
        
        return backup_files
    
    @staticmethod
    def get_backup_info(backup_file):
        """
        获取备份文件的信息
        :param backup_file: 备份文件名
        :return: 备份日期时间
        """
        try:
            # 提取日期时间字符串
            datetime_str = backup_file.replace("water_electricity_", "").replace(".db", "")
            # 解析为datetime对象
            backup_datetime = datetime.datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
            return backup_datetime
        except Exception as e:
            print(f"解析备份文件信息失败: {str(e)}")
            return None