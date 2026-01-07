#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据卡片组件
实现中央数据概览区的卡片式网格布局
每个KPI指标卡片包含：指标名称、当前数值、计量单位、同比/环比变化百分比、趋势微图表、数据更新时间戳
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from models.tenant import Tenant


class DataCards:
    """数据卡片组件类"""
    
    def __init__(self, parent):
        """
        初始化数据卡片组件
        :param parent: 父容器
        """
        self.parent = parent
        self.cards_data = []
        self.dashboard_view = None  # 用于获取语言工具
        
        # 数据缓存机制，避免频繁查询数据库
        self.data_cache = {
            'tenant_stats': None,
            'meter_stats': None,
            'charge_stats': {},  # 按月份缓存
            'unpaid_amount': {},  # 按月份缓存
            'cache_time': 0
        }
        self.CACHE_DURATION = 300  # 缓存过期时间（秒）
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.parent, style="DataCards.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始化样式
        self._init_style()
        
        # 模拟数据初始化
        self._init_mock_data()
        
        # 创建数据卡片
        self.create_data_cards()
    
    def set_dashboard_view(self, dashboard_view):
        """
        设置仪表盘视图引用，用于获取语言工具
        :param dashboard_view: 仪表盘视图实例
        """
        self.dashboard_view = dashboard_view
    
    def get_text(self, key):
        """
        获取当前语言的文本
        :param key: 文本键名
        :return: 对应语言的文本
        """
        if self.dashboard_view and hasattr(self.dashboard_view, 'main_window'):
            return self.dashboard_view.main_window.get_text(key)
        # 默认返回键名
        return key
    
    def update_language(self):
        """
        更新数据卡片的语言
        只更新现有卡片的文本内容，不重新创建卡片
        """
        # 更新所有数据卡片的文本
        for card_frame in self.main_frame.winfo_children():
            if isinstance(card_frame, ttk.Frame) and card_frame['style'] == 'Card.TFrame':
                card_children = card_frame.winfo_children()
                if len(card_children) >= 4:
                    # 更新标题
                    title_label = card_children[0]
                    if isinstance(title_label, ttk.Label):
                        current_text = title_label.cget('text')
                        # 根据当前文本更新为对应语言
                        if current_text in ['租户总数', 'Total Tenants']:
                            title_label.config(text=self.get_text('total_tenants'))
                        elif current_text in ['仪表总数', 'Total Meters']:
                            title_label.config(text='仪表总数') if self.dashboard_view.main_window.current_language == 'zh_CN' else title_label.config(text='Total Meters')
                        elif current_text in ['总收入', 'Total Income']:
                            title_label.config(text='总收入') if self.dashboard_view.main_window.current_language == 'zh_CN' else title_label.config(text='Total Income')
                        elif current_text in ['未收金额', 'Unpaid Amount']:
                            title_label.config(text='未收金额') if self.dashboard_view.main_window.current_language == 'zh_CN' else title_label.config(text='Unpaid Amount')
                        elif current_text in ['总用水量', 'Total Water Consumption']:
                            title_label.config(text='总用水量') if self.dashboard_view.main_window.current_language == 'zh_CN' else title_label.config(text='Total Water Consumption')
                        elif current_text in ['总用电量', 'Total Electricity Consumption']:
                            title_label.config(text='总用电量') if self.dashboard_view.main_window.current_language == 'zh_CN' else title_label.config(text='Total Electricity Consumption')
                    
                    # 更新单位
                    unit_label = card_children[2]
                    if isinstance(unit_label, ttk.Label):
                        current_text = unit_label.cget('text')
                        if current_text in ['户', 'Households']:
                            unit_label.config(text=self.get_text('households'))
                        elif current_text in ['元', 'Yuan']:
                            unit_label.config(text='元') if self.dashboard_view.main_window.current_language == 'zh_CN' else unit_label.config(text='Yuan')
                        elif current_text in ['吨', 'Tons']:
                            unit_label.config(text='吨') if self.dashboard_view.main_window.current_language == 'zh_CN' else unit_label.config(text='Tons')
                        elif current_text in ['度', 'KWh']:
                            unit_label.config(text='度') if self.dashboard_view.main_window.current_language == 'zh_CN' else unit_label.config(text='KWh')
                    
                    # 更新变化率标签
                    change_label = card_children[3]
                    if isinstance(change_label, ttk.Label):
                        current_text = change_label.cget('text')
                        if '%' in current_text:
                            # 保留百分比数值，只更新前缀
                            if current_text.startswith('环比') or current_text.startswith('MoM'):
                                if self.dashboard_view.main_window.current_language == 'zh_CN':
                                    change_label.config(text=f"环比{current_text[3:]}")
                                else:
                                    change_label.config(text=f"MoM{current_text[2:]}")
    
    def _init_style(self):
        """
        初始化样式
        """
        style = ttk.Style()
        style.configure("DataCards.TFrame", background="white")
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1, bordercolor="#e0e0e0")
        style.configure("CardTitle.TLabel", font=("", 10))
        style.configure("CardValue.TLabel", font=("", 11, "bold"))
        # 创建基础样式
        style.configure("CardChange.TLabel", font=("", 9))
        # 使用map方法定义不同状态下的样式（这里我们直接使用前景色）
        style.configure("PositiveChange.TLabel", foreground="green")
        style.configure("NegativeChange.TLabel", foreground="red")
        style.configure("NeutralChange.TLabel", foreground="gray")
    
    def _is_cache_valid(self):
        """
        检查缓存是否有效
        :return: 缓存是否有效的布尔值
        """
        from time import time
        return (time() - self.data_cache['cache_time']) < self.CACHE_DURATION
    
    def _get_tenant_stats(self):
        """
        获取租户统计数据
        1. 从数据库获取所有租户
        2. 统计租户总数和停用租户数量
        :return: 包含租户总数和停用租户数量的字典
        """
        # 检查缓存是否有效
        if self._is_cache_valid() and self.data_cache['tenant_stats']:
            return self.data_cache['tenant_stats']
        
        # 获取所有租户
        tenants = Tenant.get_all()
        
        # 统计租户总数和停用租户数量
        total_count = len(tenants)
        deactivated_count = 0
        
        for tenant in tenants:
            # 统计停用租户数量
            if tenant.deactivated:
                deactivated_count += 1
        
        result = {
            "total": total_count,
            "deactivated": deactivated_count
        }
        
        # 更新缓存
        self.data_cache['tenant_stats'] = result
        return result
    
    def _get_meter_stats(self):
        """
        获取仪表统计数据
        1. 从数据库获取所有水电表
        2. 按表类型（水/电）分别统计数量
        :return: 包含水表数量和电表数量的字典
        """
        # 检查缓存是否有效
        if self._is_cache_valid() and self.data_cache['meter_stats']:
            return self.data_cache['meter_stats']
        
        from models.meter import Meter
        
        # 获取所有水电表
        meters = Meter.get_all()
        
        # 按表类型统计数量
        water_count = 0
        electricity_count = 0
        
        for meter in meters:
            if meter.meter_type == '水':
                water_count += 1
            elif meter.meter_type == '电':
                electricity_count += 1
        
        result = {
            "water": water_count,
            "electricity": electricity_count,
            "total": water_count + electricity_count
        }
        
        # 更新缓存
        self.data_cache['meter_stats'] = result
        return result
    
    def _get_monthly_charge_stats(self, selected_month=None):
        """
        获取费用统计数据
        1. 从费用管理列表获取指定月份的所有费用记录
        2. 统计水费、电费收入和用量
        :param selected_month: 选中的月份，格式为YYYY-MM，None表示全部月份
        :return: 包含费用统计数据的字典
        """
        # 使用None作为默认月份的键
        cache_key = selected_month or 'all'
        
        # 检查缓存是否有效
        if self._is_cache_valid() and cache_key in self.data_cache['charge_stats']:
            return self.data_cache['charge_stats'][cache_key]
        
        from models.charge import Charge
        from datetime import datetime
        
        # 获取指定月份的费用记录
        if selected_month:
            charges = Charge.get_by_month(selected_month)
        else:
            charges = Charge.get_all()
        
        # 初始化统计数据
        total_income = 0.0
        water_fee = 0.0
        electricity_fee = 0.0
        water_usage = 0.0
        electricity_usage = 0.0
        
        # 遍历费用记录，统计各项数据
        for charge in charges:
            # 统计收入
            water_fee += charge.water_charge
            electricity_fee += charge.electricity_charge
            
            # 统计用量
            water_usage += charge.water_usage
            electricity_usage += charge.electricity_usage
        
        # 计算总收入
        total_income = water_fee + electricity_fee
        
        result = {
            "total_income": round(total_income, 2),
            "water_fee": round(water_fee, 2),
            "electricity_fee": round(electricity_fee, 2),
            "water_usage": round(water_usage, 2),
            "electricity_usage": round(electricity_usage, 2)
        }
        
        # 更新缓存
        self.data_cache['charge_stats'][cache_key] = result
        return result
    
    def _get_unpaid_amount(self, selected_month=None):
        """
        获取未收金额数据
        1. 从所有费用记录中获取未缴纳或部分缴纳的费用
        2. 计算实际未收金额（总费用减去已收金额）
        :param selected_month: 选中的月份，格式为YYYY-MM，None表示全部月份
        :return: 未收金额总和
        """
        # 使用None作为默认月份的键
        cache_key = selected_month or 'all'
        
        # 检查缓存是否有效
        if self._is_cache_valid() and cache_key in self.data_cache['unpaid_amount']:
            return self.data_cache['unpaid_amount'][cache_key]
        
        from models.charge import Charge
        from models.payment import Payment
        
        # 获取费用记录
        if selected_month:
            charges = Charge.get_by_month(selected_month)
        else:
            charges = Charge.get_all()
        
        # 初始化未收金额
        unpaid_amount = 0.0
        
        # 遍历所有费用记录，统计未收金额
        for charge in charges:
            # 只统计未缴纳或部分缴纳的费用
            if charge.status in ("未缴", "部分缴纳"):
                # 获取已收金额
                payments = Payment.get_by_charge(charge.id)
                paid_amount = sum(payment.amount for payment in payments)
                # 计算未收金额
                actual_unpaid = charge.total_charge - paid_amount
                # 确保未收金额为正数
                if actual_unpaid > 0:
                    unpaid_amount += actual_unpaid
        
        result = round(unpaid_amount, 2)
        
        # 更新缓存
        self.data_cache['unpaid_amount'][cache_key] = result
        return result
    
    def _update_cache_time(self):
        """
        更新缓存时间
        """
        from time import time
        self.data_cache['cache_time'] = time()
    
    def _init_mock_data(self, selected_month=None):
        """
        初始化数据
        从数据库获取真实租户、仪表和费用数据
        :param selected_month: 选中的月份，格式为YYYY-MM，None表示全部月份
        """
        # 首次加载或缓存过期时更新缓存时间
        if not self._is_cache_valid():
            self._update_cache_time()
        
        # 获取租户统计数据
        tenant_stats = self._get_tenant_stats()
        # 获取仪表统计数据
        meter_stats = self._get_meter_stats()
        # 获取费用统计数据
        charge_stats = self._get_monthly_charge_stats(selected_month)
        # 获取未收金额数据
        unpaid_amount = self._get_unpaid_amount(selected_month)
        
        # 根据是否选择了月份，调整卡片标题
        if selected_month:
            month_title = f"{selected_month}{self.get_text('monthly_revenue')}"
            water_title = f"{selected_month}{self.get_text('total_water_consumption')}"
            electricity_title = f"{selected_month}{self.get_text('total_electricity_consumption')}"
        else:
            month_title = self.get_text('monthly_revenue')
            water_title = self.get_text('total_water_consumption')
            electricity_title = self.get_text('total_electricity_consumption')
        
        self.cards_data = [
            {
                "id": "total_tenants",
                "title": self.get_text('total_tenants'),
                "value": tenant_stats["total"],
                "deactivated": tenant_stats["deactivated"],
                "unit": self.get_text('households'),
                "change_type": "month",  # month=环比, year=同比
                "change_value": 5.4,
                "change_trend": "up",  # up=上升, down=下降, flat=持平
                "update_time": datetime.now()
            },
            {
                "id": "total_meters",
                "title": self.get_text('total_meters'),
                "value": meter_stats["total"],
                "water_count": meter_stats["water"],
                "electricity_count": meter_stats["electricity"],
                "unit": "",
                "change_type": "month",
                "change_value": 2.8,
                "change_trend": "up",
                "update_time": datetime.now()
            },
            {
                "id": "monthly_revenue",
                "title": month_title,
                "value": charge_stats["total_income"],
                "water_fee": charge_stats["water_fee"],
                "electricity_fee": charge_stats["electricity_fee"],
                "unit": "",
                "change_type": "year",
                "change_value": 12.3,
                "change_trend": "up",
                "update_time": datetime.now()
            },
            {
                "id": "unpaid_amount",
                "title": self.get_text('unpaid_amount'),
                "value": unpaid_amount,
                "unit": "",
                "change_type": "month",
                "change_value": -8.5,
                "change_trend": "down",
                "update_time": datetime.now()
            },
            {
                "id": "water_consumption",
                "title": water_title,
                "value": charge_stats["water_usage"],
                "unit": self.get_text('ton'),
                "change_type": "month",
                "change_value": 3.2,
                "change_trend": "up",
                "update_time": datetime.now()
            },
            {
                "id": "electricity_consumption",
                "title": electricity_title,
                "value": charge_stats["electricity_usage"],
                "unit": self.get_text('kwh'),
                "change_type": "month",
                "change_value": -5.6,
                "change_trend": "down",
                "update_time": datetime.now()
            }
        ]
    
    def create_data_cards(self):
        """
        创建数据卡片
        优化：避免不必要的卡片销毁和重建，只更新数据
        """
        # 检查是否已经创建过卡片框架
        if hasattr(self, 'card_frames') and len(self.card_frames) == len(self.cards_data):
            # 卡片框架已存在，只更新数据
            self.update_card_data()
        else:
            # 清除现有卡片
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            
            # 创建卡片网格布局
            self.card_frames = []
            for i, card_data in enumerate(self.cards_data):
                card_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
                card_frame.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky=tk.NSEW)
                self.main_frame.grid_columnconfigure(i % 3, weight=1, uniform="card")
                self.main_frame.grid_rowconfigure(i // 3, weight=1, uniform="card")
                
                # 配置卡片内部布局
                card_frame.grid_rowconfigure(0, weight=0)
                card_frame.grid_rowconfigure(1, weight=1)
                card_frame.grid_rowconfigure(2, weight=0)
                card_frame.grid_columnconfigure(0, weight=1)
                card_frame.grid_columnconfigure(1, weight=0)
                
                self.card_frames.append(card_frame)
            
            # 更新卡片数据
            self.update_card_data()
    
    def update_card_data(self):
        """
        更新卡片数据，避免不必要的卡片销毁和重建
        """
        for card_frame, card_data in zip(self.card_frames, self.cards_data):
            # 清除卡片内的所有控件
            for widget in card_frame.winfo_children():
                widget.destroy()
            
            # 卡片标题
            title_label = ttk.Label(card_frame, text=card_data["title"], style="CardTitle.TLabel")
            title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=15, pady=8)
            
            # 卡片数值
            if card_data['id'] == 'total_tenants':
                # 租户总数卡片特殊格式："5 (其中：停用: 2)"
                value_text = f"{card_data['value']:,} ({self.get_text('deactivated')}: {card_data['deactivated']}){card_data['unit']}"
                value_label = ttk.Label(card_frame, text=value_text, style="CardValue.TLabel")
                value_label.grid(row=1, column=0, sticky=tk.W, padx=15, pady=5)
            elif card_data['id'] == 'total_meters':
                # 仪表总数卡片特殊格式："水表：X个，电表：X个"
                value_text = f"{self.get_text('water_meter')}：{card_data['water_count']:,}，{self.get_text('electric_meter')}：{card_data['electricity_count']:,}"
                value_label = ttk.Label(card_frame, text=value_text, style="CardValue.TLabel")
                value_label.grid(row=1, column=0, sticky=tk.W, padx=15, pady=5)
            elif card_data['id'] == 'monthly_revenue':
                # 本月收入卡片特殊格式：使用Frame容器来放置总收入和明细部分
                # 创建一个容器Frame来放置这两个标签
                value_container = ttk.Frame(card_frame)
                value_container.grid(row=1, column=0, sticky=tk.W, padx=15, pady=5, columnspan=2)
                value_container.grid_columnconfigure(0, weight=0)
                value_container.grid_columnconfigure(1, weight=1)
                
                # 1. 创建总收入部分标签
                main_value_text = f" {card_data['value']:,.2f}  {self.get_text('yuan')}"
                main_value_label = ttk.Label(value_container, text=main_value_text, style="CardValue.TLabel")
                main_value_label.grid(row=0, column=0, sticky=tk.W)
                
                # 2. 创建明细部分标签（使用固定字体大小，避免频繁动态调整）
                detail_text = f"（{self.get_text('water_fee')}： {card_data['water_fee']:,.2f}   {self.get_text('electricity_fee')}： {card_data['electricity_fee']:,.2f} ）"
                # 使用固定字体大小，减少性能开销
                detail_label = ttk.Label(value_container, text=detail_text, font=('', 9))
                detail_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
            else:
                # 普通卡片格式
                value_text = f"{card_data['value']:,}{card_data['unit']}" if isinstance(card_data['value'], int) else f"{card_data['value']:,.2f}{card_data['unit']}"
                value_label = ttk.Label(card_frame, text=value_text, style="CardValue.TLabel")
                value_label.grid(row=1, column=0, sticky=tk.W, padx=15, pady=5)
            
            # 变化趋势图标
            trend_icon = "↗" if card_data["change_trend"] == "up" else "↘" if card_data["change_trend"] == "down" else "→"
            trend_label = ttk.Label(card_frame, text=trend_icon, font=("", 16))
            trend_label.grid(row=1, column=1, sticky=tk.E, padx=15, pady=5)
            
            # 创建第2行框架，用于放置变化百分比和更新时间
            bottom_frame = ttk.Frame(card_frame)
            bottom_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=15, pady=8)
            bottom_frame.grid_columnconfigure(0, weight=1)
            bottom_frame.grid_columnconfigure(1, weight=1)
            
            # 变化百分比（左对齐）
            change_type_text = self.get_text('month_on_month') if card_data["change_type"] == "month" else self.get_text('year_on_year')
            change_value = abs(card_data["change_value"])
            change_text = f"{change_type_text} {trend_icon} {change_value}%"
            
            if card_data["change_trend"] == "up":
                change_style = "PositiveChange.TLabel"
            elif card_data["change_trend"] == "down":
                change_style = "NegativeChange.TLabel"
            else:
                change_style = "NeutralChange.TLabel"
            
            change_label = ttk.Label(bottom_frame, text=change_text, style=change_style)
            change_label.grid(row=0, column=0, sticky=tk.W)
            
            # 更新时间（右对齐）
            update_time_text = card_data["update_time"].strftime("%Y-%m-%d %H:%M")
            update_label = ttk.Label(bottom_frame, text=f"{self.get_text('update_time')}: {update_time_text}", font=("", 8))
            update_label.grid(row=0, column=1, sticky=tk.E)
            
            # 为卡片添加点击事件
            card_frame.bind("<Button-1>", lambda e, card_id=card_data["id"]: self.on_card_click(card_id))
            for child in card_frame.winfo_children():
                child.bind("<Button-1>", lambda e, card_id=card_data["id"]: self.on_card_click(card_id))
    
    def _adjust_font_size(self, value_label, card_frame):
        """
        动态调整标签的字体大小，确保文本完整显示在卡片内
        
        :param value_label: 需要调整字体大小的标签
        :param card_frame: 标签所在的卡片框架
        """
        # 强制更新界面，确保能够获取到正确的宽度
        card_frame.update_idletasks()
        
        # 获取卡片可用宽度（减去边距）
        card_width = card_frame.winfo_width() - 30  # 减去左右边距
        
        # 如果卡片宽度大于0，开始调整字体大小
        if card_width > 0:
            # 获取当前文本
            text = value_label.cget("text")
            
            # 初始字体大小范围
            min_font_size = 8
            max_font_size = 14
            
            # 创建临时标签用于测量不同字体大小的文本宽度
            temp_label = ttk.Label(card_frame, text=text, style="CardValue.TLabel")
            
            # 先找到最大可能的字体大小，确保文本能完整显示
            optimal_size = min_font_size
            for size in range(min_font_size, max_font_size + 1):
                temp_font = ("", size, "bold")
                temp_label.configure(font=temp_font)
                card_frame.update_idletasks()
                text_width = temp_label.winfo_reqwidth()
                
                if text_width < card_width * 0.95:
                    optimal_size = size
                else:
                    break
            
            # 应用最佳字体大小
            value_label.configure(font=("", optimal_size, "bold"))
            
            # 删除临时标签
            temp_label.destroy()
    
    def on_card_click(self, card_id):
        """
        卡片点击事件
        :param card_id: 卡片ID
        """
        print(f"点击了卡片: {card_id}")
        # 这里可以添加跳转到详情页的逻辑
    
    def _validate_data(self, data, data_type):
        """
        数据验证函数
        :param data: 要验证的数据
        :param data_type: 数据类型 ('int' 或 'float')
        :return: 验证后的数据
        """
        try:
            if data_type == 'int':
                return int(data)
            elif data_type == 'float':
                return float(data)
            return data
        except (ValueError, TypeError):
            return 0
    
    def refresh_data(self, selected_month=None):
        """
        刷新数据卡片
        重新从数据库获取租户数据、仪表数据和费用数据并更新卡片显示
        添加数据加载状态提示和异常处理机制
        :param selected_month: 选中的月份，格式为YYYY-MM，None表示全部月份
        """
        try:
            # 重新初始化数据
            self._init_mock_data(selected_month)
            
            # 重新创建数据卡片
            self.create_data_cards()
            print("数据卡片已刷新")
        except Exception as e:
            print(f"刷新数据卡片失败: {str(e)}")
            # 异常处理：在控制台输出错误信息，确保系统不会崩溃
            # 可以根据需要添加更详细的日志记录或用户提示
