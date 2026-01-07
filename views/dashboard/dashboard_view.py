#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仪表盘主视图
整合顶部导航栏、左侧菜单、数据卡片和图表组件
实现关键业务数据的直观化展示与高效管理
"""

import tkinter as tk
from tkinter import ttk
from .nav_bar import NavBar
from .side_menu import SideMenu
from .data_cards import DataCards
from .charts import Charts


class DashboardView:
    """仪表盘主视图类"""
    
    def __init__(self, parent, main_window):
        """
        初始化仪表盘主视图
        :param parent: 父容器
        :param main_window: MainWindow实例
        """
        self.parent = parent
        self.main_window = main_window
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        # 执行初始化后的配置
        self.__post_init__()
    
    def get_text(self, key):
        """
        获取当前语言的文本
        :param key: 文本键名
        :return: 对应语言的文本
        """
        if self.main_window:
            return self.main_window.get_text(key)
        return key
    
    def __post_init__(self):
        """
        初始化完成后的配置
        """
        # 配置主框架的网格布局
        # 第0行：顶部导航栏，不可伸缩
        # 第1行：主体内容区，可伸缩
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # 创建顶部导航栏
        self.nav_bar_frame = ttk.Frame(self.main_frame)
        self.nav_bar_frame.grid(row=0, column=0, sticky=tk.EW)
        self.nav_bar = NavBar(self.nav_bar_frame, self)
        
        # 创建主体内容区框架
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky=tk.NSEW)
        
        # 配置主体内容区的网格布局
        # 第0列：左侧菜单，固定宽度
        # 第1列：主内容区，可伸缩
        self.content_frame.grid_columnconfigure(0, weight=0)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # 创建主内容区
        self.main_content_frame = ttk.Frame(self.content_frame)
        self.main_content_frame.grid(row=0, column=1, sticky=tk.NSEW)
        
        # 配置主内容区的网格布局
        # 第0行：数据卡片区域，固定高度
        # 第1行：图表区域，可伸缩
        self.main_content_frame.grid_rowconfigure(0, weight=0)
        self.main_content_frame.grid_rowconfigure(1, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        
        # 创建数据卡片区域
        self.data_cards_frame = ttk.Frame(self.main_content_frame)
        self.data_cards_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=10)
        self.data_cards = DataCards(self.data_cards_frame)
        self.data_cards.set_dashboard_view(self)  # 设置仪表盘视图引用
        
        # 创建图表区域
        self.charts_frame = ttk.Frame(self.main_content_frame)
        self.charts_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=0, rowspan=1)
        self.charts = Charts(self.charts_frame)
        self.charts.set_dashboard_view(self)  # 设置仪表盘视图引用
        
        # 创建左侧菜单（最后创建，确保数据卡片和图表已初始化）
        self.side_menu_frame = ttk.Frame(self.content_frame, width=200)
        self.side_menu_frame.grid(row=0, column=0, sticky=tk.NS)
        self.side_menu_frame.grid_propagate(False)
        self.side_menu = SideMenu(self.side_menu_frame, self)
        
    def refresh_data(self, selected_month=None):
        """
        刷新仪表盘数据
        :param selected_month: 选中的月份，格式为YYYY-MM，None表示全部月份
        """
        # 只有当data_cards和charts属性存在时，才刷新数据和图表
        if hasattr(self, 'data_cards') and hasattr(self, 'charts'):
            # 传递月份参数给数据卡片和图表组件
            self.data_cards.refresh_data(selected_month)
            self.charts.refresh_charts(selected_month)
        
    def on_menu_select(self, menu_item):
        """
        菜单选择事件处理
        :param menu_item: 选中的菜单项
        """
        print(f"选中菜单项：{menu_item}")
        # 根据选中的菜单项更新主内容区
        # 注意：menu_item现在是翻译后的文本，我们需要使用get_text来比较
        if menu_item == self.get_text('menu_overview'):
            # 显示概览页面
            self.show_overview()
        elif menu_item == self.get_text('menu_group_data_management'):
            # 显示数据管理页面
            self.show_data_management()
        elif menu_item == self.get_text('menu_group_system_config'):
            # 显示系统配置页面
            self.show_system_config()
    
    def show_overview(self):
        """
        显示概览页面
        优化：复用现有组件，只刷新数据，避免不必要的控件销毁和重建
        """
        # 如果数据卡片和图表组件已存在，只刷新数据
        if hasattr(self, 'data_cards') and hasattr(self, 'charts'):
            # 确保组件可见
            self.data_cards_frame.grid()
            self.charts_frame.grid()
            # 刷新数据
            self.refresh_data()
        else:
            # 组件不存在时才创建
            # 数据卡片区域
            self.data_cards_frame = ttk.Frame(self.main_content_frame)
            self.data_cards_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=10)
            self.data_cards = DataCards(self.data_cards_frame)
            self.data_cards.set_dashboard_view(self)  # 设置仪表盘视图引用
            
            # 图表区域
            self.charts_frame = ttk.Frame(self.main_content_frame)
            self.charts_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=0, rowspan=1)
            self.charts = Charts(self.charts_frame)
            self.charts.set_dashboard_view(self)  # 设置仪表盘视图引用
            
            # 刷新数据
            self.refresh_data()
    
    def show_data_management(self):
        """
        显示数据管理页面
        """
        # 实现数据管理页面逻辑
        pass
    
    def show_system_config(self):
        """
        显示系统配置页面
        """
        # 实现系统配置页面逻辑
        pass
    
    def update_user_info(self):
        """
        更新用户信息
        当用户信息变更时调用，用于更新导航栏的用户信息
        """
        if hasattr(self, 'nav_bar'):
            self.nav_bar.update_user_info()
    
    def update_language(self):
        """
        更新仪表盘所有组件的语言
        """
        # 更新侧边菜单语言
        if hasattr(self, 'side_menu') and hasattr(self.side_menu, 'update_language'):
            self.side_menu.update_language()
        
        # 更新导航栏语言
        if hasattr(self, 'nav_bar') and hasattr(self.nav_bar, 'update_language'):
            self.nav_bar.update_language()
        
        # 更新数据卡片语言
        if hasattr(self, 'data_cards') and hasattr(self.data_cards, 'update_language'):
            self.data_cards.update_language()
        
        # 更新图表语言
        if hasattr(self, 'charts') and hasattr(self.charts, 'update_language'):
            self.charts.update_language()
