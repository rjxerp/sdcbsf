#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收费记录模型
负责处理收费信息的录入、查询和管理
"""

from database.db_manager import get_db
from models.charge import Charge

class Payment:
    """收费记录类"""
    
    def __init__(self, id=None, charge_id=None, payment_date='', amount=0, payment_method='现金', payer='', notes='', create_time=None):
        """
        初始化收费记录对象
        :param id: 收费ID
        :param charge_id: 费用ID
        :param payment_date: 收费日期
        :param amount: 收费金额
        :param payment_method: 支付方式
        :param payer: 收费人
        :param notes: 备注
        :param create_time: 创建时间
        """
        self.id = id
        self.charge_id = charge_id
        self.payment_date = payment_date
        self.amount = amount
        self.payment_method = payment_method
        self.payer = payer
        self.notes = notes
        self.create_time = create_time
        self.charge = None  # 关联的费用对象
    
    def save(self):
        """
        保存收费记录
        如果是新记录则插入，否则更新
        :return: 是否保存成功
        """
        db = get_db()
        
        # 确保收费金额四舍五入保留两位小数
        self.amount = round(self.amount, 2)
        
        if self.id:
            # 更新现有记录
            data = {
                'charge_id': self.charge_id,
                'payment_date': self.payment_date,
                'amount': self.amount,
                'payment_method': self.payment_method,
                'payer': self.payer,
                'notes': self.notes
            }
            result = db.update('payments', data, f'id = {self.id}')
        else:
            # 插入新记录
            data = {
                'charge_id': self.charge_id,
                'payment_date': self.payment_date,
                'amount': self.amount,
                'payment_method': self.payment_method,
                'payer': self.payer,
                'notes': self.notes
            }
            self.id = db.insert('payments', data)
            result = self.id is not None
        
        return result
    
    def delete(self):
        """
        删除收费记录
        :return: 是否删除成功
        """
        if not self.id:
            return False
        
        db = get_db()
        return db.delete('payments', f'id = {self.id}')
    
    def load_charge_info(self):
        """
        加载关联的费用信息
        """
        if self.charge_id:
            self.charge = Charge.get_by_id(self.charge_id)
    
    @classmethod
    def get_by_id(cls, payment_id):
        """
        根据ID获取收费记录
        :param payment_id: 收费ID
        :return: 收费记录对象或None
        """
        db = get_db()
        sql = "SELECT * FROM payments WHERE id = ?"
        result = db.fetch_one(sql, (payment_id,))
        
        if result:
            payment = cls(*result)
            payment.load_charge_info()
            return payment
        return None
    
    @classmethod
    def get_by_charge(cls, charge_id):
        """
        根据费用ID获取所有收费记录
        :param charge_id: 费用ID
        :return: 收费记录列表
        """
        db = get_db()
        sql = """
        SELECT * FROM payments 
        WHERE charge_id = ? 
        ORDER BY payment_date DESC
        """
        results = db.fetch_all(sql, (charge_id,))
        
        payments = []
        for result in results:
            payment = cls(*result)
            payment.load_charge_info()
            payments.append(payment)
        
        return payments
    
    @classmethod
    def get_by_month(cls, month):
        """
        根据月份获取所有收费记录
        :param month: 月份（如2023-05）
        :return: 收费记录列表
        """
        db = get_db()
        sql = """
        SELECT p.* FROM payments p
        JOIN charges c ON p.charge_id = c.id
        WHERE c.month = ?
        ORDER BY p.payment_date DESC
        """
        results = db.fetch_all(sql, (month,))
        
        payments = []
        for result in results:
            payment = cls(*result)
            payment.load_charge_info()
            payments.append(payment)
        
        return payments
    
    @classmethod
    def get_total_by_month(cls, month):
        """
        统计指定月份的总收费金额
        :param month: 月份（如2023-05）
        :return: 总收费金额
        """
        db = get_db()
        sql = """
        SELECT COALESCE(SUM(amount), 0) FROM payments p
        JOIN charges c ON p.charge_id = c.id
        WHERE c.month = ?
        """
        result = db.fetch_one(sql, (month,))
        
        return result[0] if result else 0
    
    @classmethod
    def get_all(cls):
        """
        获取所有收费记录
        :return: 收费记录列表
        """
        db = get_db()
        sql = "SELECT * FROM payments ORDER BY payment_date DESC"
        results = db.fetch_all(sql)
        
        payments = []
        for result in results:
            payment = cls(*result)
            payment.load_charge_info()
            payments.append(payment)
        
        return payments
