#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册界面模块
用于用户输入注册码进行注册
"""

import tkinter as tk
from tkinter import ttk, messagebox
from license.license_manager import LicenseManager

class RegisterView:
    """注册界面类"""
    
    def __init__(self, parent=None, license_manager=None):
        """
        初始化注册界面
        :param parent: 父窗口
        :param license_manager: 注册管理器实例
        """
        self.parent = parent
        self.license_manager = license_manager or LicenseManager()
        
        # 创建注册窗口
        if parent:
            self.window = tk.Toplevel(parent)
            self.window.transient(parent)  # 设置为父窗口的子窗口
        else:
            self.window = tk.Tk()
        
        self.window.title("软件注册")
        self.window.geometry("450x350")
        self.window.resizable(False, False)
        
        # 设置窗口样式
        self._setup_style()
        
        # 创建界面组件
        self._create_widgets()
        
        # 设置焦点
        self.license_entry.focus_set()
        
        # 注册快捷键
        self._setup_shortcuts()
    
    def _setup_style(self):
        """
        设置界面样式
        """
        style = ttk.Style()
        style.configure("Register.TLabel", font=(".AppleSystemUIFont", 12))
        style.configure("Title.TLabel", font=(".AppleSystemUIFont", 16, "bold"))
        style.configure("Status.TLabel", font=(".AppleSystemUIFont", 10))
        style.configure("Register.TButton", font=(".AppleSystemUIFont", 11))
    
    def _create_widgets(self):
        """
        创建界面组件
        """
        # 主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="软件注册", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # 说明文本
        info_label = ttk.Label(
            main_frame, 
            text="请输入您的注册码以激活软件。注册码区分大小写。",
            style="Register.TLabel",
            wraplength=400,
            justify=tk.CENTER
        )
        info_label.pack(pady=(0, 20))
        
        # 注册码输入框
        license_frame = ttk.Frame(main_frame)
        license_frame.pack(fill=tk.X, pady=(0, 15))
        
        license_label = ttk.Label(license_frame, text="注册码:", style="Register.TLabel")
        license_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.license_entry = ttk.Entry(
            license_frame, 
            font=(".AppleSystemUIFont", 12),
            show="*",
            width=40
        )
        self.license_entry.pack(fill=tk.X)
        
        # 显示/隐藏密码按钮
        self.show_license_var = tk.BooleanVar(value=False)
        show_license_btn = ttk.Checkbutton(
            license_frame, 
            text="显示注册码",
            variable=self.show_license_var,
            command=self._toggle_license_visibility
        )
        show_license_btn.pack(anchor=tk.W, pady=(5, 0))
        
        # 状态标签
        self.status_var = tk.StringVar(value="")
        status_label = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            style="Status.TLabel",
            foreground="#666666"
        )
        status_label.pack(pady=(0, 20))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame, 
            text="取消",
            command=self._on_cancel,
            style="Register.TButton"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 注册按钮
        self.register_btn = ttk.Button(
            button_frame, 
            text="注册",
            command=self._on_register,
            style="Register.TButton"
        )
        self.register_btn.pack(side=tk.RIGHT)
        
        # 试用按钮
        trial_btn = ttk.Button(
            button_frame, 
            text="试用",
            command=self._on_trial,
            style="Register.TButton"
        )
        trial_btn.pack(side=tk.LEFT)
    
    def _setup_shortcuts(self):
        """
        设置快捷键
        """
        # Enter键触发注册
        self.window.bind('<Return>', lambda e: self._on_register())
        # Escape键触发取消
        self.window.bind('<Escape>', lambda e: self._on_cancel())
    
    def _toggle_license_visibility(self):
        """
        切换注册码显示/隐藏状态
        """
        if self.show_license_var.get():
            self.license_entry.config(show="")
        else:
            self.license_entry.config(show="*")
    
    def _on_register(self):
        """
        注册按钮点击事件
        """
        license_key = self.license_entry.get().strip()
        
        if not license_key:
            messagebox.showerror("错误", "请输入注册码")
            return
        
        # 禁用注册按钮，防止重复点击
        self.register_btn.config(state=tk.DISABLED)
        self.status_var.set("正在验证注册码...")
        self.window.update()  # 刷新界面
        
        try:
            # 调用注册管理器进行注册
            result, msg, info = self.license_manager.register_license(license_key)
            
            if result:
                # 注册成功
                messagebox.showinfo("成功", f"注册成功！\n{msg}")
                # 在销毁窗口前恢复按钮状态
                self.register_btn.config(state=tk.NORMAL)
                self.status_var.set("")
                self.window.destroy()
            else:
                # 注册失败
                messagebox.showerror("注册失败", msg)
        except Exception as e:
            messagebox.showerror("错误", f"注册过程中发生错误: {str(e)}")
        finally:
            # 只有当窗口未被销毁时才恢复按钮状态
            try:
                # 检查窗口是否仍然存在
                if self.window.winfo_exists():
                    self.register_btn.config(state=tk.NORMAL)
                    self.status_var.set("")
            except Exception:
                # 窗口已被销毁，忽略异常
                pass
    
    def _on_cancel(self):
        """
        取消按钮点击事件
        """
        self.window.destroy()
    
    def _on_trial(self):
        """
        试用按钮点击事件
        """
        try:
            # 生成试用注册码
            trial_license = self.license_manager.generate_trial_license()
            # 自动填充到输入框
            self.license_entry.delete(0, tk.END)
            self.license_entry.insert(0, trial_license)
            # 显示注册码
            self.show_license_var.set(True)
            self._toggle_license_visibility()
            # 显示提示信息
            messagebox.showinfo("试用版", f"已生成30天试用注册码。\n请点击'注册'按钮激活试用版。")
        except Exception as e:
            messagebox.showerror("错误", f"生成试用注册码失败: {str(e)}")
    
    def show(self):
        """
        显示注册窗口
        """
        if self.parent:
            self.window.grab_set()  # 模态窗口
            self.parent.wait_window(self.window)
        else:
            self.window.mainloop()

if __name__ == "__main__":
    # 测试注册界面
    register_view = RegisterView()
    register_view.show()