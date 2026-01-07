#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块
负责处理数据库连接、查询和基本操作
"""

import sqlite3
from datetime import datetime

class DBManager:
    """数据库管理类"""
    
    def __init__(self, db_path='water_electricity.db'):
        """
        初始化数据库连接
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            # 启用外键约束
            self.cursor.execute("PRAGMA foreign_keys = ON;")
            # 自动更新表结构
            self.auto_update_schema()
        except sqlite3.Error as e:
            print(f"数据库连接失败: {e}")
    
    def auto_update_schema(self):
        """
        自动更新数据库表结构
        为meter_readings表添加remark字段（如果不存在）
        """
        try:
            # 检查meter_readings表是否有remark字段
            self.cursor.execute("PRAGMA table_info(meter_readings);")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'remark' not in columns:
                # 添加remark字段
                self.cursor.execute("ALTER TABLE meter_readings ADD COLUMN remark TEXT DEFAULT '';")
                self.conn.commit()
                print("数据库表结构已更新：为meter_readings表添加了remark字段")
        except sqlite3.Error as e:
            print(f"自动更新表结构失败: {e}")
            self.conn.rollback()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def execute(self, sql, params=None):
        """
        执行SQL语句
        :param sql: SQL语句
        :param params: SQL参数
        :return: 执行结果
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"SQL执行失败: {e}\nSQL: {sql}\nParams: {params}")
            self.conn.rollback()
            return False
    
    def fetch_one(self, sql, params=None):
        """
        获取单条查询结果
        :param sql: SQL查询语句
        :param params: SQL参数
        :return: 查询结果
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"查询失败: {e}\nSQL: {sql}\nParams: {params}")
            return None
    
    def fetch_all(self, sql, params=None):
        """
        获取所有查询结果
        :param sql: SQL查询语句
        :param params: SQL参数
        :return: 查询结果列表
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"查询失败: {e}\nSQL: {sql}\nParams: {params}")
            return []
    
    def fetch_many(self, sql, size, params=None):
        """
        获取指定数量的查询结果
        :param sql: SQL查询语句
        :param size: 结果数量
        :param params: SQL参数
        :return: 查询结果列表
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return self.cursor.fetchmany(size)
        except sqlite3.Error as e:
            print(f"查询失败: {e}\nSQL: {sql}\nParams: {params}")
            return []
    
    def insert(self, table, data):
        """
        插入数据
        :param table: 表名
        :param data: 字典格式的数据
        :return: 插入的ID
        """
        try:
            # 获取表结构，检查是否有create_time和update_time字段
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # 只在表有对应字段时添加时间
            if 'create_time' in columns and 'create_time' not in data:
                data['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if 'update_time' in columns and 'update_time' not in data:
                data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            keys = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
            
            self.cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"插入失败: {e}\nTable: {table}\nData: {data}")
            self.conn.rollback()
            return None
    
    def update(self, table, data, condition):
        """
        更新数据
        :param table: 表名
        :param data: 字典格式的数据
        :param condition: 更新条件
        :return: 是否更新成功
        """
        try:
            # 获取表结构，检查是否有update_time字段
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # 只在表有对应字段时添加时间
            if 'update_time' in columns:
                data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {condition}"
            
            self.cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新失败: {e}\nTable: {table}\nData: {data}\nCondition: {condition}")
            self.conn.rollback()
            return False
    
    def delete(self, table, condition):
        """
        删除数据
        :param table: 表名
        :param condition: 删除条件
        :return: 是否删除成功
        """
        try:
            sql = f"DELETE FROM {table} WHERE {condition}"
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"删除失败: {e}\nTable: {table}\nCondition: {condition}")
            self.conn.rollback()
            return False
    
    def get_last_insert_id(self):
        """
        获取最后插入的ID
        :return: 最后插入的ID
        """
        return self.cursor.lastrowid

# 导入线程本地存储
import threading

# 线程本地存储，用于存储每个线程的数据库连接
thread_local = threading.local()

def get_db():
    """
    获取当前线程的数据库实例
    为每个线程创建一个独立的数据库连接，确保线程安全
    :return: 数据库实例
    """
    if not hasattr(thread_local, "db_manager"):
        thread_local.db_manager = DBManager()
    return thread_local.db_manager