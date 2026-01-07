#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抄表记录模型
负责处理抄表数据的录入、查询和管理
"""

from database.db_manager import get_db
from models.meter import Meter

class MeterReading:
    """抄表记录类"""
    
    def __init__(self, id=None, meter_id=None, reading_date='', current_reading=0, previous_reading=0, usage=0, adjustment=0, reader='', remark='', create_time=None):
        """
        初始化抄表记录对象
        :param id: 记录ID
        :param meter_id: 表ID
        :param reading_date: 抄表日期
        :param current_reading: 当前读数
        :param previous_reading: 上次读数
        :param usage: 用量
        :param adjustment: 调整值
        :param reader: 抄表人
        :param remark: 备注
        :param create_time: 创建时间
        """
        self.id = id
        self.meter_id = meter_id
        self.reading_date = reading_date
        self.current_reading = current_reading
        self.previous_reading = previous_reading
        self.usage = usage
        self.adjustment = adjustment
        self.reader = reader
        self.remark = remark
        self.create_time = create_time
        self.meter = None  # 关联的水电表对象
    
    def save(self):
        """
        保存抄表记录
        如果是新记录则插入，否则更新
        :return: 是否保存成功
        """
        db = get_db()
        
        if self.id:
            # 更新现有记录
            data = {
                'meter_id': self.meter_id,
                'reading_date': self.reading_date,
                'current_reading': self.current_reading,
                'previous_reading': self.previous_reading,
                'usage': self.usage,
                'adjustment': self.adjustment,
                'reader': self.reader,
                'remark': self.remark
            }
            result = db.update('meter_readings', data, f'id = {self.id}')
        else:
            # 插入新记录
            data = {
                'meter_id': self.meter_id,
                'reading_date': self.reading_date,
                'current_reading': self.current_reading,
                'previous_reading': self.previous_reading,
                'usage': self.usage,
                'adjustment': self.adjustment,
                'reader': self.reader,
                'remark': self.remark
            }
            self.id = db.insert('meter_readings', data)
            result = self.id is not None
        
        return result
    
    def delete(self):
        """
        删除抄表记录
        :return: 是否删除成功
        """
        if not self.id:
            return False
        
        db = get_db()
        return db.delete('meter_readings', f'id = {self.id}')
    
    def load_meter_info(self):
        """
        加载关联的水电表信息
        """
        if self.meter_id:
            self.meter = Meter.get_by_id(self.meter_id)
    
    @classmethod
    def get_by_id(cls, reading_id):
        """
        根据ID获取抄表记录
        :param reading_id: 记录ID
        :return: 抄表记录对象或None
        """
        db = get_db()
        sql = "SELECT * FROM meter_readings WHERE id = ?"
        result = db.fetch_one(sql, (reading_id,))
        
        if result:
            # 显式指定每个字段的值，避免顺序问题
            reading = cls(
                id=result[0],
                meter_id=result[1],
                reading_date=result[2],
                current_reading=result[3],
                previous_reading=result[4],
                usage=result[5],
                reader=result[6],
                create_time=result[7],
                adjustment=result[8] if len(result) > 8 else 0,
                remark=result[9] if len(result) > 9 else ''
            )
            reading.load_meter_info()
            return reading
        return None
    
    @classmethod
    def get_by_month(cls, month):
        """
        根据月份获取所有抄表记录
        :param month: 月份（如2023-05）
        :return: 抄表记录列表
        """
        db = get_db()
        sql = """
        SELECT mr.* FROM meter_readings mr
        JOIN meters m ON mr.meter_id = m.id
        JOIN tenants t ON m.tenant_id = t.id
        WHERE strftime('%Y-%m', mr.reading_date) = ? 
        ORDER BY strftime('%Y-%m', mr.reading_date) DESC, t.name ASC
        """
        results = db.fetch_all(sql, (month,))
        
        readings = []
        for result in results:
            # 显式指定每个字段的值，避免顺序问题
            reading = cls(
                id=result[0],
                meter_id=result[1],
                reading_date=result[2],
                current_reading=result[3],
                previous_reading=result[4],
                usage=result[5],
                reader=result[6],
                create_time=result[7],
                adjustment=result[8] if len(result) > 8 else 0,
                remark=result[9] if len(result) > 9 else ''
            )
            reading.load_meter_info()
            readings.append(reading)
        
        return readings
    
    @classmethod
    def get_by_meter(cls, meter_id, limit=10):
        """
        根据表ID获取最近的抄表记录
        :param meter_id: 表ID
        :param limit: 返回记录数量
        :return: 抄表记录列表
        """
        db = get_db()
        sql = """
        SELECT * FROM meter_readings 
        WHERE meter_id = ? 
        ORDER BY reading_date DESC 
        LIMIT ?
        """
        results = db.fetch_all(sql, (meter_id, limit))
        
        readings = []
        for result in results:
            # 显式指定每个字段的值，避免顺序问题
            reading = cls(
                id=result[0],
                meter_id=result[1],
                reading_date=result[2],
                current_reading=result[3],
                previous_reading=result[4],
                usage=result[5],
                reader=result[6],
                create_time=result[7],
                adjustment=result[8] if len(result) > 8 else 0,
                remark=result[9] if len(result) > 9 else ''
            )
            reading.load_meter_info()
            readings.append(reading)
        
        return readings
    
    @classmethod
    def calculate_usage(cls, meter_id, current_reading, adjustment=0):
        """
        计算用量
        :param meter_id: 表ID
        :param current_reading: 当前读数
        :param adjustment: 调整值
        :return: (上次读数, 用量)
        """
        previous_reading = Meter.get_last_reading(meter_id)
        usage = round(current_reading - previous_reading + adjustment, 2)
        return previous_reading, usage
    
    @classmethod
    def get_last_reading_date(cls, meter_id):
        """
        获取指定电表的最后一次抄表日期
        :param meter_id: 表ID
        :return: 最后一次抄表日期字符串，如"2023-05-15"，如果没有记录则返回None
        """
        db = get_db()
        sql = """
        SELECT reading_date FROM meter_readings 
        WHERE meter_id = ? 
        ORDER BY reading_date DESC 
        LIMIT 1
        """
        result = db.fetch_one(sql, (meter_id,))
        
        if result:
            return result[0]
        return None
    
    @classmethod
    def get_all(cls):
        """
        获取所有抄表记录
        :return: 抄表记录列表
        """
        db = get_db()
        sql = """
        SELECT mr.* FROM meter_readings mr
        JOIN meters m ON mr.meter_id = m.id
        JOIN tenants t ON m.tenant_id = t.id
        ORDER BY strftime('%Y-%m', mr.reading_date) DESC, t.name ASC
        """
        results = db.fetch_all(sql)
        
        readings = []
        for result in results:
            # 显式指定每个字段的值，避免顺序问题
            reading = cls(
                id=result[0],
                meter_id=result[1],
                reading_date=result[2],
                current_reading=result[3],
                previous_reading=result[4],
                usage=result[5],
                reader=result[6],
                create_time=result[7],
                adjustment=result[8] if len(result) > 8 else 0,
                remark=result[9] if len(result) > 9 else ''
            )
            reading.load_meter_info()
            readings.append(reading)
        
        return readings
    
    @classmethod
    def exists(cls, meter_id, reading_date):
        """
        检查是否已存在相同的抄表记录
        根据表ID和抄表日期月份进行检查
        :param meter_id: 表ID
        :param reading_date: 抄表日期
        :return: 是否已存在
        """
        from datetime import datetime
        
        # 格式化日期获取月份
        if isinstance(reading_date, str):
            # 尝试解析日期字符串
            try:
                date_obj = datetime.strptime(reading_date, "%Y-%m-%d")
                month_str = date_obj.strftime("%Y-%m")
            except ValueError:
                # 如果日期格式不正确，直接返回False
                return False
        else:
            # 如果是日期对象，直接格式化
            month_str = reading_date.strftime("%Y-%m")
        
        db = get_db()
        sql = """
        SELECT COUNT(*) FROM meter_readings 
        WHERE meter_id = ? 
        AND strftime('%Y-%m', reading_date) = ?
        """
        result = db.fetch_one(sql, (meter_id, month_str))
        
        return result[0] > 0
    
    @classmethod
    def is_duplicate(cls, month, tenant_id, meter_no):
        """
        检查是否存在重复的抄表记录
        根据月份、租户ID和表编号的组合进行检查
        :param month: 月份，格式为YYYY-MM
        :param tenant_id: 租户ID
        :param meter_no: 表编号
        :return: 是否已存在重复记录
        """
        db = get_db()
        sql = """
        SELECT COUNT(*) FROM meter_readings mr
        JOIN meters m ON mr.meter_id = m.id
        WHERE strftime('%Y-%m', mr.reading_date) = ? 
        AND m.tenant_id = ?
        AND m.meter_no = ?
        """
        result = db.fetch_one(sql, (month, tenant_id, meter_no))
        
        return result[0] > 0
    
    @classmethod
    def get_all_months(cls):
        """
        获取所有已存在的月份数据
        :return: 月份列表，格式为YYYY-MM，按时间倒序排列
        """
        db = get_db()
        sql = """
        SELECT DISTINCT strftime('%Y-%m', mr.reading_date) as month
        FROM meter_readings mr
        ORDER BY month DESC
        """
        results = db.fetch_all(sql)
        
        # 转换结果为列表
        months = [result[0] for result in results]
        return months
