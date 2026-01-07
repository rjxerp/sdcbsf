#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统登录窗口
负责处理用户登录认证和相关操作
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import hashlib
import os

# 使用统一的路径处理模块
from utils.path_utils import add_project_root_to_path
add_project_root_to_path()

from models.user import User
from utils.settings_utils import SettingsUtils
from utils.language_utils import LanguageUtils

class LoginWindow:
    """
    登录窗口类
    实现用户登录认证功能
    """
    def __init__(self, parent=None):
        """
        初始化登录窗口
        :param parent: 父窗口
        """
        if parent:
            self.parent = parent
            self.login_window = tk.Toplevel(parent)
        else:
            self.parent = None
            self.login_window = tk.Tk()
        
        # 初始化语言和设置工具
        self.settings = SettingsUtils()
        self.language_utils = LanguageUtils()
        
        # 从配置文件获取语言设置
        saved_language = self.settings.get_setting('system', 'language', 'zh_CN')
        self.language_utils.set_language(saved_language)
        
        # 动态生成软件标题
        dynamic_title = self.get_dynamic_system_title()
        
        # 设置窗口标题，包含登录字样
        self.login_window.title(f"{dynamic_title} - {self.language_utils.get_text('login')}")
        self.login_window.geometry("400x300")
        self.login_window.resizable(False, False)
        
        # 设置窗口居中
        self.center_window()
        
        # 创建登录表单
        self.create_login_form()
        
        # 加载记住我信息
        self.load_remember_me()
        
        # 登录成功标志
        self.login_success = False
        self.logged_in_user = None
        
        # 启动事件循环
        if not parent:
            self.login_window.mainloop()
        else:
            # 如果有父窗口，等待登录窗口关闭
            parent.wait_window(self.login_window)
    
    def get_text(self, key):
        """
        获取当前语言的文本
        :param key: 文本键名
        :return: 对应语言的文本
        """
        return self.language_utils.get_text(key)
    
    def get_dynamic_system_title(self):
        """
        从软件信息数据源中动态获取字段值，生成软件标题
        :return: 动态生成的软件标题字符串
        """
        # 从配置文件中获取软件信息
        settings = SettingsUtils()
        
        # 动态获取三个字段的值
        software_brand = settings.get_setting('software', 'software_brand', self.get_text('window_title'))
        software_name = settings.get_setting('software', 'software_name', self.get_text('window_title'))
        software_version = settings.get_setting('software', 'software_version', '1.0.0')
        
        # 按照指定格式组合成软件标题
        return f"{software_brand} {software_name} v{software_version}"
    
    def center_window(self):
        """
        使窗口居中显示
        """
        # 获取屏幕尺寸
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        
        # 计算窗口位置
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        
        # 设置窗口位置
        self.login_window.geometry(f"400x300+{x}+{y}")
    
    def create_login_form(self):
        """
        创建登录表单
        """
        # 主框架
        main_frame = ttk.Frame(self.login_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题 - 使用动态生成的软件标题
        dynamic_title = self.get_dynamic_system_title()
        
        # 将标题拆分为系统名称和版本号两部分
        if " v" in dynamic_title:
            system_name, version = dynamic_title.split(" v", 1)
            version = "v" + version
        else:
            system_name = dynamic_title
            version = ""
        
        # 创建标题框架，用于水平排列系统名称和版本号
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=20)
        
        # 系统名称标签 - 使用系统默认字体，加粗样式
        system_name_label = ttk.Label(title_frame, text=system_name, font=('', 14, 'bold'))
        system_name_label.pack(side=tk.LEFT, anchor=tk.S)
        
        # 版本号标签 - 字体大小为标题的50%，使用系统默认字体，底部对齐
        if version:
            version_label = ttk.Label(title_frame, text=f" {version}", font=('', 8))
            version_label.pack(side=tk.LEFT, anchor=tk.S)
        
        # 用户名输入
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(username_frame, text=self.get_text('login_username'), width=8).pack(side=tk.LEFT, padx=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(username_frame, textvariable=self.username_var, width=25)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        # 密码输入
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(password_frame, text=self.get_text('login_password'), width=8).pack(side=tk.LEFT, padx=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*", width=25)
        self.password_entry.pack(side=tk.LEFT, padx=5)
        
        # 设置密码输入框自动获得焦点
        self.password_entry.focus_set()
        
        # 显示/隐藏密码按钮
        self.show_password = False
        self.toggle_password_btn = ttk.Button(password_frame, text="👁", width=2, command=self.toggle_password)
        self.toggle_password_btn.pack(side=tk.LEFT, padx=5)
        
        # 记住我选项
        remember_frame = ttk.Frame(main_frame)
        remember_frame.pack(fill=tk.X, pady=10, anchor=tk.W)
        
        self.remember_var = tk.BooleanVar()
        self.remember_check = ttk.Checkbutton(remember_frame, text=self.get_text('login_remember_me'), variable=self.remember_var)
        self.remember_check.pack(side=tk.LEFT, padx=5)
        
        # 忘记密码链接 - 向左移动，减小与"记住我"之间的间距
        self.forgot_password_label = ttk.Label(remember_frame, text=self.get_text('login_forgot_password'), foreground="blue", cursor="hand2")
        self.forgot_password_label.pack(side=tk.LEFT, padx=50, anchor=tk.W)
        self.forgot_password_label.bind("<Button-1>", self.forgot_password)
        
        # 按钮容器，用于放置登录和取消按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        # 登录按钮
        self.login_btn = ttk.Button(button_frame, text=self.get_text('login_login'), command=self.login, width=10)
        self.login_btn.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        self.cancel_btn = ttk.Button(button_frame, text=self.get_text('login_cancel'), command=self.cancel, width=10)
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # 错误信息标签
        self.error_label = ttk.Label(main_frame, text="", foreground="red")
        self.error_label.pack(pady=10)
        
        # 绑定回车键登录
        self.username_entry.bind("<Return>", self.login)
        self.password_entry.bind("<Return>", self.login)
    
    def toggle_password(self):
        """
        切换密码显示/隐藏状态
        """
        self.show_password = not self.show_password
        if self.show_password:
            self.password_entry.config(show="")
            self.toggle_password_btn.config(text="🙈")
        else:
            self.password_entry.config(show="*")
            self.toggle_password_btn.config(text="👁")
    
    def forgot_password(self, event=None):
        """
        忘记密码处理
        """
        messagebox.showinfo(self.get_text('login_forgot_password'), self.get_text('login_forgot_password_info'))
    
    def cancel(self):
        """
        取消登录，关闭窗口
        """
        self.login_success = False
        self.login_window.destroy()
    
    def login(self, event=None):
        """
        用户登录处理
        """
        # 获取用户名和密码
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        # 表单验证
        if not username:
            messagebox.showwarning(self.get_text('error'), self.get_text('login_warning_username'))
            self.username_entry.focus()
            return
        
        if not password:
            messagebox.showwarning(self.get_text('error'), self.get_text('login_warning_password'))
            self.password_entry.focus()
            return
        
        try:
            # 安全的密码验证方式：哈希值比对
            # 注意：当前User模型的authenticate方法直接比较密码明文，需要修改为哈希值比对
            # 这里先使用现有方法，后续可以优化
            user = User.authenticate(username, password)
            
            if user:
                # 登录成功
                self.login_success = True
                self.logged_in_user = user
                
                # 记住我功能
                if self.remember_var.get():
                    self.save_remember_me(username)
                else:
                    self.clear_remember_me()
                
                # 关闭登录窗口
                self.login_window.destroy()
            else:
                # 登录失败
                messagebox.showerror(self.get_text('error'), self.get_text('login_error_invalid'))
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
        except Exception as e:
            # 错误处理
            messagebox.showerror(self.get_text('error'), f"{self.get_text('login_error_exception')}{str(e)}")
    
    def save_remember_me(self, username):
        """
        保存记住我信息
        """
        # 这里可以使用配置文件或数据库来保存记住我信息
        # 简单实现，使用文本文件保存
        try:
            with open("remember_me.txt", "w") as f:
                f.write(username)
        except Exception as e:
            print(f"保存记住我信息失败: {str(e)}")
    
    def clear_remember_me(self):
        """
        清除记住我信息
        """
        try:
            if os.path.exists("remember_me.txt"):
                os.remove("remember_me.txt")
        except Exception as e:
            print(f"清除记住我信息失败: {str(e)}")
    
    def load_remember_me(self):
        """
        加载记住我信息
        """
        try:
            if os.path.exists("remember_me.txt"):
                with open("remember_me.txt", "r") as f:
                    username = f.read().strip()
                    self.username_var.set(username)
                    self.remember_var.set(True)
        except Exception as e:
            print(f"加载记住我信息失败: {str(e)}")

if __name__ == "__main__":
    login_window = LoginWindow()
    if login_window.login_success:
        print(f"登录成功，用户: {login_window.logged_in_user.username}")
        # 这里可以启动主应用
    else:
        print("登录失败")
