"""
Reflex 应用入口 - Charlie Kirk Twitter 数据分析仪表板

功能：
- Executive Overview: KPI 总览与关键指标
- Temporal Analysis: 时间序列分析与趋势
- Network Intelligence: 网络结构与影响力分析
- Content Semantics: 主题建模与情感分析
"""

import reflex as rx
from .pages import executive, temporal, network, content


def navbar() -> rx.Component:
    """导航栏组件"""
    return rx.box(
        rx.hstack(
            rx.heading("📊 Charlie Kirk Twitter Analytics", size="7"),
            rx.spacer(),
            rx.hstack(
                rx.link("Executive", href="/", padding="0.5em"),
                rx.link("Temporal", href="/temporal", padding="0.5em"),
                rx.link("Network", href="/network", padding="0.5em"),
                rx.link("Content", href="/content", padding="0.5em"),
                spacing="4",
            ),
            width="100%",
            padding="1em",
            align_items="center",
        ),
        background="linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
        color="white",
        width="100%",
    )


def footer() -> rx.Component:
    """页脚组件"""
    return rx.box(
        rx.text(
            "© 2025 Charlie Kirk Twitter Analytics | Data-driven insights from social media",
            text_align="center",
            color="gray",
            padding="1em",
        ),
        width="100%",
    )


def base_layout(content: rx.Component) -> rx.Component:
    """基础布局模板"""
    return rx.vstack(
        navbar(),
        rx.container(
            content,
            max_width="1400px",
            padding="2em",
        ),
        footer(),
        spacing="0",
        min_height="100vh",
        width="100%",
    )


def index() -> rx.Component:
    """主页 - Executive Dashboard"""
    return base_layout(executive.executive_page())


def temporal_page() -> rx.Component:
    """时间序列分析页面"""
    return base_layout(temporal.temporal_page())


def network_page() -> rx.Component:
    """网络分析页面"""
    return base_layout(network.network_page())


def content_page() -> rx.Component:
    """内容语义分析页面"""
    return base_layout(content.content_page())


# 创建应用
app = rx.App()
app.add_page(index, route="/")
app.add_page(temporal_page, route="/temporal")
app.add_page(network_page, route="/network")
app.add_page(content_page, route="/content")
