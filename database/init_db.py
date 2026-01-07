#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化模块
负责创建数据库表结构和添加默认数据
"""

from database.db_manager import DBManager

def init_database():
    """
    初始化数据库
    创建所有表结构并添加默认数据
    """
    db = DBManager()
    
    # 创建租户表
    create_tenants_table(db)
    
    # 创建水电表表
    create_meters_table(db)
    
    # 创建价格表
    create_prices_table(db)
    
    # 创建抄表记录表
    create_meter_readings_table(db)
    
    # 创建费用表
    create_charges_table(db)
    
    # 创建收费记录表
    create_payments_table(db)
    
    # 创建结算记录表
    create_settlements_table(db)
    
    # 创建用户表
    create_users_table(db)
    
    # 添加默认数据
    add_default_data(db)
    
    db.close()

def create_tenants_table(db):
    """
    创建租户表
    """
    sql = """
    CREATE TABLE IF NOT EXISTS tenants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        address TEXT NOT NULL,
        contact_person TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        deactivated INTEGER NOT NULL DEFAULT 0,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    db.execute(sql)
    
    # 添加索引
    db.execute("CREATE INDEX IF NOT EXISTS idx_tenants_type ON tenants(type);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_tenants_name ON tenants(name);")

def create_meters_table(db):
    """
    创建水电表表
    """
    sql = """
    CREATE TABLE IF NOT EXISTS meters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meter_no TEXT NOT NULL UNIQUE,
        meter_type TEXT NOT NULL,
        tenant_id INTEGER NOT NULL,
        location TEXT NOT NULL,
        initial_reading REAL NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT '正常',
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
    );
    """
    db.execute(sql)
    
    # 添加索引
    db.execute("CREATE INDEX IF NOT EXISTS idx_meters_tenant_id ON meters(tenant_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_meters_type ON meters(meter_type);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_meters_status ON meters(status);")

def create_prices_table(db):
    """
    创建价格表
    """
    sql = """
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_type TEXT NOT NULL,
        tenant_type TEXT,
        price REAL NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    db.execute(sql)
    
    # 添加索引
    db.execute("CREATE INDEX IF NOT EXISTS idx_prices_resource_type ON prices(resource_type);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_prices_tenant_type ON prices(tenant_type);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_prices_start_date ON prices(start_date);")

def create_meter_readings_table(db):
    """
    创建抄表记录表
    """
    sql = """
    CREATE TABLE IF NOT EXISTS meter_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meter_id INTEGER NOT NULL,
        reading_date DATE NOT NULL,
        current_reading REAL NOT NULL,
        previous_reading REAL NOT NULL,
        usage REAL NOT NULL,
        adjustment REAL NOT NULL DEFAULT 0,
        reader TEXT NOT NULL,
        remark TEXT DEFAULT '',
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (meter_id) REFERENCES meters(id) ON DELETE CASCADE
    );
    """
    db.execute(sql)
    
    # 添加索引
    db.execute("CREATE INDEX IF NOT EXISTS idx_meter_readings_meter_id ON meter_readings(meter_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_meter_readings_date ON meter_readings(reading_date);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_meter_readings_reader ON meter_readings(reader);")

def create_charges_table(db):
    """
    创建费用表
    """
    sql = """
    CREATE TABLE IF NOT EXISTS charges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER NOT NULL,
        month TEXT NOT NULL,
        water_usage REAL NOT NULL,
        water_price REAL NOT NULL,
        water_charge REAL NOT NULL,
        electricity_usage REAL NOT NULL,
        electricity_price REAL NOT NULL,
        electricity_charge REAL NOT NULL,
        total_charge REAL NOT NULL,
        status TEXT NOT NULL DEFAULT '未缴',
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
    );
    """
    db.execute(sql)
    
    # 添加索引
    db.execute("CREATE INDEX IF NOT EXISTS idx_charges_tenant_id ON charges(tenant_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_charges_month ON charges(month);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_charges_status ON charges(status);")

def create_payments_table(db):
    """
    创建收费记录表
    """
    sql = """
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        charge_id INTEGER NOT NULL,
        payment_date DATE NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payer TEXT NOT NULL,
        notes TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (charge_id) REFERENCES charges(id) ON DELETE CASCADE
    );
    """
    db.execute(sql)
    
    # 添加索引
    db.execute("CREATE INDEX IF NOT EXISTS idx_payments_charge_id ON payments(charge_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_payments_method ON payments(payment_method);")

def create_settlements_table(db):
    """
    创建结算记录表
    """
    sql = """
    CREATE TABLE IF NOT EXISTS settlements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        settle_date DATE NOT NULL,
        settle_month TEXT NOT NULL,
        total_amount REAL NOT NULL,
        cashier TEXT NOT NULL,
        notes TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    db.execute(sql)
    
    # 添加索引
    db.execute("CREATE INDEX IF NOT EXISTS idx_settlements_month ON settlements(settle_month);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_settlements_date ON settlements(settle_date);")

def create_users_table(db):
    """
    创建用户表
    """
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT '启用',
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    db.execute(sql)

def add_default_data(db):
    """
    添加默认数据
    """
    # 检查是否已有管理员用户
    admin = db.fetch_one("SELECT * FROM users WHERE username = 'admin'")
    if not admin:
        # 添加默认管理员用户，密码为admin123
        db.insert('users', {
            'username': 'admin',
            'password': 'admin123',  # 实际项目中应该加密存储
            'role': '管理员'
        })
    
    # 添加默认价格
    water_price = db.fetch_one("SELECT * FROM prices WHERE resource_type = '水' AND end_date IS NULL")
    if not water_price:
        db.insert('prices', {
            'resource_type': '水',
            'tenant_type': '全部',
            'price': 3.5,
            'start_date': '2023-01-01'
        })
    
    electricity_price = db.fetch_one("SELECT * FROM prices WHERE resource_type = '电' AND end_date IS NULL")
    if not electricity_price:
        db.insert('prices', {
            'resource_type': '电',
            'tenant_type': '全部',
            'price': 0.8,
            'start_date': '2023-01-01'
        })

if __name__ == "__main__":
    init_database()
    print("数据库初始化完成！")
