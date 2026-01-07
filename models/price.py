#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格模型
负责处理水电费价格相关的数据操作
"""

from database.db_manager import get_db

class Price:
    """价格类"""
    
    def __init__(self, id=None, resource_type='水', tenant_type='全部', price=0, start_date='', end_date=None, create_time=None):
        """
        初始化价格对象
        :param id: 价格ID
        :param resource_type: 资源类型（水/电）
        :param tenant_type: 租户类型（办公室/门面/全部）
        :param price: 单价
        :param start_date: 生效开始日期
        :param end_date: 生效结束日期
        :param create_time: 创建时间
        """
        self.id = id
        self.resource_type = resource_type
        self.tenant_type = tenant_type
        self.price = price
        self.start_date = start_date
        self.end_date = end_date
        self.create_time = create_time
    
    def save(self):
        """
        保存价格信息
        如果是新价格则插入，否则更新
        :return: 是否保存成功
        """
        db = get_db()
        
        # 确保价格四舍五入保留两位小数
        self.price = round(self.price, 2)
        
        if self.id:
            # 更新现有价格
            data = {
                'resource_type': self.resource_type,
                'tenant_type': self.tenant_type,
                'price': self.price,
                'start_date': self.start_date,
                'end_date': self.end_date
            }
            result = db.update('prices', data, f'id = {self.id}')
        else:
            # 插入新价格
            data = {
                'resource_type': self.resource_type,
                'tenant_type': self.tenant_type,
                'price': self.price,
                'start_date': self.start_date,
                'end_date': self.end_date
            }
            self.id = db.insert('prices', data)
            result = self.id is not None
        
        return result
    
    def delete(self):
        """
        删除价格
        :return: 是否删除成功
        """
        if not self.id:
            return False
        
        db = get_db()
        return db.delete('prices', f'id = {self.id}')
    
    @classmethod
    def get_by_id(cls, price_id):
        """
        根据ID获取价格
        :param price_id: 价格ID
        :return: 价格对象或None
        """
        db = get_db()
        sql = "SELECT * FROM prices WHERE id = ?"
        result = db.fetch_one(sql, (price_id,))
        
        if result:
            return cls(*result)
        return None
    
    @classmethod
    def get_current_price(cls, resource_type, tenant_type):
        """
        获取当前有效价格
        :param resource_type: 资源类型（水/电）
        :param tenant_type: 租户类型（办公室/门面）
        :return: 价格对象或None
        """
        db = get_db()
        
        # 先查找特定租户类型的价格
        sql = """
        SELECT * FROM prices 
        WHERE resource_type = ? AND tenant_type = ? AND end_date IS NULL 
        ORDER BY start_date DESC 
        LIMIT 1
        """
        result = db.fetch_one(sql, (resource_type, tenant_type))
        
        if result:
            return cls(*result)
        
        # 如果没有特定租户类型的价格，查找通用价格
        sql = """
        SELECT * FROM prices 
        WHERE resource_type = ? AND tenant_type = '全部' AND end_date IS NULL 
        ORDER BY start_date DESC 
        LIMIT 1
        """
        result = db.fetch_one(sql, (resource_type,))
        
        if result:
            return cls(*result)
        
        return None
    
    @classmethod
    def get_all(cls, filters=None):
        """
        获取所有价格
        :param filters: 过滤条件
        :return: 价格列表
        """
        db = get_db()
        sql = "SELECT * FROM prices"
        params = []
        
        if filters:
            where_clauses = []
            if 'resource_type' in filters and filters['resource_type']:
                where_clauses.append("resource_type = ?")
                params.append(filters['resource_type'])
            if 'tenant_type' in filters and filters['tenant_type']:
                where_clauses.append("tenant_type = ?")
                params.append(filters['tenant_type'])
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
        
        sql += " ORDER BY resource_type, tenant_type, start_date DESC"
        results = db.fetch_all(sql, tuple(params))
        
        return [cls(*result) for result in results]
