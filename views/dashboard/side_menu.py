#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
左侧功能菜单组件
实现可折叠式设计，包含仪表盘分类导航、数据管理入口、系统配置选项
支持多级菜单与高亮当前选中项
"""

import tkinter as tk
from tkinter import ttk


class SideMenu:
    """左侧功能菜单类"""
    
    def __init__(self, parent, dashboard_view):
        """
        初始化左侧功能菜单
        :param parent: 父容器
        :param dashboard_view: 仪表盘主视图引用
        """
        self.parent = parent
        self.dashboard_view = dashboard_view
        self.selected_menu = None
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.parent, style="SideMenu.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始化样式
        self._init_style()
        
        # 创建菜单列表
        self.create_menu_items()
    
    def get_text(self, key):
        """
        获取当前语言的文本
        :param key: 文本键名
        :return: 对应语言的文本
        """
        if hasattr(self.dashboard_view, 'main_window') and self.dashboard_view.main_window:
            return self.dashboard_view.main_window.get_text(key)
        # 默认返回键名
        return key
    
    def update_language(self):
        """
        更新菜单的语言
        """
        # 保存当前选中的菜单项
        current_selected = self.selected_menu
        
        # 销毁当前菜单并重新创建
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # 创建新菜单项
        self.create_menu_items()
        
        # 恢复之前选中的菜单项，避免不必要的页面刷新
        if current_selected and hasattr(self, 'overview_btn'):
            # 只更新菜单文本，不触发菜单点击事件
            pass
    
    def _init_style(self):
        """
        初始化样式
        """
        style = ttk.Style()
        style.configure("SideMenu.TFrame", background="#f8f9fa")
        style.configure("Menu.TButton", width=15, anchor=tk.W, padding=(10, 8))
        # 使用map方法定义按钮在不同状态下的样式
        style.map("Menu.TButton", background=[("active", "#e9ecef"), ("!active", "#f8f9fa")])
        style.configure("SubMenu.TButton", width=13, anchor=tk.W, padding=(25, 5))
    
    def create_menu_items(self):
        """
        创建菜单项
        """
        # 菜单标题
        menu_title = ttk.Label(self.main_frame, text=self.get_text('menu_title'), font=("", 12, "bold"), background="#f8f9fa")
        menu_title.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
        
        # 仪表盘菜单组
        self.dashboard_menu_frame = ttk.LabelFrame(self.main_frame, text=self.get_text('menu_group_dashboard'), style="MenuGroup.TLabelframe")
        self.dashboard_menu_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 概览菜单项
        self.overview_btn = ttk.Button(self.dashboard_menu_frame, text="📊 " + self.get_text('menu_overview'), style="Menu.TButton", 
                                      command=lambda: self.on_menu_click('overview'))
        self.overview_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 数据管理菜单组
        self.data_menu_frame = ttk.LabelFrame(self.main_frame, text=self.get_text('menu_group_data_management'), style="MenuGroup.TLabelframe")
        self.data_menu_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 租户管理菜单项
        self.tenant_btn = ttk.Button(self.data_menu_frame, text="👥 " + self.get_text('menu_tenant'), style="Menu.TButton", 
                                    command=lambda: self.on_menu_click('tenant'))
        self.tenant_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 水电表管理菜单项
        self.meter_btn = ttk.Button(self.data_menu_frame, text="⚡ " + self.get_text('menu_meter'), style="Menu.TButton", 
                                   command=lambda: self.on_menu_click('meter'))
        self.meter_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 抄表管理菜单项
        self.reading_btn = ttk.Button(self.data_menu_frame, text="📋 " + self.get_text('menu_reading_entry'), style="Menu.TButton", 
                                     command=lambda: self.on_menu_click('reading_entry'))
        self.reading_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 费用管理菜单项
        self.charge_btn = ttk.Button(self.data_menu_frame, text="💰 " + self.get_text('menu_charge_calculation'), style="Menu.TButton", 
                                    command=lambda: self.on_menu_click('charge_calculation'))
        self.charge_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 收费管理菜单项
        self.payment_btn = ttk.Button(self.data_menu_frame, text="💳 " + self.get_text('menu_payment_entry'), style="Menu.TButton", 
                                     command=lambda: self.on_menu_click('payment_entry'))
        self.payment_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 费用结算菜单项
        self.settlement_btn = ttk.Button(self.data_menu_frame, text="📝 " + self.get_text('menu_settlement_management'), style="Menu.TButton", 
                                     command=lambda: self.on_menu_click('settlement_management'))
        self.settlement_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 系统配置菜单组
        self.system_menu_frame = ttk.LabelFrame(self.main_frame, text=self.get_text('menu_group_system_config'), style="MenuGroup.TLabelframe")
        self.system_menu_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 价格管理菜单项
        self.price_btn = ttk.Button(self.system_menu_frame, text="📊 " + self.get_text('menu_price'), style="Menu.TButton", 
                                   command=lambda: self.on_menu_click('price_management'))
        self.price_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 用户管理菜单项
        self.user_btn = ttk.Button(self.system_menu_frame, text="👤 " + self.get_text('menu_user_management'), style="Menu.TButton", 
                                  command=lambda: self.on_menu_click('user_management'))
        self.user_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 系统设置菜单项
        self.settings_btn = ttk.Button(self.system_menu_frame, text="⚙️ " + self.get_text('menu_system_config'), style="Menu.TButton", 
                                     command=lambda: self.on_menu_click('system_settings'))
        self.settings_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 只有在第一次创建菜单时才默认选中概览菜单
        # 避免在语言切换时导致不必要的页面刷新
        if not hasattr(self, 'menu_initialized'):
            self.on_menu_click('overview')
            self.menu_initialized = True
    
    def on_menu_click(self, menu_item):
        """
        菜单项点击事件
        :param menu_item: 菜单项标识符
        """
        # 更新选中状态
        self.selected_menu = menu_item
        
        # 通知主视图更新内容
        self.dashboard_view.on_menu_select(self.get_text(f'menu_{menu_item}'))
        
        # 根据菜单项调用相应的MainWindow方法
        if hasattr(self.dashboard_view, 'main_window') and self.dashboard_view.main_window:
            main_window = self.dashboard_view.main_window
            
            if menu_item == 'tenant':
                main_window.open_tenant_management()
            elif menu_item == 'meter':
                main_window.open_meter_management()
            elif menu_item == 'reading_entry':
                main_window.open_meter_reading()
            elif menu_item == 'charge_calculation':
                main_window.open_charge_calculation()
            elif menu_item == 'payment_entry':
                main_window.open_payment_entry()
            elif menu_item == 'settlement_management':
                main_window.open_settlement_management()
            elif menu_item == 'price_management':
                main_window.open_price_management()
            elif menu_item == 'user_management':
                main_window.open_user_management()
            elif menu_item == 'system_settings':
                main_window.open_system_settings()
