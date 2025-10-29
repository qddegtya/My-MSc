"""
Network Intelligence - 网络结构深度分析页面

核心洞察：
- 21.3万 回复关系边，19万+ 节点
- 幂律分布：少数超级节点控制大部分连接
- 度中心性揭示影响力核心
"""

import reflex as rx
import polars as pl
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path


# 获取项目根目录的 parquet 路径
PARQUET_DIR = Path(__file__).parent.parent.parent.parent / "notebooks" / "parquet"


def load_network_data() -> dict:
    """加载网络数据"""
    try:
        # 加载边列表
        edges_df = pl.read_parquet(str(PARQUET_DIR / "network_edges.parquet"))

        # 加载中心性指标
        centrality_df = pl.read_parquet(str(PARQUET_DIR / "network_centrality.parquet"))

        # 基本统计
        total_edges = edges_df.height
        unique_sources = edges_df["pseudo_author_userName"].n_unique()
        unique_targets = edges_df["pseudo_inReplyToUsername"].n_unique()

        # 计算总节点数（去重）
        all_nodes = set(edges_df["pseudo_author_userName"].to_list()) | set(edges_df["pseudo_inReplyToUsername"].to_list())
        total_nodes = len(all_nodes)

        # Top 影响力节点
        top_nodes = centrality_df.sort("degree_centrality", descending=True).head(20)

        # 度分布统计
        degree_dist = centrality_df.with_columns(
            (pl.col("degree_centrality") * total_nodes).cast(pl.Int32).alias("degree")
        ).group_by("degree").agg(
            pl.len().alias("count")
        ).sort("degree")

        # 网络密度 = 实际边数 / 可能边数
        max_possible_edges = total_nodes * (total_nodes - 1)
        density = total_edges / max_possible_edges if max_possible_edges > 0 else 0

        return {
            "edges_df": edges_df,
            "centrality_df": centrality_df,
            "degree_dist": degree_dist,
            "total_edges": total_edges,
            "total_nodes": total_nodes,
            "unique_sources": unique_sources,
            "unique_targets": unique_targets,
            "top_nodes": top_nodes,
            "density": density,
            "avg_degree": centrality_df["degree_centrality"].mean() * total_nodes,
        }
    except Exception as e:
        return {
            "error": str(e),
            "edges_df": None,
            "centrality_df": None,
            "degree_dist": None,
            "total_edges": 0,
            "total_nodes": 0,
            "unique_sources": 0,
            "unique_targets": 0,
            "top_nodes": None,
            "density": 0,
            "avg_degree": 0,
        }


def create_degree_distribution_chart(degree_dist: pl.DataFrame) -> str:
    """创建度分布图（双对数）"""

    degree_pd = degree_dist.filter(pl.col("degree") > 0).to_pandas()

    fig = go.Figure()

    # 散点图
    fig.add_trace(go.Scatter(
        x=degree_pd['degree'],
        y=degree_pd['count'],
        mode='markers',
        marker=dict(
            size=8,
            color=degree_pd['count'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="节点数")
        ),
        name='度分布',
        hovertemplate='<b>度数: %{x}</b><br>节点数: %{y}<extra></extra>'
    ))

    # 幂律参考线（示意）
    x_ref = np.logspace(np.log10(degree_pd['degree'].min()), np.log10(degree_pd['degree'].max()), 50)
    y_ref = x_ref ** (-1.5) * degree_pd['count'].max() * 10

    fig.add_trace(go.Scatter(
        x=x_ref,
        y=y_ref,
        mode='lines',
        line=dict(color='red', dash='dash', width=2),
        name='幂律参考 (α≈1.5)',
        hoverinfo='skip'
    ))

    fig.update_xaxes(type='log', title='度数 (对数轴)')
    fig.update_yaxes(type='log', title='节点数 (对数轴)')

    fig.update_layout(
        title={
            'text': "度分布 - 双对数图<br><sub>检验幂律分布（富者愈富）</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        template='plotly_white',
        height=500,
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="degree_distribution")


def create_top_nodes_chart(top_nodes: pl.DataFrame) -> str:
    """创建 Top 20 影响力节点水平柱状图"""

    top_pd = top_nodes.head(20).sort("degree_centrality").to_pandas()

    fig = go.Figure(go.Bar(
        y=[f"节点 {n}" for n in top_pd['node']],
        x=top_pd['degree_centrality'],
        orientation='h',
        marker=dict(
            color=top_pd['degree_centrality'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="中心性")
        ),
        text=[f"{c:.4f}" for c in top_pd['degree_centrality']],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>度中心性: %{x:.4f}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': "Top 20 影响力节点<br><sub>度中心性排行榜</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="度中心性",
        yaxis_title="",
        template='plotly_white',
        height=700,
        margin=dict(l=120)
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="top_nodes")


def create_centrality_histogram(centrality_df: pl.DataFrame) -> str:
    """创建中心性分布直方图"""

    cent_pd = centrality_df.to_pandas()

    fig = go.Figure(data=[go.Histogram(
        x=cent_pd['degree_centrality'],
        nbinsx=50,
        marker_color='rgba(102, 126, 234, 0.7)',
        marker_line=dict(color='white', width=1),
        hovertemplate='中心性范围: %{x}<br>节点数: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title={
            'text': "度中心性分布直方图<br><sub>大多数节点的中心性很低</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="度中心性",
        yaxis_title="节点数",
        template='plotly_white',
        height=450,
        bargap=0.05
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="centrality_histogram")


def network_page() -> rx.Component:
    """网络分析页面"""
    data = load_network_data()

    # 错误处理
    if "error" in data and data["error"]:
        return rx.vstack(
            rx.heading("🕸️ Network Intelligence", size="8"),
            rx.box(
                rx.text(f"⚠️ 数据加载错误: {data['error']}", color="red"),
                padding="2em",
                background="#fee",
                border_radius="10px"
            ),
            spacing="5"
        )

    # 生成图表
    degree_dist_html = create_degree_distribution_chart(data["degree_dist"]) if data["degree_dist"] is not None else ""
    top_nodes_html = create_top_nodes_chart(data["top_nodes"]) if data["top_nodes"] is not None else ""
    centrality_hist_html = create_centrality_histogram(data["centrality_df"]) if data["centrality_df"] is not None else ""

    return rx.vstack(
        # 标题
        rx.heading("🕸️ Network Intelligence", size="8"),
        rx.text(
            "网络结构深度分析：揭示权力集中与影响力分布",
            font_size="1.1em",
            color="gray"
        ),

        # KPI 卡片
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.text("总节点数", font_size="0.9em", color="gray"),
                    rx.text(f"{data['total_nodes']:,}", font_size="2.5em", font_weight="bold", color="#667eea"),
                    spacing="2"
                ),
                padding="1.5em",
                background="white",
                border_radius="10px",
                box_shadow="0 2px 8px rgba(0,0,0,0.1)",
                text_align="center"
            ),
            rx.box(
                rx.vstack(
                    rx.text("总边数", font_size="0.9em", color="gray"),
                    rx.text(f"{data['total_edges']:,}", font_size="2.5em", font_weight="bold", color="#764ba2"),
                    spacing="2"
                ),
                padding="1.5em",
                background="white",
                border_radius="10px",
                box_shadow="0 2px 8px rgba(0,0,0,0.1)",
                text_align="center"
            ),
            rx.box(
                rx.vstack(
                    rx.text("网络密度", font_size="0.9em", color="gray"),
                    rx.text(f"{data['density']:.2e}", font_size="1.8em", font_weight="bold", color="#f59e0b"),
                    rx.text("稀疏网络", font_size="0.8em", color="gray"),
                    spacing="2"
                ),
                padding="1.5em",
                background="white",
                border_radius="10px",
                box_shadow="0 2px 8px rgba(0,0,0,0.1)",
                text_align="center"
            ),
            rx.box(
                rx.vstack(
                    rx.text("平均度数", font_size="0.9em", color="gray"),
                    rx.text(f"{data['avg_degree']:.1f}", font_size="2.5em", font_weight="bold", color="#ff6b6b"),
                    spacing="2"
                ),
                padding="1.5em",
                background="white",
                border_radius="10px",
                box_shadow="0 2px 8px rgba(0,0,0,0.1)",
                text_align="center"
            ),
            columns="4",
            spacing="5",
            width="100%"
        ),

        # 图表 1: 度分布
        rx.box(
            rx.html(degree_dist_html),
            width="100%",
            padding="2em",
            background="white",
            border_radius="10px",
            box_shadow="0 4px 12px rgba(0,0,0,0.1)"
        ),

        # 双列布局：Top 节点 + 中心性分布
        rx.grid(
            rx.box(
                rx.html(top_nodes_html),
                padding="2em",
                background="white",
                border_radius="10px",
                box_shadow="0 4px 12px rgba(0,0,0,0.1)"
            ),
            rx.box(
                rx.html(centrality_hist_html),
                padding="2em",
                background="white",
                border_radius="10px",
                box_shadow="0 4px 12px rgba(0,0,0,0.1)"
            ),
            columns="2",
            spacing="5",
            width="100%"
        ),

        # 洞察总结
        rx.box(
            rx.vstack(
                rx.heading("🔍 关键洞察", size="6"),
                rx.divider(),
                rx.text(
                    f"📊 网络规模：{data['total_nodes']:,} 个节点，{data['total_edges']:,} 条边，网络密度极低 ({data['density']:.2e})，呈现典型的稀疏社交网络特征",
                    font_size="1.1em"
                ),
                rx.text(
                    "💡 幂律分布：度分布接近幂律（富者愈富），少数超级节点（influencer）占据大量连接",
                    color="gray"
                ),
                rx.text(
                    f"🎯 中心化程度：平均度数 {data['avg_degree']:.1f}，但 Top 20 节点的中心性显著高于平均水平",
                    color="gray"
                ),
                rx.text(
                    "🕸️ 网络结构：高度集中的星型结构，信息流动依赖核心节点",
                    color="gray"
                ),
                spacing="4",
                align_items="flex-start"
            ),
            padding="2em",
            background="linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
            border_radius="10px",
            margin_top="2em"
        ),

        spacing="7",
        width="100%",
        align_items="stretch"
    )
