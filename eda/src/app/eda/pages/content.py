"""
Content Semantics - 内容语义深度分析页面

核心洞察：
- 49 个主题，蓝标 vs 非蓝标的语言差异巨大
- 蓝标用户：词数 +58%，互动 +1200%
- 主题互动效能分析
"""

import reflex as rx
import polars as pl
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path


# 获取项目根目录的 parquet 路径
PARQUET_DIR = Path(__file__).parent.parent.parent.parent / "notebooks" / "parquet"


def load_content_data() -> dict:
    """加载内容分析数据"""
    try:
        # 加载内容分析样本
        content_df = pl.read_parquet(str(PARQUET_DIR / "content_analysis.parquet"))

        # 加载蓝标对比
        comparison_df = pl.read_parquet(str(PARQUET_DIR / "verified_comparison.parquet"))

        # 加载主题分布
        topic_dist_df = pl.read_parquet(str(PARQUET_DIR / "topic_distribution.parquet"))

        # 基本统计
        total_analyzed = content_df.height
        unique_topics = content_df["topic"].n_unique()

        # 主题互动聚合（过滤噪音主题 -1）
        topic_engagement = content_df.filter(pl.col("topic") >= 0).group_by("topic").agg([
            pl.len().alias("count"),
            pl.col("retweetCount").mean().alias("avg_retweets"),
            pl.col("likeCount").mean().alias("avg_likes"),
            pl.col("word_count").mean().alias("avg_words"),
            pl.col("readability").mean().alias("avg_readability")
        ]).sort("count", descending=True)

        return {
            "content_df": content_df,
            "comparison_df": comparison_df,
            "topic_dist_df": topic_dist_df,
            "topic_engagement": topic_engagement,
            "total_analyzed": total_analyzed,
            "unique_topics": unique_topics,
        }
    except Exception as e:
        return {
            "error": str(e),
            "content_df": None,
            "comparison_df": None,
            "topic_dist_df": None,
            "topic_engagement": None,
            "total_analyzed": 0,
            "unique_topics": 0,
        }


def create_verified_comparison_chart(comparison_df: pl.DataFrame) -> str:
    """创建蓝标 vs 非蓝标对比分组柱状图"""

    comp_pd = comparison_df.to_pandas()

    # 准备数据
    metrics = ['avg_word_count', 'avg_readability', 'avg_retweets', 'avg_likes']
    metric_names = ['平均词数', '可读性分数', '平均转发', '平均点赞']

    fig = go.Figure()

    # 非蓝标
    fig.add_trace(go.Bar(
        name='⚪ 非蓝标',
        x=metric_names,
        y=[comp_pd.loc[comp_pd['author_isBlueVerified'] == False, m].values[0] if len(comp_pd[comp_pd['author_isBlueVerified'] == False]) > 0 else 0 for m in metrics],
        marker_color='rgba(150, 150, 150, 0.7)',
        text=[f"{comp_pd.loc[comp_pd['author_isBlueVerified'] == False, m].values[0]:.1f}" if len(comp_pd[comp_pd['author_isBlueVerified'] == False]) > 0 else "0" for m in metrics],
        textposition='auto'
    ))

    # 蓝标
    fig.add_trace(go.Bar(
        name='🔵 蓝标',
        x=metric_names,
        y=[comp_pd.loc[comp_pd['author_isBlueVerified'] == True, m].values[0] if len(comp_pd[comp_pd['author_isBlueVerified'] == True]) > 0 else 0 for m in metrics],
        marker_color='rgba(102, 126, 234, 0.8)',
        text=[f"{comp_pd.loc[comp_pd['author_isBlueVerified'] == True, m].values[0]:.1f}" if len(comp_pd[comp_pd['author_isBlueVerified'] == True]) > 0 else "0" for m in metrics],
        textposition='auto'
    ))

    fig.update_layout(
        title={
            'text': "蓝标 vs 非蓝标语言特征对比<br><sub>揭示认证用户的语言策略</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        barmode='group',
        template='plotly_white',
        height=500,
        yaxis_title="数值",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="verified_comparison")


def create_topic_engagement_scatter(topic_engagement: pl.DataFrame) -> str:
    """创建主题互动散点图（词数 vs 互动量）"""

    topic_pd = topic_engagement.head(30).to_pandas()  # Top 30 主题

    # 计算总互动
    topic_pd['total_engagement'] = topic_pd['avg_retweets'] + topic_pd['avg_likes']

    fig = px.scatter(
        topic_pd,
        x='avg_words',
        y='total_engagement',
        size='count',
        color='avg_readability',
        hover_data=['topic', 'count', 'avg_retweets', 'avg_likes'],
        labels={
            'avg_words': '平均词数',
            'total_engagement': '平均总互动量',
            'count': '推文数量',
            'avg_readability': '可读性'
        },
        color_continuous_scale='Viridis',
        title="主题互动效能分析<br><sub>词数 vs 互动量，气泡大小=推文数量</sub>"
    )

    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white'),
            opacity=0.8
        )
    )

    fig.update_layout(
        template='plotly_white',
        height=550,
        title={
            'x': 0.5,
            'xanchor': 'center'
        },
        coloraxis_colorbar=dict(title="可读性")
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="topic_engagement_scatter")


def create_topic_distribution_chart(topic_engagement: pl.DataFrame) -> str:
    """创建主题分布水平柱状图（Top 20）"""

    topic_pd = topic_engagement.head(20).sort("count").to_pandas()

    fig = go.Figure(go.Bar(
        y=[f"主题 {t}" for t in topic_pd['topic']],
        x=topic_pd['count'],
        orientation='h',
        marker=dict(
            color=topic_pd['count'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="推文数")
        ),
        text=topic_pd['count'],
        textposition='auto',
        hovertemplate='<b>主题 %{y}</b><br>推文数: %{x}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': "Top 20 主题分布<br><sub>按推文数量排序</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="推文数量",
        yaxis_title="",
        template='plotly_white',
        height=600,
        margin=dict(l=100)
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="topic_distribution")


def content_page() -> rx.Component:
    """内容语义分析页面"""
    data = load_content_data()

    # 错误处理
    if "error" in data and data["error"]:
        return rx.vstack(
            rx.heading("📝 Content Semantics", size="8"),
            rx.box(
                rx.text(f"⚠️ 数据加载错误: {data['error']}", color="red"),
                padding="2em",
                background="#fee",
                border_radius="10px"
            ),
            spacing="5"
        )

    # 生成图表
    comparison_html = create_verified_comparison_chart(data["comparison_df"]) if data["comparison_df"] is not None else ""
    topic_scatter_html = create_topic_engagement_scatter(data["topic_engagement"]) if data["topic_engagement"] is not None else ""
    topic_dist_html = create_topic_distribution_chart(data["topic_engagement"]) if data["topic_engagement"] is not None else ""

    # 计算关键指标
    if data["comparison_df"] is not None and data["comparison_df"].height >= 2:
        verified_row = data["comparison_df"].filter(pl.col("author_isBlueVerified") == True)
        non_verified_row = data["comparison_df"].filter(pl.col("author_isBlueVerified") == False)

        if verified_row.height > 0 and non_verified_row.height > 0:
            word_diff = ((verified_row[0, "avg_word_count"] / non_verified_row[0, "avg_word_count"] - 1) * 100)
            retweet_diff = ((verified_row[0, "avg_retweets"] / non_verified_row[0, "avg_retweets"] - 1) * 100)
            like_diff = ((verified_row[0, "avg_likes"] / non_verified_row[0, "avg_likes"] - 1) * 100)
        else:
            word_diff = retweet_diff = like_diff = 0
    else:
        word_diff = retweet_diff = like_diff = 0

    return rx.vstack(
        # 标题
        rx.heading("📝 Content Semantics", size="8"),
        rx.text(
            "内容语义深度分析：揭示蓝标用户的语言优势",
            font_size="1.1em",
            color="gray"
        ),

        # KPI 卡片
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.text("分析样本", font_size="0.9em", color="gray"),
                    rx.text(f"{data['total_analyzed']:,}", font_size="2.5em", font_weight="bold", color="#667eea"),
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
                    rx.text("发现主题", font_size="0.9em", color="gray"),
                    rx.text(f"{data['unique_topics']}", font_size="2.5em", font_weight="bold", color="#764ba2"),
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
                    rx.text("词数差异", font_size="0.9em", color="gray"),
                    rx.text(f"+{word_diff:.0f}%" if word_diff > 0 else "N/A", font_size="2em", font_weight="bold", color="#f59e0b"),
                    rx.text("蓝标 vs 非蓝标", font_size="0.8em", color="gray"),
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
                    rx.text("互动放大", font_size="0.9em", color="gray"),
                    rx.text(f"+{like_diff:.0f}%" if like_diff > 0 else "N/A", font_size="2em", font_weight="bold", color="#ff6b6b"),
                    rx.text("蓝标点赞优势", font_size="0.8em", color="gray"),
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

        # 图表 1: 蓝标对比
        rx.box(
            rx.html(comparison_html),
            width="100%",
            padding="2em",
            background="white",
            border_radius="10px",
            box_shadow="0 4px 12px rgba(0,0,0,0.1)"
        ),

        # 图表 2: 主题互动散点图
        rx.box(
            rx.html(topic_scatter_html),
            width="100%",
            padding="2em",
            background="white",
            border_radius="10px",
            box_shadow="0 4px 12px rgba(0,0,0,0.1)"
        ),

        # 图表 3: 主题分布
        rx.box(
            rx.html(topic_dist_html),
            width="100%",
            padding="2em",
            background="white",
            border_radius="10px",
            box_shadow="0 4px 12px rgba(0,0,0,0.1)"
        ),

        # 洞察总结
        rx.box(
            rx.vstack(
                rx.heading("🔍 关键洞察", size="6"),
                rx.divider(),
                rx.text(
                    f"📊 蓝标用户的语言策略：平均词数多 {word_diff:.0f}%，但可读性更低（更复杂），暗示使用更专业的语言",
                    font_size="1.1em"
                ),
                rx.text(
                    f"💡 传播优势：蓝标用户的推文平均获得 {like_diff:.0f}% 更多点赞，{retweet_diff:.0f}% 更多转发",
                    color="gray"
                ),
                rx.text(
                    "📚 主题效能：散点图显示部分主题（高互动+适中词数）具有更高的传播效能",
                    color="gray"
                ),
                rx.text(
                    "🔵 认证效应：蓝标认证不仅是身份标识，更是传播力的放大器",
                    color="gray"
                ),
                spacing="4",
                align_items="flex-start"
            ),
            padding="2em",
            background="linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)",
            border_radius="10px",
            margin_top="2em"
        ),

        spacing="7",
        width="100%",
        align_items="stretch"
    )
