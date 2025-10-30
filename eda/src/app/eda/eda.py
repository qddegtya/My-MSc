"""
Reflex 应用入口 - Charlie Kirk Twitter 数据分析报告

Tableau-Style 单页滚动报告
"""

import reflex as rx
from .pages import report


def index() -> rx.Component:
    """主页 - Tableau 风格单页报告"""
    return report.report_page()


# 创建应用
app = rx.App()
app.add_page(index, route="/")
