#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水电费抄收管理系统主程序入口
"""

import tkinter as tk

# 使用统一的路径处理模块
from utils.path_utils import add_project_root_to_path
add_project_root_to_path()

from database.init_db import init_database
from views.login_view import LoginWindow
from views.main_window import MainWindow
from license.license_manager import LicenseManager

def main():
    """
    主程序入口
    """
    print("程序启动")
    
    # 初始化注册管理器
    license_manager = LicenseManager()
    
    # 初始化数据库
    try:
        init_database()
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        return
    
    try:
        # 创建登录窗口（让LoginWindow管理自己的Tk实例）
        login_window = LoginWindow()
        print(f"登录窗口创建完成，登录状态: {login_window.login_success}")
        
        # 登录成功后才显示主窗口
        if login_window.login_success:
            # 创建Tkinter根窗口
            root = tk.Tk()
            
            # 实例化主窗口，传递LoginWindow的LanguageUtils实例和注册管理器
            app = MainWindow(root, login_window.logged_in_user, login_window.language_utils, license_manager)
            print("主窗口创建完成")
            
            # 启动事件循环
            root.mainloop()
        else:
            # 登录失败，退出程序
            print("登录失败，程序退出")
    except Exception as e:
        print(f"程序运行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
