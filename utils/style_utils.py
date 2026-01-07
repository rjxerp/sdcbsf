#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI样式工具模块
提供统一的样式定义和管理，确保界面风格一致性
"""

import tkinter as tk
from tkinter import ttk


class StyleUtils:
    """UI样式工具类"""
    
    def __init__(self):
        """初始化样式工具"""
        self.style = ttk.Style()
        self._init_colors()
        self._init_fonts()
        self._init_spacing()
        self._init_styles()
    
    def _init_colors(self):
        """
        初始化色彩系统
        定义主色、辅助色、功能色、中性色等
        """
        # 主色调
        self.PRIMARY_COLOR = "#2196F3"
        self.PRIMARY_LIGHT = "#64B5F6"
        self.PRIMARY_DARK = "#1976D2"
        
        # 辅助色
        self.SECONDARY_COLOR = "#607D8B"
        self.SECONDARY_LIGHT = "#90A4AE"
        self.SECONDARY_DARK = "#455A64"
        
        # 功能色
        self.SUCCESS_COLOR = "#4CAF50"
        self.SUCCESS_LIGHT = "#81C784"
        self.SUCCESS_DARK = "#388E3C"
        
        self.WARNING_COLOR = "#FF9800"
        self.WARNING_LIGHT = "#FFB74D"
        self.WARNING_DARK = "#F57C00"
        
        self.ERROR_COLOR = "#F44336"
        self.ERROR_LIGHT = "#E57373"
        self.ERROR_DARK = "#D32F2F"
        
        self.INFO_COLOR = "#00BCD4"
        self.INFO_LIGHT = "#4DD0E1"
        self.INFO_DARK = "#0097A7"
        
        # 中性色
        self.BG_PRIMARY = "#FFFFFF"
        self.BG_SECONDARY = "#F5F5F5"
        self.BG_TERTIARY = "#FAFAFA"
        self.BG_DARK = "#212121"
        
        self.TEXT_PRIMARY = "#212121"
        self.TEXT_SECONDARY = "#757575"
        self.TEXT_DISABLED = "#BDBDBD"
        self.TEXT_WHITE = "#FFFFFF"
        
        self.BORDER_LIGHT = "#E0E0E0"
        self.BORDER_NORMAL = "#BDBDBD"
        self.BORDER_DARK = "#9E9E9E"
        
        self.DIVIDER_LIGHT = "#F0F0F0"
        self.DIVIDER_NORMAL = "#E0E0E0"
    
    def _init_fonts(self):
        """
        初始化字体系统
        定义字体家族、字号、字重等
        """
        # 字体家族
        self.FONT_FAMILY = "Microsoft YaHei UI"
        self.FONT_FAMILY_EN = "Arial"
        self.FONT_FAMILY_MONO = "Consolas"
        self.FONT_FAMILY_FALLBACK = "Microsoft YaHei UI, Arial, sans-serif"
        
        # 字号
        self.FONT_SIZE_H1 = 24
        self.FONT_SIZE_H2 = 20
        self.FONT_SIZE_H3 = 18
        self.FONT_SIZE_H4 = 16
        self.FONT_SIZE_BODY_LARGE = 14
        self.FONT_SIZE_BODY_NORMAL = 12
        self.FONT_SIZE_BODY_SMALL = 10
        self.FONT_SIZE_CAPTION = 9
        
        # 字重
        self.FONT_WEIGHT_NORMAL = "normal"
        self.FONT_WEIGHT_BOLD = "bold"
        
        # 预定义字体
        self.TITLE_FONT = (self.FONT_FAMILY, self.FONT_SIZE_H1, self.FONT_WEIGHT_BOLD)
        self.SECTION_TITLE_FONT = (self.FONT_FAMILY, self.FONT_SIZE_H3, self.FONT_WEIGHT_BOLD)
        self.LABEL_FONT = (self.FONT_FAMILY, self.FONT_SIZE_BODY_NORMAL, self.FONT_WEIGHT_NORMAL)
        self.BUTTON_FONT = (self.FONT_FAMILY, self.FONT_SIZE_BODY_SMALL, self.FONT_WEIGHT_NORMAL)
        self.TABLE_FONT = (self.FONT_FAMILY, self.FONT_SIZE_BODY_SMALL, self.FONT_WEIGHT_NORMAL)
        self.STATUS_FONT = (self.FONT_FAMILY, self.FONT_SIZE_CAPTION, self.FONT_WEIGHT_NORMAL)
    
    def _init_spacing(self):
        """
        初始化间距系统
        定义基础间距单位和各级别间距
        """
        # 基础间距单位（8px网格系统）
        self.SPACING_BASE = 8
        
        # 间距级别
        self.SPACING_XS = 4
        self.SPACING_SM = 8
        self.SPACING_MD = 16
        self.SPACING_LG = 24
        self.SPACING_XL = 32
        self.SPACING_XXL = 48
        
        # 布局间距
        self.PAGE_MARGIN = 24
        self.SECTION_SPACING = 24
        self.FORM_FIELD_SPACING = 16
        self.BUTTON_GROUP_SPACING = 8
        self.CARD_SPACING = 16
        self.TAB_SPACING = 0
        
        # 组件间距
        self.BUTTON_PADDING = (8, 16)
        self.ENTRY_PADDING = (8, 12)
        self.FORM_GROUP_PADDING = 16
        self.CARD_PADDING = 16
        self.TABLE_CELL_PADDING = (8, 12)
        self.LIST_ITEM_PADDING = (12, 16)
        self.TOOLBAR_PADDING = (8, 16)
        self.STATUSBAR_PADDING = (6, 10)
    
    def _init_styles(self):
        """
        初始化所有样式
        为Tkinter组件定义统一的样式
        """
        self._init_button_styles()
        self._init_entry_styles()
        self._init_combobox_styles()
        self._init_checkbutton_styles()
        self._init_radiobutton_styles()
        self._init_treeview_styles()
        self._init_notebook_styles()
        self._init_progressbar_styles()
        self._init_scrollbar_styles()
        self._init_label_styles()
        self._init_frame_styles()
    
    def _init_button_styles(self):
        """
        初始化按钮样式
        包括主要按钮、次要按钮、危险按钮等
        """
        # 主要按钮
        self.style.configure(
            "Primary.TButton",
            background=self.PRIMARY_COLOR,
            foreground=self.TEXT_WHITE,
            borderwidth=0,
            focuscolor="none",
            padding=self.BUTTON_PADDING,
            font=self.BUTTON_FONT
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", self.PRIMARY_DARK), ("pressed", self.PRIMARY_DARK)]
        )
        
        # 次要按钮
        self.style.configure(
            "Secondary.TButton",
            background=self.BG_PRIMARY,
            foreground=self.PRIMARY_COLOR,
            borderwidth=1,
            relief="solid",
            focuscolor="none",
            padding=self.BUTTON_PADDING,
            font=self.BUTTON_FONT
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", self.BG_SECONDARY), ("pressed", self.BG_SECONDARY)]
        )
        
        # 危险按钮
        self.style.configure(
            "Danger.TButton",
            background=self.ERROR_COLOR,
            foreground=self.TEXT_WHITE,
            borderwidth=0,
            focuscolor="none",
            padding=self.BUTTON_PADDING,
            font=self.BUTTON_FONT
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", self.ERROR_DARK), ("pressed", self.ERROR_DARK)]
        )
        
        # 成功按钮
        self.style.configure(
            "Success.TButton",
            background=self.SUCCESS_COLOR,
            foreground=self.TEXT_WHITE,
            borderwidth=0,
            focuscolor="none",
            padding=self.BUTTON_PADDING,
            font=self.BUTTON_FONT
        )
        self.style.map(
            "Success.TButton",
            background=[("active", self.SUCCESS_DARK), ("pressed", self.SUCCESS_DARK)]
        )
        
        # 工具栏按钮
        self.style.configure(
            "Toolbar.TButton",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            borderwidth=0,
            focuscolor="none",
            padding=(6, 12),
            font=self.BUTTON_FONT
        )
        self.style.map(
            "Toolbar.TButton",
            background=[("active", self.BG_SECONDARY), ("pressed", self.BG_SECONDARY)]
        )
        
        # 禁用按钮样式
        self.style.configure(
            "TButton",
            background=self.BG_SECONDARY,
            foreground=self.TEXT_DISABLED,
            borderwidth=0,
            focuscolor="none",
            padding=self.BUTTON_PADDING,
            font=self.BUTTON_FONT
        )
    
    def _init_entry_styles(self):
        """
        初始化输入框样式
        包括默认、聚焦、错误、禁用等状态
        """
        # 默认输入框
        self.style.configure(
            "TEntry",
            fieldbackground=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            borderwidth=1,
            relief="solid",
            padding=self.ENTRY_PADDING,
            font=self.LABEL_FONT,
            insertcolor=self.PRIMARY_COLOR,
            selectbackground=self.PRIMARY_COLOR,
            selectforeground=self.TEXT_WHITE
        )
        
        # 聚焦输入框
        self.style.map(
            "TEntry",
            bordercolor=[("focus", self.PRIMARY_COLOR)]
        )
        
        # 错误输入框
        self.style.configure(
            "Error.TEntry",
            fieldbackground=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            borderwidth=2,
            relief="solid",
            padding=self.ENTRY_PADDING,
            font=self.LABEL_FONT,
            insertcolor=self.ERROR_COLOR,
            selectbackground=self.ERROR_COLOR,
            selectforeground=self.TEXT_WHITE
        )
        self.style.map(
            "Error.TEntry",
            bordercolor=[("focus", self.ERROR_COLOR)]
        )
    
    def _init_combobox_styles(self):
        """
        初始化下拉框样式
        """
        self.style.configure(
            "TCombobox",
            fieldbackground=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            borderwidth=1,
            relief="solid",
            padding=self.ENTRY_PADDING,
            font=self.LABEL_FONT,
            arrowcolor=self.TEXT_SECONDARY
        )
        self.style.map(
            "TCombobox",
            bordercolor=[("focus", self.PRIMARY_COLOR)]
        )
    
    def _init_checkbutton_styles(self):
        """
        初始化复选框样式
        """
        self.style.configure(
            "TCheckbutton",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            font=self.LABEL_FONT,
            focuscolor="none",
            padding=(8, 4)
        )
        self.style.map(
            "TCheckbutton",
            background=[("active", self.BG_PRIMARY)],
            foreground=[("active", self.PRIMARY_COLOR)]
        )
    
    def _init_radiobutton_styles(self):
        """
        初始化单选按钮样式
        """
        self.style.configure(
            "TRadiobutton",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            font=self.LABEL_FONT,
            focuscolor="none",
            padding=(8, 4)
        )
        self.style.map(
            "TRadiobutton",
            background=[("active", self.BG_PRIMARY)],
            foreground=[("active", self.PRIMARY_COLOR)]
        )
    
    def _init_treeview_styles(self):
        """
        初始化表格样式
        包括表头、行、选中状态等
        """
        # 表格整体样式
        self.style.configure(
            "Treeview",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            borderwidth=1,
            relief="solid",
            rowheight=32,
            font=self.TABLE_FONT,
            fieldbackground=self.BG_PRIMARY
        )
        
        # 表头样式
        self.style.configure(
            "Treeview.Heading",
            background=self.BG_SECONDARY,
            foreground=self.TEXT_PRIMARY,
            relief="flat",
            borderwidth=0,
            font=(self.FONT_FAMILY, self.FONT_SIZE_BODY_SMALL, self.FONT_WEIGHT_BOLD)
        )
        
        # 选中行样式
        self.style.map(
            "Treeview",
            background=[("selected", self.PRIMARY_LIGHT)],
            foreground=[("selected", self.PRIMARY_DARK)]
        )
        
        # 交替行样式
        self.style.configure(
            "Treeview.Alternate",
            background=self.BG_TERTIARY,
            foreground=self.TEXT_PRIMARY,
            rowheight=32,
            font=self.TABLE_FONT,
            fieldbackground=self.BG_TERTIARY
        )
    
    def _init_notebook_styles(self):
        """
        初始化标签页样式
        """
        # 标签页整体样式
        self.style.configure(
            "TNotebook",
            background=self.BG_SECONDARY,
            borderwidth=0,
            tabposition="n"
        )
        
        # 标签页标题样式
        self.style.configure(
            "TNotebook.Tab",
            background=self.BG_SECONDARY,
            foreground=self.TEXT_SECONDARY,
            padding=(16, 8),
            font=self.BUTTON_FONT,
            borderwidth=0
        )
        
        # 选中标签页样式
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.BG_PRIMARY)],
            foreground=[("selected", self.PRIMARY_COLOR)],
            expand=[("selected", [1, 1, 1, 0])]
        )
    
    def _init_progressbar_styles(self):
        """
        初始化进度条样式
        """
        self.style.configure(
            "TProgressbar",
            thickness=8,
            troughcolor=self.BORDER_LIGHT,
            background=self.PRIMARY_COLOR,
            borderwidth=0,
            relief="flat"
        )
    
    def _init_scrollbar_styles(self):
        """
        初始化滚动条样式
        """
        self.style.configure(
            "TScrollbar",
            background=self.BG_SECONDARY,
            troughcolor=self.BG_SECONDARY,
            borderwidth=0,
            relief="flat",
            arrowsize=12
        )
        self.style.map(
            "TScrollbar",
            background=[("active", self.BORDER_NORMAL)]
        )
    
    def _init_label_styles(self):
        """
        初始化标签样式
        """
        # 主要标签
        self.style.configure(
            "TLabel",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            font=self.LABEL_FONT
        )
        
        # 标题标签
        self.style.configure(
            "Title.TLabel",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            font=self.TITLE_FONT
        )
        
        # 区块标题标签
        self.style.configure(
            "Section.TLabel",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            font=self.SECTION_TITLE_FONT
        )
        
        # 次要标签
        self.style.configure(
            "Secondary.TLabel",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_SECONDARY,
            font=self.LABEL_FONT
        )
        
        # 成功标签
        self.style.configure(
            "Success.TLabel",
            background=self.BG_PRIMARY,
            foreground=self.SUCCESS_COLOR,
            font=self.LABEL_FONT
        )
        
        # 警告标签
        self.style.configure(
            "Warning.TLabel",
            background=self.BG_PRIMARY,
            foreground=self.WARNING_COLOR,
            font=self.LABEL_FONT
        )
        
        # 错误标签
        self.style.configure(
            "Error.TLabel",
            background=self.BG_PRIMARY,
            foreground=self.ERROR_COLOR,
            font=self.LABEL_FONT
        )
    
    def _init_frame_styles(self):
        """
        初始化框架样式
        """
        # 默认框架
        self.style.configure(
            "TFrame",
            background=self.BG_PRIMARY,
            relief="flat",
            borderwidth=0
        )
        
        # 卡片框架
        self.style.configure(
            "Card.TFrame",
            background=self.BG_PRIMARY,
            relief="flat",
            borderwidth=1
        )
        
        # 分组框架
        self.style.configure(
            "Group.TLabelframe",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            relief="raised",
            borderwidth=1,
            font=self.LABEL_FONT
        )
        self.style.configure(
            "Group.TLabelframe.Label",
            background=self.BG_PRIMARY,
            foreground=self.TEXT_PRIMARY,
            font=self.LABEL_FONT
        )
    
    def get_color(self, color_type):
        """
        获取指定类型的颜色
        :param color_type: 颜色类型，如 'primary', 'success', 'error' 等
        :return: 颜色值（十六进制字符串）
        """
        color_map = {
            'primary': self.PRIMARY_COLOR,
            'primary_light': self.PRIMARY_LIGHT,
            'primary_dark': self.PRIMARY_DARK,
            'secondary': self.SECONDARY_COLOR,
            'success': self.SUCCESS_COLOR,
            'warning': self.WARNING_COLOR,
            'error': self.ERROR_COLOR,
            'info': self.INFO_COLOR,
            'bg_primary': self.BG_PRIMARY,
            'bg_secondary': self.BG_SECONDARY,
            'text_primary': self.TEXT_PRIMARY,
            'text_secondary': self.TEXT_SECONDARY,
            'border': self.BORDER_NORMAL,
        }
        return color_map.get(color_type, self.PRIMARY_COLOR)
    
    def get_font(self, font_type):
        """
        获取指定类型的字体
        :param font_type: 字体类型，如 'title', 'label', 'button' 等
        :return: 字体元组
        """
        font_map = {
            'title': self.TITLE_FONT,
            'section_title': self.SECTION_TITLE_FONT,
            'label': self.LABEL_FONT,
            'button': self.BUTTON_FONT,
            'table': self.TABLE_FONT,
            'status': self.STATUS_FONT,
        }
        return font_map.get(font_type, self.LABEL_FONT)
    
    def get_spacing(self, spacing_type):
        """
        获取指定类型的间距
        :param spacing_type: 间距类型，如 'xs', 'sm', 'md', 'lg', 'xl' 等
        :return: 间距值（整数）
        """
        spacing_map = {
            'xs': self.SPACING_XS,
            'sm': self.SPACING_SM,
            'md': self.SPACING_MD,
            'lg': self.SPACING_LG,
            'xl': self.SPACING_XL,
            'xxl': self.SPACING_XXL,
        }
        return spacing_map.get(spacing_type, self.SPACING_MD)
    
    def apply_button_style(self, button, style_type="primary"):
        """
        为按钮应用指定样式
        :param button: 按钮组件
        :param style_type: 样式类型，如 'primary', 'secondary', 'danger', 'success' 等
        """
        style_map = {
            'primary': 'Primary.TButton',
            'secondary': 'Secondary.TButton',
            'danger': 'Danger.TButton',
            'success': 'Success.TButton',
            'toolbar': 'Toolbar.TButton',
        }
        style_name = style_map.get(style_type, 'Primary.TButton')
        button.configure(style=style_name)
    
    def apply_entry_style(self, entry, style_type="default"):
        """
        为输入框应用指定样式
        :param entry: 输入框组件
        :param style_type: 样式类型，如 'default', 'error' 等
        """
        if style_type == "error":
            entry.configure(style="Error.TEntry")
        else:
            entry.configure(style="TEntry")
    
    def apply_label_style(self, label, style_type="default"):
        """
        为标签应用指定样式
        :param label: 标签组件
        :param style_type: 样式类型，如 'default', 'title', 'secondary', 'success', 'warning', 'error' 等
        """
        style_map = {
            'default': 'TLabel',
            'title': 'Title.TLabel',
            'section': 'Section.TLabel',
            'secondary': 'Secondary.TLabel',
            'success': 'Success.TLabel',
            'warning': 'Warning.TLabel',
            'error': 'Error.TLabel',
        }
        style_name = style_map.get(style_type, 'TLabel')
        label.configure(style=style_name)
    
    def apply_frame_style(self, frame, style_type="default"):
        """
        为框架应用指定样式
        :param frame: 框架组件
        :param style_type: 样式类型，如 'default', 'card', 'group' 等
        """
        style_map = {
            'default': 'TFrame',
            'card': 'Card.TFrame',
            'group': 'Group.TLabelframe',
        }
        style_name = style_map.get(style_type, 'TFrame')
        frame.configure(style=style_name)
    
    def create_card(self, parent, title=None, padding=None):
        """
        创建卡片组件
        :param parent: 父容器
        :param title: 卡片标题（可选）
        :param padding: 内边距（可选）
        :return: 卡片框架
        """
        if padding is None:
            padding = self.CARD_PADDING
        
        if title:
            card = ttk.LabelFrame(parent, text=title, padding=padding, style="Group.TLabelframe")
        else:
            card = ttk.Frame(parent, padding=padding, style="Card.TFrame")
        
        return card
    
    def create_button(self, parent, text, command=None, style_type="primary", width=None):
        """
        创建按钮组件
        :param parent: 父容器
        :param text: 按钮文本
        :param command: 点击事件处理函数
        :param style_type: 样式类型
        :param width: 按钮宽度
        :return: 按钮组件
        """
        style_map = {
            'primary': 'Primary.TButton',
            'secondary': 'Secondary.TButton',
            'danger': 'Danger.TButton',
            'success': 'Success.TButton',
            'toolbar': 'Toolbar.TButton',
        }
        style_name = style_map.get(style_type, 'Primary.TButton')
        
        button = ttk.Button(parent, text=text, command=command, style=style_name)
        if width:
            button.configure(width=width)
        
        return button
    
    def create_entry(self, parent, textvariable=None, style_type="default", width=None):
        """
        创建输入框组件
        :param parent: 父容器
        :param textvariable: 文本变量
        :param style_type: 样式类型
        :param width: 输入框宽度
        :return: 输入框组件
        """
        if style_type == "error":
            style_name = "Error.TEntry"
        else:
            style_name = "TEntry"
        
        entry = ttk.Entry(parent, textvariable=textvariable, style=style_name)
        if width:
            entry.configure(width=width)
        
        return entry
    
    def create_label(self, parent, text, style_type="default", font=None):
        """
        创建标签组件
        :param parent: 父容器
        :param text: 标签文本
        :param style_type: 样式类型
        :param font: 自定义字体（可选）
        :return: 标签组件
        """
        style_map = {
            'default': 'TLabel',
            'title': 'Title.TLabel',
            'section': 'Section.TLabel',
            'secondary': 'Secondary.TLabel',
            'success': 'Success.TLabel',
            'warning': 'Warning.TLabel',
            'error': 'Error.TLabel',
        }
        style_name = style_map.get(style_type, 'TLabel')
        
        label = ttk.Label(parent, text=text, style=style_name)
        if font:
            label.configure(font=font)
        
        return label


# 创建全局样式工具实例
style_utils = StyleUtils()
