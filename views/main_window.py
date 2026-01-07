#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口视图
包含菜单栏、工具栏、主工作区和状态栏
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from .tenant_view import TenantView
from .meter_view import MeterView
from .price_view import PriceView
from .reading_view import ReadingView
from .charge_view import ChargeView
from .payment_view import PaymentView
from .report_view import ReportView
from .user_view import UserView
from .settlement_view import SettlementView
from .dashboard.dashboard_view import DashboardView
from .login_view import LoginWindow
from .register_view import RegisterView
from utils.backup_utils import BackupUtils
from utils.settings_utils import SettingsUtils
from utils.language_utils import LanguageUtils
import os

class MainWindow:
    """主窗口类"""
    
    def __init__(self, root, current_user=None, language_utils=None, license_manager=None):
        """
        初始化主窗口
        :param root: Tk根窗口
        :param current_user: 当前登录用户对象
        :param language_utils: 从LoginWindow传递的LanguageUtils实例
        :param license_manager: 注册管理器实例
        """
        # 初始化设置和语言工具
        self.settings = SettingsUtils()
        
        # 使用传入的LanguageUtils实例或创建新实例
        if language_utils:
            self.language_utils = language_utils
        else:
            self.language_utils = LanguageUtils()
        
        # 设置当前语言
        self.current_language = self.settings.get_setting('system', 'language', 'zh_CN')
        # 订阅语言变化事件
        self.language_utils.subscribe(self.on_language_changed)
        self.language_utils.set_language(self.current_language)
        
        # 初始化注册管理器
        self.license_manager = license_manager
        
        self.root = root
        self.root.title(self.get_dynamic_system_title())
        
        # 设置窗口图标（可选）
        # self.root.iconbitmap("icon.ico")
        
        # 当前用户信息
        self.current_user = current_user  # 从登录信息获取
        if not self.current_user:
            # 默认为admin用户
            from models.user import User
            self.current_user = User(id=1, username="admin", role="管理员", status="启用")
        
        # 存储已创建的视图实例，用于视图间通信
        self.view_instances = {}
        
        # 设置主窗口的grid布局，确保各组件正确排列
        # 第0行：工具栏，不可伸缩
        # 第1行：工作区，可伸缩
        # 第2行：状态栏，不可伸缩
        self.root.grid_rowconfigure(0, weight=0)  # 工具栏行不可伸缩
        self.root.grid_rowconfigure(1, weight=1)  # 工作区行可伸缩
        self.root.grid_rowconfigure(2, weight=0)  # 状态栏行不可伸缩
        self.root.grid_columnconfigure(0, weight=1)  # 列可伸缩
        
        # 设置窗口最小尺寸，避免界面变形
        self.root.minsize(800, 600)
        
        # 跨平台实现窗口最大化
        try:
            # 方法1：使用state('zoomed') - Windows上有效，部分Linux桌面环境也支持
            self.root.state('zoomed')
        except tk.TclError:
            try:
                # 方法2：使用attributes('-zoomed', True) - 部分系统支持
                self.root.attributes('-zoomed', True)
            except tk.TclError:
                # 方法3：获取屏幕尺寸并设置窗口大小 - 跨平台通用
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                # 设置窗口大小为屏幕尺寸，考虑不同操作系统的任务栏和标题栏
                # 减去少量像素，确保窗口不会超出屏幕边界
                self.root.geometry(f"{screen_width}x{screen_height}")
        
        # 如果以上方法都失败，使用默认尺寸
        if self.root.winfo_width() < 800 or self.root.winfo_height() < 600:
            self.root.geometry("1200x800")
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主工作区
        self.create_workspace()
        
        # 创建状态栏
        self.create_statusbar()
        
        # 使用grid布局放置各组件
        self.toolbar.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=2)
        self.workspace.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=2)
        self.statusbar.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=2)
        
        # 更新状态栏时间
        self.update_status_time()
        
    def get_text(self, key):
        """
        获取当前语言的文本
        :param key: 文本键名
        :return: 对应语言的文本
        """
        return self.language_utils.get_text(key)
    
    def on_language_changed(self, old_language, new_language):
        """
        语言变化事件处理方法
        :param old_language: 旧语言代码
        :param new_language: 新语言代码
        """
        if new_language != self.current_language:
            self.current_language = new_language
            self.settings.set_setting('system', 'language', new_language)
            # 更新主窗口标题
            self.root.title(self.get_dynamic_system_title())
            # 更新菜单栏和工具栏语言（不重新创建）
            self.update_menu_language()
            self.update_toolbar_language()
            # 更新Notebook标签页标题
            self.update_notebook_tabs_language()
            # 更新当前显示视图的语言
            self.update_current_view_language()
            # 更新状态栏语言
            self.update_status_bar_language()
    
    def update_language(self, new_language):
        """
        更新语言设置并保存
        :param new_language: 新的语言代码
        """
        # 调用language_utils的set_language方法，这将触发on_language_changed事件
        self.language_utils.set_language(new_language)
    
    def update_current_view_language(self):
        """
        更新所有视图的语言
        """
        # 更新仪表盘侧边栏菜单的语言
        if hasattr(self, 'dashboard_view') and self.dashboard_view:
            self.dashboard_view.update_language()
        
        # 更新所有已创建的视图语言
        for view_name, view_instance in self.view_instances.items():
            self.update_view_language(view_instance)
        
        # 更新状态栏语言
        self.update_status_bar_language()
        
        # 更新帮助文档窗口语言
        self.update_help_window_language()
    
    def update_help_window_language(self):
        """
        更新帮助文档窗口的语言
        """
        try:
            if hasattr(self, 'help_window') and self.help_window:
                # 检查窗口是否已被销毁
                if self.help_window.winfo_exists():
                    # 更新窗口标题
                    self.help_window.title(self.get_text('menu_help'))
                    
                    # 更新选项卡标题
                    if hasattr(self, 'help_notebook') and self.help_notebook:
                        # 检查notebook是否已被销毁
                        if self.help_notebook.winfo_exists():
                            # 获取所有选项卡
                            tabs = self.help_notebook.tabs()
                            if len(tabs) >= 3:
                                self.help_notebook.tab(tabs[0], text=self.get_text('menu_help'))
                                self.help_notebook.tab(tabs[1], text=self.get_text('technical_support'))
                                self.help_notebook.tab(tabs[2], text=self.get_text('system_about_title'))
                            
                            # 重新创建帮助文档内容
                            for i, tab_id in enumerate(tabs):
                                # 获取选项卡的frame
                                tab_frame = self.help_notebook.nametowidget(tab_id)
                                # 清空frame内容
                                for widget in tab_frame.winfo_children():
                                    widget.destroy()
                                # 重新创建内容
                                if i == 0:
                                    self.create_help_documentation(tab_frame)
                                elif i == 1:
                                    self.create_technical_support(tab_frame)
                                elif i == 2:
                                    self.create_about_system(tab_frame)
        except tk.TclError as e:
            # 忽略已销毁窗口的错误
            print(f"更新帮助窗口语言时发生错误: {str(e)}")
    
    def update_view_language(self, view_instance):
        """
        更新指定视图实例的语言
        :param view_instance: 视图实例
        """
        if hasattr(view_instance, 'update_language'):
            try:
                view_instance.update_language()
            except Exception as e:
                print(f"更新视图语言失败: {str(e)}")
    
    def update_notebook_tabs_language(self):
        """
        更新Notebook标签页标题的语言
        确保所有标签页都能被正确更新，包括组合标签和动态创建的标签页
        """
        # 获取所有标签页
        tabs = self.notebook.tabs()
        
        # 定义标签文本映射，包含中文和英文的所有可能值
        label_mapping = {
            # 欢迎页面
            'welcome': ['Welcome', '欢迎', 'Welcome', '欢迎'],
            # 租户管理
            'form_title_tenant_management': ['Tenant Management', '租户管理', 'Tenant Management', '租户管理'],
            # 水电表管理
            'form_title_meter_management': ['Meter Management', '水电表管理', 'Meter Management', '水电表管理'],
            # 价格管理
            'form_title_price_management': ['Price Management', '价格管理', 'Price Management', '价格管理'],
            # 抄表录入
            'form_title_reading_entry': ['Reading Entry', '抄表录入', 'Reading Entry', '抄表录入'],
            # 费用计算
            'form_title_charge_calculation': ['Charge Calculation', '费用计算', 'Charge Calculation', '费用计算'],
            # 收费录入
            'form_title_payment_entry': ['Payment Entry', '收费录入', 'Payment Entry', '收费录入'],
            # 费用结算
            'form_title_settlement_management': ['Settlement Management', '费用结算', 'Settlement Management', '费用结算'],
            # 报表中心
            'form_title_report_management': ['Report Center', '报表中心', 'Report Center', '报表中心'],
            # 用户管理
            'form_title_user_management': ['User Management', '用户管理', 'User Management', '用户管理'],
            # 欠费查询
            'arrears_query': ['Arrears Query', '欠费查询', 'Arrears Query', '欠费查询'],
            # 抄表历史
            'reading_management': ['Reading History', '抄表历史', 'Reading History', '抄表历史'],
            # 费用查询
            'charge_query': ['Charge Query', '费用查询', 'Charge Query', '费用查询'],
            # 收费查询
            'payment_query': ['Payment Query', '收费查询', 'Payment Query', '收费查询'],
        }
        
        for tab_id in tabs:
            current_text = self.notebook.tab(tab_id, "text")
            updated = False
            
            # 检查当前文本是否匹配任何映射值
            for key, values in label_mapping.items():
                if current_text in values or any(v in current_text for v in values):
                    self.notebook.tab(tab_id, text=self.get_text(key))
                    updated = True
                    break
            
            # 特殊处理组合标签
            if not updated and ('report' in current_text.lower() or '报表' in current_text):
                # 检查是否是租户明细报表
                if any(term in current_text.lower() for term in ['tenant', '租户', 'detail']):
                    self.notebook.tab(tab_id, text=f"{self.get_text('tenant_management')} {self.get_text('menu_report')}")
                    updated = True
                # 检查是否是收费统计报表
                elif any(term in current_text.lower() for term in ['payment', '收费', 'stat', '统计']):
                    self.notebook.tab(tab_id, text=f"{self.get_text('payment_management')} {self.get_text('menu_report')}")
                    updated = True
                # 检查是否是结算报表
                elif any(term in current_text.lower() for term in ['settlement', '结算']):
                    self.notebook.tab(tab_id, text=self.get_text('settlement_report'))
                    updated = True
            
            # 处理动态创建的标签页，直接根据当前语言重新生成标题
            if not updated:
                # 遍历所有可能的标签页类型，尝试匹配
                for key in ['form_title_tenant_management', 'form_title_meter_management', 'form_title_price_management',
                           'form_title_reading_entry', 'form_title_charge_calculation', 'form_title_payment_entry',
                           'form_title_settlement_management', 'form_title_report_management', 'form_title_user_management',
                           'arrears_query', 'reading_management', 'charge_query', 'payment_query', 'welcome']:
                    try:
                        tab_text = self.get_text(key)
                        # 检查当前标签页是否与该类型匹配
                        if tab_text.lower() in current_text.lower() or current_text.lower() in tab_text.lower() or 'welcome' in current_text.lower():
                            self.notebook.tab(tab_id, text=tab_text)
                            updated = True
                            break
                    except Exception as e:
                        print(f"Error updating tab text: {e}")
                
                # 如果仍然没有更新，尝试根据标签页内容猜测类型
                if not updated:
                    if 'tenant' in current_text.lower() or '租户' in current_text:
                        self.notebook.tab(tab_id, text=f"{self.get_text('tenant_management')} {self.get_text('menu_report')}")
                    elif 'payment' in current_text.lower() or '收费' in current_text:
                        self.notebook.tab(tab_id, text=f"{self.get_text('payment_management')} {self.get_text('menu_report')}")
                    elif 'settlement' in current_text.lower() or '结算' in current_text:
                        self.notebook.tab(tab_id, text=self.get_text('settlement_report'))
                    elif 'welcome' in current_text.lower() or '欢迎' in current_text:
                        self.notebook.tab(tab_id, text=self.get_text('welcome'))
                    else:
                        # 最后的兜底方案：尝试根据标签页ID或其他属性更新
                        for key in label_mapping:
                            try:
                                self.notebook.tab(tab_id, text=self.get_text(key))
                                updated = True
                                break
                            except:
                                pass
            
        # 确保所有未来可能被添加的标签页也使用正确的语言
        # 我们需要在各个open_xxx_management方法中确保使用当前语言
        # 这里我们可以通过更新标签文本映射
    
    def update_status_bar_language(self):
        """
        更新状态栏语言
        """
        if hasattr(self, 'user_label') and hasattr(self, 'db_info_label'):
            # 中文到英文翻译键的映射
            role_mapping = {
                '管理员': 'admin',
                '抄表员': 'reader'
            }
            status_mapping = {
                '启用': 'enabled',
                '禁用': 'disabled'
            }
            
            # 获取翻译键
            role_key = role_mapping.get(self.current_user.role, self.current_user.role)
            status_key = status_mapping.get(self.current_user.status, self.current_user.status)
            
            # 更新状态栏用户信息，对角色和状态进行翻译
            translated_role = self.get_text(role_key) if role_key else ''
            translated_status = self.get_text(status_key) if status_key else ''
            user_info = f"{self.get_text('current_user')}: {self.current_user.username} | {self.get_text('role')}: {translated_role} | {self.get_text('status')}: {translated_status}"
            self.user_label.config(text=user_info)
            
            # 更新数据库连接信息
            import os
            db_path = os.path.abspath("water_electricity.db")
            db_name = os.path.basename(db_path)
            db_dir = os.path.dirname(db_path)
            self.db_info_label.config(text=f"{self.get_text('database')}: {db_name} ({db_dir})")
            
            # 更新数据状态
            if hasattr(self, 'data_status_label'):
                self.data_status_label.config(text=f"{self.get_text('data_status')}: {self.get_text('normal')}")
    
    def refresh_view(self, view_name):
        """
        通知指定视图刷新数据
        :param view_name: 视图名称，如 "charge" 表示费用管理视图
        """
        if view_name in self.view_instances:
            view = self.view_instances[view_name]
            # 检查视图是否有load_charge_list方法（费用管理视图）
            if hasattr(view, "load_charge_list"):
                view.load_charge_list()
            # 检查视图是否有load_payment_list方法（收费管理视图）
            elif hasattr(view, "load_payment_list"):
                view.load_payment_list()
            # 检查视图是否有load_meter_list方法（水电表管理视图）
            elif hasattr(view, "load_meter_list"):
                view.load_meter_list()
            # 检查视图是否有load_price_list方法（价格管理视图）
            elif hasattr(view, "load_price_list"):
                view.load_price_list()
            # 检查视图是否有load_tenant_list方法（租户管理视图）
            elif hasattr(view, "load_tenant_list"):
                view.load_tenant_list()
        
        # 刷新仪表盘视图，无论哪个视图数据发生变化
        if hasattr(self, "dashboard_view"):
            self.dashboard_view.refresh_data()
    
    def create_menu(self):
        """
        创建菜单栏
        """
        self.menubar = tk.Menu(self.root)
        
        # 文件菜单
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label=self.get_text('menu_logout'), command=self.quit_app)
        self.menubar.add_cascade(label=self.get_text('menu_file'), menu=self.file_menu)
        
        # 基础信息菜单
        self.base_info_menu = tk.Menu(self.menubar, tearoff=0)
        self.base_info_menu.add_command(label=self.get_text('menu_tenant'), command=self.open_tenant_management)
        self.base_info_menu.add_command(label=self.get_text('menu_meter'), command=self.open_meter_management)
        self.base_info_menu.add_command(label=self.get_text('menu_price'), command=self.open_price_management)
        self.menubar.add_cascade(label=self.get_text('menu_base_info'), menu=self.base_info_menu)
        
        # 抄表管理菜单
        self.reading_menu = tk.Menu(self.menubar, tearoff=0)
        self.reading_menu.add_command(label=self.get_text('menu_meter_reading'), command=self.open_meter_reading)
        self.menubar.add_cascade(label=self.get_text('menu_reading'), menu=self.reading_menu)
        
        # 费用管理菜单
        self.charge_menu = tk.Menu(self.menubar, tearoff=0)
        self.charge_menu.add_command(label=self.get_text('menu_charge_calculation'), command=self.open_charge_calculation)
        self.menubar.add_cascade(label=self.get_text('menu_charge'), menu=self.charge_menu)
        
        # 收费管理菜单
        self.payment_menu = tk.Menu(self.menubar, tearoff=0)
        self.payment_menu.add_command(label=self.get_text('menu_payment_entry'), command=self.open_payment_entry)
        self.payment_menu.add_command(label=self.get_text('menu_settlement'), command=self.open_settlement_management)
        self.menubar.add_cascade(label=self.get_text('menu_payment'), menu=self.payment_menu)
        
        # 报表中心菜单
        self.report_menu = tk.Menu(self.menubar, tearoff=0)
        self.report_menu.add_command(label=self.get_text('menu_monthly_report'), command=self.open_monthly_report)
        self.menubar.add_cascade(label=self.get_text('menu_report'), menu=self.report_menu)
        
        # 系统设置菜单
        self.system_menu = tk.Menu(self.menubar, tearoff=0)
        self.system_menu.add_command(label=self.get_text('menu_user_management'), command=self.open_user_management)
        self.system_menu.add_command(label=self.get_text('menu_data_backup'), command=self.open_data_backup)
        self.system_menu.add_command(label=self.get_text('menu_data_restore'), command=self.open_data_restore)
        self.system_menu.add_command(label=self.get_text('menu_data_initialization'), command=self.open_data_initialization)
        self.system_menu.add_command(label=self.get_text('menu_system_settings'), command=self.open_system_settings)
        # 添加注册菜单项
        self.system_menu.add_separator()
        self.system_menu.add_command(label="软件注册", command=self.open_register)
        self.system_menu.add_command(label="注册信息", command=self.show_license_info)
        self.menubar.add_cascade(label=self.get_text('menu_system_settings'), menu=self.system_menu)
        
        # 帮助菜单
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label=self.get_text('menu_help'), command=self.open_help)
        self.help_menu.add_command(label=self.get_text('menu_about'), command=self.open_about)
        self.menubar.add_cascade(label=self.get_text('menu_help'), menu=self.help_menu)
        
        # 设置菜单栏
        self.root.config(menu=self.menubar)
        
    def update_menu_language(self):
        """
        更新菜单栏语言
        重新创建整个菜单栏，确保所有菜单文本都正确更新
        """
        # 保存当前选中的菜单项（如果有）
        current_selected_tab = None
        if hasattr(self, 'notebook'):
            current_selected_tab = self.notebook.select()
        
        # 重新创建菜单栏
        self.create_menu()
        
        # 恢复之前选中的标签页（如果有）
        if current_selected_tab and hasattr(self, 'notebook'):
            try:
                self.notebook.select(current_selected_tab)
            except:
                pass
    
    def create_toolbar(self):
        """
        创建工具栏
        """
        # 如果工具栏已存在，先从根窗口移除
        if hasattr(self, 'toolbar') and self.toolbar.winfo_exists():
            self.toolbar.grid_forget()
        
        # 创建新的工具栏
        self.toolbar = ttk.Frame(self.root, height=40, relief=tk.RAISED)
        
        # 租户管理按钮
        self.tenant_btn = ttk.Button(self.toolbar, text=self.get_text('menu_tenant'), width=10, command=self.open_tenant_management)
        self.tenant_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # 抄表录入按钮
        self.reading_btn = ttk.Button(self.toolbar, text=self.get_text('menu_meter_reading'), width=10, command=self.open_meter_reading)
        self.reading_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # 费用计算按钮
        self.calc_btn = ttk.Button(self.toolbar, text=self.get_text('menu_charge_calculation'), width=10, command=self.open_charge_calculation)
        self.calc_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # 收费录入按钮
        self.payment_btn = ttk.Button(self.toolbar, text=self.get_text('menu_payment_entry'), width=10, command=self.open_payment_entry)
        self.payment_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # 费用结算按钮
        self.settlement_btn = ttk.Button(self.toolbar, text=self.get_text('menu_settlement'), width=10, command=self.open_settlement_management)
        self.settlement_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # 报表生成按钮
        self.report_btn = ttk.Button(self.toolbar, text=self.get_text('menu_monthly_report'), width=10, command=self.open_monthly_report)
        self.report_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # 分隔线
        separator = ttk.Separator(self.toolbar, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 退出按钮
        self.quit_btn = ttk.Button(self.toolbar, text=self.get_text('menu_logout'), width=10, command=self.quit_app)
        self.quit_btn.pack(side=tk.RIGHT, padx=2, pady=5)
        
        # 重新登录按钮
        self.relogin_btn = ttk.Button(self.toolbar, text=self.get_text('menu_relogin'), width=10, command=self.relogin)
        self.relogin_btn.pack(side=tk.RIGHT, padx=2, pady=5)
        
        # 重新使用grid布局放置工具栏
        self.toolbar.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=2)
        
    def update_toolbar_language(self):
        """
        更新工具栏语言
        只更新现有按钮的文本，不重新创建整个工具栏
        """
        # 更新按钮文本
        if hasattr(self, 'tenant_btn'):
            self.tenant_btn.config(text=self.get_text('menu_tenant'))
        if hasattr(self, 'reading_btn'):
            self.reading_btn.config(text=self.get_text('menu_meter_reading'))
        if hasattr(self, 'calc_btn'):
            self.calc_btn.config(text=self.get_text('menu_charge_calculation'))
        if hasattr(self, 'payment_btn'):
            self.payment_btn.config(text=self.get_text('menu_payment_entry'))
        if hasattr(self, 'settlement_btn'):
            self.settlement_btn.config(text=self.get_text('menu_settlement'))
        if hasattr(self, 'report_btn'):
            self.report_btn.config(text=self.get_text('menu_monthly_report'))
        if hasattr(self, 'quit_btn'):
            self.quit_btn.config(text=self.get_text('menu_logout'))
        if hasattr(self, 'relogin_btn'):
            self.relogin_btn.config(text=self.get_text('menu_relogin'))
    
    def create_workspace(self):
        """
        创建主工作区
        使用Notebook组件实现标签页布局
        """
        self.workspace = ttk.Frame(self.root)
        
        # 创建Notebook
        self.notebook = ttk.Notebook(self.workspace)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 添加欢迎页面（仪表盘）
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text=self.get_text('welcome'))
        
        # 创建仪表盘视图，并传递MainWindow实例
        self.dashboard_view = DashboardView(welcome_frame, self)
        
        # 添加其他功能页面的占位符
        self.tenant_frame = ttk.Frame(self.notebook)
        self.meter_frame = ttk.Frame(self.notebook)
        self.price_frame = ttk.Frame(self.notebook)
        self.reading_frame = ttk.Frame(self.notebook)
        self.charge_frame = ttk.Frame(self.notebook)
        self.payment_frame = ttk.Frame(self.notebook)
        self.settlement_frame = ttk.Frame(self.notebook)
        self.report_frame = ttk.Frame(self.notebook)
        self.user_frame = ttk.Frame(self.notebook)
    
    def create_statusbar(self):
        """
        创建状态栏
        使用grid布局替代pack布局，解决在不同窗口尺寸下的显示问题
        """
        self.statusbar = ttk.Frame(self.root, relief=tk.SUNKEN)  # ttk.Frame不支持ipady参数，移除该参数
        
        # 配置grid布局
        self.statusbar.grid_columnconfigure(2, weight=1)  # 中间列（数据库信息）可伸缩
        self.statusbar.grid_rowconfigure(0, weight=1)  # 第一行可伸缩
        
        # 中文到英文翻译键的映射
        role_mapping = {
            '管理员': 'admin',
            '抄表员': 'reader'
        }
        status_mapping = {
            '启用': 'enabled',
            '禁用': 'disabled'
        }
        
        # 获取翻译键
        role_key = role_mapping.get(self.current_user.role, self.current_user.role)
        status_key = status_mapping.get(self.current_user.status, self.current_user.status)
        
        # 当前用户信息，显示用户名、角色和状态
        translated_role = self.get_text(role_key) if role_key else ''
        translated_status = self.get_text(status_key) if status_key else ''
        user_info = f"{self.get_text('current_user')}: {self.current_user.username} | {self.get_text('role')}: {translated_role} | {self.get_text('status')}: {translated_status}"
        self.user_label = ttk.Label(self.statusbar, text=user_info)
        self.user_label.grid(row=0, column=0, sticky=tk.W, padx=(10, 5), pady=(3, 3))
        
        # 分隔线
        separator = ttk.Separator(self.statusbar, orient=tk.VERTICAL)
        separator.grid(row=0, column=1, sticky=tk.NS, padx=5, pady=(3, 3))
        
        # 数据库连接信息
        import os
        db_path = os.path.abspath("water_electricity.db")
        db_name = os.path.basename(db_path)
        db_dir = os.path.dirname(db_path)
        self.db_info_label = ttk.Label(self.statusbar, text=f"{self.get_text('database')}: {db_name} ({db_dir})")
        self.db_info_label.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(3, 3))  # 只左对齐，不填充整个列
        
        # 分隔线
        separator2 = ttk.Separator(self.statusbar, orient=tk.VERTICAL)
        separator2.grid(row=0, column=3, sticky=tk.NS, padx=5, pady=(3, 3))
        
        # 数据状态
        self.data_status_label = ttk.Label(self.statusbar, text=f"{self.get_text('data_status')}: {self.get_text('normal')}")
        self.data_status_label.grid(row=0, column=4, sticky=tk.E, padx=(5, 10), pady=(3, 3))
        
        # 系统时间
        self.time_label = ttk.Label(self.statusbar, text="")
        self.time_label.grid(row=0, column=5, sticky=tk.E, padx=(5, 10), pady=(3, 3))
    
    def update_user_info(self, user):
        """
        更新用户信息
        :param user: 用户对象
        """
        self.current_user = user
        
        # 中文到英文翻译键的映射
        role_mapping = {
            '管理员': 'admin',
            '抄表员': 'reader'
        }
        status_mapping = {
            '启用': 'enabled',
            '禁用': 'disabled'
        }
        
        # 获取翻译键
        role_key = role_mapping.get(self.current_user.role, self.current_user.role)
        status_key = status_mapping.get(self.current_user.status, self.current_user.status)
        
        # 更新状态栏用户信息
        translated_role = self.get_text(role_key) if role_key else ''
        translated_status = self.get_text(status_key) if status_key else ''
        user_info = f"{self.get_text('current_user')}: {self.current_user.username} | {self.get_text('role')}: {translated_role} | {self.get_text('status')}: {translated_status}"
        self.user_label.config(text=user_info)
        
        # 更新仪表盘导航栏用户信息
        if hasattr(self, 'dashboard_view'):
            self.dashboard_view.update_user_info()
    
    def update_status_time(self):
        """
        更新状态栏时间
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        # 每秒更新一次
        self.root.after(1000, self.update_status_time)
    
    # 菜单和工具栏事件处理函数
    def open_tenant_management(self):
        """
        打开租户管理界面
        """
        # 检查租户管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('form_title_tenant_management'):
                self.notebook.select(tab_id)
                return
        
        # 先将frame添加到notebook中，然后再创建视图实例
        self.notebook.add(self.tenant_frame, text=self.get_text('form_title_tenant_management'))
        self.notebook.select(self.tenant_frame)
        
        # 创建租户管理视图
        tenant_view = TenantView(self.tenant_frame, self, self.language_utils)
        # 存储视图实例
        self.view_instances["tenant"] = tenant_view
    
    def open_meter_management(self):
        """
        打开水电表管理界面
        """
        # 检查水电表管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('form_title_meter_management'):
                self.notebook.select(tab_id)
                # 如果视图实例已经存在，刷新数据
                if "meter" in self.view_instances:
                    meter_view = self.view_instances["meter"]
                    if hasattr(meter_view, "load_meter_list"):
                        meter_view.load_meter_list()
                        # 刷新租户列表
                        if hasattr(meter_view, "load_tenants_to_form"):
                            meter_view.load_tenants_to_form()
                return
        
        # 先将frame添加到notebook中，然后再创建视图实例
        self.notebook.add(self.meter_frame, text=self.get_text('form_title_meter_management'))
        self.notebook.select(self.meter_frame)
        
        # 创建水电表管理视图
        meter_view = MeterView(self.meter_frame, self.language_utils)
        # 存储视图实例
        self.view_instances["meter"] = meter_view
    
    def open_price_management(self):
        """
        打开价格管理界面
        """
        # 检查价格管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('form_title_price_management'):
                self.notebook.select(tab_id)
                return
        
        # 先将frame添加到notebook中，然后再创建视图实例
        # 这样可以确保视图中的组件在创建时已经完全集成到Tkinter的事件循环中
        self.notebook.add(self.price_frame, text=self.get_text('form_title_price_management'))
        self.notebook.select(self.price_frame)
        
        # 创建价格管理视图并存储实例
        price_view = PriceView(self.price_frame, self.language_utils)
        self.view_instances["price"] = price_view
    
    def open_meter_reading(self):
        """
        打开抄表录入界面
        """
        # 检查抄表管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('form_title_reading_entry'):
                self.notebook.select(tab_id)
                return
        
        # 先将frame添加到notebook中，然后再创建视图实例
        self.notebook.add(self.reading_frame, text=self.get_text('form_title_reading_entry'))
        self.notebook.select(self.reading_frame)
        
        # 创建抄表管理视图并存储实例
        reading_view = ReadingView(self.reading_frame, self.language_utils)
        self.view_instances["reading"] = reading_view
    
    def open_reading_history(self):
        """
        打开抄表历史查询界面
        """
        # 检查抄表历史查询页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('reading_management'):
                self.notebook.select(tab_id)
                return
        
        # 创建抄表历史查询视图并添加到notebook
        # 创建新的frame用于抄表历史查询
        self.reading_history_frame = ttk.Frame(self.notebook)
        reading_view = ReadingView(self.reading_history_frame, self.language_utils)
        self.view_instances["reading_history"] = reading_view
        self.notebook.add(self.reading_history_frame, text=self.get_text('reading_management'))
        self.notebook.select(self.reading_history_frame)
    
    def open_charge_calculation(self):
        """
        打开费用计算界面
        """
        # 检查费用管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('form_title_charge_calculation'):
                self.notebook.select(tab_id)
                return
        
        # 先将frame添加到notebook中，然后再创建视图实例
        self.notebook.add(self.charge_frame, text=self.get_text('form_title_charge_calculation'))
        self.notebook.select(self.charge_frame)
        
        # 创建费用管理视图
        charge_view = ChargeView(self.charge_frame, self.language_utils)
        # 存储视图实例
        self.view_instances["charge"] = charge_view
    
    def open_charge_query(self):
        """
        打开费用查询界面
        """
        # 检查费用查询页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('charge_query'):
                self.notebook.select(tab_id)
                return
        
        # 创建费用查询视图并添加到notebook
        # 复用现有的charge_frame和ChargeView
        charge_view = ChargeView(self.charge_frame, self.language_utils)
        # 存储视图实例
        self.view_instances["charge"] = charge_view
        self.notebook.add(self.charge_frame, text=self.get_text('charge_query'))
        self.notebook.select(self.charge_frame)
    
    def open_payment_entry(self):
        """
        打开收费录入界面
        """
        # 检查收费管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('form_title_payment_entry'):
                self.notebook.select(tab_id)
                return
        
        # 先将frame添加到notebook中，然后再创建视图实例
        self.notebook.add(self.payment_frame, text=self.get_text('form_title_payment_entry'))
        self.notebook.select(self.payment_frame)
        
        # 创建收费管理视图
        payment_view = PaymentView(self.payment_frame, self, self.language_utils)
        # 存储视图实例
        self.view_instances["payment"] = payment_view
    
    def open_payment_query(self):
        """
        打开收费查询界面
        """
        # 检查收费查询页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('payment_query'):
                self.notebook.select(tab_id)
                return
        
        # 创建收费查询视图并添加到notebook
        # 复用现有的payment_frame和PaymentView
        payment_view = PaymentView(self.payment_frame, self, self.language_utils)
        # 存储视图实例
        self.view_instances["payment"] = payment_view
        self.notebook.add(self.payment_frame, text=self.get_text('payment_query'))
        self.notebook.select(self.payment_frame)
    
    def open_arrears_management(self):
        """
        打开欠费管理界面
        """
        # 检查欠费管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('arrears_query'):
                self.notebook.select(tab_id)
                return
        
        # 创建欠费管理视图并添加到notebook
        payment_view = PaymentView(self.payment_frame, self, self.language_utils)
        # 存储视图实例
        self.view_instances["payment"] = payment_view
        self.notebook.add(self.payment_frame, text=self.get_text('arrears_query'))
        self.notebook.select(self.payment_frame)
    
    def open_settlement_management(self):
        """
        打开结算管理界面
        """
        # 检查结算管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('form_title_settlement_management'):
                self.notebook.select(tab_id)
                return
        
        # 先将frame添加到notebook中，然后再创建视图实例
        self.notebook.add(self.settlement_frame, text=self.get_text('form_title_settlement_management'))
        self.notebook.select(self.settlement_frame)
        
        # 创建结算管理视图并存储实例
        settlement_view = SettlementView(self.settlement_frame, self.language_utils)
        self.view_instances["settlement"] = settlement_view
    
    def open_monthly_report(self):
        """
        打开月度报表界面
        """
        # 检查报表管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('form_title_report_management'):
                self.notebook.select(tab_id)
                return
        
        # 先将frame添加到notebook中，然后再创建视图实例
        self.notebook.add(self.report_frame, text=self.get_text('form_title_report_management'))
        self.notebook.select(self.report_frame)
        
        # 创建报表管理视图并存储实例
        report_view = ReportView(self.report_frame, self.language_utils)
        self.view_instances["report"] = report_view
    
    def open_tenant_detail_report(self):
        """
        打开租户明细报表界面
        """
        # 检查租户明细报表页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == f"{self.get_text('tenant_management')} {self.get_text('menu_report')}":
                self.notebook.select(tab_id)
                return
        
        # 创建租户明细报表视图并添加到notebook
        # 创建新的frame用于租户明细报表
        self.tenant_detail_report_frame = ttk.Frame(self.notebook)
        report_view = ReportView(self.tenant_detail_report_frame, self.language_utils)
        self.view_instances["tenant_detail_report"] = report_view
        self.notebook.add(self.tenant_detail_report_frame, text=f"{self.get_text('tenant_management')} {self.get_text('menu_report')}")
        self.notebook.select(self.tenant_detail_report_frame)
    
    def open_payment_stat_report(self):
        """
        打开收费统计报表界面
        """
        # 检查收费统计报表页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == f"{self.get_text('payment_management')} {self.get_text('menu_report')}":
                self.notebook.select(tab_id)
                return
        
        # 创建收费统计报表视图并添加到notebook
        # 创建新的frame用于收费统计报表
        self.payment_stat_report_frame = ttk.Frame(self.notebook)
        report_view = ReportView(self.payment_stat_report_frame, self.language_utils)
        self.view_instances["payment_stat_report"] = report_view
        self.notebook.add(self.payment_stat_report_frame, text=f"{self.get_text('payment_management')} {self.get_text('menu_report')}")
        self.notebook.select(self.payment_stat_report_frame)
    
    def open_user_management(self):
        """
        打开用户管理界面
        """
        # 检查用户管理页面是否已经存在
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == self.get_text('form_title_user_management'):
                self.notebook.select(tab_id)
                return
        
        # 创建用户管理视图并存储实例
        user_view = UserView(self.user_frame, self.current_user, self.language_utils)
        self.view_instances["user"] = user_view
        self.notebook.add(self.user_frame, text=self.get_text('form_title_user_management'))
        self.notebook.select(self.user_frame)
    
    def open_data_backup(self):
        """
        打开数据备份界面
        """
        # 获取数据库路径
        db_path = os.path.join(os.getcwd(), "water_electricity.db")
        
        # 执行备份
        backup_path = BackupUtils.backup_database(db_path)
        
        if backup_path:
            messagebox.showinfo(self.get_text('success'), self.get_text('system_backup_success').format(backup_path))
        else:
            messagebox.showerror(self.get_text('error'), self.get_text('system_backup_fail'))
    
    def open_data_restore(self):
        """
        打开数据恢复界面
        """
        # 获取备份目录
        backup_dir = os.path.join(os.getcwd(), "backup")
        
        # 检查备份目录是否存在
        if not os.path.exists(backup_dir):
            messagebox.showwarning(self.get_text('warning'), self.get_text('system_no_backup_dir'))
            return
        
        # 获取备份文件列表
        backup_files = BackupUtils.get_backup_list(backup_dir)
        
        if not backup_files:
            messagebox.showwarning(self.get_text('warning'), self.get_text('system_no_backup_files'))
            return
        
        # 创建备份恢复窗口
        restore_window = tk.Toplevel(self.root)
        restore_window.title(self.get_text('data_restore'))
        
        # 动态计算窗口高度：根据备份文件数量调整
        # 基础高度 + 列表高度（每行22像素） + 分隔线高度 + 按钮区域高度
        base_height = 150  # 基础高度（标题、标签、边距等）
        list_height = min(len(backup_files), 15) * 22  # 列表高度，最多15行
        separator_height = 10  # 分隔线高度
        button_height = 50  # 按钮区域高度（包含边距）
        window_height = base_height + list_height + separator_height + button_height
        restore_window.geometry(f"500x{window_height}")
        
        # 允许窗口调整大小
        restore_window.resizable(True, True)
        
        # 创建备份文件列表
        ttk.Label(restore_window, text=self.get_text('select_backup_file'), font=("Arial", 12)).pack(pady=10)
        
        # 创建滚动列表
        list_frame = ttk.Frame(restore_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建列表控件：根据文件数量动态调整高度，最多显示15行
        columns = ("filename", "date")
        tree_height = min(len(backup_files), 15)
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=tree_height)
        
        # 设置列标题和宽度
        tree.heading("filename", text=self.get_text('filename'))
        tree.column("filename", width=200, anchor="w")
        
        tree.heading("date", text=self.get_text('backup_date'))
        tree.column("date", width=200, anchor="w")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 填充备份文件列表
        for backup_file in backup_files:
            # 获取备份日期
            backup_datetime = BackupUtils.get_backup_info(backup_file)
            if backup_datetime:
                backup_date_str = backup_datetime.strftime("%Y-%m-%d %H:%M:%S")
            else:
                backup_date_str = self.get_text('unknown_date')
            
            tree.insert("", tk.END, values=(backup_file, backup_date_str))
        
        # 恢复按钮
        def on_restore():
            """
            执行恢复操作
            """
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning(self.get_text('warning'), self.get_text('system_select_backup_file'))
                return
            
            # 获取选中的备份文件名
            item_id = selected_items[0]
            values = tree.item(item_id, "values")
            backup_filename = values[0]
            
            # 确认恢复
            if messagebox.askyesno(self.get_text('system_confirm_delete'), self.get_text('system_confirm_restore').format(backup_filename)):
                # 执行恢复
                backup_path = os.path.join(backup_dir, backup_filename)
                db_path = os.path.join(os.getcwd(), "water_electricity.db")
                
                if BackupUtils.restore_database(backup_path, db_path):
                    messagebox.showinfo(self.get_text('success'), self.get_text('system_restore_success'))
                    restore_window.destroy()
                else:
                    messagebox.showerror(self.get_text('error'), self.get_text('system_restore_fail'))
        
        # 添加一个分隔线
        ttk.Separator(restore_window, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=(10, 5))
        
        # 创建按钮容器框架
        button_frame = ttk.Frame(restore_window, height=50)
        button_frame.pack(fill=tk.X, padx=20, pady=(5, 15))
        # 允许框架内容决定其实际高度
        button_frame.pack_propagate(False)
        
        # 创建一个内部框架来容纳按钮，居中对齐
        inner_button_frame = ttk.Frame(button_frame)
        inner_button_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 恢复按钮
        restore_button = ttk.Button(inner_button_frame, text=self.get_text('button_restore'), command=on_restore, width=12)
        restore_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 取消按钮
        cancel_button = ttk.Button(inner_button_frame, text=self.get_text('button_cancel'), command=restore_window.destroy, width=12)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def open_system_settings(self):
        """
        打开系统设置界面
        只有管理员用户才能访问系统设置
        """
        # 检查用户权限，只有管理员才能访问系统设置
        if self.current_user.role != "管理员":
            messagebox.showerror(self.get_text('error'), self.get_text('system_admin_only'))
            return
            
        # 初始化系统设置工具
        self.settings = SettingsUtils()
        
        # 创建系统设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title(self.get_text('menu_system_settings'))
        settings_window.geometry("800x600")
        
        # 创建设置选项卡
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 抄表设置
        reading_frame = ttk.Frame(notebook)
        notebook.add(reading_frame, text=self.get_text('tab_reading_settings'))
        
        # 抄表设置内容
        ttk.Label(reading_frame, text=self.get_text('label_default_reading_day')).grid(row=0, column=0, sticky=tk.E, padx=10, pady=10)
        default_reading_day = ttk.Entry(reading_frame, width=10)
        default_reading_day.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        default_reading_day.insert(0, self.settings.get_setting('reading', 'default_reading_day', '25'))
        
        ttk.Label(reading_frame, text=self.get_text('label_reading_time_format')).grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)
        reading_time_format = ttk.Entry(reading_frame, width=20)
        reading_time_format.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        reading_time_format.insert(0, self.settings.get_setting('reading', 'reading_time_format', '%Y-%m-%d'))
        
        ttk.Label(reading_frame, text=self.get_text('label_max_usage_difference')).grid(row=2, column=0, sticky=tk.E, padx=10, pady=10)
        max_usage_difference = ttk.Entry(reading_frame, width=10)
        max_usage_difference.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        max_usage_difference.insert(0, self.settings.get_setting('reading', 'max_usage_difference', '200'))
        
        # 系统设置
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text=self.get_text('tab_system_settings'))
        
        # 系统设置内容
        ttk.Label(system_frame, text=self.get_text('label_auto_backup')).grid(row=0, column=0, sticky=tk.E, padx=10, pady=10)
        auto_backup_var = tk.BooleanVar()
        auto_backup_var.set(self.settings.get_setting('system', 'auto_backup', 'false').lower() == 'true')
        ttk.Checkbutton(system_frame, variable=auto_backup_var, text=self.get_text('checkbox_enable_auto_backup')).grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        ttk.Label(system_frame, text=self.get_text('label_backup_interval_days')).grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)
        backup_interval = ttk.Entry(system_frame, width=10)
        backup_interval.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        backup_interval.insert(0, self.settings.get_setting('system', 'backup_interval_days', '7'))
        
        ttk.Label(system_frame, text=self.get_text('label_language')).grid(row=2, column=0, sticky=tk.E, padx=10, pady=10)
        language_var = tk.StringVar()
        language_combo = ttk.Combobox(system_frame, textvariable=language_var, values=['zh_CN', 'en_US'])
        language_combo.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        language_combo.set(self.settings.get_setting('system', 'language', 'zh_CN'))
        
        # 语言选择事件处理
        def on_language_change(event):
            """
            语言选择变化事件处理
            """
            new_language = language_var.get()
            self.update_language(new_language)
        
        language_combo.bind("<<ComboboxSelected>>", on_language_change)
        
        # 软件信息模块
        ttk.Separator(system_frame, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=15)
        software_info_label = ttk.Label(system_frame, text=self.get_text('software_info'), font=('', 11, 'bold'))
        software_info_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=20, pady=10)
        
        # 创建软件信息框架
        software_info_frame = ttk.LabelFrame(system_frame, padding=15)
        software_info_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=20, pady=10)
        
        # 软件信息字段配置
        software_info_fields = [
            {"key": "software_brand", "label": self.get_text('software_brand'), "default": "水电费抄收管理系统"},
            {"key": "software_name", "label": self.get_text('software_name'), "default": "水电费抄收管理系统"},
            {"key": "software_version", "label": self.get_text('software_version'), "default": "1.0.0"},
            {"key": "developer", "label": self.get_text('developer'), "default": "llm"},
            {"key": "development_date", "label": self.get_text('development_date'), "default": "2025-12-30"}
        ]
        
        # 存储Entry组件引用，用于保存设置
        self.software_info_entries = {}
        
        # 创建标签和数据显示区域（只读）
        row_idx = 0
        for field in software_info_fields:
            # 标签区域 - 次要文本样式
            label = ttk.Label(software_info_frame, text=field["label"] + ":", font=('', 10, 'normal'))
            label.grid(row=row_idx, column=0, sticky=tk.E, padx=10, pady=10)
            
            # 数据显示区域 - 主要内容文本样式，设置为只读状态
            # 从配置文件读取值，若无则使用默认值
            current_value = self.settings.get_setting('software', field["key"], field["default"])
            
            # 创建一个Frame作为容器，用于设置背景色
            entry_container = ttk.Frame(software_info_frame)
            entry_container.grid(row=row_idx, column=1, sticky=tk.W, padx=10, pady=10)
            
            # 设置容器的背景色
            entry_container.configure(style='ReadOnlyFrame.TFrame')
            
            # 创建Entry组件，使用常规状态，通过其他方式实现只读
            entry = ttk.Entry(entry_container, font=('', 10, 'normal'), width=40)
            entry.insert(0, current_value)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # 禁用Entry组件，实现只读效果
            entry.configure(state='disabled')
            entry.bind('<FocusIn>', lambda e: e.widget.blur() if hasattr(e.widget, 'blur') else None)
            
            # 存储Entry引用
            self.software_info_entries[field["key"]] = entry
            
            row_idx += 1
        
        # 设置列宽，确保布局美观
        software_info_frame.columnconfigure(1, weight=1)
        
        # 为system_frame添加列宽配置，确保软件信息框架能正确显示
        system_frame.columnconfigure(0, weight=0)
        system_frame.columnconfigure(1, weight=1)
        
        # 保存按钮
        def on_save_settings():
            """
            保存设置
            """
            try:
                # 保存抄表设置
                self.settings.set_setting('reading', 'default_reading_day', default_reading_day.get())
                self.settings.set_setting('reading', 'reading_time_format', reading_time_format.get())
                self.settings.set_setting('reading', 'max_usage_difference', max_usage_difference.get())
                
                # 保存系统设置
                self.settings.set_setting('system', 'auto_backup', str(auto_backup_var.get()).lower())
                self.settings.set_setting('system', 'backup_interval_days', backup_interval.get())
                
                # 软件信息字段为只读，无需保存（保持配置文件中原值不变）
                
                # 保存语言设置并立即更新界面
                new_language = language_var.get()
                self.settings.set_setting('system', 'language', new_language)
                # 调用update_language确保所有界面元素立即更新
                self.update_language(new_language)
                
                messagebox.showinfo(self.get_text('success'), self.get_text('success_save_settings'))
                settings_window.destroy()
            except Exception as e:
                messagebox.showerror(self.get_text('error'), f"{self.get_text('error_save_settings')}{str(e)}")
        
        ttk.Button(settings_window, text=self.get_text('button_save'), command=on_save_settings).pack(side=tk.RIGHT, padx=20, pady=10)
        




        # 价格设置功能已移除，相关代码已清理
        ttk.Button(settings_window, text=self.get_text('button_cancel'), command=settings_window.destroy).pack(side=tk.RIGHT, padx=20, pady=10)
    
    def open_help(self):
        """
        打开使用帮助文档窗口
        """
        # 创建帮助文档窗口
        help_window = tk.Toplevel(self.root)
        help_window.title(self.get_text('menu_help'))
        help_window.geometry("850x600")
        help_window.minsize(650, 500)
        
        # 居中显示窗口
        self.center_window(help_window)
        
        # 创建Notebook用于多选项卡帮助
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 帮助文档选项卡
        doc_frame = ttk.Frame(notebook)
        notebook.add(doc_frame, text=self.get_text('menu_help'))
        
        # 添加帮助文档内容
        self.create_help_documentation(doc_frame)
        
        # 技术支持选项卡
        support_frame = ttk.Frame(notebook)
        notebook.add(support_frame, text=self.get_text('technical_support'))
        
        # 添加技术支持内容
        self.create_technical_support(support_frame)
        
        # 关于系统选项卡
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text=self.get_text('system_about_title'))
        
        # 添加关于系统内容
        self.create_about_system(about_frame)
        
        # 存储帮助窗口引用，以便语言切换时更新
        self.help_window = help_window
        self.help_notebook = notebook
    
    def get_dynamic_system_title(self):
        """
        从软件信息数据源中动态获取字段值，生成软件标题
        :return: 动态生成的软件标题字符串
        """
        # 从配置文件中获取软件信息
        settings = SettingsUtils()
        
        # 动态获取三个字段的值
        software_brand = settings.get_setting('software', 'software_brand', self.get_text("window_title"))
        software_name = settings.get_setting('software', 'software_name', self.get_text("window_title"))
        software_version = settings.get_setting('software', 'software_version', '1.0.0')
        
        # 基础标题
        base_title = f"{software_brand}{software_name}v{software_version}"
        
        # 添加注册状态
        if hasattr(self, 'license_manager') and self.license_manager:
            license_display = self.license_manager.get_license_display_info()
            base_title += f" {license_display}"
        else:
            base_title += " [未注册]"
        
        return base_title
    
    def open_register(self):
        """
        打开软件注册窗口
        """
        register_view = RegisterView(self.root, self.license_manager)
        register_view.show()
        
        # 注册成功后刷新主窗口标题
        self.root.title(self.get_dynamic_system_title())
    
    def show_license_info(self):
        """
        显示注册信息
        """
        if not self.license_manager:
            messagebox.showinfo("注册信息", "未初始化注册管理器")
            return
        
        status = self.license_manager.get_registration_status()
        
        if not status["is_registered"]:
            messagebox.showinfo("注册信息", "软件尚未注册")
            return
        
        # 格式化注册信息
        license_type = status["license_type_name"]
        issued_at = datetime.fromtimestamp(status["issued_at"]).strftime("%Y-%m-%d %H:%M:%S")
        expires_at = datetime.fromtimestamp(status["expires_at"]).strftime("%Y-%m-%d %H:%M:%S")
        remaining_days = status["remaining_days"]
        features = ", ".join(status["features"]) if status["features"] else "无"
        
        info_text = f"授权类型: {license_type}\n"
        info_text += f"颁发时间: {issued_at}\n"
        info_text += f"到期时间: {expires_at}\n"
        info_text += f"剩余天数: {remaining_days} 天\n"
        info_text += f"功能权限: {features}\n"
        info_text += f"机器ID: {status['machine_id'][:16]}..."
        
        messagebox.showinfo("注册信息", info_text)
    
    def open_about(self):
        """
        打开关于系统
        """
        # 使用动态生成的系统标题
        dynamic_title = self.get_dynamic_system_title()
        about_content = self.get_text('system_about_content').format(dynamic_title)
        messagebox.showinfo(self.get_text('system_about_title'), about_content)
    
    def create_help_documentation(self, parent):
        """
        创建帮助文档内容
        :param parent: 父容器
        """
        # 创建主容器框架，实现框架化布局
        main_container = ttk.Frame(parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # 创建标题区域
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, padx=10, pady=(20, 10))
        
        # 添加主标题，使用系统默认字体，11号，加粗
        title_label = ttk.Label(title_frame, text=self.get_text('system_about_title'), font=('', 11, 'bold'))
        title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # 创建内容显示区域，带滚动条
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局Canvas和Scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加帮助文档内容，采用框架化布局
        # 使用动态生成的系统标题
        dynamic_title = self.get_dynamic_system_title()
        sections = [
            {
                "title": "1. " + self.get_text('menu_group_dashboard'),
                "content": self.get_text('system_about_content').format(dynamic_title)
            },
            {
                "title": "2. " + self.get_text('menu_tenant'),
                "content": self.get_text('tenant_management_desc')
            },
            {
                "title": "3. " + self.get_text('menu_meter'),
                "content": self.get_text('meter_management_desc')
            },
            {
                "title": "4. " + self.get_text('menu_reading'),
                "content": self.get_text('reading_management_desc')
            },
            {
                "title": "5. " + self.get_text('menu_charge'),
                "content": self.get_text('charge_management_desc')
            },
            {
                "title": "6. " + self.get_text('menu_payment'),
                "content": self.get_text('payment_management_desc')
            },
            {
                "title": "7. " + self.get_text('menu_report'),
                "content": self.get_text('report_management_desc')
            }
        ]
        
        for section in sections:
            # 每个章节使用独立框架，实现模块化布局
            section_frame = ttk.LabelFrame(scrollable_frame, padding=5, relief=tk.RAISED)
            section_frame.pack(fill=tk.X, padx=10, pady=2, ipady=2)
            
            # 章节标题，使用系统默认字体，11号，加粗
            section_title = ttk.Label(section_frame, text=section["title"], font=('', 11, 'bold'))
            section_title.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=(2, 5))
            
            # 章节内容，使用系统默认字体，10号，常规
            section_content = ttk.Label(section_frame, text=section["content"], font=('', 10), 
                                     wraplength=700, justify=tk.LEFT)
            section_content.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=3)
    
    def create_technical_support(self, parent):
        """
        创建技术支持内容
        :param parent: 父容器
        """
        # 添加标题
        title_label = ttk.Label(parent, text=self.get_text('technical_support'), font=('', 11, 'bold'))
        title_label.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=20)
        
        # 创建支持信息框架
        support_frame = ttk.Frame(parent)
        support_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 联系方式
        contact_frame = ttk.LabelFrame(support_frame, text=self.get_text('contact_info'), padding=10)
        contact_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(contact_frame, text=self.get_text('phone')+':', width=10, anchor=tk.W).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(contact_frame, text="18273949470", anchor=tk.W).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(contact_frame, text=self.get_text('email')+':', width=10, anchor=tk.W).grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(contact_frame, text="lymin_li@qq.com", anchor=tk.W).grid(row=1, column=1, padx=5, pady=5)
        
        # 在线帮助
        online_frame = ttk.LabelFrame(support_frame, text=self.get_text('menu_help'), padding=10)
        online_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(online_frame, text=self.get_text('official_website') + ':', width=10, anchor=tk.W).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(online_frame, text="http://www.example.com", anchor=tk.W).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(online_frame, text=self.get_text('online_docs') + ':', width=10, anchor=tk.W).grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(online_frame, text="http://docs.example.com", anchor=tk.W).grid(row=1, column=1, padx=5, pady=5)
        
        # 常见问题
        faq_frame = ttk.LabelFrame(support_frame, text=self.get_text('menu_help'), padding=10)
        faq_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建滚动区域框架
        scroll_frame = ttk.Frame(faq_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 创建内容窗口
        content_frame = ttk.Frame(canvas)
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # 将内容窗口添加到Canvas
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # 布局Canvas和Scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加常见问题内容到滚动区域
        faqs = [
            {
                'title': 'faq_how_to_view_history_charges',
                'answer': 'faq_answer_view_history_charges'
            },
            {
                'title': 'faq_how_to_add_meter',
                'answer': 'faq_answer_add_meter'
            },
            {
                'title': 'faq_how_to_modify_tenant_info',
                'answer': 'faq_answer_modify_tenant_info'
            },
            {
                'title': 'faq_how_to_generate_tenant_report',
                'answer': 'faq_answer_generate_tenant_report'
            },
            {
                'title': 'faq_how_to_set_system_params',
                'answer': 'faq_answer_set_system_params'
            }
        ]
        
        for i, faq in enumerate(faqs, 1):
            ttk.Label(content_frame, text=f"{i}. {self.get_text(faq['title'])}", font=('', 11, 'bold')).pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
            ttk.Label(content_frame, text=f"   {self.get_text(faq['answer'])}", wraplength=700, justify=tk.LEFT).pack(side=tk.TOP, anchor=tk.W, padx=15, pady=2)
    
    def create_about_system(self, parent):
        """
        创建关于系统内容
        :param parent: 父容器
        """
        # 添加标题
        title_label = ttk.Label(parent, text=self.get_text("system_about_title"), font=('', 11, 'bold'))
        title_label.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=20)
        
        # 创建系统信息框架
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 系统Logo
        logo_label = ttk.Label(info_frame, text="💧⚡", font=('', 48))
        logo_label.pack(side=tk.TOP, anchor=tk.CENTER, pady=20)
        
        # 系统名称和版本 - 动态生成
        dynamic_title = self.get_dynamic_system_title()
        name_label = ttk.Label(info_frame, text=dynamic_title, font=('', 11, 'bold'))
        name_label.pack(side=tk.TOP, anchor=tk.CENTER, pady=10)
        
        # 系统版本 - 不再单独显示，已包含在动态标题中
        
        # 系统描述
        desc_text = self.get_text("system_about_content").format(dynamic_title)
        desc_label = ttk.Label(info_frame, text=desc_text)
        desc_label.pack(side=tk.TOP, anchor=tk.CENTER, pady=5)
        
        # 版权信息
        system_name = self.get_text("window_title")
        copyright_text = self.get_text("copyright").format(system_name)
        copyright_label = ttk.Label(info_frame, text=copyright_text, font=('', 10), foreground="gray")
        copyright_label.pack(side=tk.TOP, anchor=tk.CENTER, pady=20)
        
        # 技术支持
        support_text = f"{self.get_text('technical_support')}: lymin_li@qq.com"
        support_label = ttk.Label(info_frame, text=support_text, font=('', 10), foreground="blue")
        support_label.pack(side=tk.TOP, anchor=tk.CENTER, pady=5)
    
    def open_data_initialization(self):
        """
        打开数据初始化界面
        """
        # 权限控制：只有admin用户可以执行数据初始化
        if self.current_user.username != "admin":
            messagebox.showerror(self.get_text('error'), self.get_text('system_init_admin_only'))
            return
        
        # 操作确认
        if not messagebox.askyesnocancel(self.get_text('warning'), self.get_text('system_init_warning')):
            return
        
        try:
            # 1. 创建数据备份
            from utils.backup_utils import BackupUtils
            import os
            import sqlite3
            
            db_path = os.path.join(os.getcwd(), "water_electricity.db")
            backup_path = BackupUtils.backup_database(db_path)
            
            if not backup_path:
                if not messagebox.askyesno(self.get_text('warning'), self.get_text('system_backup_fail_continue')):
                    return
            
            # 2. 连接数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 3. 获取所有表名，排除users表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'users'")
            tables = [table[0] for table in cursor.fetchall()]
            
            success_count = 0
            failed_tables = []
            
            # 4. 执行数据初始化
            for table_name in tables:
                try:
                    # 开始事务
                    conn.execute("BEGIN TRANSACTION")
                    
                    # 清空表数据
                    cursor.execute(f"DELETE FROM {table_name}")
                    
                    # 重置自增ID
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
                    
                    # 提交事务
                    conn.commit()
                    
                    success_count += 1
                except Exception as e:
                    # 回滚事务
                    conn.rollback()
                    failed_tables.append(f"{table_name}: {str(e)}")
            
            conn.close()
            
            # 5. 记录操作日志
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 用户 {self.current_user.username} 执行数据初始化\n"
            log_entry += f"成功初始化 {success_count} 个表，失败 {len(failed_tables)} 个表\n"
            if failed_tables:
                log_entry += f"失败的表：\n{chr(10).join(failed_tables)}\n"
            
            # 确保logs目录存在
            logs_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            # 写入日志文件
            log_file_path = os.path.join(logs_dir, "system_log.txt")
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry + "\n")
            
            # 6. 显示操作结果
            result_msg = f"数据初始化完成！\n\n"
            result_msg += f"成功初始化 {success_count} 个表\n"
            if failed_tables:
                result_msg += f"失败 {len(failed_tables)} 个表\n\n"
                result_msg += f"失败详情：\n{chr(10).join(failed_tables)}\n"
            else:
                result_msg += "所有表初始化成功！\n"
            
            messagebox.showinfo(self.get_text('system_operation_result'), result_msg)
            
        except Exception as e:
            messagebox.showerror(self.get_text('error'), self.get_text('system_init_fail').format(str(e)))
    
    def quit_app(self):
        """
        退出应用程序
        """
        if messagebox.askyesno(self.get_text('system_confirm_delete'), self.get_text('system_confirm_exit')):
            self.root.quit()
    
    def relogin(self):
        """
        重新登录功能
        完全退出应用程序，然后重新启动并打开登录窗口
        """
        try:
            # 显示加载状态提示
            self.data_status_label.config(text=f"{self.get_text('data_status')}: {self.get_text('logging_in')}")
            self.root.update()
            
            # 关闭当前应用并重新启动
            import os
            import sys
            import subprocess
            
            # 获取Python解释器路径和脚本路径
            python = sys.executable
            script = os.path.abspath(sys.argv[0])
            
            # 首先启动新的应用程序实例
            # 使用subprocess.Popen启动新进程，CREATE_NO_WINDOW确保不显示控制台窗口
            subprocess.Popen([python, script], creationflags=subprocess.CREATE_NO_WINDOW)
            
            # 然后关闭当前应用程序
            # 先销毁当前窗口
            self.root.destroy()
            
            # 确保应用程序完全退出
            sys.exit(0)
        except Exception as e:
            # 错误处理
            self.data_status_label.config(text=f"{self.get_text('data_status')}: {self.get_text('normal')}")
            messagebox.showerror(self.get_text('error'), f"{self.get_text('relogin_error')}: {str(e)}")
    
    def show_tool_tip(self, event, text):
        """
        显示工具提示
        :param event: 事件对象
        :param text: 提示文本
        """
        # 创建工具提示窗口
        self.tool_tip = tk.Toplevel(self.root)
        self.tool_tip.wm_overrideredirect(True)  # 无边框
        self.tool_tip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        
        # 创建提示标签
        label = ttk.Label(self.tool_tip, text=text, 
                          background="#333", foreground="white", 
                          font=('Arial', 9), padding=(5, 3),
                          relief="solid", borderwidth=1)
        label.pack()
        
        # 添加淡入效果
        self.tool_tip.attributes('-alpha', 0.0)
        self.fade_in(self.tool_tip)
    
    def fade_in(self, window, alpha=0.0):
        """
        窗口淡入效果
        :param window: 窗口对象
        :param alpha: 当前透明度
        """
        if alpha < 0.9:
            alpha += 0.1
            window.attributes('-alpha', alpha)
            self.root.after(20, lambda: self.fade_in(window, alpha))
        else:
            window.attributes('-alpha', 1.0)
    
    def hide_tool_tip(self, _event=None):
        """
        隐藏工具提示
        :param _event: 事件对象（未使用）
        """
        if hasattr(self, 'tool_tip') and self.tool_tip:
            # 添加淡出效果
            self.fade_out(self.tool_tip)
    
    def fade_out(self, window, alpha=1.0):
        """
        窗口淡出效果
        :param window: 窗口对象
        :param alpha: 当前透明度
        """
        if alpha > 0.0:
            alpha -= 0.1
            window.attributes('-alpha', alpha)
            self.root.after(20, lambda: self.fade_out(window, alpha))
        else:
            window.destroy()
            if hasattr(self, 'tool_tip'):
                del self.tool_tip
    
    def center_window(self, window):
        """
        居中显示窗口
        :param window: 窗口对象
        """
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_window_resize(self, _event=None):
        """
        窗口大小改变事件处理
        :param _event: 事件对象（未使用）
        """
        # 获取窗口宽度
        window_width = self.root.winfo_width()
        
        # 根据窗口宽度调整按钮大小
        if window_width < 800:
            # 小屏幕设备，缩小按钮宽度
            style = ttk.Style()
            style.configure(".TButton", width=10)
        else:
            # 大屏幕设备，恢复正常按钮宽度
            style = ttk.Style()
            style.configure(".TButton", width=12)
    
    def load_tenant_prices(self):
        """
        加载租户价格数据
        只显示那些在配置中有价格设置的租户类型
        """
        try:
            # 从配置中加载租户价格数据
            self.tenant_prices = []
            
            # 获取所有租户类型
            for tenant_type in self.tenant_types:
                # 从配置中获取水价和电价
                water_price = self.settings.get_setting('price', f'{tenant_type}_water_price')
                electricity_price = self.settings.get_setting('price', f'{tenant_type}_electricity_price')
                
                # 只有当水价或电价存在时，才添加到数据列表
                if water_price is not None or electricity_price is not None:
                    # 使用默认值0.00如果价格不存在
                    self.tenant_prices.append({
                        'tenant_type': tenant_type,
                        'water_price': water_price or '0.00',
                        'electricity_price': electricity_price or '0.00'
                    })
            
            # 应用过滤、排序和分页
            self.apply_tenant_price_filters()
        except Exception as e:
            messagebox.showerror("错误", f"加载租户价格数据失败：{str(e)}")
    
    def apply_tenant_price_filters(self):
        """
        应用过滤和排序，显示所有数据
        """
        # 过滤
        search_text = self.search_tenant_type_entry.get().strip().lower()
        if search_text:
            self.filtered_tenant_prices = [price for price in self.tenant_prices 
                                         if search_text in price['tenant_type'].lower()]
        else:
            self.filtered_tenant_prices = self.tenant_prices.copy()
        
        # 排序
        self.filtered_tenant_prices.sort(key=lambda x: x[self.sort_column], 
                                      reverse=(self.sort_order == "desc"))
        
        # 显示所有数据
        self.display_all_tenant_prices()
    
    def display_all_tenant_prices(self):
        """
        显示所有租户价格数据
        """
        # 清空表格
        for item in self.tenant_price_tree.get_children():
            self.tenant_price_tree.delete(item)
        
        # 添加所有数据到表格
        for price in self.filtered_tenant_prices:
            # 添加行到表格
            self.tenant_price_tree.insert("", tk.END, values=(
                price['tenant_type'],
                price['water_price'],
                price['electricity_price']
            ))
    
    def search_tenant_prices(self):
        """
        搜索租户价格
        """
        self.apply_tenant_price_filters()
    
    def reset_tenant_price_search(self):
        """
        重置租户价格搜索
        """
        self.search_tenant_type_entry.delete(0, tk.END)
        self.apply_tenant_price_filters()
    
    def sort_tenant_prices(self, column):
        """
        排序租户价格
        """
        if self.sort_column == column:
            # 切换排序顺序
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            # 新列，默认升序
            self.sort_column = column
            self.sort_order = "asc"
        
        # 应用排序
        self.apply_tenant_price_filters()
    

    
    def on_tenant_price_select(self, _event=None):
        """
        表格选择事件
        """
        selected_items = self.tenant_price_tree.selection()
        if selected_items:
            selected_count = len(selected_items)
            
            # 根据选择数量设置按钮状态
            if selected_count == 1:
                # 选择单行，启用编辑和删除按钮
                self.edit_btn.config(state="normal")
                self.delete_btn.config(state="normal")
                self.bottom_edit_btn.config(state="normal")
                self.bottom_delete_btn.config(state="normal")
                self.operation_hint.config(text=f"已选择 {selected_count} 项，可以编辑或删除")
            else:
                # 选择多行，仅启用删除按钮
                self.edit_btn.config(state="disabled")
                self.delete_btn.config(state="normal")
                self.bottom_edit_btn.config(state="disabled")
                self.bottom_delete_btn.config(state="normal")
                self.operation_hint.config(text=f"已选择 {selected_count} 项，仅支持删除操作")
        else:
            # 未选择任何项，禁用所有按钮
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            self.bottom_edit_btn.config(state="disabled")
            self.bottom_delete_btn.config(state="disabled")
            self.operation_hint.config(text="请选择要操作的价格配置项")
    
    def edit_selected_tenant_price(self):
        """
        编辑选中的租户价格配置
        """
        selected_items = self.tenant_price_tree.selection()
        if not selected_items:
            return
        
        item_id = selected_items[0]
        values = self.tenant_price_tree.item(item_id, "values")
        tenant_type = values[0]
        
        # 查找对应的价格配置
        price_data = next((p for p in self.tenant_prices if p['tenant_type'] == tenant_type), None)
        if price_data:
            self.edit_tenant_price(price_data)
    
    def delete_selected_tenant_price(self):
        """
        删除选中的租户价格配置
        支持单条或多条选中项删除
        """
        selected_items = self.tenant_price_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的价格配置项")
            return
        
        selected_count = len(selected_items)
        
        # 获取选中的租户类型列表
        tenant_types = []
        for item_id in selected_items:
            values = self.tenant_price_tree.item(item_id, "values")
            tenant_types.append(values[0])
        
        # 显示确认对话框
        if selected_count == 1:
            # 单条删除确认
            confirm_message = f"确定要删除{tenant_types[0]}的价格配置吗？\n\n删除后将无法恢复，请谨慎操作！"
        else:
            # 多条删除确认
            confirm_message = f"确定要删除选中的{selected_count}个价格配置吗？\n\n删除后将无法恢复，请谨慎操作！"
        
        if messagebox.askyesno("确认删除", confirm_message):
            try:
                # 执行删除操作
                deleted_count = 0
                
                # 先从表格中删除选中项
                for item_id in selected_items:
                    # 删除表格中的项
                    self.tenant_price_tree.delete(item_id)
                    deleted_count += 1
                
                # 再从配置文件中删除对应的价格项
                for tenant_type in tenant_types:
                    try:
                        # 查找对应的价格配置
                        price_data = next((p for p in self.tenant_prices if p['tenant_type'] == tenant_type), None)
                        if price_data:
                            # 调用删除方法
                            self.delete_tenant_price(price_data)
                    except Exception as e:
                        messagebox.showerror("错误", f"删除{tenant_type}价格配置时发生错误：{str(e)}")
                
                # 显示删除结果
                if deleted_count > 0:
                    if deleted_count == 1:
                        messagebox.showinfo("成功", f"已成功删除{tenant_types[0]}的价格配置")
                    else:
                        messagebox.showinfo("成功", f"已成功删除{deleted_count}个价格配置")
                    
                    # 重新加载数据并应用过滤
                    self.load_tenant_prices()
                    
                    # 更新选择状态和提示
                    self.tenant_price_tree.selection_remove(self.tenant_price_tree.selection())
                    self.operation_hint.config(text="请选择要操作的价格配置项")
                else:
                    messagebox.showwarning("警告", "删除操作未执行")
            except Exception as e:
                messagebox.showerror("错误", f"删除操作失败：{str(e)}")
    
    def add_tenant_price(self):
        """
        新增租户价格配置
        """
        # 创建新增窗口
        add_window = tk.Toplevel(self.root)
        add_window.title("新增价格配置")
        add_window.geometry("400x300")
        add_window.resizable(False, False)
        
        # 居中显示
        self.center_window(add_window)
        
        # 创建表单框架
        form_frame = ttk.Frame(add_window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 租户类型
        ttk.Label(form_frame, text=self.get_text("tenant_type")+":").grid(row=0, column=0, sticky=tk.E, padx=10, pady=10)
        tenant_type_var = tk.StringVar()
        tenant_type_combobox = ttk.Combobox(form_frame, textvariable=tenant_type_var, 
                                           values=[tt for tt in self.tenant_types 
                                                  if tt not in [p['tenant_type'] for p in self.tenant_prices]])
        tenant_type_combobox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        # 水价
        ttk.Label(form_frame, text=self.get_text("water_price")+"（元/吨）:").grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)
        water_price_var = tk.StringVar()
        water_price_entry = ttk.Entry(form_frame, textvariable=water_price_var, width=15)
        water_price_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        water_price_entry.insert(0, "0.00")
        
        # 电价
        ttk.Label(form_frame, text=self.get_text("electricity_price")+"（元/度）:").grid(row=2, column=0, sticky=tk.E, padx=10, pady=10)
        electricity_price_var = tk.StringVar()
        electricity_price_entry = ttk.Entry(form_frame, textvariable=electricity_price_var, width=15)
        electricity_price_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        electricity_price_entry.insert(0, "0.00")
        
        # 保存按钮
        def save_new_price():
            """保存新价格配置"""
            tenant_type = tenant_type_var.get().strip()
            water_price = water_price_var.get().strip()
            electricity_price = electricity_price_var.get().strip()
            
            # 验证数据
            is_valid = True
            error_messages = []
            
            # 验证租户类型
            if not tenant_type:
                error_messages.append("请选择租户类型")
                is_valid = False
            
            # 验证水价
            try:
                water_price_val = float(water_price)
                if water_price_val < 0:
                    error_messages.append("水价不能为负数")
                    is_valid = False
                elif water_price_val == 0:
                    # 允许水价为0，但给出提示
                    result = messagebox.askyesno("提示", "水价设置为0，确定要继续吗？")
                    if not result:
                        return
                elif water_price_val > 10000:
                    # 水价过高，给出警告
                    result = messagebox.askyesno("警告", f"水价({water_price_val})过高，确定要继续吗？")
                    if not result:
                        return
            except ValueError:
                error_messages.append("水价必须是有效的数字")
                is_valid = False
            
            # 验证电价
            try:
                electricity_price_val = float(electricity_price)
                if electricity_price_val < 0:
                    error_messages.append("电价不能为负数")
                    is_valid = False
                elif electricity_price_val == 0:
                    # 允许电价为0，但给出提示
                    result = messagebox.askyesno("提示", "电价设置为0，确定要继续吗？")
                    if not result:
                        return
                elif electricity_price_val > 100:
                    # 电价过高，给出警告
                    result = messagebox.askyesno("警告", f"电价({electricity_price_val})过高，确定要继续吗？")
                    if not result:
                        return
            except ValueError:
                error_messages.append("电价必须是有效的数字")
                is_valid = False
            
            # 显示所有错误信息
            if not is_valid:
                messagebox.showwarning("表单验证失败", "\n".join(error_messages))
                return
            
            # 格式化价格为两位小数
            water_price_formatted = f"{float(water_price):.2f}"
            electricity_price_formatted = f"{float(electricity_price):.2f}"
            
            try:
                # 保存到配置
                self.settings.set_setting('price', f'{tenant_type}_water_price', water_price_formatted)
                self.settings.set_setting('price', f'{tenant_type}_electricity_price', electricity_price_formatted)
                
                # 重新加载数据
                self.load_tenant_prices()
                
                # 关闭窗口
                add_window.destroy()
                
                # 显示成功消息
                messagebox.showinfo("成功", f"{tenant_type}价格配置新增成功！\n水价：{water_price_formatted}元/吨\n电价：{electricity_price_formatted}元/度")
            except Exception as e:
                messagebox.showerror("错误", f"保存租户价格配置失败：{str(e)}")
        
        # 按钮框架
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text=self.get_text("button_save"), command=save_new_price).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text=self.get_text("button_cancel"), command=add_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def edit_tenant_price(self, price_data):
        """
        编辑租户价格配置
        """
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑价格配置")
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)
        
        # 居中显示
        self.center_window(edit_window)
        
        # 创建表单框架
        form_frame = ttk.Frame(edit_window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 租户类型（只读）
        ttk.Label(form_frame, text=self.get_text("tenant_type")+":").grid(row=0, column=0, sticky=tk.E, padx=10, pady=10)
        tenant_type_var = tk.StringVar(value=price_data['tenant_type'])
        tenant_type_entry = ttk.Entry(form_frame, textvariable=tenant_type_var, width=15)
        tenant_type_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        tenant_type_entry.config(state="readonly")
        
        # 水价
        ttk.Label(form_frame, text=self.get_text("water_price")+"（元/吨）:").grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)
        water_price_var = tk.StringVar(value=price_data['water_price'])
        water_price_entry = ttk.Entry(form_frame, textvariable=water_price_var, width=15)
        water_price_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        # 电价
        ttk.Label(form_frame, text=self.get_text("electricity_price")+"（元/度）:").grid(row=2, column=0, sticky=tk.E, padx=10, pady=10)
        electricity_price_var = tk.StringVar(value=price_data['electricity_price'])
        electricity_price_entry = ttk.Entry(form_frame, textvariable=electricity_price_var, width=15)
        electricity_price_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        
        # 保存按钮
        def save_edited_price():
            """保存编辑后的价格配置"""
            tenant_type = tenant_type_var.get().strip()
            water_price = water_price_var.get().strip()
            electricity_price = electricity_price_var.get().strip()
            
            # 验证数据
            is_valid = True
            error_messages = []
            
            # 验证水价
            try:
                water_price_val = float(water_price)
                if water_price_val < 0:
                    error_messages.append("水价不能为负数")
                    is_valid = False
                elif water_price_val == 0:
                    # 允许水价为0，但给出提示
                    result = messagebox.askyesno("提示", "水价设置为0，确定要继续吗？")
                    if not result:
                        return
                elif water_price_val > 10000:
                    # 水价过高，给出警告
                    result = messagebox.askyesno("警告", f"水价({water_price_val})过高，确定要继续吗？")
                    if not result:
                        return
            except ValueError:
                error_messages.append("水价必须是有效的数字")
                is_valid = False
            
            # 验证电价
            try:
                electricity_price_val = float(electricity_price)
                if electricity_price_val < 0:
                    error_messages.append("电价不能为负数")
                    is_valid = False
                elif electricity_price_val == 0:
                    # 允许电价为0，但给出提示
                    result = messagebox.askyesno("提示", "电价设置为0，确定要继续吗？")
                    if not result:
                        return
                elif electricity_price_val > 100:
                    # 电价过高，给出警告
                    result = messagebox.askyesno("警告", f"电价({electricity_price_val})过高，确定要继续吗？")
                    if not result:
                        return
            except ValueError:
                error_messages.append("电价必须是有效的数字")
                is_valid = False
            
            # 显示所有错误信息
            if not is_valid:
                messagebox.showerror("验证失败", "\n".join(error_messages))
                return
            
            # 格式化价格为两位小数
            water_price_formatted = f"{float(water_price):.2f}"
            electricity_price_formatted = f"{float(electricity_price):.2f}"
            
            try:
                # 保存到配置
                self.settings.set_setting('price', f'{tenant_type}_water_price', water_price_formatted)
                self.settings.set_setting('price', f'{tenant_type}_electricity_price', electricity_price_formatted)
                
                # 重新加载数据
                self.load_tenant_prices()
                
                # 关闭窗口
                edit_window.destroy()
                
                # 显示成功消息
                messagebox.showinfo("成功", f"{tenant_type}价格配置编辑成功！\n水价：{water_price_formatted}元/吨\n电价：{electricity_price_formatted}元/度")
            except Exception as e:
                messagebox.showerror("错误", f"保存租户价格配置失败：{str(e)}")
        
        # 按钮框架
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text=self.get_text("button_save"), command=save_edited_price).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text=self.get_text("button_cancel"), command=edit_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def delete_tenant_price(self, price_data):
        """
        删除租户价格配置
        """
        tenant_type = price_data['tenant_type']
        
        try:
            # 从配置中删除价格配置
            self.settings.delete_setting('price', f'{tenant_type}_water_price')
            self.settings.delete_setting('price', f'{tenant_type}_electricity_price')
        except Exception as e:
            raise Exception(f"删除租户价格配置失败：{str(e)}")
