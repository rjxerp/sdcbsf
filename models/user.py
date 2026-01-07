#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模型
负责处理用户相关的数据操作
"""

from database.db_manager import get_db

class User:
    """用户类"""
    
    def __init__(self, id=None, username='', password='', role='管理员', status='启用', create_time=None, update_time=None):
        """
        初始化用户对象
        :param id: 用户ID
        :param username: 用户名
        :param password: 密码
        :param role: 角色（管理员/抄表员）
        :param status: 状态（启用/禁用）
        :param create_time: 创建时间
        :param update_time: 更新时间
        """
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.status = status
        self.create_time = create_time
        self.update_time = update_time
    
    def __str__(self):
        """
        字符串表示，返回用户名
        :return: 用户名
        """
        return self.username
    
    def save(self, current_user=None):
        """
        保存用户信息
        如果是新用户则插入，否则更新
        非管理员只能更新自己的信息，且不能修改角色
        :param current_user: 当前登录用户对象，用于权限验证
        :return: 是否保存成功
        """
        db = get_db()
        
        if self.id:
            # 更新现有用户
            # 权限验证：非管理员只能更新自己的信息
            if current_user and current_user.role != '管理员' and current_user.id != self.id:
                return False
            
            # 数据准备
            data = {
                'username': self.username,
                'password': self.password,
                'status': self.status
            }
            
            # 非管理员不能修改角色
            if current_user and current_user.role == '管理员':
                data['role'] = self.role
            
            result = db.update('users', data, f'id = {self.id}')
        else:
            # 插入新用户：只有管理员可以添加新用户
            if current_user and current_user.role != '管理员':
                return False
            
            data = {
                'username': self.username,
                'password': self.password,
                'role': self.role,
                'status': self.status
            }
            self.id = db.insert('users', data)
            result = self.id is not None
        
        return result
    
    def delete(self, current_user=None):
        """
        删除用户
        只有管理员可以删除用户
        :param current_user: 当前登录用户对象，用于权限验证
        :return: 是否删除成功
        """
        if not self.id:
            return False
        
        # 权限验证：只有管理员可以删除用户
        if current_user and current_user.role != '管理员':
            return False
        
        db = get_db()
        return db.delete('users', f'id = {self.id}')
    
    @classmethod
    def get_by_username(cls, username):
        """
        根据用户名获取用户
        :param username: 用户名
        :return: 用户对象或None
        """
        db = get_db()
        sql = "SELECT * FROM users WHERE username = ?"
        result = db.fetch_one(sql, (username,))
        
        if result:
            return cls(*result)
        return None
    
    @classmethod
    def get_all(cls, current_user=None):
        """
        获取所有用户
        非管理员只能获取自己的信息
        :param current_user: 当前登录用户对象，用于权限验证
        :return: 用户列表
        """
        db = get_db()
        
        if current_user and current_user.role != '管理员':
            # 非管理员只能获取自己的信息
            sql = "SELECT * FROM users WHERE id = ? ORDER BY id"
            results = db.fetch_all(sql, (current_user.id,))
        else:
            # 管理员可以获取所有用户信息
            sql = "SELECT * FROM users ORDER BY id"
            results = db.fetch_all(sql)
        
        return [cls(*result) for result in results]
    
    @classmethod
    def get_by_id(cls, user_id, current_user=None):
        """
        根据ID获取用户
        非管理员只能获取自己的信息
        :param user_id: 用户ID
        :param current_user: 当前登录用户对象，用于权限验证
        :return: 用户对象或None
        """
        # 权限验证：非管理员只能获取自己的信息
        if current_user and current_user.role != '管理员' and current_user.id != user_id:
            return None
        
        db = get_db()
        sql = "SELECT * FROM users WHERE id = ?"
        result = db.fetch_one(sql, (user_id,))
        
        if result:
            return cls(*result)
        return None
    
    @classmethod
    def authenticate(cls, username, password):
        """
        用户认证
        :param username: 用户名
        :param password: 密码
        :return: 用户对象或None
        """
        user = cls.get_by_username(username)
        if user and user.password == password and user.status == '启用':
            return user
        return None