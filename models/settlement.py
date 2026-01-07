#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结算记录模型
负责处理与出纳的结算上缴信息
"""

from database.db_manager import get_db

class Settlement:
    """结算记录类"""
    
    def __init__(self, id=None, settle_date='', settle_month='', total_amount=0, cashier='', notes='', create_time=None):
        """
        初始化结算记录对象
        :param id: 结算ID
        :param settle_date: 结算日期
        :param settle_month: 结算月份（如2023-05）
        :param total_amount: 结算总金额
        :param cashier: 出纳姓名
        :param notes: 备注
        :param create_time: 创建时间
        """
        self.id = id
        self.settle_date = settle_date
        self.settle_month = settle_month
        self.total_amount = total_amount
        self.cashier = cashier
        self.notes = notes
        self.create_time = create_time
    
    def save(self):
        """
        保存结算记录
        如果是新记录则插入，否则更新
        :return: 是否保存成功
        """
        db = get_db()
        
        # 确保结算金额四舍五入保留两位小数
        self.total_amount = round(self.total_amount, 2)
        
        if self.id:
            # 更新现有记录
            data = {
                'settle_date': self.settle_date,
                'settle_month': self.settle_month,
                'total_amount': self.total_amount,
                'cashier': self.cashier,
                'notes': self.notes
            }
            result = db.update('settlements', data, f'id = {self.id}')
        else:
            # 插入新记录
            data = {
                'settle_date': self.settle_date,
                'settle_month': self.settle_month,
                'total_amount': self.total_amount,
                'cashier': self.cashier,
                'notes': self.notes
            }
            self.id = db.insert('settlements', data)
            result = self.id is not None
        
        return result
    
    def delete(self):
        """
        删除结算记录
        :return: 是否删除成功
        """
        if not self.id:
            return False
        
        db = get_db()
        return db.delete('settlements', f'id = {self.id}')
    
    @classmethod
    def get_by_id(cls, settlement_id):
        """
        根据ID获取结算记录
        :param settlement_id: 结算ID
        :return: 结算记录对象或None
        """
        db = get_db()
        sql = "SELECT * FROM settlements WHERE id = ?"
        result = db.fetch_one(sql, (settlement_id,))
        
        if result:
            return cls(*result)
        return None
    
    @classmethod
    def get_by_month(cls, month):
        """
        根据月份获取结算记录
        :param month: 结算月份（如2023-05）
        :return: 结算记录对象或None
        """
        db = get_db()
        sql = "SELECT * FROM settlements WHERE settle_month = ?"
        result = db.fetch_one(sql, (month,))
        
        if result:
            return cls(*result)
        return None
    
    @classmethod
    def get_all(cls, limit=12):
        """
        获取最近的结算记录
        :param limit: 返回记录数量
        :return: 结算记录列表
        """
        db = get_db()
        sql = """
        SELECT * FROM settlements 
        ORDER BY settle_month DESC 
        LIMIT ?
        """
        results = db.fetch_all(sql, (limit,))
        
        return [cls(*result) for result in results]
