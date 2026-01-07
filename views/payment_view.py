#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收费管理视图
负责处理收费记录、欠费管理等功能
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from models.tenant import Tenant
from models.charge import Charge
from models.payment import Payment
from models.meter import Meter
from models.reading import MeterReading
from models.settlement import Settlement

class PaymentView:
    """收费管理视图类"""
    
    def __init__(self, parent, main_window=None, language_utils=None):
        """
        初始化收费管理视图
        :param parent: 父窗口组件
        :param main_window: 主窗口实例，用于视图间通信
        :param language_utils: 语言工具类实例
        """
        self.parent = parent
        self.main_window = main_window
        self.language_utils = language_utils
        self.payment_list = []
        self.selected_payment = None
        
        # 用于优化连续快速修改时的性能
        self._match_timer = None
        self._last_match_params = None
        
        self.create_widgets()
        self.load_payment_list()
        
    def get_text(self, key):
        """
        获取翻译文本
        :param key: 文本键名
        :return: 翻译后的文本
        """
        return self.language_utils.get_text(key) if self.language_utils else key
        
    def update_language(self):
        """
        更新界面语言
        """
        # 更新筛选框文本
        self.filter_labels['month_label']['text'] = self.get_text('month') + ':'
        self.filter_labels['tenant_label']['text'] = self.get_text('tenant') + ':'
        self.filter_buttons['search_btn']['text'] = self.get_text('button_search')
        self.filter_buttons['reset_btn']['text'] = self.get_text('button_reset')
        
        # 更新操作按钮文本
        self.action_buttons['query_arrears_btn']['text'] = self.get_text('query_arrears')
        self.action_buttons['delete_payment_btn']['text'] = self.get_text('delete_payment')
        self.action_buttons['generate_receipt_btn']['text'] = self.get_text('generate_payment_receipt')
        
        # 更新列表列标题
        self.payment_tree.heading("serial", text=self.get_text('serial'))
        self.payment_tree.heading("tenant_name", text=self.get_text('tenant_name'))
        self.payment_tree.heading("month", text=self.get_text('month'))
        self.payment_tree.heading("payment_date", text=self.get_text('payment_date'))
        self.payment_tree.heading("amount", text=self.get_text('amount'))
        self.payment_tree.heading("payment_method", text=self.get_text('payment_method'))
        self.payment_tree.heading("payer", text=self.get_text('payer'))
        self.payment_tree.heading("settlement_date", text=self.get_text('settlement_date'))
        self.payment_tree.heading("notes", text=self.get_text('notes'))
        
        # 更新表单文本
        self.form_labels['tenant_label']['text'] = self.get_text('tenant') + ':'
        self.form_labels['month_label']['text'] = self.get_text('charge_month') + ':'
        self.form_labels['payment_date_label']['text'] = self.get_text('payment_date') + ':'
        self.form_labels['amount_label']['text'] = self.get_text('amount') + ':'
        self.form_labels['payment_method_label']['text'] = self.get_text('payment_method') + ':'
        self.form_labels['payer_label']['text'] = self.get_text('payer') + ':'
        self.form_labels['notes_label']['text'] = self.get_text('notes') + ':'
        
        # 更新表单按钮文本
        self.form_buttons['save_btn']['text'] = self.get_text('button_save')
        self.form_buttons['cancel_btn']['text'] = self.get_text('button_cancel')
        
        # 更新支付方式选项
        self.form_payment_method['values'] = [self.get_text('cash'), self.get_text('bank_transfer'), self.get_text('wechat'), self.get_text('alipay')]
        
        # 重新加载列表，确保状态文本正确
        self.load_payment_list()
    
    def create_widgets(self):
        """
        创建收费管理界面组件
        """
        # 创建主框架
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 顶部：筛选和操作按钮
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 筛选条件
        filter_frame = ttk.Frame(top_frame)
        filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 筛选标签字典
        self.filter_labels = {}
        # 筛选按钮字典
        self.filter_buttons = {}
        # 操作按钮字典
        self.action_buttons = {}
        # 表单标签字典
        self.form_labels = {}
        # 表单按钮字典
        self.form_buttons = {}
        
        # 月份标签
        self.filter_labels['month_label'] = ttk.Label(filter_frame, text=self.get_text('month') + ':')
        self.filter_labels['month_label'].pack(side=tk.LEFT, padx=5)
        
        self.month_var = tk.StringVar()
        self.month_var.set(datetime.now().strftime("%Y-%m"))
        
        # 将月份选择组件改为具备自动完成功能的下拉列表
        self.month_combobox = ttk.Combobox(filter_frame, textvariable=self.month_var, width=10, state="normal", values=[])
        self.month_combobox.pack(side=tk.LEFT, padx=5)
        
        # 加载所有已存在的月份数据
        self.load_existing_months()
        
        # 绑定月份选择事件
        self.month_combobox.bind("<<ComboboxSelected>>", self.on_month_selected_filter)
        # 绑定输入事件，实现自动匹配
        self.month_combobox.bind("<KeyRelease>", self.on_month_input_filter)
        # 绑定回车键确认选择
        self.month_combobox.bind("<Return>", self.on_month_confirm_filter)
        # 绑定ESC键关闭下拉面板
        self.month_combobox.bind("<Escape>", self.on_month_escape_filter)
        
        # 租户标签
        self.filter_labels['tenant_label'] = ttk.Label(filter_frame, text=self.get_text('tenant') + ':')
        self.filter_labels['tenant_label'].pack(side=tk.LEFT, padx=5)
        
        self.tenant_var = tk.StringVar()
        self.tenant_combobox = ttk.Combobox(filter_frame, textvariable=self.tenant_var)
        self.load_tenants_to_combobox()
        self.tenant_combobox.pack(side=tk.LEFT, padx=5)
        
        # 查询按钮
        self.filter_buttons['search_btn'] = ttk.Button(filter_frame, text=self.get_text('button_search'), command=self.search_payments)
        self.filter_buttons['search_btn'].pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        self.filter_buttons['reset_btn'] = ttk.Button(filter_frame, text=self.get_text('button_reset'), command=self.reset_filter)
        self.filter_buttons['reset_btn'].pack(side=tk.LEFT, padx=5)
        
        # 操作按钮
        action_frame = ttk.Frame(top_frame)
        action_frame.pack(side=tk.RIGHT)
        
        # 欠费查询按钮
        self.action_buttons['query_arrears_btn'] = ttk.Button(action_frame, text=self.get_text('query_arrears'), command=self.query_arrears)
        self.action_buttons['query_arrears_btn'].pack(side=tk.LEFT, padx=5)
        
        # 删除收费按钮
        self.action_buttons['delete_payment_btn'] = ttk.Button(action_frame, text=self.get_text('delete_payment'), command=self.delete_payment)
        self.action_buttons['delete_payment_btn'].pack(side=tk.LEFT, padx=5)
        
        # 收费凭证按钮
        self.action_buttons['generate_receipt_btn'] = ttk.Button(action_frame, text=self.get_text('generate_payment_receipt'), command=self.generate_payment_receipt)
        self.action_buttons['generate_receipt_btn'].pack(side=tk.LEFT, padx=5)
        
        # 中部：收费记录列表
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 列表控件 - 添加序号列，将ID列移到最后，添加结算时间列
        columns = ("serial", "tenant_name", "month", "payment_date", "amount", 
                  "payment_method", "payer", "settlement_date", "notes", "id")
        self.payment_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        
        # 配置Treeview的tag，用于实现隔行背景色
        # 奇数行使用深灰色，偶数行使用白色，与charge_view.py保持一致
        self.payment_tree.tag_configure('odd', background='#c0c0c0')
        self.payment_tree.tag_configure('even', background='#ffffff')
        
        # 设置列标题和宽度
        self.payment_tree.heading("serial", text=self.get_text('serial'))
        self.payment_tree.column("serial", width=60, anchor="center")
        
        # ID列设置为完全隐藏
        self.payment_tree.heading("id", text="ID")
        self.payment_tree.column("id", width=0, anchor="center", stretch=False)
        
        self.payment_tree.heading("tenant_name", text=self.get_text('tenant_name'))
        self.payment_tree.column("tenant_name", width=150, anchor="w")
        
        self.payment_tree.heading("month", text=self.get_text('month'))
        self.payment_tree.column("month", width=100, anchor="center")
        
        self.payment_tree.heading("payment_date", text=self.get_text('payment_date'))
        self.payment_tree.column("payment_date", width=120, anchor="center")
        
        self.payment_tree.heading("amount", text=self.get_text('amount'))
        self.payment_tree.column("amount", width=100, anchor="e")
        
        self.payment_tree.heading("payment_method", text=self.get_text('payment_method'))
        self.payment_tree.column("payment_method", width=100, anchor="center")
        
        self.payment_tree.heading("payer", text=self.get_text('payer'))
        self.payment_tree.column("payer", width=100, anchor="center")
        
        self.payment_tree.heading("settlement_date", text=self.get_text('settlement_date'))
        self.payment_tree.column("settlement_date", width=120, anchor="center")
        
        self.payment_tree.heading("notes", text=self.get_text('notes'))
        self.payment_tree.column("notes", width=120, anchor="w")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.payment_tree.yview)
        self.payment_tree.configure(yscroll=scrollbar.set)
        
        self.payment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右侧：收费表单
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 表单标题
        self.form_title = ttk.Label(right_frame, text=self.get_text('charge_information'), font=("Arial", 14))
        self.form_title.pack(side=tk.TOP, pady=10)
        
        # 表单框架
        form_frame = ttk.Frame(right_frame)
        form_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置grid布局的列权重，使组件能够自适应宽度
        for i in range(12):  # 12列：6个标签 + 6个输入框
            form_frame.grid_columnconfigure(i, weight=1, uniform="form")
        
        # 租户
        self.form_labels['tenant_label'] = ttk.Label(form_frame, text=self.get_text('tenant') + ':')
        self.form_labels['tenant_label'].grid(row=0, column=0, padx=(5, 2), pady=5, sticky=tk.E)
        
        self.form_tenant = ttk.Combobox(form_frame, values=[])
        self.form_tenant.grid(row=0, column=1, padx=(2, 5), pady=5, sticky=tk.W+tk.E)
        # 加载表单租户数据
        self.load_tenants_to_form_combobox()
        
        # 费用月份
        self.form_labels['month_label'] = ttk.Label(form_frame, text=self.get_text('charge_month') + ':')
        self.form_labels['month_label'].grid(row=0, column=2, padx=(5, 2), pady=5, sticky=tk.E)
        
        self.form_month = ttk.Combobox(form_frame, values=[])
        self.form_month.grid(row=0, column=3, padx=(2, 5), pady=5, sticky=tk.W+tk.E)
        
        # 收费日期
        self.form_labels['payment_date_label'] = ttk.Label(form_frame, text=self.get_text('payment_date') + ':')
        self.form_labels['payment_date_label'].grid(row=0, column=4, padx=(5, 2), pady=5, sticky=tk.E)
        
        self.form_payment_date = ttk.Entry(form_frame)
        self.form_payment_date.grid(row=0, column=5, padx=(2, 5), pady=5, sticky=tk.W+tk.E)
        self.form_payment_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 收费金额
        self.form_labels['amount_label'] = ttk.Label(form_frame, text=self.get_text('amount') + ':')
        self.form_labels['amount_label'].grid(row=0, column=6, padx=(5, 2), pady=5, sticky=tk.E)
        
        self.form_amount = ttk.Entry(form_frame)
        self.form_amount.grid(row=0, column=7, padx=(2, 5), pady=5, sticky=tk.W+tk.E)
        
        # 支付方式
        self.form_labels['payment_method_label'] = ttk.Label(form_frame, text=self.get_text('payment_method') + ':')
        self.form_labels['payment_method_label'].grid(row=0, column=8, padx=(5, 2), pady=5, sticky=tk.E)
        
        self.form_payment_method = ttk.Combobox(form_frame, values=[self.get_text('cash'), self.get_text('bank_transfer'), self.get_text('wechat'), self.get_text('alipay')])
        self.form_payment_method.grid(row=0, column=9, padx=(2, 5), pady=5, sticky=tk.W+tk.E)
        self.form_payment_method.set(self.get_text('cash'))
        
        # 收款人
        self.form_labels['payer_label'] = ttk.Label(form_frame, text=self.get_text('payer') + ':')
        self.form_labels['payer_label'].grid(row=0, column=10, padx=(5, 2), pady=5, sticky=tk.E)
        
        self.form_payer = ttk.Entry(form_frame)
        self.form_payer.grid(row=0, column=11, padx=(2, 5), pady=5, sticky=tk.W+tk.E)
        self.form_payer.insert(0, "admin")  # 默认当前用户
        
        # 备注
        self.form_labels['notes_label'] = ttk.Label(form_frame, text=self.get_text('notes') + ':')
        self.form_labels['notes_label'].grid(row=1, column=0, padx=(5, 2), pady=5, sticky=tk.E)
        
        # 将备注从Text修改为Entry文本框
        self.form_notes = ttk.Entry(form_frame)
        self.form_notes.grid(row=1, column=1, columnspan=11, padx=(2, 5), pady=5, sticky=tk.W+tk.E)
        
        # 表单操作按钮
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=12, padx=5, pady=5, sticky=tk.E)
        
        self.form_buttons['save_btn'] = ttk.Button(button_frame, text=self.get_text('button_save'), command=self.save_payment)
        self.form_buttons['save_btn'].pack(side=tk.RIGHT, padx=5, pady=2)
        
        self.form_buttons['cancel_btn'] = ttk.Button(button_frame, text=self.get_text('button_cancel'), command=self.clear_form)
        self.form_buttons['cancel_btn'].pack(side=tk.RIGHT, padx=5, pady=2)
        
        # 绑定列表选择事件
        self.payment_tree.bind("<<TreeviewSelect>>", self.on_payment_select)
        # 绑定租户选择事件，动态加载费用月份
        self.form_tenant.bind("<<ComboboxSelected>>", self.on_tenant_selected)
        # 绑定费用月份选择事件，用于自动匹配费用记录
        self.form_month.bind("<<ComboboxSelected>>", self.on_month_selected)
    
    def load_tenants_to_combobox(self):
        """
        加载租户数据到筛选下拉框
        """
        try:
            tenants = Tenant.get_all()
            tenant_names = [""] + [t.name for t in tenants]
            self.tenant_combobox['values'] = tenant_names
        except Exception as e:
            messagebox.showerror(self.get_text('error'), f"{self.get_text('failed_to_load_tenant_data')}: {str(e)}")
    
    def load_existing_months(self):
        """
        加载所有已存在的月份数据到月份选择下拉列表
        """
        try:
            # 获取所有已存在的月份数据
            from models.charge import Charge
            charges = Charge.get_all()
            
            # 提取不重复的月份
            months = set()
            for charge in charges:
                if charge.month:
                    months.add(charge.month)
            
            # 转换为列表并按时间倒序排序
            existing_months = sorted(months, reverse=True)
            
            # 添加当前月份（如果不存在）
            current_month = datetime.now().strftime("%Y-%m")
            if current_month not in existing_months:
                existing_months.insert(0, current_month)
            
            # 设置下拉列表的值
            self.month_combobox['values'] = existing_months
        except Exception as e:
            # 处理空状态
            print(f"加载月份数据失败: {str(e)}")
            self.month_combobox['values'] = [datetime.now().strftime("%Y-%m")]
    
    def on_month_selected_filter(self, _event=None):
        """
        筛选条件中月份选择事件处理
        """
        # 触发数据加载或筛选操作
        self.search_payments()
    
    def on_month_input_filter(self, _event=None):
        """
        筛选条件中月份输入事件处理，实现自动匹配功能
        """
        # 获取当前输入值
        current_input = self.month_combobox.get().strip()
        
        if not current_input:
            # 输入为空，显示所有月份
            self.load_existing_months()
            return
        
        # 获取所有已存在的月份数据
        from models.charge import Charge
        charges = Charge.get_all()
        
        # 提取不重复的月份
        months = set()
        for charge in charges:
            if charge.month:
                months.add(charge.month)
        
        # 添加当前月份（如果不存在）
        current_month = datetime.now().strftime("%Y-%m")
        months.add(current_month)
        
        # 转换为列表并按时间倒序排序
        existing_months = sorted(months, reverse=True)
        
        # 筛选包含输入内容的月份
        filtered_months = [month for month in existing_months if current_input in month]
        
        # 设置下拉列表的值
        self.month_combobox['values'] = filtered_months
        
        # 如果有匹配项，自动展开下拉列表
        if filtered_months:
            self.month_combobox.event_generate("<<ComboboxSelected>>")
    
    def on_month_confirm_filter(self, _event=None):
        """
        筛选条件中回车键确认选择事件处理
        """
        # 验证输入的月份格式
        month_input = self.month_combobox.get().strip()
        try:
            datetime.strptime(month_input, "%Y-%m")
            # 格式正确，触发数据加载
            self.search_payments()
        except ValueError:
            # 格式错误，显示错误提示
            messagebox.showwarning("格式错误", "月份格式不正确，应为YYYY-MM格式")
            # 重置为当前月份
            self.month_var.set(datetime.now().strftime("%Y-%m"))
            self.load_existing_months()
    
    def on_month_escape_filter(self, _event=None):
        """
        筛选条件中ESC键关闭下拉面板事件处理
        """
        # 重置为当前月份
        self.month_var.set(datetime.now().strftime("%Y-%m"))
        self.load_existing_months()
        # 关闭下拉面板
        self.month_combobox.event_generate("<<ComboboxSelected>>")
    
    def load_tenants_to_form_combobox(self):
        """
        加载租户数据到表单租户下拉框
        数据来源于租户管理列表
        """
        try:
            # 动态从租户管理模块获取所有租户
            tenants = Tenant.get_all()
            tenant_names = [t.name for t in tenants]
            self.form_tenant['values'] = tenant_names
            self.form_tenant.set("" if tenant_names else "")
        except Exception as e:
            messagebox.showerror(self.get_text('error'), f"{self.get_text('failed_to_load_form_tenant_data')}: {str(e)}")
            self.form_tenant['values'] = []
            self.form_tenant.set("")
    
    def load_payment_list(self):
        """
        加载收费记录列表
        """
        # 清空现有列表
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        
        # 获取收费记录
        # 这里简化实现，实际应该根据月份筛选
        self.payment_list = Payment.get_by_month(self.month_var.get())
        
        # 创建租户ID到名称的映射
        tenants = Tenant.get_all()
        tenant_map = {t.id: t.name for t in tenants}
        
        # 创建费用ID到月份的映射
        charges = Charge.get_by_month(self.month_var.get())
        charge_map = {c.id: c.month for c in charges}
        
        # 添加到列表控件 - 第一个值为序号，最后一个值为ID
        for idx, payment in enumerate(self.payment_list, 1):
            # 获取费用信息
            charge = Charge.get_by_id(payment.charge_id)
            tenant_name = tenant_map.get(charge.tenant_id, "未知租户") if charge else "未知租户"
            month = charge_map.get(payment.charge_id, "未知月份") if charge else "未知月份"
            
            # 获取结算时间
            settlement = Settlement.get_by_month(month)
            settlement_date = settlement.settle_date if settlement else ""
            
            # 根据索引应用奇偶行标签
            row_tag = 'odd' if idx % 2 != 0 else 'even'
            self.payment_tree.insert("", tk.END, values=(idx, tenant_name, 
                                                      month, 
                                                      payment.payment_date, 
                                                      payment.amount, 
                                                      payment.payment_method, 
                                                      payment.payer, 
                                                      settlement_date, 
                                                      payment.notes, 
                                                      payment.id), tags=(row_tag,))
    
    def search_payments(self):
        """
        搜索收费记录
        根据月份和租户进行筛选
        """
        # 清空现有列表
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        
        # 获取筛选条件
        month = self.month_var.get()
        tenant_name = self.tenant_var.get()
        
        # 获取所有收费记录
        all_payments = Payment.get_all()
        
        # 创建租户ID到名称的映射
        tenants = Tenant.get_all()
        tenant_map = {t.id: t.name for t in tenants}
        tenant_id_map = {t.name: t.id for t in tenants}
        
        # 应用筛选条件
        filtered_payments = []
        for payment in all_payments:
            # 加载费用信息（如果尚未加载）
            if not payment.charge:
                payment.load_charge_info()
            
            if not payment.charge:
                continue
            
            # 按月份筛选
            if month and payment.charge.month != month:
                continue
            
            # 按租户筛选
            if tenant_name:
                tenant_id = tenant_id_map.get(tenant_name)
                if payment.charge.tenant_id != tenant_id:
                    continue
            
            filtered_payments.append(payment)
        
        # 确保过滤结果与load_payment_list方法的排序规则一致：按缴费日期降序排序
        filtered_payments.sort(key=lambda x: x.payment_date, reverse=True)
        
        # 更新收费记录列表
        self.payment_list = filtered_payments
        
        # 添加到列表控件 - 第一个值为序号，最后一个值为ID
        for idx, payment in enumerate(filtered_payments, 1):
            if payment.charge:
                # 获取租户名称
                tenant_name = tenant_map.get(payment.charge.tenant_id, "未知租户")
                
                # 获取结算时间
                month = payment.charge.month
                settlement = Settlement.get_by_month(month)
                settlement_date = settlement.settle_date if settlement else ""
                
                # 根据索引应用奇偶行标签
                row_tag = 'odd' if idx % 2 != 0 else 'even'
                self.payment_tree.insert("", tk.END, values=(idx, tenant_name, 
                                                          payment.charge.month, 
                                                          payment.payment_date, 
                                                          payment.amount, 
                                                          payment.payment_method, 
                                                          payment.payer, 
                                                          settlement_date, 
                                                          payment.notes, 
                                                          payment.id), tags=(row_tag,))
    
    def reset_filter(self):
        """
        重置筛选条件
        """
        self.month_var.set(datetime.now().strftime("%Y-%m"))
        self.tenant_combobox.set("")
        self.load_payment_list()
    
    def on_payment_select(self, _event=None):
        """
        列表选择事件处理
        """
        selected_items = self.payment_tree.selection()
        if selected_items:
            item_id = selected_items[0]
            values = self.payment_tree.item(item_id, "values")
            payment_id_str = values[-1]  # ID现在在最后一列
            
            try:
                # 转换为整数类型以匹配Payment对象的id类型
                payment_id = int(payment_id_str)
                
                # 查找对应的收费记录
                self.selected_payment = next((p for p in self.payment_list if p.id == payment_id), None)
                if self.selected_payment:
                    self.fill_form()
            except (ValueError, TypeError):
                messagebox.showerror(self.get_text('error'), self.get_text('invalid_payment_record_id'))
                self.selected_payment = None
    
    def fill_form(self):
        """
        填充表单
        """
        if self.selected_payment:
            # 获取费用信息
            charge = Charge.get_by_id(self.selected_payment.charge_id)
            if charge:
                # 获取租户信息
                tenant = Tenant.get_by_id(charge.tenant_id)
                if tenant:
                    self.form_tenant.set(tenant.name)
                    
                    # 加载费用月份
                    self.load_charge_months(tenant.id)
                    self.form_month.set(charge.month)
            
            # 填充其他字段
            self.form_payment_date.delete(0, tk.END)
            self.form_payment_date.insert(0, self.selected_payment.payment_date)
            
            self.form_amount.delete(0, tk.END)
            self.form_amount.insert(0, str(self.selected_payment.amount))
            
            self.form_payment_method.set(self.selected_payment.payment_method)
            
            self.form_payer.delete(0, tk.END)
            self.form_payer.insert(0, self.selected_payment.payer)
            
            self.form_notes.delete(0, tk.END)
            self.form_notes.insert(0, self.selected_payment.notes)
    
    def clear_form(self):
        """
        清空表单
        """
        self.selected_payment = None
        self.form_tenant.set("")
        self.form_month.set("")
        self.form_month['values'] = []
        self.form_payment_date.delete(0, tk.END)
        self.form_payment_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.form_amount.delete(0, tk.END)
        self.form_payment_method.set("现金")
        self.form_payer.delete(0, tk.END)
        self.form_payer.insert(0, "admin")
        self.form_notes.delete(0, tk.END)
    
    def add_payment(self):
        """
        添加收费记录
        """
        self.clear_form()
    
    def edit_payment(self):
        """
        编辑收费记录
        """
        if not self.selected_payment:
            messagebox.showwarning("警告", "请先选择要编辑的收费记录")
            return
        # 表单已经填充，直接编辑
    
    def delete_payment(self):
        """
        删除收费记录并更新相关费用记录状态
        前置检查：如果收费记录已结算，则禁止删除
        """
        if not self.selected_payment:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_payment_to_delete'))
            return
        
        # 检查结算状态：获取收费记录的月份，查看是否已结算
        # 加载费用信息（如果尚未加载）
        if not self.selected_payment.charge:
            self.selected_payment.load_charge_info()
        
        if self.selected_payment.charge:
            month = self.selected_payment.charge.month
            settlement = Settlement.get_by_month(month)
            
            # 如果结算时间不为空，则禁止删除
            if settlement and settlement.settle_date:
                messagebox.showwarning(self.get_text('operation_restriction'), self.get_text('payment_record_settled_cannot_delete'))
                return
        
        if messagebox.askyesno(self.get_text('confirm_delete'), f"{self.get_text('confirm_delete_this_payment_record')}?\n{self.get_text('this_operation_cannot_be_undone')}"):
            try:
                # 获取要删除的收费记录的费用ID
                charge_id = self.selected_payment.charge_id
                
                # 删除收费记录
                if self.selected_payment.delete():
                    # 删除成功后，更新相关费用记录的状态
                    self.update_charge_status(charge_id=charge_id)
                    
                    messagebox.showinfo(self.get_text('success'), self.get_text('payment_record_deleted_successfully_status_updated'))
                    self.load_payment_list()
                    self.clear_form()
                    
                    # 通知费用管理视图刷新列表
                    if self.main_window:
                        self.main_window.refresh_view("charge")
                else:
                    messagebox.showerror(self.get_text('error'), self.get_text('failed_to_delete_payment_record'))
            except Exception as e:
                messagebox.showerror(self.get_text('error'), f"{self.get_text('failed_to_delete_payment_record')}: {str(e)}")
    
    def save_payment(self):
        """
        保存收费记录
        """
        # 获取表单数据
        tenant_name = self.form_tenant.get().strip()
        month = self.form_month.get().strip()
        payment_date = self.form_payment_date.get().strip()
        amount_str = self.form_amount.get().strip()
        payment_method = self.form_payment_method.get().strip()
        payer = self.form_payer.get().strip()
        notes = self.form_notes.get().strip()
        
        # 验证数据
        if not tenant_name:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_tenant'))
            return
        
        if not month:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_charge_month'))
            return
        
        if not amount_str:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_enter_amount'))
            return
        
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning(self.get_text('warning'), self.get_text('amount_must_be_number'))
            return
        
        if amount <= 0:
            messagebox.showwarning(self.get_text('warning'), self.get_text('amount_must_be_greater_than_zero'))
            return
        
        if not payment_date:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_enter_payment_date'))
            return
        
        if not payment_method:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_payment_method'))
            return
        
        if not payer:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_enter_payer'))
            return
        
        # 获取租户对象
        tenant = next((t for t in Tenant.get_all() if t.name == tenant_name), None)
        if not tenant:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_valid_tenant'))
            return
        
        # 获取费用对象
        charge = next((c for c in Charge.get_by_tenant(tenant.id) if c.month == month), None)
        if not charge:
            messagebox.showwarning(self.get_text('warning'), self.get_text('tenant_no_charge_for_month'))
            return
        
        # 保存收费记录
        if self.selected_payment:
            # 更新现有记录
            self.selected_payment.charge_id = charge.id
            self.selected_payment.payment_date = payment_date
            self.selected_payment.amount = amount
            self.selected_payment.payment_method = payment_method
            self.selected_payment.payer = payer
            self.selected_payment.notes = notes
            
            if self.selected_payment.save():
                # 保存成功后，更新费用记录状态
                self.update_charge_status(tenant, month, amount)
                
                messagebox.showinfo(self.get_text('success'), self.get_text('payment_record_updated_successfully'))
                self.load_payment_list()
                
                # 通知费用管理视图刷新列表
                if self.main_window:
                    self.main_window.refresh_view("charge")
            else:
                messagebox.showerror(self.get_text('error'), self.get_text('failed_to_update_payment_record'))
        else:
            # 添加新记录
            payment = Payment(
                charge_id=charge.id,
                payment_date=payment_date,
                amount=amount,
                payment_method=payment_method,
                payer=payer,
                notes=notes
            )
            
            if payment.save():
                # 保存成功后，更新费用记录状态
                self.update_charge_status(tenant, month, amount)
                
                messagebox.showinfo(self.get_text('success'), self.get_text('payment_record_added_successfully'))
                self.load_payment_list()
                self.clear_form()
                
                # 通知费用管理视图刷新列表
                if self.main_window:
                    self.main_window.refresh_view("charge")
            else:
                messagebox.showerror(self.get_text('error'), self.get_text('failed_to_add_payment_record'))
    
    def on_tenant_selected(self, _event=None):
        """
        租户选择事件处理，动态加载费用月份
        """
        tenant_name = self.form_tenant.get()
        if tenant_name:
            tenant = next((t for t in Tenant.get_all() if t.name == tenant_name), None)
            if tenant:
                self.load_charge_months(tenant.id)
                # 检查是否已选择月份，如果是则自动匹配费用记录
                month = self.form_month.get()
                if month:
                    self.debounce_match_charge()
    
    def on_month_selected(self, _event=None):
        """
        费用月份选择事件处理，自动匹配费用记录
        """
        # 检查是否已选择租户，如果是则自动匹配费用记录
        tenant_name = self.form_tenant.get()
        if tenant_name:
            self.debounce_match_charge()
    
    def debounce_match_charge(self):
        """
        防抖处理，避免频繁查询导致的页面卡顿
        当用户连续快速修改字段值时，只在最后一次修改后执行匹配
        """
        # 取消之前的定时器
        if self._match_timer:
            self.parent.after_cancel(self._match_timer)
        
        # 获取当前参数
        tenant_name = self.form_tenant.get().strip()
        month = self.form_month.get().strip()
        current_params = (tenant_name, month)
        
        # 保存当前参数
        self._last_match_params = current_params
        
        # 设置新的定时器，300毫秒后执行匹配
        self._match_timer = self.parent.after(300, lambda: self.match_charge(current_params))
    
    def calculate_paid_amount(self, charge_id):
        """
        计算指定费用记录的已收费用
        :param charge_id: 费用记录ID
        :return: 已收费用总额
        """
        try:
            # 获取该费用记录的所有收费记录
            payments = Payment.get_by_charge(charge_id)
            # 计算已收费用
            paid_amount = sum(payment.amount for payment in payments)
            return paid_amount
        except Exception:
            return 0
    
    def match_charge(self, params):
        """
        自动匹配费用记录
        当租户和月份都选择后，自动查询匹配的费用记录
        :param params: 包含租户名称和月份的元组
        """
        # 检查是否是最新的参数，如果不是则忽略
        if params != self._last_match_params:
            return
        
        # 获取表单数据
        tenant_name, month = params
        
        # 验证租户和月份是否都已选择
        if not tenant_name or not month:
            return
        
        try:
            # 获取租户对象
            tenant = next((t for t in Tenant.get_all() if t.name == tenant_name), None)
            if not tenant:
                return
            
            # 查询满足条件的费用记录
            charges = Charge.get_by_tenant(tenant.id)
            # 严格执行精确匹配，不考虑状态
            matching_charges = [c for c in charges if c.month == month]
            
            # 处理不同的匹配情况
            if len(matching_charges) == 1:
                # 唯一匹配，自动填充金额
                charge = matching_charges[0]
                
                # 计算已收费用
                paid_amount = self.calculate_paid_amount(charge.id)
                # 计算应收费用（应收费用 = 总费用 - 已收费用）
                due_amount = round(charge.total_charge - paid_amount, 2)
                
                # 检查应收费用是否为有效数字
                if (due_amount is not None and isinstance(due_amount, (int, float)) and 
                    not (isinstance(due_amount, float) and (due_amount != due_amount)) and 
                    due_amount > 0):
                    # 覆盖原字段值
                    self.form_amount.delete(0, tk.END)
                    self.form_amount.insert(0, str(due_amount))
                else:
                    # 应收费用为0或无效数字，保持当前值不变
                    pass
            # 如果没有匹配或多条匹配，保持当前值不变
        except Exception as e:
            # 发生错误时，保持当前值不变，显示错误信息
            messagebox.showerror(self.get_text('error'), f"{self.get_text('auto_match_charge_fail')}: {str(e)}")
    
    def show_loading(self, message):
        """
        显示加载状态提示
        :param message: 加载提示信息
        """
        # 检查是否已存在加载提示
        if hasattr(self, 'loading_window') and self.loading_window:
            self.loading_window.destroy()
        
        # 创建加载提示窗口
        self.loading_window = tk.Toplevel(self.parent)
        self.loading_window.title(self.get_text('querying'))
        self.loading_window.geometry("250x80")
        self.loading_window.resizable(False, False)
        
        # 计算位置，使其居中显示
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - 125
        y = parent_y + (parent_height // 2) - 40
        self.loading_window.geometry(f"250x80+{x}+{y}")
        
        # 创建加载标签
        ttk.Label(self.loading_window, text=message).pack(pady=20)
        
        # 更新窗口以确保显示
        self.loading_window.update()
    
    def hide_loading(self):
        """
        隐藏加载状态提示
        """
        if hasattr(self, 'loading_window') and self.loading_window:
            try:
                self.loading_window.destroy()
                self.loading_window = None
            except:
                pass

    def calculate_total_paid(self, charge_id):
        """
        计算指定费用记录的总缴费金额
        :param charge_id: 费用记录ID
        :return: 总缴费金额
        """
        try:
            # 获取该费用记录的所有缴费记录
            payments = Payment.get_by_charge(charge_id)
            # 计算总缴费金额
            total_paid = sum(payment.amount for payment in payments)
            return total_paid
        except Exception as e:
            messagebox.showerror("错误", f"计算总缴费金额失败: {str(e)}")
            return 0

    def update_charge_status(self, tenant=None, month=None, amount=None, charge_id=None):
        """
        根据收费金额或总缴费金额更新费用记录状态
        :param tenant: 租户对象（用于保存收费时）
        :param month: 费用月份（用于保存收费时）
        :param amount: 收费金额（用于保存收费时）
        :param charge_id: 费用记录ID（用于删除收费时）
        """
        try:
            charges = []
            
            if charge_id:
                # 通过费用ID获取特定费用记录
                charge = Charge.get_by_id(charge_id)
                if charge:
                    charges = [charge]
            elif tenant and month:
                # 查询该租户该月份的费用记录
                tenant_charges = Charge.get_by_tenant(tenant.id)
                charges = [c for c in tenant_charges if c.month == month]
            else:
                return
            
            for charge in charges:
                if amount is not None:
                    # 保存收费时，根据当前收费金额更新状态
                    if amount >= charge.total_charge:
                        # 全额缴纳或超额缴纳，状态更新为"已缴"
                        charge.status = self.get_text('paid')
                    else:
                        # 部分缴纳，状态更新为"部分缴纳"
                        charge.status = self.get_text('partially_paid')
                else:
                    # 删除收费时，根据总缴费金额更新状态
                    total_paid = self.calculate_total_paid(charge.id)
                    if total_paid == 0:
                        # 未缴纳，状态更新为"未缴"
                        charge.status = self.get_text('unpaid')
                    elif total_paid >= charge.total_charge:
                        # 全额缴纳或超额缴纳，状态更新为"已缴"
                        charge.status = self.get_text('paid')
                    else:
                        # 部分缴纳，状态更新为"部分缴纳"
                        charge.status = self.get_text('partially_paid')
                
                # 保存费用记录状态更新
                charge.save()
        except Exception as e:
            messagebox.showerror("错误", f"更新费用状态失败: {str(e)}")
    
    def load_charge_months(self, tenant_id):
        """
        加载指定租户的费用月份
        数据来源于抄表管理模块
        :param tenant_id: 租户ID
        """
        try:
            # 获取该租户的所有水电表
            meters = Meter.get_by_tenant(tenant_id)
            if not meters:
                self.form_month['values'] = []
                self.form_month.set("")
                return
            
            # 从抄表记录中获取所有月份
            all_readings = []
            for meter in meters:
                # 获取该电表的所有抄表记录
                meter_readings = MeterReading.get_by_meter(meter.id, limit=100)  # 获取足够多的记录
                all_readings.extend(meter_readings)
            
            # 提取月份并去重
            months = set()
            for reading in all_readings:
                # 从抄表日期中提取月份（格式：YYYY-MM）
                if reading.reading_date:
                    # 确保reading_date是字符串类型
                    reading_date_str = str(reading.reading_date)
                    # 从抄表日期中提取月份（格式：YYYY-MM）
                    if len(reading_date_str) >= 7:
                        month = reading_date_str[:7]  # 提取YYYY-MM部分
                        months.add(month)
            
            # 按时间倒序排序
            sorted_months = sorted(list(months), reverse=True)
            
            # 更新月份下拉框
            self.form_month['values'] = sorted_months
            self.form_month.set("" if sorted_months else "")
        except Exception as e:
            messagebox.showerror("错误", f"加载费用月份失败: {str(e)}")
            self.form_month['values'] = []
            self.form_month.set("")
    
    def query_arrears(self):
        """
        查询欠费信息
        显示所有欠费租户的信息，包括欠费金额和欠费月份
        """
        # 获取所有费用记录
        all_charges = Charge.get_all()
        
        # 创建租户ID到名称的映射
        tenants = Tenant.get_all()
        tenant_map = {t.id: t.name for t in tenants}
        
        # 创建费用ID到已收金额的映射
        payments = Payment.get_all()
        payment_map = {}
        for payment in payments:
            if payment.charge_id not in payment_map:
                payment_map[payment.charge_id] = 0
            payment_map[payment.charge_id] += payment.amount
        
        # 计算欠费信息并更新状态
        arrears_list = []
        for charge in all_charges:
            # 计算已收金额
            received = payment_map.get(charge.id, 0)
            
            # 计算欠费金额
            arrears = charge.total_charge - received
            
            # 更新费用记录状态，确保状态与实际欠费情况一致
            new_status = charge.status
            if arrears == 0:
                new_status = self.get_text('paid')
            elif received > 0:
                new_status = self.get_text('partially_paid')
            else:
                new_status = self.get_text('unpaid')
            
            # 如果状态发生变化，更新数据库
            if charge.status != new_status:
                charge.status = new_status
                charge.save()
            
            # 只有欠费金额大于0的记录才会显示在欠费列表中
            if arrears > 0:
                # 添加到欠费列表
                arrears_list.append({
                    "tenant_id": charge.tenant_id,
                    "tenant_name": tenant_map.get(charge.tenant_id, "未知租户"),
                    "month": charge.month,
                    "total_charge": charge.total_charge,
                    "received": received,
                    "arrears": arrears,
                    "status": charge.status
                })
        
        # 创建欠费查询结果窗口
        arrears_window = tk.Toplevel(self.parent)
        arrears_window.title(self.get_text('arrears_query'))
        arrears_window.geometry("900x500")
        
        # 创建主容器，用于放置表格和统计信息
        main_container = ttk.Frame(arrears_window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 表格和滚动条容器
        table_container = ttk.Frame(main_container)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建结果表格
        columns = ("tenant_name", "month", "total_charge", "received", "arrears", "status")
        tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="extended")
        
        # 设置列标题和宽度
        tree.heading("tenant_name", text=self.get_text('tenant_name'))
        tree.column("tenant_name", width=200, anchor="w")
        
        tree.heading("month", text=self.get_text('month'))
        tree.column("month", width=120, anchor="center")
        
        tree.heading("total_charge", text=self.get_text('total_charge'))
        tree.column("total_charge", width=120, anchor="e")
        
        tree.heading("received", text=self.get_text('paid_amount'))
        tree.column("received", width=120, anchor="e")
        
        tree.heading("arrears", text=self.get_text('due_amount'))
        tree.column("arrears", width=120, anchor="e")
        
        tree.heading("status", text=self.get_text('charge_status'))
        tree.column("status", width=100, anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加数据到表格
        total_arrears = 0
        for arrears in arrears_list:
            tree.insert("", tk.END, values=(arrears["tenant_name"], 
                                           arrears["month"], 
                                           f"{arrears['total_charge']:.2f}", 
                                           f"{arrears['received']:.2f}", 
                                           f"{arrears['arrears']:.2f}", 
                                           arrears["status"]))
            total_arrears += arrears["arrears"]
        
        # 添加总计行
        tree.insert("", tk.END, values=(self.get_text('total'), "", "", f"", f"{total_arrears:.2f}", ""))
        
        # 统计信息和关闭按钮 - 迁移至表格正下方
        stats_frame = ttk.Frame(main_container)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 左侧统计信息区域
        left_stats = ttk.Frame(stats_frame)
        left_stats.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 显示统计信息，水平排列，更紧凑
        ttk.Label(left_stats, text=f"{self.get_text('arrears_count')}: {len(set([a['tenant_id'] for a in arrears_list]))} {self.get_text('households')}").pack(side=tk.LEFT, anchor=tk.CENTER, padx=15, pady=5)
        ttk.Label(left_stats, text=f"{self.get_text('payment_records')}: {len(arrears_list)} {self.get_text('records')}").pack(side=tk.LEFT, anchor=tk.CENTER, padx=15, pady=5)
        ttk.Label(left_stats, text=f"{self.get_text('total_arrears')}: {total_arrears:.2f} {self.get_text('yuan')}").pack(side=tk.LEFT, anchor=tk.CENTER, padx=15, pady=5)
        
        # 右侧操作按钮区域
        right_buttons = ttk.Frame(stats_frame)
        right_buttons.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 全选按钮
        select_all_var = tk.BooleanVar()
        
        def toggle_select_all():
            """
            全选/取消全选功能
            """
            select_all = select_all_var.get()
            for i in range(len(arrears_list)):  # 只处理数据行，不包括总计行
                item = tree.get_children()[i]
                if select_all:
                    tree.selection_add(item)
                else:
                    tree.selection_remove(item)
            
        def on_selection_change(event=None):
            """
            处理列表选择变化，更新全选按钮状态
            """
            selected_items = tree.selection()
            total_items = len(tree.get_children()) - 1  # 减去总计行
            # 检查是否所有数据行都被选中
            if len(selected_items) == total_items and total_items > 0:
                select_all_var.set(True)
            else:
                select_all_var.set(False)
        
        # 创建全选按钮
        select_all_btn = ttk.Checkbutton(right_buttons, text=self.get_text('select_all'), variable=select_all_var, command=toggle_select_all)
        select_all_btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 导入到收费按钮
        ttk.Button(right_buttons, text=self.get_text('import_to_payment'), command=lambda: self.import_to_payment(tree, arrears_window, arrears_list)).pack(side=tk.LEFT, padx=10, pady=5)
        
        # 关闭按钮
        ttk.Button(right_buttons, text=self.get_text('close'), command=arrears_window.destroy).pack(side=tk.LEFT, padx=10, pady=5)
        
        # 绑定选择变化事件
        tree.bind("<<TreeviewSelect>>", on_selection_change)
    
    def import_to_payment(self, tree, arrears_window, arrears_list):
        """
        将选中的欠费记录导入到收费管理页面的明细列表中
        :param tree: 欠费查询结果表格
        :param arrears_window: 欠费查询窗口
        :param arrears_list: 欠费记录列表
        """
        # 获取选中的记录
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_records_to_import'))
            return
        
        # 导入选中的记录
        imported_count = 0
        for item_id in selected_items:
            # 获取选中行的索引
            index = tree.index(item_id)
            # 跳过总计行
            if index >= len(arrears_list):
                continue
            
            # 获取对应的欠费记录
            arrears = arrears_list[index]
            
            # 获取租户对象
            tenant = next((t for t in Tenant.get_all() if t.name == arrears["tenant_name"]), None)
            if not tenant:
                continue
            
            # 获取费用对象
            charge = next((c for c in Charge.get_by_tenant(tenant.id) if c.month == arrears["month"]), None)
            if not charge:
                continue
            
            # 创建Payment对象并保存到数据库
            payment = Payment(
                charge_id=charge.id,
                payment_date=datetime.now().strftime("%Y-%m-%d"),
                amount=arrears["arrears"],
                payment_method="现金",
                payer="admin",
                notes=""
            )
            
            if payment.save():
                # 更新费用记录状态
                self.update_charge_status(tenant=tenant, month=arrears["month"], amount=arrears["arrears"])
                imported_count += 1
        
        # 显示导入结果
        if imported_count > 0:
            # 重新加载收费记录列表，确保显示最新数据
            self.load_payment_list()
            
            # 通知费用管理视图刷新列表
            if self.main_window:
                self.main_window.refresh_view("charge")
                
            messagebox.showinfo("成功", f"已成功导入 {imported_count} 条记录到收费管理页面")
            # 关闭欠费查询窗口
            arrears_window.destroy()
        else:
            messagebox.showwarning("警告", "未导入任何记录")
    
    def generate_payment_receipt(self):
        """
        生成收费凭证
        为选中的收费记录生成PDF格式的收费凭证
        """
        # 检查是否有选中的收费记录
        selected_items = self.payment_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择一条收费记录")
            return
        
        # 获取选中的收费记录
        item_id = selected_items[0]
        values = self.payment_tree.item(item_id, "values")
        payment_id_str = values[-1]  # ID现在在最后一列
        
        try:
            # 转换为整数类型以匹配Payment对象的id类型
            payment_id = int(payment_id_str)
            
            # 查找对应的收费记录
            payment = next((p for p in self.payment_list if p.id == payment_id), None)
        except (ValueError, TypeError):
            messagebox.showerror("错误", "无效的收费记录ID")
            return
        if not payment:
            messagebox.showerror("错误", "未找到选中的收费记录")
            return
        
        # 获取关联的费用和租户信息
        charge = Charge.get_by_id(payment.charge_id)
        if not charge:
            messagebox.showerror("错误", "未找到关联的费用记录")
            return
        
        tenant = Tenant.get_by_id(charge.tenant_id)
        if not tenant:
            messagebox.showerror("错误", "未找到关联的租户信息")
            return
        
        # 1. 解决中文乱码问题：设置支持中文的字体
        # 导入reportlab的字体注册模块
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os
        
        # 2. 自动生成文件名：租户名称+月份+时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"收费凭证_{tenant.name}_{charge.month.replace('-', '')}_{timestamp}.pdf"
        
        # 3. 调整文件保存路径：当前目录下的"导出文件"文件夹
        export_dir = os.path.join(os.getcwd(), "导出文件")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        file_path = os.path.join(export_dir, filename)
        
        try:
            # 注册中文黑体字体
            pdfmetrics.registerFont(TTFont('SimHei', 'simhei.ttf'))
            pdfmetrics.registerFont(TTFont('SimHei-Bold', 'simhei.ttf'))
            
            # 创建PDF文件
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4
            
            # 4. 优化PDF文件的格式和样式
            # 设置标题
            c.setFont("SimHei-Bold", 16)
            c.drawString(100, height - 50, "收费凭证")
            
            # 画分隔线
            c.line(50, height - 60, width - 50, height - 60)
            
            # 设置内容字体
            c.setFont("SimHei", 12)
            
            # 填写收费凭证内容
            y = height - 100
            c.drawString(100, y, f"租户名称: {tenant.name}")
            y -= 25
            c.drawString(100, y, f"租户类型: {tenant.type}")
            y -= 25
            c.drawString(100, y, f"费用月份: {charge.month}")
            y -= 25
            c.drawString(100, y, f"收费日期: {payment.payment_date}")
            y -= 25
            c.drawString(100, y, f"总费用: {charge.total_charge:.2f} 元")
            y -= 25
            c.drawString(100, y, f"本次收费: {payment.amount:.2f} 元")
            y -= 25
            c.drawString(100, y, f"支付方式: {payment.payment_method}")
            y -= 25
            c.drawString(100, y, f"收款人: {payment.payer}")
            y -= 25
            c.drawString(100, y, f"备注: {payment.notes if payment.notes else '无'}")
            
            # 画分隔线
            y -= 50
            c.line(50, y, width - 50, y)
            
            # 填写底部信息
            c.setFont("SimHei", 10)
            c.drawString(100, y - 25, "本凭证为电子凭证，与纸质凭证具有同等效力")
            c.drawString(100, y - 45, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, y - 65, f"凭证编号: {payment.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            # 保存PDF文件
            c.save()
            
            messagebox.showinfo("成功", f"收费凭证已成功生成到\n{file_path}")
            
            # 5. 实现PDF文件生成完成后自动打开的功能
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # macOS or Linux
                    subprocess.Popen(['open', file_path])
            except Exception as e:
                print(f"自动打开PDF失败: {str(e)}")
            
            # 询问是否打印
            if messagebox.askyesno("打印", "是否要打印该收费凭证？"):
                # 这里简化实现，实际应该调用打印功能
                os.startfile(file_path, "print")
                
        except Exception as e:
            messagebox.showerror("错误", f"生成收费凭证失败：{str(e)}")
            import traceback
            traceback.print_exc()


class BatchPaymentDialog:
    """
    批量收费对话框类
    用于处理多条收费记录的批量收费操作
    """
    
    def __init__(self, parent, selected_items, payment_list):
        """
        初始化批量收费对话框
        :param parent: 父窗口
        :param selected_items: 选中的Treeview项
        :param payment_list: 收费记录列表
        """
        self.parent = parent
        self.selected_items = selected_items
        self.payment_list = payment_list
        self.success = False
        
        # 创建对话框
        self.top = tk.Toplevel(parent)
        self.top.title("批量收费")
        self.top.geometry("600x500")
        self.top.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(self.top)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部：标题
        title_label = ttk.Label(main_frame, text="批量收费", font=("Arial", 16))
        title_label.pack(side=tk.TOP, pady=10)
        
        # 中部：收费设置
        settings_frame = ttk.LabelFrame(main_frame, text="收费设置")
        settings_frame.pack(fill=tk.X, padx=5, pady=5, expand=False)
        
        # 收费日期
        date_frame = ttk.Frame(settings_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(date_frame, text="收费日期:", width=12).pack(side=tk.LEFT, padx=5, pady=5)
        self.payment_date_var = tk.StringVar()
        self.payment_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.payment_date_var, width=20).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 支付方式
        method_frame = ttk.Frame(settings_frame)
        method_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(method_frame, text="支付方式:", width=12).pack(side=tk.LEFT, padx=5, pady=5)
        self.payment_method_var = tk.StringVar()
        self.payment_method_var.set("现金")
        ttk.Combobox(method_frame, textvariable=self.payment_method_var, 
                     values=["现金", "银行转账", "微信", "支付宝"], width=18).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 收款人
        payer_frame = ttk.Frame(settings_frame)
        payer_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(payer_frame, text="收款人:", width=12).pack(side=tk.LEFT, padx=5, pady=5)
        self.payer_var = tk.StringVar()
        self.payer_var.set("admin")
        ttk.Entry(payer_frame, textvariable=self.payer_var, width=20).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 备注
        notes_frame = ttk.Frame(settings_frame)
        notes_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(notes_frame, text="备注:", width=12).pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.N)
        self.notes_var = tk.StringVar()
        ttk.Entry(notes_frame, textvariable=self.notes_var, width=40).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # 中部：选中记录列表
        list_frame = ttk.LabelFrame(main_frame, text="选中的收费记录")
        list_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)
        
        # 创建列表控件
        columns = ("tenant_name", "month", "amount", "status")
        self.selected_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # 设置列标题和宽度
        self.selected_tree.heading("tenant_name", text="租户名称")
        self.selected_tree.column("tenant_name", width=150, anchor="w")
        
        self.selected_tree.heading("month", text="月份")
        self.selected_tree.column("month", width=100, anchor="center")
        
        self.selected_tree.heading("amount", text="金额")
        self.selected_tree.column("amount", width=100, anchor="e")
        
        self.selected_tree.heading("status", text="状态")
        self.selected_tree.column("status", width=100, anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.selected_tree.yview)
        self.selected_tree.configure(yscroll=scrollbar.set)
        
        self.selected_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 填充选中记录
        self.fill_selected_list()
        
        # 底部：操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # 加载状态标签
        self.loading_label = ttk.Label(button_frame, text="", foreground="blue")
        self.loading_label.pack(side=tk.LEFT, padx=5)
        
        # 右侧：确认和取消按钮
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(right_buttons, text="取消", command=self.cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(right_buttons, text="确认收费", command=self.confirm_payment).pack(side=tk.RIGHT, padx=5)
        
        # 设置窗口居中
        self.top.after(100, self.center_window)
    
    def center_window(self):
        """
        将窗口居中显示
        """
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f"{width}x{height}+{x}+{y}")
    
    def fill_selected_list(self):
        """
        填充选中的收费记录列表
        """
        # 清空现有列表
        for item in self.selected_tree.get_children():
            self.selected_tree.delete(item)
        

        
        # 添加选中的记录
        for item_id in self.selected_items:
            # 获取记录的值
            values = self.parent.payment_tree.item(item_id, "values")
            if values:
                tenant_name = values[1]
                month = values[2]
                amount = values[4]
                
                # 添加到选中列表
                self.selected_tree.insert("", tk.END, values=(tenant_name, month, amount, "待收费"))
    
    def confirm_payment(self):
        """
        确认批量收费
        """
        # 显示确认对话框
        if not messagebox.askyesno("确认批量收费", f"确定要对选中的 {len(self.selected_items)} 条记录进行批量收费吗？"):
            return
        
        # 显示加载状态
        self.loading_label.config(text="正在处理批量收费，请稍候...")
        self.top.update()
        
        # 执行批量收费
        success_count = 0
        fail_count = 0
        failed_records = []
        
        try:
            for item_id in self.selected_items:
                # 获取记录的值
                values = self.parent.payment_tree.item(item_id, "values")
                if values:
                    # 获取费用ID（从values中获取，假设ID在最后一列）
                    charge_id = int(values[-1])
                    
                    # 创建新的收费记录
                    payment = Payment(
                        charge_id=charge_id,
                        payment_date=self.payment_date_var.get(),
                        amount=float(values[4]),
                        payment_method=self.payment_method_var.get(),
                        payer=self.payer_var.get(),
                        notes=self.notes_var.get()
                    )
                    
                    # 保存收费记录
                    if payment.save():
                        success_count += 1
                        # 更新费用状态
                        charge = Charge.get_by_id(charge_id)
                        if charge:
                            # 计算总缴费金额
                            total_paid = sum(p.amount for p in Payment.get_by_charge(charge_id))
                            if total_paid >= charge.total_charge:
                                charge.status = "已缴"
                            elif total_paid > 0:
                                charge.status = "部分缴纳"
                            else:
                                charge.status = "未缴"
                            charge.save()
                    else:
                        fail_count += 1
                        failed_records.append(values[1])  # 记录失败的租户名称
        except Exception as e:
            messagebox.showerror("错误", f"批量收费失败：{str(e)}")
            self.success = False
            self.cancel()
            return
        finally:
            # 隐藏加载状态
            self.loading_label.config(text="")
            self.top.update()
        
        # 显示操作结果
        result_message = f"批量收费完成！\n\n成功: {success_count} 条\n失败: {fail_count} 条"
        if failed_records:
            result_message += f"\n\n失败的记录：\n" + "\n".join(failed_records)
        
        messagebox.showinfo("批量收费结果", result_message)
        
        # 设置成功标志
        self.success = True
        
        # 关闭对话框
        self.top.destroy()
    
    def cancel(self):
        """
        取消批量收费
        """
        self.success = False
        self.top.destroy()
