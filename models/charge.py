#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
费用模型
负责处理费用计算、生成和管理
"""

import logging
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from database.db_manager import get_db
from models.tenant import Tenant
from models.price import Price
from utils.settings_utils import SettingsUtils

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getcwd(), 'charge_calculation.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Charge:
    """费用类"""
    
    def __init__(self, id: Optional[int] = None, tenant_id: Optional[int] = None, month: str = '', water_usage: float = 0.0, water_price: float = 0.0, water_charge: float = 0.0,
                 electricity_usage: float = 0.0, electricity_price: float = 0.0, electricity_charge: float = 0.0, total_charge: float = 0.0, status: str = '未缴', create_time: Optional[datetime] = None, update_time: Optional[datetime] = None):
        """
        初始化费用对象
        :param id: 费用ID
        :param tenant_id: 租户ID
        :param month: 费用月份（如2023-05）
        :param water_usage: 水费用量
        :param water_price: 水费单价
        :param water_charge: 水费金额
        :param electricity_usage: 电费用量
        :param electricity_price: 电费单价
        :param electricity_charge: 电费金额
        :param total_charge: 总费用
        :param status: 状态（未缴/已缴/部分缴纳）
        :param create_time: 创建时间
        :param update_time: 更新时间
        """
        self.id: Optional[int] = id
        self.tenant_id: Optional[int] = tenant_id
        self.month: str = month
        self.water_usage: float = water_usage
        self.water_price: float = water_price
        self.water_charge: float = water_charge
        self.electricity_usage: float = electricity_usage
        self.electricity_price: float = electricity_price
        self.electricity_charge: float = electricity_charge
        self.total_charge: float = total_charge
        self.status: str = status
        self.create_time: Optional[datetime] = create_time
        self.update_time: Optional[datetime] = update_time
        self.tenant: Optional[Tenant] = None  # 关联的租户对象
    
    def save(self) -> bool:
        """
        保存费用信息
        如果是新费用则插入，否则更新
        :return: 是否保存成功
        """
        db = get_db()
        
        if self.id:
            # 更新现有费用
            data: Dict[str, Any] = {
                'tenant_id': self.tenant_id,
                'month': self.month,
                'water_usage': self.water_usage,
                'water_price': self.water_price,
                'water_charge': self.water_charge,
                'electricity_usage': self.electricity_usage,
                'electricity_price': self.electricity_price,
                'electricity_charge': self.electricity_charge,
                'total_charge': self.total_charge,
                'status': self.status
            }
            result = db.update('charges', data, f'id = {self.id}')
        else:
            # 插入新费用
            data: Dict[str, Any] = {
                'tenant_id': self.tenant_id,
                'month': self.month,
                'water_usage': self.water_usage,
                'water_price': self.water_price,
                'water_charge': self.water_charge,
                'electricity_usage': self.electricity_usage,
                'electricity_price': self.electricity_price,
                'electricity_charge': self.electricity_charge,
                'total_charge': self.total_charge,
                'status': self.status
            }
            self.id = db.insert('charges', data)
            result = self.id is not None
        
        return bool(result)
    
    def delete(self) -> bool:
        """
        删除费用
        :return: 是否删除成功
        """
        if not self.id:
            return False
        
        db = get_db()
        return bool(db.delete('charges', f'id = {self.id}'))
    
    def load_tenant_info(self) -> None:
        """
        加载关联的租户信息
        """
        if self.tenant_id:
            self.tenant = Tenant.get_by_id(self.tenant_id)
    
    @classmethod
    def get_by_id(cls, charge_id: int) -> Optional['Charge']:
        """
        根据ID获取费用
        :param charge_id: 费用ID
        :return: 费用对象或None
        """
        db = get_db()
        sql = "SELECT * FROM charges WHERE id = ?"
        result = db.fetch_one(sql, (charge_id,))
        
        if result:
            charge = cls(*result)
            charge.load_tenant_info()
            return charge
        return None
    
    @classmethod
    def get_by_month(cls, month: str) -> List['Charge']:
        """
        根据月份获取所有费用
        :param month: 月份（如2023-05）
        :return: 费用列表
        """
        db = get_db()
        sql = """
        SELECT * FROM charges 
        WHERE month = ? 
        ORDER BY tenant_id
        """
        results = db.fetch_all(sql, (month,))
        
        charges: List['Charge'] = []
        for result in results:
            charge = cls(*result)
            charge.load_tenant_info()
            charges.append(charge)
        
        return charges
    
    @classmethod
    def get_by_tenant(cls, tenant_id: int, limit: int = 12) -> List['Charge']:
        """
        根据租户ID获取最近的费用记录
        :param tenant_id: 租户ID
        :param limit: 返回记录数量
        :return: 费用列表
        """
        db = get_db()
        sql = """
        SELECT * FROM charges 
        WHERE tenant_id = ? 
        ORDER BY month DESC 
        LIMIT ?
        """
        results = db.fetch_all(sql, (tenant_id, limit))
        
        charges: List['Charge'] = []
        for result in results:
            charge = cls(*result)
            charge.load_tenant_info()
            charges.append(charge)
        
        return charges
    
    @classmethod
    def get_by_tenant_and_month(cls, tenant_id: int, month: str) -> Optional['Charge']:
        """
        根据租户ID和月份获取费用记录
        :param tenant_id: 租户ID
        :param month: 月份（如2023-05）
        :return: 费用对象或None
        """
        db = get_db()
        sql = "SELECT * FROM charges WHERE tenant_id = ? AND month = ?"
        result = db.fetch_one(sql, (tenant_id, month))
        
        if result:
            return cls(*result)
        return None
    
    @classmethod
    def calculate_charge(cls, tenant_id: int, month: str, water_usage: float, electricity_usage: float) -> Optional['Charge']:
        """
        计算费用
        :param tenant_id: 租户ID
        :param month: 费用月份
        :param water_usage: 水费用量
        :param electricity_usage: 电费用量
        :return: 费用对象
        """
        try:
            logger.info(f"开始计算租户ID {tenant_id} 的{month}月份费用")
            
            # 获取租户信息
            tenant = Tenant.get_by_id(tenant_id)
            if not tenant:
                logger.error(f"找不到租户ID {tenant_id} 的信息")
                return None
            
            logger.info(f"获取到租户信息：ID={tenant.id}, 名称={tenant.name}, 类型={tenant.type}")
            
            # 获取当前价格
            logger.info(f"开始获取 {tenant.type} 类型租户的最新水价和电价")
            water_price_obj = Price.get_current_price('水', tenant.type)
            electricity_price_obj = Price.get_current_price('电', tenant.type)
            
            water_price = water_price_obj.price if water_price_obj else 0.0
            electricity_price = electricity_price_obj.price if electricity_price_obj else 0.0
            
            logger.info(f"获取到价格：水价={water_price}元/吨, 电价={electricity_price}元/度")
            
            # 验证价格是否有效
            if water_price <= 0:
                logger.warning(f"水价 {water_price} 无效，将使用默认值 0")
            if electricity_price <= 0:
                logger.warning(f"电价 {electricity_price} 无效，将使用默认值 0")
            
            # 处理用量：确保用量为非负数
            water_usage = max(0.0, water_usage)
            electricity_usage = max(0.0, electricity_usage)
            
            logger.info(f"处理后的用量：用水量={water_usage}吨, 用电量={electricity_usage}度")
            
            # 计算水费
            water_charge = round(water_usage * water_price)
            logger.info(f"计算水费：{water_usage}吨 × {water_price}元/吨 = {water_charge}元")
            
            # 计算电费
            electricity_charge = round(electricity_usage * electricity_price)
            logger.info(f"计算电费：{electricity_usage}度 × {electricity_price}元/度 = {electricity_charge}元")
            
            # 计算总费用
            total_charge = round(water_charge + electricity_charge)
            logger.info(f"计算总费用：{water_charge}元 + {electricity_charge}元 = {total_charge}元")
            
            # 检查是否已存在该月份的费用记录
            existing_charge = cls.get_by_tenant_and_month(tenant_id, month)
            
            if existing_charge:
                logger.info(f"更新现有费用记录：ID={existing_charge.id}")
                # 更新现有记录
                existing_charge.water_usage = water_usage
                existing_charge.water_price = water_price
                existing_charge.water_charge = water_charge
                existing_charge.electricity_usage = electricity_usage
                existing_charge.electricity_price = electricity_price
                existing_charge.electricity_charge = electricity_charge
                existing_charge.total_charge = total_charge
                logger.info(f"费用记录更新完成：ID={existing_charge.id}")
                return existing_charge
            else:
                logger.info(f"创建新费用记录")
                # 创建新费用对象
                charge = cls(
                    tenant_id=tenant_id,
                    month=month,
                    water_usage=water_usage,
                    water_price=water_price,
                    water_charge=water_charge,
                    electricity_usage=electricity_usage,
                    electricity_price=electricity_price,
                    electricity_charge=electricity_charge,
                    total_charge=total_charge,
                    status='未缴'
                )
                logger.info(f"新费用记录创建完成：租户ID={tenant_id}, 月份={month}, 总费用={total_charge}元")
                return charge
                
        except Exception as e:
            logger.error(f"计算费用失败：{str(e)}", exc_info=True)
            return None
    
    @classmethod
    def get_all(cls) -> List['Charge']:
        """
        获取所有费用记录
        :return: 费用列表
        """
        db = get_db()
        sql = "SELECT * FROM charges ORDER BY month DESC, tenant_id"
        results = db.fetch_all(sql)
        
        charges: List['Charge'] = []
        for result in results:
            charge = cls(*result)
            charge.load_tenant_info()
            charges.append(charge)
        
        return charges
    
    @classmethod
    def update_status(cls, charge_id: int, status: str) -> bool:
        """
        更新费用状态
        :param charge_id: 费用ID
        :param status: 新状态
        :return: 是否更新成功
        """
        db = get_db()
        return bool(db.update('charges', {'status': status}, f'id = {charge_id}'))
