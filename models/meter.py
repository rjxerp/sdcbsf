#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水电表模型
负责处理水电表相关的数据操作
"""

from database.db_manager import get_db

class Meter:
    """水电表类"""
    
    def __init__(self, id=None, meter_no='', meter_type='水', tenant_id=None, location='', initial_reading=0, status='正常', create_time=None, update_time=None):
        """
        初始化水电表对象
        :param id: 表ID
        :param meter_no: 表编号
        :param meter_type: 表类型（水/电）
        :param tenant_id: 所属租户ID
        :param location: 安装位置
        :param initial_reading: 初始读数
        :param status: 状态（正常/损坏/更换）
        :param create_time: 创建时间
        :param update_time: 更新时间
        """
        self.id = id
        self.meter_no = meter_no
        self.meter_type = meter_type
        self.tenant_id = tenant_id
        self.location = location
        self.initial_reading = initial_reading
        self.status = status
        self.create_time = create_time
        self.update_time = update_time
    
    def save(self):
        """
        保存水电表信息
        如果是新表则插入，否则更新
        :return: 是否保存成功
        """
        db = get_db()
        
        # 确保初始读数四舍五入保留两位小数
        self.initial_reading = round(self.initial_reading, 2)
        
        if self.id:
            # 更新现有表
            data = {
                'meter_no': self.meter_no,
                'meter_type': self.meter_type,
                'tenant_id': self.tenant_id,
                'location': self.location,
                'initial_reading': self.initial_reading,
                'status': self.status
            }
            result = db.update('meters', data, f'id = {self.id}')
        else:
            # 插入新表
            data = {
                'meter_no': self.meter_no,
                'meter_type': self.meter_type,
                'tenant_id': self.tenant_id,
                'location': self.location,
                'initial_reading': self.initial_reading,
                'status': self.status
            }
            self.id = db.insert('meters', data)
            result = self.id is not None
        
        return result
    
    def delete(self):
        """
        删除水电表
        :return: 是否删除成功
        """
        if not self.id:
            return False
        
        db = get_db()
        
        # 检查是否有关联的抄表记录
        sql = "SELECT COUNT(*) FROM meter_readings WHERE meter_id = ?"
        result = db.fetch_one(sql, (self.id,))
        if result and result[0] > 0:
            return False
        
        # 检查是否有关联的费用记录
        sql = "SELECT COUNT(*) FROM charges WHERE meter_id = ?"
        result = db.fetch_one(sql, (self.id,))
        if result and result[0] > 0:
            return False
        
        return db.delete('meters', f'id = {self.id}')
    
    @classmethod
    def get_by_id(cls, meter_id):
        """
        根据ID获取水电表
        :param meter_id: 表ID
        :return: 水电表对象或None
        """
        db = get_db()
        sql = "SELECT * FROM meters WHERE id = ?"
        result = db.fetch_one(sql, (meter_id,))
        
        if result:
            return cls(*result)
        return None
    
    @classmethod
    def get_by_tenant(cls, tenant_id):
        """
        根据租户ID获取所有水电表
        :param tenant_id: 租户ID
        :return: 水电表列表
        """
        db = get_db()
        sql = "SELECT * FROM meters WHERE tenant_id = ? ORDER BY meter_type, meter_no"
        results = db.fetch_all(sql, (tenant_id,))
        
        return [cls(*result) for result in results]
    
    @classmethod
    def get_all(cls, filters=None):
        """
        获取所有水电表
        :param filters: 过滤条件
        :return: 水电表列表
        """
        db = get_db()
        sql = "SELECT * FROM meters"
        params = []
        
        if filters:
            where_clauses = []
            if 'meter_type' in filters and filters['meter_type']:
                where_clauses.append("meter_type = ?")
                params.append(filters['meter_type'])
            if 'status' in filters and filters['status']:
                where_clauses.append("status = ?")
                params.append(filters['status'])
            if 'tenant_id' in filters and filters['tenant_id']:
                where_clauses.append("tenant_id = ?")
                params.append(filters['tenant_id'])
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
        
        sql += " ORDER BY meter_type, meter_no"
        results = db.fetch_all(sql, tuple(params))
        
        return [cls(*result) for result in results]
    
    @classmethod
    def get_last_reading(cls, meter_id):
        """
        获取水电表的上次读数
        :param meter_id: 表ID
        :return: 上次读数或初始读数
        """
        db = get_db()
        # 查找最近的抄表记录
        sql = """
        SELECT current_reading FROM meter_readings 
        WHERE meter_id = ? 
        ORDER BY reading_date DESC 
        LIMIT 1
        """
        result = db.fetch_one(sql, (meter_id,))
        
        if result:
            return result[0]
        
        # 如果没有抄表记录，返回初始读数
        sql = "SELECT initial_reading FROM meters WHERE id = ?"
        result = db.fetch_one(sql, (meter_id,))
        return result[0] if result else 0
    
    @classmethod
    def exists_by_meter_no(cls, meter_no, exclude_id=None):
        """
        检查表编号是否已存在
        :param meter_no: 表编号
        :param exclude_id: 排除的ID（用于编辑时）
        :return: 是否存在
        """
        db = get_db()
        if exclude_id:
            sql = "SELECT COUNT(*) FROM meters WHERE meter_no = ? AND id != ?"
            result = db.fetch_one(sql, (meter_no, exclude_id))
        else:
            sql = "SELECT COUNT(*) FROM meters WHERE meter_no = ?"
            result = db.fetch_one(sql, (meter_no,))
        return result[0] > 0
