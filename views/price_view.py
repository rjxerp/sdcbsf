#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格管理视图
负责处理水电费价格的添加、编辑、删除和查询功能
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from models.price import Price
from utils.language_utils import LanguageUtils

class PriceView:
    """价格管理视图类"""
    
    def __init__(self, parent, language_utils):
        """
        初始化价格管理视图
        :param parent: 父窗口组件
        :param language_utils: 语言工具类实例
        """
        self.parent = parent
        self.language_utils = language_utils
        self.price_list = []
        self.selected_price = None
        self.create_widgets()
        self.load_price_list()
        
    def get_text(self, key):
        """
        获取翻译文本
        :param key: 文本键名
        :return: 翻译后的文本
        """
        return self.language_utils.get_text(key)
        
    def resource_type_to_text(self, resource_type):
        """
        将数据库中的资源类型转换为显示文本
        :param resource_type: 数据库中的资源类型
        :return: 翻译后的显示文本
        """
        if resource_type == 'water':
            return self.get_text('water')
        elif resource_type == 'electricity':
            return self.get_text('electricity')
        return resource_type
        
    def text_to_resource_type(self, text):
        """
        将显示文本转换为数据库中的资源类型
        :param text: 显示文本
        :return: 数据库中的资源类型
        """
        if text == self.get_text('water'):
            return 'water'
        elif text == self.get_text('electricity'):
            return 'electricity'
        return text
        
    def tenant_type_to_text(self, tenant_type):
        """
        将数据库中的租户类型转换为显示文本
        :param tenant_type: 数据库中的租户类型
        :return: 翻译后的显示文本
        """
        if tenant_type == 'office':
            return self.get_text('office')
        elif tenant_type == 'storefront':
            return self.get_text('storefront')
        elif tenant_type == 'all':
            return self.get_text('all')
        return tenant_type
        
    def text_to_tenant_type(self, text):
        """
        将显示文本转换为数据库中的租户类型
        :param text: 显示文本
        :return: 数据库中的租户类型
        """
        if text == self.get_text('office'):
            return 'office'
        elif text == self.get_text('storefront'):
            return 'storefront'
        elif text == self.get_text('all'):
            return 'all'
        return text
        
    def update_language(self):
        """
        更新界面语言
        """
        # 更新搜索框文本
        self.search_labels['resource_type_label']['text'] = self.get_text('resource_type') + ':'
        self.search_labels['tenant_type_label']['text'] = self.get_text('tenant_type') + ':'
        self.search_buttons['search_btn']['text'] = self.get_text('button_search')
        self.search_buttons['reset_btn']['text'] = self.get_text('button_reset')
        
        # 更新搜索下拉框选项
        self.search_resource_type['values'] = ["", self.get_text('water'), self.get_text('electricity')]
        self.search_tenant_type['values'] = ["", self.get_text('office'), self.get_text('storefront'), self.get_text('all')]
        
        # 更新列表列标题
        self.price_tree.heading("serial", text=self.get_text('serial'))
        self.price_tree.heading("resource_type", text=self.get_text('resource_type'))
        self.price_tree.heading("tenant_type", text=self.get_text('tenant_type'))
        self.price_tree.heading("price", text=self.get_text('price'))
        self.price_tree.heading("start_date", text=self.get_text('effective_start_date'))
        self.price_tree.heading("end_date", text=self.get_text('effective_end_date'))
        self.price_tree.heading("create_time", text=self.get_text('create_time'))
        
        # 更新操作按钮文本
        self.action_buttons['add_btn']['text'] = self.get_text('button_add') + self.get_text('price')
        self.action_buttons['edit_btn']['text'] = self.get_text('button_edit') + self.get_text('price')
        self.action_buttons['delete_btn']['text'] = self.get_text('button_delete') + self.get_text('price')
        self.action_buttons['refresh_btn']['text'] = self.get_text('refresh_list')
        
        # 更新表单标题
        self.form_title['text'] = self.get_text('price_details')
        
        # 更新表单标签
        self.form_labels['resource_type_label']['text'] = self.get_text('resource_type') + ':'
        self.form_labels['tenant_type_label']['text'] = self.get_text('tenant_type') + ':'
        self.form_labels['price_label']['text'] = self.get_text('price') + ':'
        self.form_labels['start_date_label']['text'] = self.get_text('effective_start_date') + ':'
        self.form_labels['date_format_label']['text'] = self.get_text('date_format_yyyy_mm_dd')
        self.form_labels['end_date_label']['text'] = self.get_text('effective_end_date') + ':'
        self.form_labels['end_date_note_label']['text'] = self.get_text('leave_empty_for_permanent')
        
        # 更新表单下拉框选项
        self.form_resource_type['values'] = [self.get_text('water'), self.get_text('electricity')]
        self.form_tenant_type['values'] = [self.get_text('all'), self.get_text('office'), self.get_text('storefront')]
        
        # 更新表单按钮
        self.form_buttons['save_btn']['text'] = self.get_text('button_save')
        self.form_buttons['cancel_btn']['text'] = self.get_text('button_cancel')
        
        # 重新加载列表，确保数据显示正确
        self.load_price_list()
    
    def create_widgets(self):
        """
        创建价格管理界面组件
        """
        # 创建主框架
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧：价格列表和搜索框
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 搜索框
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 搜索标签字典
        self.search_labels = {}
        # 搜索按钮字典
        self.search_buttons = {}
        # 表单标签字典
        self.form_labels = {}
        # 表单按钮字典
        self.form_buttons = {}
        # 操作按钮字典
        self.action_buttons = {}
        
        # 资源类型标签
        self.search_labels['resource_type_label'] = ttk.Label(search_frame, text=self.get_text('resource_type') + ':')
        self.search_labels['resource_type_label'].pack(side=tk.LEFT, padx=5)
        
        self.search_resource_type = ttk.Combobox(search_frame, values=["", self.get_text('water'), self.get_text('electricity')])
        self.search_resource_type.pack(side=tk.LEFT, padx=5)
        
        # 租户类型标签
        self.search_labels['tenant_type_label'] = ttk.Label(search_frame, text=self.get_text('tenant_type') + ':')
        self.search_labels['tenant_type_label'].pack(side=tk.LEFT, padx=5)
        
        self.search_tenant_type = ttk.Combobox(search_frame, values=["", self.get_text('office'), self.get_text('storefront'), self.get_text('all')])
        self.search_tenant_type.pack(side=tk.LEFT, padx=5)
        
        # 搜索按钮
        self.search_buttons['search_btn'] = ttk.Button(search_frame, text=self.get_text('button_search'), command=self.search_prices)
        self.search_buttons['search_btn'].pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        self.search_buttons['reset_btn'] = ttk.Button(search_frame, text=self.get_text('button_reset'), command=self.reset_search)
        self.search_buttons['reset_btn'].pack(side=tk.LEFT, padx=5)
        
        # 价格列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 列表控件 - 修改列定义，添加序号列，移除ID列显示
        columns = ("serial", "resource_type", "tenant_type", "price", "start_date", "end_date", "create_time")
        self.price_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        self.price_tree.heading("serial", text=self.get_text('serial'))
        self.price_tree.column("serial", width=80, anchor="center")
        
        self.price_tree.heading("resource_type", text=self.get_text('resource_type'))
        self.price_tree.column("resource_type", width=80, anchor="center")
        
        self.price_tree.heading("tenant_type", text=self.get_text('tenant_type'))
        self.price_tree.column("tenant_type", width=100, anchor="center")
        
        self.price_tree.heading("price", text=self.get_text('price'))
        self.price_tree.column("price", width=80, anchor="e")
        
        self.price_tree.heading("start_date", text=self.get_text('effective_start_date'))
        self.price_tree.column("start_date", width=120, anchor="center")
        
        self.price_tree.heading("end_date", text=self.get_text('effective_end_date'))
        self.price_tree.column("end_date", width=120, anchor="center")
        
        self.price_tree.heading("create_time", text=self.get_text('create_time'))
        self.price_tree.column("create_time", width=150, anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.price_tree.yview)
        self.price_tree.configure(yscroll=scrollbar.set)
        
        self.price_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 列表操作按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # 添加价格按钮
        self.action_buttons['add_btn'] = ttk.Button(button_frame, text=self.get_text('button_add') + self.get_text('price'), command=self.add_price)
        self.action_buttons['add_btn'].pack(side=tk.LEFT, padx=5)
        
        # 编辑价格按钮
        self.action_buttons['edit_btn'] = ttk.Button(button_frame, text=self.get_text('button_edit') + self.get_text('price'), command=self.edit_price)
        self.action_buttons['edit_btn'].pack(side=tk.LEFT, padx=5)
        
        # 删除价格按钮
        self.action_buttons['delete_btn'] = ttk.Button(button_frame, text=self.get_text('button_delete') + self.get_text('price'), command=self.delete_price)
        self.action_buttons['delete_btn'].pack(side=tk.LEFT, padx=5)
        
        # 刷新列表按钮
        self.action_buttons['refresh_btn'] = ttk.Button(button_frame, text=self.get_text('refresh_list'), command=self.load_price_list)
        self.action_buttons['refresh_btn'].pack(side=tk.LEFT, padx=5)
        
        # 右侧：价格明细表单
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 表单标题
        self.form_title = ttk.Label(right_frame, text=self.get_text('price_details'), font=("Arial", 14))
        self.form_title.pack(side=tk.TOP, pady=10)
        
        # 表单框架
        form_frame = ttk.Frame(right_frame)
        form_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 表单控件
        row = 0
        
        # 资源类型
        self.form_labels['resource_type_label'] = ttk.Label(form_frame, text=self.get_text('resource_type') + ':')
        self.form_labels['resource_type_label'].grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.form_resource_type = ttk.Combobox(form_frame, values=[self.get_text('water'), self.get_text('electricity')])
        self.form_resource_type.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 租户类型
        self.form_labels['tenant_type_label'] = ttk.Label(form_frame, text=self.get_text('tenant_type') + ':')
        self.form_labels['tenant_type_label'].grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.form_tenant_type = ttk.Combobox(form_frame, values=[self.get_text('all'), self.get_text('office'), self.get_text('storefront')])
        self.form_tenant_type.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 单价
        self.form_labels['price_label'] = ttk.Label(form_frame, text=self.get_text('price') + ':')
        self.form_labels['price_label'].grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.form_price = ttk.Entry(form_frame)
        self.form_price.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 生效开始日期
        self.form_labels['start_date_label'] = ttk.Label(form_frame, text=self.get_text('effective_start_date') + ':')
        self.form_labels['start_date_label'].grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.form_start_date = ttk.Entry(form_frame)
        self.form_start_date.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.form_labels['date_format_label'] = ttk.Label(form_frame, text="(" + self.get_text('date_format') + ": YYYY-MM-DD)")
        self.form_labels['date_format_label'].grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 生效结束日期
        self.form_labels['end_date_label'] = ttk.Label(form_frame, text=self.get_text('effective_end_date') + ':')
        self.form_labels['end_date_label'].grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.form_end_date = ttk.Entry(form_frame)
        self.form_end_date.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.form_labels['end_date_note_label'] = ttk.Label(form_frame, text="(" + self.get_text('leave_empty_for_permanent') + ")")
        self.form_labels['end_date_note_label'].grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 表单操作按钮
        self.form_buttons['save_btn'] = ttk.Button(form_frame, text=self.get_text('button_save'), command=self.save_price)
        self.form_buttons['save_btn'].grid(row=row, column=0, sticky=tk.E, padx=5, pady=10)
        
        self.form_buttons['cancel_btn'] = ttk.Button(form_frame, text=self.get_text('button_cancel'), command=self.clear_form)
        self.form_buttons['cancel_btn'].grid(row=row, column=1, sticky=tk.W, padx=5, pady=10)
        
        # 绑定列表选择事件
        self.price_tree.bind("<<TreeviewSelect>>", self.on_price_select)
    
    def load_price_list(self):
        """
        加载价格列表
        """
        # 清空现有列表
        for item in self.price_tree.get_children():
            self.price_tree.delete(item)
        
        try:
            # 获取价格列表
            self.price_list = Price.get_all()
            
            # 按租户类型升序排列
            self.price_list.sort(key=lambda x: x.tenant_type)
            
            # 添加到列表控件，添加序号列
            for idx, price in enumerate(self.price_list, 1):
                # 转换资源类型和租户类型为显示文本
                display_resource_type = self.resource_type_to_text(price.resource_type)
                display_tenant_type = self.tenant_type_to_text(price.tenant_type)
                self.price_tree.insert("", tk.END, values=(idx, display_resource_type, 
                                                        display_tenant_type, 
                                                        price.price, 
                                                        price.start_date, 
                                                        price.end_date or "", 
                                                        price.create_time), tags=(str(price.id),))
        except Exception as e:
            # 添加错误处理，处理数据加载失败的情况
            messagebox.showerror(self.get_text('error'), f"{self.get_text('price_list_refresh_fail')}: {str(e)}")
            # 恢复到空列表状态
            self.price_list = []
    
    def search_prices(self):
        """
        搜索价格
        """
        # 获取搜索条件
        resource_type_text = self.search_resource_type.get()
        tenant_type_text = self.search_tenant_type.get()
        
        # 构建过滤条件
        filters = {}
        if resource_type_text:
            resource_type = self.text_to_resource_type(resource_type_text)
            filters['resource_type'] = resource_type
        if tenant_type_text:
            tenant_type = self.text_to_tenant_type(tenant_type_text)
            filters['tenant_type'] = tenant_type
        
        # 加载过滤后的列表
        self.price_list = Price.get_all(filters)
        
        # 按租户类型升序排列
        self.price_list.sort(key=lambda x: x.tenant_type)
        
        # 清空现有列表
        for item in self.price_tree.get_children():
            self.price_tree.delete(item)
        
        # 添加到列表控件，添加序号列
        for idx, price in enumerate(self.price_list, 1):
            # 转换资源类型和租户类型为显示文本
            display_resource_type = self.resource_type_to_text(price.resource_type)
            display_tenant_type = self.tenant_type_to_text(price.tenant_type)
            self.price_tree.insert("", tk.END, values=(idx, display_resource_type, 
                                                    display_tenant_type, 
                                                    price.price, 
                                                    price.start_date, 
                                                    price.end_date or "", 
                                                    price.create_time), tags=(str(price.id),))
    
    def reset_search(self):
        """
        重置搜索条件
        """
        self.search_resource_type.set("")
        self.search_tenant_type.set("")
        self.load_price_list()
    
    def on_price_select(self, _event=None):
        """
        列表选择事件处理
        """
        selected_items = self.price_tree.selection()
        if selected_items:
            item_id = selected_items[0]
            # 从tags中获取价格ID，而不是从values[0]获取
            tags = self.price_tree.item(item_id, "tags")
            if tags:
                price_id = int(tags[0])
                
                # 查找对应的价格对象
                # 首先尝试从当前价格列表中查找
                self.selected_price = next((p for p in self.price_list if p.id == price_id), None)
                
                # 如果当前列表中找不到（可能是因为搜索后的列表没有包含完整的价格对象信息），则重新从数据库获取
                if not self.selected_price:
                    self.selected_price = Price.get_by_id(price_id)
                
                if self.selected_price:
                    self.fill_form()
                else:
                    messagebox.showwarning(self.get_text('warning'), self.get_text('cannot_find_price_details'))
        else:
            # 取消选择时，清空表单和选择状态
            self.clear_form()
    
    def fill_form(self):
        """
        填充表单
        """
        if self.selected_price:
            # 保存当前选中的价格对象，避免被清空
            current_selected = self.selected_price
            
            # 清空表单字段，但保留选中状态
            self.form_resource_type.set("")
            self.form_tenant_type.set("")
            self.form_price.delete(0, tk.END)
            self.form_start_date.delete(0, tk.END)
            self.form_end_date.delete(0, tk.END)
            
            # 恢复选中的价格对象
            self.selected_price = current_selected
            
            # 资源类型
            display_resource_type = self.resource_type_to_text(self.selected_price.resource_type)
            self.form_resource_type.set(display_resource_type)
            
            # 租户类型
            display_tenant_type = self.tenant_type_to_text(self.selected_price.tenant_type)
            self.form_tenant_type.set(display_tenant_type)
            
            # 单价
            self.form_price.delete(0, tk.END)
            self.form_price.insert(0, str(self.selected_price.price))
            
            # 生效开始日期
            self.form_start_date.delete(0, tk.END)
            self.form_start_date.insert(0, self.selected_price.start_date)
            
            # 生效结束日期
            self.form_end_date.delete(0, tk.END)
            if self.selected_price.end_date:
                self.form_end_date.insert(0, self.selected_price.end_date)
            
            # 确保表单处于编辑模式，禁用资源类型和租户类型的更改
            # 这样可以避免用户在编辑时更改关键分类字段
            self.form_resource_type['state'] = 'disabled'
            self.form_tenant_type['state'] = 'disabled'
        else:
            # 如果没有选中的价格，确保表单处于添加模式，启用所有字段
            self.form_resource_type['state'] = 'normal'
            self.form_tenant_type['state'] = 'normal'
    
    def clear_form(self):
        """
        清空表单
        """
        self.selected_price = None
        
        # 清空表单字段
        self.form_resource_type.set("")
        self.form_tenant_type.set("")
        self.form_price.delete(0, tk.END)
        self.form_start_date.delete(0, tk.END)
        self.form_end_date.delete(0, tk.END)
        
        # 确保所有字段处于可编辑状态（添加模式）
        self.form_resource_type['state'] = 'normal'
        self.form_tenant_type['state'] = 'normal'
    
    def add_price(self):
        """
        添加价格
        """
        self.clear_form()
    
    def edit_price(self):
        """
        编辑价格
        """
        if not self.selected_price:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_price_edit'))
            return
        
        # 确保表单已填充数据
        self.fill_form()
        
        # 添加明确的用户反馈，提示用户正在编辑价格
        messagebox.showinfo(self.get_text('info'), f"{self.get_text('entered_edit_mode')} {self.selected_price.resource_type} {self.get_text('price_record')}\n{self.get_text('please_modify_form_and_save')}")
        
        # 高亮显示正在编辑的行
        for item in self.price_tree.get_children():
            tags = self.price_tree.item(item, "tags")
            if tags and int(tags[0]) == self.selected_price.id:
                self.price_tree.selection_set(item)
                self.price_tree.focus(item)
                break
    
    def delete_price(self):
        """
        删除价格
        """
        if not self.selected_price:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_price_delete'))
            return
        
        # 显示更详细的确认对话框，包含要删除的价格信息
        confirm_message = f"{self.get_text('confirm_delete')} {self.get_text('price_record')}?\n\n"
        confirm_message += f"{self.get_text('resource_type')}: {self.selected_price.resource_type}\n"
        confirm_message += f"{self.get_text('tenant_type')}: {self.selected_price.tenant_type}\n"
        confirm_message += f"{self.get_text('price')}: {self.selected_price.price} {self.get_text('yuan')}\n"
        confirm_message += f"{self.get_text('effective_start_date')}: {self.selected_price.start_date}\n"
        confirm_message += f"{self.get_text('effective_end_date')}: {self.selected_price.end_date or self.get_text('permanent')}\n\n"
        confirm_message += f"{self.get_text('delete_irreversible')} {self.get_text('continue')}?"
        
        if messagebox.askyesno(self.get_text('confirm_delete'), confirm_message):
            try:
                # 执行删除操作
                if self.selected_price.delete():
                    messagebox.showinfo(self.get_text('success'), f"{self.get_text('price')} {self.get_text('delete_success')}")
                    # 刷新列表
                    self.load_price_list()
                    # 清空表单
                    self.clear_form()
                else:
                    messagebox.showerror(self.get_text('error'), f"{self.get_text('price')} {self.get_text('delete_fail')} {self.get_text('database_error')}")
            except Exception as e:
                # 添加必要的错误处理机制
                messagebox.showerror(self.get_text('error'), f"{self.get_text('delete_price_exception')}: {str(e)}")
    
    def save_price(self):
        """
        保存价格信息
        """
        # 获取表单数据
        resource_type_text = self.form_resource_type.get().strip()
        tenant_type_text = self.form_tenant_type.get().strip()
        
        # 转换为数据库中的值
        resource_type = self.text_to_resource_type(resource_type_text)
        tenant_type = self.text_to_tenant_type(tenant_type_text)
        price_str = self.form_price.get().strip()
        start_date = self.form_start_date.get().strip()
        end_date = self.form_end_date.get().strip() or None
        
        # 验证数据
        if not resource_type:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_resource_type'))
            return
        
        if not tenant_type:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_select_tenant_type'))
            return
        
        if not price_str:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_enter_price'))
            return
        
        try:
            price = float(price_str)
            if price < 0:
                messagebox.showwarning(self.get_text('warning'), self.get_text('price_cannot_be_negative'))
                return
            elif price == 0:
                messagebox.showwarning(self.get_text('warning'), self.get_text('price_cannot_be_zero'))
                return
        except ValueError:
            messagebox.showwarning(self.get_text('warning'), self.get_text('price_must_be_valid_number'))
            return
        
        if not start_date:
            messagebox.showwarning(self.get_text('warning'), self.get_text('please_enter_effective_start_date'))
            return
        
        # 验证日期格式
        if len(start_date) != 10 or start_date[4] != '-' or start_date[7] != '-':
            messagebox.showwarning(self.get_text('warning'), f"{self.get_text('effective_start_date_format_error')}\n{self.get_text('correct_format')}: YYYY-MM-DD")
            return
        
        if end_date:
            if len(end_date) != 10 or end_date[4] != '-' or end_date[7] != '-':
                messagebox.showwarning(self.get_text('warning'), f"{self.get_text('effective_end_date_format_error')}\n{self.get_text('correct_format')}: YYYY-MM-DD")
                return
            
            # 检查日期逻辑：开始日期不能晚于结束日期
            if start_date > end_date:
                messagebox.showwarning(self.get_text('warning'), self.get_text('start_date_cannot_be_later_than_end_date'))
                return
        
        try:
            # 保存价格信息
            if self.selected_price:
                # 更新现有价格
                self.selected_price.resource_type = resource_type
                self.selected_price.tenant_type = tenant_type
                self.selected_price.price = price
                self.selected_price.start_date = start_date
                self.selected_price.end_date = end_date
                
                if self.selected_price.save():
                    messagebox.showinfo(self.get_text('success'), f"{self.get_text('price')} {self.get_text('update_success')}")
                    self.load_price_list()
                    self.clear_form()
                else:
                    messagebox.showerror(self.get_text('error'), f"{self.get_text('price')} {self.get_text('update_fail')} {self.get_text('database_error')}")
            else:
                # 添加新价格
                new_price = Price(
                    resource_type=resource_type,
                    tenant_type=tenant_type,
                    price=price,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if new_price.save():
                    messagebox.showinfo(self.get_text('success'), f"{self.get_text('price')} {self.get_text('add_success')}")
                    self.load_price_list()
                    self.clear_form()
                else:
                    messagebox.showerror(self.get_text('error'), f"{self.get_text('price')} {self.get_text('add_fail')} {self.get_text('database_error_or_duplicate')}")
        except Exception as e:
            # 添加错误处理，处理保存过程中可能出现的异常
            messagebox.showerror(self.get_text('error'), f"{self.get_text('save_price_exception')}: {str(e)}")