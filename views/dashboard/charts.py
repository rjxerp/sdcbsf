#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化图表组件
实现至少3个独立图表模块：
- 折线图：展示关键指标的时间序列变化趋势，支持多维度对比
- 柱状图：实现分类数据的横向/纵向对比分析
- 饼图/环形图：展示数据构成比例与占比关系
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db_manager import get_db
from models.tenant import Tenant
from models.charge import Charge


class Charts:
    """数据可视化图表组件类"""
    
    def __init__(self, parent):
        """
        初始化数据可视化图表组件
        :param parent: 父容器
        """
        self.parent = parent
        self.dashboard_view = None  # 用于获取语言工具
        
        # 数据缓存机制，避免频繁查询数据库
        self.data_cache = {
            'tenant_pie_data': None,
            'revenue_pie_data': {},  # 按月份缓存
            'line_chart_data': None,
            'cache_time': 0
        }
        self.CACHE_DURATION = 300  # 缓存过期时间（秒）
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.parent, style="Charts.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置主框架的网格布局
        # 第0行：图表1（折线图）- 占据2列
        # 第1行：图表2（租户类型分布饼图）和图表3（收入来源构成饼图）- 水平排列
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # 初始化样式
        self._init_style()
        
        # 创建图表容器
        self.create_chart_containers()
        
        # 创建图表
        self.create_line_chart()
        self.create_tenant_pie_chart()
        self.create_pie_chart()
        
        # 绑定窗口大小变化事件，实现响应式布局
        # 使用idle_add延迟执行resize事件，避免频繁触发
        self.resize_after_id = None
        self.parent.bind('<Configure>', lambda event: self.on_resize_debounced(event))
        self.main_frame.bind('<Configure>', lambda event: self.on_resize_debounced(event))
    
    def set_dashboard_view(self, dashboard_view):
        """
        设置仪表盘视图引用，用于获取语言工具
        :param dashboard_view: 仪表盘视图实例
        """
        self.dashboard_view = dashboard_view
    
    def get_text(self, key):
        """
        获取当前语言的文本
        :param key: 文本键名
        :return: 对应语言的文本
        """
        if self.dashboard_view and hasattr(self.dashboard_view, 'main_window'):
            return self.dashboard_view.main_window.get_text(key)
        # 默认返回键名
        return key
    
    def update_language(self):
        """
        更新图表的语言
        重新创建整个图表以确保所有文本都使用新的语言
        """
        # 清除数据缓存，确保获取最新的翻译数据
        self.data_cache = {
            'tenant_pie_data': None,
            'revenue_pie_data': {},  # 按月份缓存
            'line_chart_data': None,
            'cache_time': 0
        }
        # 重新创建图表以更新所有文本
        self.recreate_charts(getattr(self, 'selected_month', None))
    
    def _is_cache_valid(self):
        """
        检查缓存是否有效
        :return: 缓存是否有效的布尔值
        """
        from time import time
        return (time() - self.data_cache['cache_time']) < self.CACHE_DURATION
    
    def _update_cache_time(self):
        """
        更新缓存时间
        """
        from time import time
        self.data_cache['cache_time'] = time()
    
    def on_resize_debounced(self, event):
        """
        防抖处理窗口大小变化事件，避免频繁触发图表重建
        :param event: 事件对象
        """
        # 取消之前的延迟执行
        if self.resize_after_id:
            self.parent.after_cancel(self.resize_after_id)
        
        # 延迟100毫秒执行resize操作
        self.resize_after_id = self.parent.after(100, lambda: self.on_resize(event))
    
    def recreate_charts(self, selected_month=None):
        """
        重新创建所有图表
        用于响应窗口大小变化或语言切换，确保图表能够根据新的容器大小或语言调整
        :param selected_month: 选中的月份，格式为YYYY-MM，None表示全部月份
        """
        # 清除图表容器中的所有控件
        self._clear_chart_containers()
        
        # 存储当前选中的月份
        self.selected_month = selected_month
        
        # 重新创建图表
        self.create_line_chart()
        self.create_tenant_pie_chart()
        self.create_pie_chart()
    
    def _init_style(self):
        """
        初始化样式
        """
        style = ttk.Style()
        style.configure("Charts.TFrame", background="white")
        style.configure("ChartContainer.TFrame", background="white", relief="solid", borderwidth=1, bordercolor="#e0e0e0")
        style.configure("ChartTitle.TLabel", font=('Arial', 10, 'bold'))
        
    def get_tenant_type_data(self):
        """
        获取租户类型分布数据
        :return: 租户类型列表和对应的数量列表
        """
        # 检查缓存是否有效
        if self._is_cache_valid() and self.data_cache['tenant_pie_data']:
            return self.data_cache['tenant_pie_data']
        
        # 从数据库获取所有租户
        tenants = Tenant.get_all()
        
        # 统计不同类型租户的数量
        type_counts = {}
        for tenant in tenants:
            if tenant.type in type_counts:
                type_counts[tenant.type] += 1
            else:
                type_counts[tenant.type] = 1
        
        # 转换为列表格式并翻译租户类型
        tenant_types = []
        tenant_counts = []
        for tenant_type, count in type_counts.items():
            # 处理数据库中存储的英文租户类型键
            translated_type = self.get_text(tenant_type)
            tenant_types.append(translated_type)
            tenant_counts.append(count)
        
        result = (tenant_types, tenant_counts)
        
        # 更新缓存
        self.data_cache['tenant_pie_data'] = result
        return result
        
    def get_revenue_source_data(self):
        """
        获取收入来源构成数据
        按租户类型对费用记录进行汇总统计
        :return: 租户类型列表和对应的收入金额列表
        """
        # 使用None作为默认月份的键
        cache_key = getattr(self, 'selected_month', None) or 'all'
        
        # 检查缓存是否有效
        if self._is_cache_valid() and cache_key in self.data_cache['revenue_pie_data']:
            return self.data_cache['revenue_pie_data'][cache_key]
        
        # 从数据库获取所有已缴费用记录
        charges = Charge.get_all()
        paid_charges = [charge for charge in charges if charge.status == '已缴']
        
        # 如果有选中的月份，只保留该月份的数据
        if cache_key != 'all':
            paid_charges = [charge for charge in paid_charges if charge.month == cache_key]
        
        # 按租户类型汇总收入
        revenue_by_type = {}
        
        for charge in paid_charges:
            # 加载租户信息
            if not charge.tenant:
                charge.load_tenant_info()
            
            # 获取租户类型，默认为"unknown_type"
            tenant_type_key = charge.tenant.type if (charge.tenant and charge.tenant.type) else "unknown_type"
            
            if tenant_type_key in revenue_by_type:
                revenue_by_type[tenant_type_key] += charge.total_charge
            else:
                revenue_by_type[tenant_type_key] = charge.total_charge
        
        # 转换为列表格式并翻译租户类型
        tenant_types = []
        revenue_values = []
        for tenant_type_key, value in revenue_by_type.items():
            # 翻译租户类型
            translated_type = self.get_text(tenant_type_key)
            tenant_types.append(translated_type)
            revenue_values.append(value)
        
        result = (tenant_types, revenue_values)
        
        # 更新缓存
        self.data_cache['revenue_pie_data'][cache_key] = result
        return result
        
    def create_chart_containers(self):
        """
        创建图表容器
        """
        # 图表1容器（折线图）- 占据2列
        self.chart1_frame = ttk.Frame(self.main_frame, style="ChartContainer.TFrame")
        self.chart1_frame.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)
        
        # 图表2容器（租户类型分布饼图）- 左侧
        self.chart2_frame = ttk.Frame(self.main_frame, style="ChartContainer.TFrame")
        self.chart2_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)
        
        # 图表3容器（收入来源构成饼图）- 右侧
        self.chart3_frame = ttk.Frame(self.main_frame, style="ChartContainer.TFrame")
        self.chart3_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=10, pady=10)
    
    def _get_monthly_revenue_data(self):
        """
        获取月度收入数据
        :return: 月份列表和对应的收入金额列表
        """
        # 检查缓存是否有效
        if self._is_cache_valid() and self.data_cache['line_chart_data']:
            return self.data_cache['line_chart_data']
        
        from models.charge import Charge
        from datetime import datetime
        import collections
        
        # 直接从数据库获取已缴费用记录，避免加载所有记录后再筛选
        db = get_db()
        # 使用SQL查询直接按月份统计已缴费用的总金额，提高性能和准确性
        sql = """
        SELECT month, SUM(total_charge) as total_revenue 
        FROM charges 
        WHERE status = '已缴' 
        GROUP BY month 
        ORDER BY month
        """
        results = db.fetch_all(sql)
        
        # 处理查询结果
        sorted_months = []
        revenue_values = []
        for result in results:
            month = result[0]  # 格式：YYYY-MM
            total_revenue = result[1]  # 总金额，已精确计算
            sorted_months.append(month)
            revenue_values.append(total_revenue)
        
        # 确保数值精确，避免浮点数精度问题
        revenue_values = [round(value, 2) for value in revenue_values]
        
        # 格式化月份显示（显示完整的YYYY-MM格式，提高可读性）
        # 对于较长的月份列表，显示为MM月，否则显示完整年份
        if len(sorted_months) <= 12:
            # 少于等于12个月，显示完整的YYYY-MM格式
            formatted_months = [month for month in sorted_months]
        else:
            # 超过12个月，只显示MM月，节省空间
            formatted_months = [f'{month.split("-")[1]}月' for month in sorted_months]
        
        result = (formatted_months, revenue_values)
        
        # 更新缓存
        self.data_cache['line_chart_data'] = result
        return result
    
    def create_line_chart(self):
        """
        创建折线图：展示关键指标的时间序列变化趋势
        """
        # 图表标题
        chart_title = ttk.Label(self.chart1_frame, text=self.get_text('monthly_income_trend'), style="ChartTitle.TLabel")
        chart_title.pack(side=tk.TOP, anchor=tk.W, padx=15, pady=8)
        
        # 创建matplotlib图表 - 使用自适应尺寸，确保所有元素都能显示
        fig = Figure(dpi=100)
        ax = fig.add_subplot(111)
        
        # 获取真实数据
        months, revenue_values = self._get_monthly_revenue_data()
        
        # 如果没有数据，使用默认数据
        if not months:
            months = ['1月', '2月', '3月', '4月', '5月', '6月']
            revenue_values = [0 for _ in months]
        
        # 使用数值索引绘制折线图，避免将字符串解析为日期，消除警告
        x_values = range(len(months))
        ax.plot(x_values, revenue_values, label=self.get_text('total_income'), marker='o', linewidth=1.5, color='#3498db',
                linestyle='-')
        
        # 设置x轴标签，使用自定义的月份字符串
        ax.set_xticks(x_values)
        ax.set_xticklabels(months)
        
        # 设置图表属性 - 移除内部重复标题
        ax.set_title('')
        ax.set_xlabel(self.get_text('month'), fontsize=8, labelpad=12, fontweight='bold')
        ax.set_ylabel(self.get_text('revenue_amount'), fontsize=8, labelpad=12, fontweight='bold')
        
        # 调整图例，将其放置在图表内部的左下角，确保不遮挡图表数据
        ax.legend(loc='lower left', fontsize=8, frameon=True, framealpha=0.9, borderpad=1.2)
        
        # 添加网格线，提高可读性
        ax.grid(True, linestyle='--', alpha=0.7, color='#e0e0e0')
        
        # 调整坐标轴刻度和标签
        ax.tick_params(axis='x', rotation=45, labelsize=8, pad=6)
        ax.tick_params(axis='y', labelsize=8, pad=6)
        
        # 确保y轴从0开始，提供完整的视觉对比
        max_revenue = max(revenue_values) if revenue_values else 100000
        ax.set_ylim(0, max_revenue * 1.2)  # 增加顶部空间，确保所有标签都能显示
        
        # 根据屏幕尺寸调整标签显示策略
        width = self.parent.winfo_width()
        font_size = 7
        rotation = 45
        
        if width < 768:  # 移动端
            font_size = 6
            rotation = 90  # 垂直旋转标签，节省水平空间
        elif width < 1200:  # 平板端
            font_size = 7
            rotation = 60
        
        # 添加数值标签到所有数据点
        for i, (x, y) in enumerate(zip(x_values, revenue_values)):
            # 调整标签位置，确保在不同屏幕尺寸下都能正确显示
            ax.text(x, y + max_revenue * 0.02, f'{y:,.0f}', ha='center', va='bottom', 
                    fontsize=font_size, color='#3498db', rotation=rotation)
        
        # 根据屏幕尺寸调整图表布局，减小边距，让图表内容完全占据可用空间
        if width < 768:  # 移动端
            fig.subplots_adjust(left=0.12, right=0.98, top=0.80, bottom=0.30)  # 减小左右边距，让图表内容完全占据宽度
        elif width < 1200:  # 平板端
            fig.subplots_adjust(left=0.08, right=0.98, top=0.85, bottom=0.25)  # 减小左右边距，让图表内容完全占据宽度
        else:  # 桌面端
            fig.subplots_adjust(left=0.06, right=0.98, top=0.85, bottom=0.20)  # 减小左右边距，让图表内容完全占据宽度
        
        # 嵌入到Tkinter窗口
        canvas = FigureCanvasTkAgg(fig, master=self.chart1_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
    
    def create_tenant_pie_chart(self):
        """
        创建饼图：展示租户类型分布
        """
        # 图表标题
        chart_title = ttk.Label(self.chart2_frame, text=self.get_text('tenant_type_distribution'), style="ChartTitle.TLabel")
        chart_title.pack(side=tk.TOP, anchor=tk.W, padx=15, pady=8)
        
        # 创建matplotlib图表 - 使用自适应尺寸，确保所有元素都能显示
        fig = Figure(dpi=100)
        ax = fig.add_subplot(111)
        
        # 获取真实数据
        tenant_types, tenant_counts = self.get_tenant_type_data()
        
        # 检查数据是否为空，如果为空则使用默认值
        if not tenant_types:
            tenant_types = ['暂无数据']
            tenant_counts = [1]
        
        # 颜色列表，确保有足够的颜色用于不同类型的租户
        colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#34495e', '#f1c40f', '#e67e22', '#e91e63']
        # 根据数据长度调整颜色列表
        colors = colors[:len(tenant_types)]
        
        # 只突出显示数量最多的租户类型
        explode = tuple(0.05 if i == tenant_counts.index(max(tenant_counts)) else 0 for i in range(len(tenant_types)))
        
        # 计算百分比并准备包含具体数值的标签
        total = sum(tenant_counts)
        legend_labels = []
        for tenant_type, count in zip(tenant_types, tenant_counts):
            percentage = count / total * 100
            legend_labels.append(f'{tenant_type} - {count}{self.get_text("households")} ({percentage:.1f}%)')
        
        # 绘制饼图
        wedges, texts, autotexts = ax.pie(
            tenant_counts, 
            explode=explode, 
            labels=tenant_types, 
            colors=colors, 
            autopct='%1.1f%%', 
            shadow=True, 
            startangle=90,
            pctdistance=0.75,  # 调整百分比标签的位置
            labeldistance=1.2,  # 调整图例标签的位置
            wedgeprops={
                'edgecolor': 'white',  # 添加饼图扇区边框
                'linewidth': 1.5,
                'antialiased': True
            }
        )
        
        # 设置图表属性 - 移除重复标题，避免显示问题
        ax.set_title('')
        ax.axis('equal')  # 确保饼图是圆形
        
        # 设置图例样式，调整到图表右侧
        ax.legend(
            wedges, 
            legend_labels, 
            title=self.get_text('tenant_type'), 
            loc='center right', 
            bbox_to_anchor=(1.3, 0.5),  # 将图例定位到图表右侧
            fontsize=8,  # 图例名称字体大小，确保清晰易读
            title_fontsize=8,  # 图例标题字体大小精确调整为8号
            frameon=True,
            framealpha=0.9,
            facecolor='#f8f9fa',
            edgecolor='#e0e0e0',
            ncol=1,  # 改为单列显示
            mode='expand',  # 图例在垂直方向上均匀分布
            borderaxespad=0.5,  # 边框与坐标轴的间距
            columnspacing=1.0,  # 列之间的间距
            handletextpad=0.5  # 图例标记与文本的间距
        )
        
        # 设置文本样式 - 扇区标签
        for text in texts:
            text.set_fontsize(8)
            text.set_color('#333333')
            text.set_fontweight('bold')
        
        # 设置文本样式 - 百分比标签
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
            autotext.set_fontweight('bold')
            autotext.set_bbox(dict(boxstyle='round,pad=0.3', fc=(0, 0, 0, 0.3), ec='none'))
        
        # 调整饼图大小，确保完整显示
        ax.set_aspect('equal')
        
        # 优化布局，为右侧图例和标题留出足够空间
        fig.subplots_adjust(left=0.05, right=0.75, top=0.85, bottom=0.05)
        
        # 嵌入到Tkinter窗口
        canvas = FigureCanvasTkAgg(fig, master=self.chart2_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
    
    def create_pie_chart(self):
        """
        创建饼图：展示数据构成比例与占比关系
        """
        # 图表标题
        chart_title = ttk.Label(self.chart3_frame, text=self.get_text('revenue_composition'), style="ChartTitle.TLabel")
        chart_title.pack(side=tk.TOP, anchor=tk.W, padx=15, pady=8)
        
        # 创建matplotlib图表 - 使用自适应尺寸，确保所有元素都能显示
        fig = Figure(dpi=100)
        ax = fig.add_subplot(111)
        
        # 获取真实数据
        revenue_sources, revenue_values = self.get_revenue_source_data()
        
        # 检查数据是否为空，如果为空则使用默认值
        if not revenue_sources:
            revenue_sources = ['暂无数据']
            revenue_values = [1]
        
        # 颜色列表，确保有足够的颜色用于不同类型的租户
        colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#34495e', '#f1c40f', '#e67e22', '#e91e63']
        # 根据数据长度调整颜色列表
        colors = colors[:len(revenue_sources)]
        
        # 只突出显示收入最高的租户类型
        explode = tuple(0.05 if i == revenue_values.index(max(revenue_values)) else 0 for i in range(len(revenue_sources)))
        
        # 计算百分比并准备包含具体数值的标签
        total = sum(revenue_values)
        legend_labels = []
        for source, value in zip(revenue_sources, revenue_values):
            percentage = value / total * 100
            legend_labels.append(f'{source} - {value:,.2f}元 ({percentage:.1f}%)')
        
        # 绘制饼图，优化布局和样式
        wedges, texts, autotexts = ax.pie(
            revenue_values, 
            explode=explode, 
            labels=revenue_sources, 
            colors=colors, 
            autopct='%1.1f%%', 
            shadow=True, 
            startangle=90,
            pctdistance=0.75,  # 调整百分比标签的位置
            labeldistance=1.2,  # 调整图例标签的位置
            wedgeprops={
                'edgecolor': 'white',  # 添加饼图扇区边框
                'linewidth': 1.5,
                'antialiased': True
            }
        )
        
        # 设置图表属性 - 移除重复标题，避免显示问题
        ax.set_title('')
        ax.axis('equal')  # 确保饼图是圆形
        
        # 设置图例样式，调整到图表右侧
        ax.legend(
            wedges, 
            legend_labels, 
            title=self.get_text('tenant_type'), 
            loc='center right', 
            bbox_to_anchor=(1.3, 0.5),  # 将图例定位到图表右侧
            fontsize=8,  # 图例名称字体大小，确保清晰易读
            title_fontsize=8,  # 图例标题字体大小精确调整为8号
            frameon=True,
            framealpha=0.9,
            facecolor='#f8f9fa',
            edgecolor='#e0e0e0',
            ncol=1,  # 改为单列显示
            mode='expand',  # 图例在垂直方向上均匀分布
            borderaxespad=0.5,  # 边框与坐标轴的间距
            columnspacing=1.0,  # 列之间的间距
            handletextpad=0.5  # 图例标记与文本的间距
        )
        
        # 设置文本样式 - 扇区标签
        for text in texts:
            text.set_fontsize(8)
            text.set_color('#333333')
            text.set_fontweight('bold')
        
        # 设置文本样式 - 百分比标签
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
            autotext.set_fontweight('bold')
            autotext.set_bbox(dict(boxstyle='round,pad=0.3', fc=(0, 0, 0, 0.3), ec='none'))
        
        # 调整饼图大小，确保完整显示
        ax.set_aspect('equal')
        
        # 优化布局，为右侧图例和标题留出足够空间
        fig.subplots_adjust(left=0.05, right=0.75, top=0.85, bottom=0.05)
        
        # 嵌入到Tkinter窗口
        canvas = FigureCanvasTkAgg(fig, master=self.chart3_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
    
    def on_resize(self, _event=None):
        """
        窗口大小变化事件处理，实现响应式布局
        :param event: 事件对象
        """
        # 获取窗口宽度
        width = self.parent.winfo_width()
        
        # 根据不同屏幕尺寸范围制定差异化布局策略
        if width < 768:
            # 移动端：所有图表垂直排列
            self.chart1_frame.grid_configure(row=0, column=0, columnspan=1)
            self.chart2_frame.grid_configure(row=1, column=0)
            self.chart3_frame.grid_configure(row=2, column=0)
        elif 768 <= width < 1200:
            # 平板端：折线图占满一行，两个饼图垂直排列在第二列
            self.chart1_frame.grid_configure(row=0, column=0, columnspan=2)
            self.chart2_frame.grid_configure(row=1, column=0, columnspan=2)
            self.chart3_frame.grid_configure(row=2, column=0, columnspan=2)
        else:
            # 桌面端：折线图占满一行，两个饼图水平排列
            self.chart1_frame.grid_configure(row=0, column=0, columnspan=2)
            self.chart2_frame.grid_configure(row=1, column=0)
            self.chart3_frame.grid_configure(row=1, column=1)
        
        # 重新创建所有图表，确保它们能够根据新的容器大小调整
        self.recreate_charts()
    
    def recreate_charts(self, selected_month=None):
        """
        重新创建所有图表
        用于响应窗口大小变化，确保图表能够根据新的容器大小调整
        :param selected_month: 选中的月份，格式为YYYY-MM，None表示全部月份
        """
        # 首次加载或缓存过期时更新缓存时间
        if not self._is_cache_valid():
            self._update_cache_time()
        
        # 清除图表容器中的所有控件
        self._clear_chart_containers()
        
        # 存储当前选中的月份
        self.selected_month = selected_month
        
        # 重新创建图表
        self.create_line_chart()
        self.create_tenant_pie_chart()
        self.create_pie_chart()
    
    def _clear_chart_containers(self):
        """
        清除图表容器中的所有控件
        """
        # 清除图表1容器
        for widget in self.chart1_frame.winfo_children():
            widget.destroy()
        
        # 清除图表2容器
        for widget in self.chart2_frame.winfo_children():
            widget.destroy()
        
        # 清除图表3容器
        for widget in self.chart3_frame.winfo_children():
            widget.destroy()
    
    def refresh_charts(self, selected_month=None):
        """
        刷新所有图表
        :param selected_month: 选中的月份，格式为YYYY-MM，None表示全部月份
        """
        # 重新创建图表，确保数据和布局都是最新的
        self.recreate_charts(selected_month)
        print("图表已刷新")
