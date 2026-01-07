#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理视图
负责处理用户的添加、编辑、删除和查询功能
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from models.user import User
from utils.language_utils import LanguageUtils

class UserView:
    """用户管理视图类"""
    
    def __init__(self, parent, current_user=None, language_utils=None):
        """
        初始化用户管理视图
        :param parent: 父窗口组件
        :param current_user: 当前登录用户对象
        :param language_utils: 语言工具类实例
        """
        self.parent = parent
        self.user_list = []
        self.selected_user = None
        # 当前登录用户信息
        self.current_user = current_user
        # 权限控制标志
        self.is_admin = False
        self.current_user_id = None
        
        # 初始化权限
        if current_user:
            self.is_admin = current_user.role == "管理员"
            self.current_user_id = current_user.id
        
        # 使用传入的语言工具或创建新实例
        self.language_utils = language_utils if language_utils else LanguageUtils()
        self.create_widgets()
        self.load_user_list()
        self.apply_permissions()
    
    def check_permission(self, action, target_user_id=None):
        """
        检查用户权限
        :param action: 操作类型（view/edit/delete）
        :param target_user_id: 目标用户ID
        :return: 是否有权限执行该操作
        """
        if self.is_admin:
            return True
        
        if target_user_id is None:
            return False
        
        # 非管理员只能操作自己
        return target_user_id == self.current_user_id
    
    def apply_permissions(self):
        """
        应用权限控制
        在页面加载时执行，控制UI元素的显示和操作权限
        """
        # 非管理员隐藏删除按钮
        if not self.is_admin:
            self.delete_button.pack_forget()
        else:
            # 管理员显示删除按钮
            self.delete_button.pack(side=tk.LEFT, padx=10)
        
        # 非管理员只能编辑自己的角色信息
        if not self.is_admin and self.selected_user:
            # 禁用角色选择，非管理员不能修改自己的角色
            self.form_role.config(state="disabled")
        else:
            self.form_role.config(state="enabled")
    
    def get_text(self, key):
        """
        获取当前语言的文本
        :param key: 文本键名
        :return: 对应语言的文本
        """
        return self.language_utils.get_text(key)
    
    def update_language(self):
        """
        更新语言
        当系统语言切换时调用，更新界面上所有文本
        """
        # 更新搜索框标签和按钮
        search_frame = self.parent.winfo_children()[0].winfo_children()[0]  # 获取搜索框架
        search_children = search_frame.winfo_children()
        
        # 更新用户名标签
        if len(search_children) > 0 and isinstance(search_children[0], ttk.Label):
            search_children[0].config(text=self.get_text("username")+":")
        
        # 更新角色标签
        if len(search_children) > 2 and isinstance(search_children[2], ttk.Label):
            search_children[2].config(text=self.get_text("role")+":")
        
        # 更新搜索按钮
        if len(search_children) > 4 and isinstance(search_children[4], ttk.Button):
            search_children[4].config(text=self.get_text("button_search"))
        
        # 更新重置按钮
        if len(search_children) > 5 and isinstance(search_children[5], ttk.Button):
            search_children[5].config(text=self.get_text("button_reset"))
        
        # 更新搜索角色下拉框选项
        self.search_role.config(values=["", self.get_text("admin"), self.get_text("reader")])
        
        # 更新列标题
        self.user_tree.heading("username", text=self.get_text("username"))
        self.user_tree.heading("role", text=self.get_text("role"))
        self.user_tree.heading("status", text=self.get_text("status"))
        self.user_tree.heading("create_time", text=self.get_text("create_time"))
        
        # 更新表单标题
        main_frame = self.parent.winfo_children()[0]
        right_frame = main_frame.winfo_children()[1] if len(main_frame.winfo_children()) > 1 else None
        if right_frame:
            form_title = right_frame.winfo_children()[0] if isinstance(right_frame.winfo_children()[0], ttk.Label) else None
            if form_title:
                form_title.config(text=self.get_text("user_details"))
        
        # 更新表单控件标签和选项
        form_frame = right_frame.winfo_children()[1] if right_frame and len(right_frame.winfo_children()) > 1 else None
        if form_frame:
            form_children = form_frame.winfo_children()
            if len(form_children) > 0 and isinstance(form_children[0], ttk.Label):
                form_children[0].config(text=self.get_text("username")+":")
            if len(form_children) > 2 and isinstance(form_children[2], ttk.Label):
                form_children[2].config(text=self.get_text("password")+":")
            if len(form_children) > 4 and isinstance(form_children[4], ttk.Label):
                form_children[4].config(text=self.get_text("role")+":")
            if len(form_children) > 6 and isinstance(form_children[6], ttk.Label):
                form_children[6].config(text=self.get_text("status")+":")
        
        # 更新表单下拉框选项
        self.form_role.config(values=[self.get_text("admin"), self.get_text("reader")])
        self.form_status.config(values=[self.get_text("enabled"), self.get_text("disabled")])
        
        # 更新按钮文本
        self.save_button.config(text=self.get_text("button_save"))
        self.delete_button.config(text=self.get_text("button_delete"))
        self.cancel_button.config(text=self.get_text("button_cancel"))
        
        # 重新加载用户列表，更新角色和状态文本
        self.load_user_list()
    
    def create_widgets(self):
        """
        创建用户管理界面组件
        """
        # 创建主框架
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧：用户列表和搜索框
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 搜索框
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text=self.get_text("username")+":").pack(side=tk.LEFT, padx=5)
        self.search_username = ttk.Entry(search_frame)
        self.search_username.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(search_frame, text=self.get_text("role")+":").pack(side=tk.LEFT, padx=5)
        self.search_role = ttk.Combobox(search_frame, values=["", self.get_text("admin"), self.get_text("reader")])
        self.search_role.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text=self.get_text("button_search"), command=self.search_users).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text=self.get_text("button_reset"), command=self.reset_search).pack(side=tk.LEFT, padx=5)
        
        # 用户列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 列表控件
        columns = ("id", "username", "role", "status", "create_time")
        self.user_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        self.user_tree.heading("id", text="ID")
        self.user_tree.column("id", width=50, anchor="center")
        
        self.user_tree.heading("username", text=self.get_text("username"))
        self.user_tree.column("username", width=150, anchor="w")
        
        self.user_tree.heading("role", text=self.get_text("role"))
        self.user_tree.column("role", width=100, anchor="center")
        
        self.user_tree.heading("status", text=self.get_text("status"))
        self.user_tree.column("status", width=100, anchor="center")
        
        self.user_tree.heading("create_time", text=self.get_text("create_time"))
        self.user_tree.column("create_time", width=150, anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscroll=scrollbar.set)
        
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        

        
        # 右侧：用户明细表单
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 表单标题
        ttk.Label(right_frame, text=self.get_text("user_details"), font=("Arial", 14)).pack(side=tk.TOP, pady=10)
        
        # 表单框架
        form_frame = ttk.Frame(right_frame)
        form_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 表单控件
        row = 0
        
        # 用户名
        ttk.Label(form_frame, text=self.get_text("username")+":").grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
        self.form_username = ttk.Entry(form_frame)
        self.form_username.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 密码
        ttk.Label(form_frame, text=self.get_text("password")+":").grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
        self.form_password = ttk.Entry(form_frame, show="*")
        self.form_password.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 角色
        ttk.Label(form_frame, text=self.get_text("role")+":").grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
        self.form_role = ttk.Combobox(form_frame, values=[self.get_text("admin"), self.get_text("reader")])
        self.form_role.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 状态
        ttk.Label(form_frame, text=self.get_text("status")+":").grid(row=row, column=0, sticky=tk.E, padx=5, pady=5)
        self.form_status = ttk.Combobox(form_frame, values=[self.get_text("enabled"), self.get_text("disabled")])
        self.form_status.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 表单操作按钮 - 优化布局
        button_container = ttk.Frame(form_frame)
        button_container.grid(row=row, column=0, columnspan=3, pady=10)
        
        # 创建并配置按钮，使用统一间距和对齐方式
        self.save_button = ttk.Button(button_container, text=self.get_text("button_save"), command=self.save_user, width=10)
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        self.delete_button = ttk.Button(button_container, text=self.get_text("button_delete"), command=self.delete_user, width=10)
        self.delete_button.pack(side=tk.LEFT, padx=10)
        
        self.cancel_button = ttk.Button(button_container, text=self.get_text("button_cancel"), command=self.clear_form, width=10)
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        
        # 绑定列表选择事件
        self.user_tree.bind("<<TreeviewSelect>>", self.on_user_select)
    
    def load_user_list(self):
        """
        加载用户列表
        包含加载状态提示、错误处理和权限控制
        """
        try:
            # 清空现有列表
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            
            # 添加临时加载提示
            self.user_tree.insert("", tk.END, values=("-", self.get_text("loading"), "", "", ""))
            
            # 获取用户列表（模拟网络延迟，提高用户体验）
            self.parent.update_idletasks()
            # 后端已实现权限控制，直接传递current_user即可
            all_users = User.get_all(self.current_user)
            self.user_list = all_users
            
            # 重新清空列表并添加实际数据
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            
            # 添加到列表控件
            for user in self.user_list:
                # 转换角色和状态为当前语言
                role_text = self.get_text("admin") if user.role == "管理员" else self.get_text("reader")
                status_text = self.get_text("enabled") if user.status == "启用" else self.get_text("disabled")
                self.user_tree.insert("", tk.END, values=(user.id, user.username, 
                                                        role_text, 
                                                        status_text, 
                                                        user.create_time))
            
            # 自动选择当前用户（非管理员）
            if not self.is_admin and self.user_list:
                self.selected_user = self.user_list[0]
                self.fill_form()
                # 高亮显示当前用户
                for item_id in self.user_tree.get_children():
                    values = self.user_tree.item(item_id, "values")
                    if str(values[0]) == str(self.current_user_id):
                        self.user_tree.selection_set(item_id)
                        break
        except Exception as e:
            # 清空列表并显示错误信息
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            messagebox.showerror(self.get_text("error"), f"{self.get_text('load_users_fail')}{str(e)}")
    
    def search_users(self):
        """
        搜索用户
        非管理员只能搜索自己
        """
        # 获取搜索条件
        username = self.search_username.get().strip()
        role = self.search_role.get().strip()
        
        # 加载所有用户（后端已实现权限控制）
        all_users = User.get_all(self.current_user)
        
        # 手动过滤
        filtered_users = []
        for user in all_users:
            match = True
            if username and username not in user.username:
                match = False
            if role and user.role != role:
                match = False
            if match:
                filtered_users.append(user)
        
        # 清空现有列表
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # 更新self.user_list为过滤后的列表
        self.user_list = filtered_users
        
        # 添加到列表控件
        for user in filtered_users:
            self.user_tree.insert("", tk.END, values=(user.id, user.username, 
                                                    user.role, 
                                                    user.status, 
                                                    user.create_time))
    
    def reset_search(self):
        """
        重置搜索条件
        """
        self.search_username.delete(0, tk.END)
        self.search_role.set("")
        self.load_user_list()
    
    def on_user_select(self, _event=None):
        """
        列表选择事件处理
        """
        selected_items = self.user_tree.selection()
        if selected_items:
            item_id = selected_items[0]
            values = self.user_tree.item(item_id, "values")
            user_id_str = values[0]
            
            # 转换user_id为整数类型，处理"加载中..."等特殊情况
            try:
                user_id = int(user_id_str)
            except ValueError:
                self.selected_user = None
                return
            
            # 查找对应的用户对象
            self.selected_user = next((u for u in self.user_list if u.id == user_id), None)
            if self.selected_user:
                self.fill_form()
                # 应用权限控制，特别是角色选择
                self.apply_permissions()
    
    def fill_form(self):
        """
        填充表单
        """
        if self.selected_user:
            # 用户名
            self.form_username.delete(0, tk.END)
            self.form_username.insert(0, self.selected_user.username)
            
            # 密码（不显示）
            self.form_password.delete(0, tk.END)
            
            # 角色 - 转换为当前语言
            role_text = self.get_text("admin") if self.selected_user.role == "管理员" else self.get_text("reader")
            self.form_role.set(role_text)
            
            # 状态 - 转换为当前语言
            status_text = self.get_text("enabled") if self.selected_user.status == "启用" else self.get_text("disabled")
            self.form_status.set(status_text)
    
    def clear_form(self):
        """
        清空表单
        """
        self.selected_user = None
        self.form_username.delete(0, tk.END)
        self.form_password.delete(0, tk.END)
        self.form_role.set("")
        self.form_status.set("")
    
    def add_user(self):
        """
        添加用户
        清空表单并设置为添加模式，提供视觉提示
        """
        self.clear_form()
        messagebox.showinfo(self.get_text("add_user"), self.get_text("please_fill_user_info"))

    def delete_user(self):
        """
        删除用户
        包含二次确认、防止删除最后一个管理员的保护机制和操作反馈
        只有管理员可以删除用户
        """
        # 权限检查：只有管理员可以删除用户
        if not self.is_admin:
            messagebox.showerror(self.get_text("error"), self.get_text("no_permission"))
            return
        
        # 首先检查Treeview的选择状态
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning(self.get_text("warning"), self.get_text("please_select_user"))
            return
        
        # 如果self.selected_user为空，尝试重新获取选中的用户
        if not self.selected_user:
            item_id = selected_items[0]
            values = self.user_tree.item(item_id, "values")
            user_id_str = values[0]
            
            try:
                user_id = int(user_id_str)
            except ValueError:
                messagebox.showwarning("警告", "请先选择要删除的用户")
                return
            
            self.selected_user = next((u for u in self.user_list if u.id == user_id), None)
            if not self.selected_user:
                messagebox.showwarning("警告", "请先选择要删除的用户")
                return
        
        # 防止删除最后一个管理员
        if self.selected_user.role == "管理员":
            # 统计管理员数量
            admin_count = 0
            for user in self.user_list:
                if user.role == "管理员":
                    admin_count += 1
            
            if admin_count <= 1:
                messagebox.showerror(self.get_text("error"), self.get_text("cannot_delete_last_admin"))
                return
        
        if messagebox.askyesno(self.get_text("system_confirm_delete"), self.get_text("confirm_delete_user").format(self.selected_user.username)):
            if self.selected_user.delete(self.current_user):
                messagebox.showinfo(self.get_text("success"), self.get_text("user_delete_success"))
                self.load_user_list()
                self.clear_form()
            else:
                messagebox.showerror(self.get_text("error"), self.get_text("user_delete_fail"))
    
    def save_user(self):
        """
        保存用户信息
        包含权限检查，防止越权操作
        """
        # 获取表单数据
        username = self.form_username.get().strip()
        password = self.form_password.get().strip()
        role = self.form_role.get().strip()
        status = self.form_status.get().strip()
        
        # 验证数据
        if not username:
            messagebox.showwarning(self.get_text("warning"), self.get_text("please_enter_username"))
            return
        
        if not role:
            messagebox.showwarning(self.get_text("warning"), self.get_text("please_select_role"))
            return
        
        if not status:
            messagebox.showwarning(self.get_text("warning"), self.get_text("please_select_status"))
            return
        
        # 保存用户信息
        if self.selected_user:
            # 更新现有用户
            # 权限检查：非管理员只能更新自己
            if not self.check_permission("edit", self.selected_user.id):
                messagebox.showerror(self.get_text("error"), self.get_text("no_permission"))
                return
            
            # 检查用户名是否已被其他用户使用
            existing_user = User.get_by_username(username)
            if existing_user and existing_user.id != self.selected_user.id:
                messagebox.showwarning(self.get_text("warning"), self.get_text("username_exists"))
                return
            
            self.selected_user.username = username
            if password:  # 只有当输入了密码时才更新
                self.selected_user.password = password
                
            # 转换状态为系统内部值
            self.selected_user.status = "启用" if status == self.get_text("enabled") else "禁用"
            
            # 非管理员不能修改自己的角色
            if self.is_admin:
                self.selected_user.role = "管理员" if role == self.get_text("admin") else "抄表员"
            
            if self.selected_user.save(self.current_user):
                messagebox.showinfo(self.get_text("success"), self.get_text("user_update_success"))
                self.load_user_list()
            else:
                messagebox.showerror(self.get_text("error"), self.get_text("user_update_fail"))
        else:
            # 添加新用户：只有管理员可以添加
            if not self.is_admin:
                messagebox.showerror(self.get_text("error"), self.get_text("no_permission"))
                return
                
            if not password:
                messagebox.showwarning(self.get_text("warning"), self.get_text("please_enter_password"))
                return
            
            # 检查用户名是否已存在
            existing_user = User.get_by_username(username)
            if existing_user:
                messagebox.showwarning(self.get_text("warning"), self.get_text("username_exists"))
                return
            
            # 转换角色和状态为系统内部值
            internal_role = "管理员" if role == self.get_text("admin") else "抄表员"
            internal_status = "启用" if status == self.get_text("enabled") else "禁用"
            
            user = User(
                username=username,
                password=password,
                role=internal_role,
                status=internal_status
            )
            
            if user.save(self.current_user):
                messagebox.showinfo(self.get_text("success"), self.get_text("user_add_success"))
                self.load_user_list()
                self.clear_form()
            else:
                messagebox.showerror(self.get_text("error"), self.get_text("user_add_fail"))