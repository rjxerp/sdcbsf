#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顶部导航栏组件
集成用户信息展示区、系统状态指示器、全局操作按钮
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class NavBar:
    """顶部导航栏类"""
    
    def __init__(self, parent, dashboard_view):
        """
        初始化顶部导航栏
        :param parent: 父容器
        :param dashboard_view: 仪表盘主视图引用
        """
        self.parent = parent
        self.dashboard_view = dashboard_view
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.parent, relief=tk.RAISED, style="NavBar.TFrame")
        self.main_frame.grid(row=0, column=0, sticky=tk.EW)
        
        # 配置主框架的网格布局
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)
        self.main_frame.grid_columnconfigure(2, weight=0)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # 左侧：用户信息区
        self.user_info_frame = ttk.Frame(self.main_frame)
        self.user_info_frame.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        # 用户头像（占位符）
        self.avatar_label = ttk.Label(self.user_info_frame, text="👤", font=("", 24))
        self.avatar_label.pack(side=tk.LEFT, padx=5)
        
        # 用户信息
        self.user_details_frame = ttk.Frame(self.user_info_frame)
        self.user_details_frame.pack(side=tk.LEFT, padx=5)
        
        self.username_label = ttk.Label(self.user_details_frame, text="", font=("", 11, "bold"))
        self.username_label.pack(side=tk.TOP, anchor=tk.W)
        
        self.role_label = ttk.Label(self.user_details_frame, text="", font=("", 9), foreground="gray")
        self.role_label.pack(side=tk.TOP, anchor=tk.W)
        
        # 初始化用户信息
        self.update_user_info()
        
        # 中间：系统状态区
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=5)
        
        # 服务器状态
        self.server_status_frame = ttk.Frame(self.status_frame)
        self.server_status_frame.pack(side=tk.LEFT, padx=10)
        
        self.server_status_indicator = ttk.Label(self.server_status_frame, text="●", foreground="green", font=('', 14))
        self.server_status_indicator.pack(side=tk.LEFT, padx=2)
        
        self.server_status_label = ttk.Label(self.server_status_frame, text=self.dashboard_view.get_text('server_online'))
        self.server_status_label.pack(side=tk.LEFT)
        
        # 数据同步状态
        self.sync_status_frame = ttk.Frame(self.status_frame)
        self.sync_status_frame.pack(side=tk.LEFT, padx=10)
        
        self.sync_status_indicator = ttk.Label(self.sync_status_frame, text="●", foreground="green", font=('', 14))
        self.sync_status_indicator.pack(side=tk.LEFT, padx=2)
        
        self.sync_status_label = ttk.Label(self.sync_status_frame, text=self.dashboard_view.get_text('data_synchronized'))
        self.sync_status_label.pack(side=tk.LEFT)
        
        # 右侧：操作按钮区
        self.actions_frame = ttk.Frame(self.main_frame)
        self.actions_frame.grid(row=0, column=2, sticky=tk.E, padx=10, pady=5)
        
        # 月份选择组件
        self.month_label = ttk.Label(self.actions_frame, text=self.dashboard_view.get_text('select_month') + ':')
        self.month_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.month_var = tk.StringVar()
        self.month_combobox = ttk.Combobox(self.actions_frame, textvariable=self.month_var, state="readonly")
        # 加载月份列表
        self.load_month_list()
        self.month_combobox.pack(side=tk.LEFT, padx=(0, 10))
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(self.actions_frame, text="🔄 " + self.dashboard_view.get_text('refresh'), command=self.on_refresh)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # 初始化样式
        self._init_style()
        
        # 初始化时间显示
        self.update_time()
    
    def _init_style(self):
        """
        初始化样式
        """
        style = ttk.Style()
        style.configure("NavBar.TFrame", background="#f0f0f0")
    
    def load_month_list(self):
        """
        加载月份列表
        从数据库中获取抄表管理列表内已存在的"所属月份"字段的所有唯一值
        """
        from models.reading import MeterReading
        from models.charge import Charge
        
        # 获取所有抄表记录的月份
        meter_readings = MeterReading.get_all()
        reading_months = {reading.reading_date[:7] for reading in meter_readings if reading.reading_date}
        
        # 获取所有费用记录的月份
        charges = Charge.get_all()
        charge_months = {charge.month for charge in charges if charge.month}
        
        # 合并所有唯一月份
        all_months = reading_months.union(charge_months)
        
        # 按降序排序
        sorted_months = sorted(all_months, reverse=True)
        
        # 添加翻译后的"全部"选项
        all_option = self.dashboard_view.get_text('all')
        sorted_months.insert(0, all_option)
        
        # 设置到combobox
        self.month_combobox['values'] = sorted_months
        
        # 默认选择第一个选项（最新月份或"全部"）
        if sorted_months:
            self.month_var.set(sorted_months[0])
    
    def on_refresh(self):
        """
        刷新按钮点击事件
        """
        print("刷新仪表盘数据")
        # 刷新数据的逻辑
        self.refresh_btn.config(text="🔄 刷新中...")
        
        # 获取选中的月份
        selected_month = self.month_var.get()
        # 获取翻译后的"全部"选项
        all_option = self.dashboard_view.get_text('all')
        # 如果选择了"全部"，则传递None
        month_param = None if selected_month == all_option else selected_month
        
        # 直接调用DashboardView的refresh_data方法，并传递月份参数
        self.dashboard_view.refresh_data(month_param)
        
        # 更新刷新按钮文本为当前语言
        self.refresh_btn.config(text="🔄 " + self.dashboard_view.get_text('refresh'))
    
    def update_time(self):
        """
        更新时间显示
        """
        # 时间显示功能暂未实现
        self.parent.after(1000, self.update_time)
    
    def update_user_info(self):
        """
        更新用户信息
        从main_window获取当前登录用户信息并更新界面
        """
        if hasattr(self.dashboard_view, 'main_window') and hasattr(self.dashboard_view.main_window, 'current_user'):
            current_user = self.dashboard_view.main_window.current_user
            if current_user:
                self.username_label.config(text=current_user.username)
                # 翻译角色文本
                if hasattr(self.dashboard_view, 'main_window') and hasattr(self.dashboard_view.main_window, 'get_text'):
                    get_text = self.dashboard_view.main_window.get_text
                    # 中文到英文翻译键的映射
                    role_mapping = {
                        '管理员': 'admin',
                        '抄表员': 'reader'
                    }
                    # 获取翻译键
                    role_key = role_mapping.get(current_user.role, current_user.role)
                    self.role_label.config(text=get_text(role_key))
    
    def update_language(self):
        """
        更新导航栏的语言
        """
        # 获取语言工具
        if hasattr(self.dashboard_view, 'main_window') and hasattr(self.dashboard_view.main_window, 'get_text'):
            get_text = self.dashboard_view.main_window.get_text
            
            # 更新服务器状态标签
            self.server_status_label.config(text=get_text('server_online'))
            
            # 更新数据同步状态标签
            self.sync_status_label.config(text=get_text('data_synchronized'))
            
            # 更新月份选择标签
            self.month_label.config(text=get_text('select_month') + ':')
            
            # 更新月份选择下拉框
            current_values = list(self.month_combobox['values'])
            if current_values:
                # 保存当前选中的值
                current_selected = self.month_var.get()
                # 获取当前语言的"全部"选项
                all_option = get_text('all')
                
                # 更新第一个选项为当前语言的"全部"
                current_values[0] = all_option
                self.month_combobox['values'] = tuple(current_values)
                
                # 如果当前选中的是任何语言的"全部"，则更新为当前语言的"全部"
                all_options_in_all_languages = ["全部", "All", all_option]
                if current_selected in all_options_in_all_languages:
                    self.month_var.set(all_option)
            
            # 更新刷新按钮文本
            self.refresh_btn.config(text="🔄 " + get_text('refresh'))
            
            # 更新用户信息，确保角色名称也被翻译
            self.update_user_info()
    

