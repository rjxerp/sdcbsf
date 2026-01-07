#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
租户模型
负责处理租户相关的数据操作
"""

from database.db_manager import get_db

class Tenant:
    """租户类"""
    
    def __init__(self, id=None, name='', type='办公室', address='', contact_person='', phone='', email='', deactivated=False, create_time=None, update_time=None):
        """
        初始化租户对象
        :param id: 租户ID
        :param name: 租户名称
        :param type: 租户类型（办公室/门面）
        :param address: 地址
        :param contact_person: 联系人
        :param phone: 联系电话
        :param email: 邮箱
        :param deactivated: 是否停用
        :param create_time: 创建时间
        :param update_time: 更新时间
        """
        self.id = id
        self.name = name
        self.type = type
        self.address = address
        self.contact_person = contact_person
        self.phone = phone
        self.email = email
        self.deactivated = deactivated
        self.create_time = create_time
        self.update_time = update_time
    
    def save(self):
        """
        保存租户信息
        如果是新租户则插入，否则更新
        :return: 是否保存成功
        """
        db = get_db()
        
        if self.id:
            # 更新现有租户
            data = {
                'name': self.name,
                'type': self.type,
                'address': self.address,
                'contact_person': self.contact_person,
                'phone': self.phone,
                'email': self.email,
                'deactivated': 1 if self.deactivated else 0
            }
            result = db.update('tenants', data, f'id = {self.id}')
        else:
            # 插入新租户
            data = {
                'name': self.name,
                'type': self.type,
                'address': self.address,
                'contact_person': self.contact_person,
                'phone': self.phone,
                'email': self.email,
                'deactivated': 1 if self.deactivated else 0
            }
            self.id = db.insert('tenants', data)
            result = self.id is not None
        
        return result
    
    def delete(self):
        """
        删除租户
        先检查该租户是否存在关联的抄表记录，若存在则阻止删除
        :return: 是否删除成功
        """
        if not self.id:
            return False
        
        db = get_db()
        
        # 前置检查：查询该租户是否存在关联的抄表记录
        # 1. 先查询该租户关联的所有水电表
        sql = "SELECT id FROM meters WHERE tenant_id = ?"
        meters = db.fetch_all(sql, (self.id,))
        
        if meters:
            # 2. 检查这些水电表是否有抄表记录
            meter_ids = [str(meter[0]) for meter in meters]
            sql = f"SELECT COUNT(*) FROM meter_readings WHERE meter_id IN ({', '.join(meter_ids)})"
            result = db.fetch_one(sql)
            
            if result and result[0] > 0:
                # 存在关联的抄表记录，阻止删除
                return False
        
        # 没有关联的抄表记录，可以删除
        return db.delete('tenants', f'id = {self.id}')
    
    @classmethod
    def get_by_id(cls, tenant_id):
        """
        根据ID获取租户
        :param tenant_id: 租户ID
        :return: 租户对象或None
        """
        db = get_db()
        sql = "SELECT id, name, type, address, contact_person, phone, email, deactivated, create_time, update_time FROM tenants WHERE id = ?"
        result = db.fetch_one(sql, (tenant_id,))
        
        if result:
            return cls(id=result[0], name=result[1], type=result[2], address=result[3], 
                      contact_person=result[4], phone=result[5], email=result[6], 
                      deactivated=bool(result[7]), create_time=result[8], update_time=result[9])
        return None
    
    @classmethod
    def get_all(cls, filters=None):
        """
        获取所有租户
        :param filters: 过滤条件
        :return: 租户列表
        """
        db = get_db()
        sql = "SELECT id, name, type, address, contact_person, phone, email, deactivated, create_time, update_time FROM tenants"
        params = []
        
        if filters:
            where_clauses = []
            if 'name' in filters and filters['name']:
                where_clauses.append("name LIKE ?")
                params.append(f"%{filters['name']}%")
            if 'type' in filters and filters['type']:
                where_clauses.append("type = ?")
                params.append(filters['type'])
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
        
        sql += " ORDER BY name"
        results = db.fetch_all(sql, tuple(params))
        
        return [cls(id=result[0], name=result[1], type=result[2], address=result[3], 
                  contact_person=result[4], phone=result[5], email=result[6], 
                  deactivated=bool(result[7]), create_time=result[8], update_time=result[9]) for result in results]
    
    @classmethod
    def search(cls, keyword):
        """
        根据关键字搜索租户
        :param keyword: 搜索关键字
        :return: 租户列表
        """
        db = get_db()
        sql = """
        SELECT id, name, type, address, contact_person, phone, email, deactivated, create_time, update_time FROM tenants 
        WHERE name LIKE ? OR address LIKE ? OR contact_person LIKE ? OR phone LIKE ?
        ORDER BY name
        """
        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        results = db.fetch_all(sql, params)
        
        return [cls(id=result[0], name=result[1], type=result[2], address=result[3], 
                  contact_person=result[4], phone=result[5], email=result[6], 
                  deactivated=bool(result[7]), create_time=result[8], update_time=result[9]) for result in results]
