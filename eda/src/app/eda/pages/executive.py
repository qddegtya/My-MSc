"""
Executive Dashboard - 执行总览仪表板

核心功能：
- 关键指标一览
- 时间趋势速览
- 蓝标 vs 非蓝标雷达对比
- 数据概览
"""

import reflex as rx
import polars as pl
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path


# 获取项目根目录的 parquet 路径
PARQUET_DIR = Path(__file__).parent.parent.parent.parent / "notebooks" / "parquet"


def load_executive_data() -> dict:
    """加载总览数据"""
    try:
        # 加载主数据集
        df = pl.read_parquet(str(PARQUET_DIR / "tweets_enriched.parquet"))

        # 加载每日数据
        daily_df = pl.read_parquet(str(PARQUET_DIR / "tweets_daily.parquet"))

        # 加载蓝标对比
        verified_comp = pl.read_parquet(str(PARQUET_DIR / "verified_comparison.parquet"))

        # 基础指标
        total_tweets = df.height
        unique_users = df["pseudo_author_userName"].n_unique()
        total_engagement = (
            df["retweetCount"].sum() +
            df["replyCount"].sum() +
            df["likeCount"].sum() +
            df["quoteCount"].sum()
        )

        # 蓝标统计
        blue_verified = df.filter(pl.col("author_isBlueVerified_right") == True).height
        blue_percentage = (blue_verified / total_tweets * 100) if total_tweets > 0 else 0

        # 时间范围
        date_min = str(df["createdAt"].min())
        date_max = str(df["createdAt"].max())

        # 平均互动
        avg_engagement = total_engagement / total_tweets if total_tweets > 0 else 0

        # 语言分布
        lang_dist = df.group_by("lang").agg(
            pl.len().alias("count")
        ).sort("count", descending=True).head(5)

        # 回复率
        reply_rate = df.filter(pl.col("isReply") == True).height / total_tweets * 100 if total_tweets > 0 else 0

        return {
            "df": df,
            "daily_df": daily_df,
            "verified_comp": verified_comp,
            "total_tweets": total_tweets,
            "unique_users": unique_users,
            "total_engagement": total_engagement,
            "blue_verified": blue_verified,
            "blue_percentage": blue_percentage,
            "date_range": f"{date_min[:10]} → {date_max[:10]}",
            "avg_engagement": avg_engagement,
            "lang_dist": lang_dist,
            "reply_rate": reply_rate,
        }
    except Exception as e:
        return {
            "error": str(e),
            "df": None,
            "daily_df": None,
            "verified_comp": None,
            "total_tweets": 0,
            "unique_users": 0,
            "total_engagement": 0,
            "blue_verified": 0,
            "blue_percentage": 0,
            "date_range": "N/A",
            "avg_engagement": 0,
            "lang_dist": None,
            "reply_rate": 0,
        }


def create_quick_trend_chart(daily_df: pl.DataFrame) -> str:
    """创建快速趋势图"""

    daily_pd = daily_df.to_pandas()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily_pd["event_date"],
        y=daily_pd["tweet_count"],
        mode='lines+markers',
        name='推文量',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))

    fig.update_layout(
        title={
            'text': "推文量时间趋势",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="日期",
        yaxis_title="推文数量",
        template='plotly_white',
        height=300,
        margin=dict(t=50, b=40, l=60, r=20),
        showlegend=False
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="quick_trend")


def create_verified_radar_chart(verified_comp: pl.DataFrame) -> str:
    """创建蓝标 vs 非蓝标雷达对比图"""

    comp_pd = verified_comp.to_pandas()

    # 归一化数据（0-1）
    metrics = ['avg_word_count', 'avg_readability', 'avg_retweets', 'avg_likes']
    metric_names = ['词数', '可读性', '转发', '点赞']

    # 获取蓝标和非蓝标数据
    verified_data = comp_pd[comp_pd['author_isBlueVerified'] == True][metrics].values[0] if len(comp_pd[comp_pd['author_isBlueVerified'] == True]) > 0 else [0, 0, 0, 0]
    non_verified_data = comp_pd[comp_pd['author_isBlueVerified'] == False][metrics].values[0] if len(comp_pd[comp_pd['author_isBlueVerified'] == False]) > 0 else [0, 0, 0, 0]

    # 归一化
    max_vals = [max(verified_data[i], non_verified_data[i]) for i in range(len(metrics))]
    verified_norm = [verified_data[i] / max_vals[i] if max_vals[i] > 0 else 0 for i in range(len(metrics))]
    non_verified_norm = [non_verified_data[i] / max_vals[i] if max_vals[i] > 0 else 0 for i in range(len(metrics))]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=non_verified_norm + [non_verified_norm[0]],
        theta=metric_names + [metric_names[0]],
        fill='toself',
        name='⚪ 非蓝标',
        line=dict(color='rgba(150, 150, 150, 0.8)', width=2),
        fillcolor='rgba(150, 150, 150, 0.3)'
    ))

    fig.add_trace(go.Scatterpolar(
        r=verified_norm + [verified_norm[0]],
        theta=metric_names + [metric_names[0]],
        fill='toself',
        name='🔵 蓝标',
        line=dict(color='rgba(102, 126, 234, 0.9)', width=2),
        fillcolor='rgba(102, 126, 234, 0.4)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title={
            'text': "蓝标 vs 非蓝标雷达对比",
            'x': 0.5,
            'xanchor': 'center'
        },
        template='plotly_white',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="verified_radar")


def create_language_pie_chart(lang_dist: pl.DataFrame) -> str:
    """创建语言分布饼图"""

    lang_pd = lang_dist.to_pandas()

    fig = px.pie(
        lang_pd,
        values='count',
        names='lang',
        title='Top 5 语言分布',
        color_discrete_sequence=px.colors.sequential.RdBu
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(
        template='plotly_white',
        height=350,
        title={
            'x': 0.5,
            'xanchor': 'center'
        }
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="language_pie")


def executive_page() -> rx.Component:
    """Executive Dashboard 主页面"""
    data = load_executive_data()

    # 错误处理
    if "error" in data and data["error"]:
        return rx.vstack(
            rx.heading("📊 Executive Dashboard", size="8"),
            rx.box(
                rx.text(f"⚠️ 数据加载错误: {data['error']}", color="red"),
                padding="2em",
                background="#fee",
                border_radius="10px"
            ),
            spacing="5"
        )

    # 生成图表
    trend_html = create_quick_trend_chart(data["daily_df"]) if data["daily_df"] is not None else ""
    radar_html = create_verified_radar_chart(data["verified_comp"]) if data["verified_comp"] is not None else ""
    lang_pie_html = create_language_pie_chart(data["lang_dist"]) if data["lang_dist"] is not None else ""

    return rx.vstack(
        # 标题与副标题
        rx.heading("📊 Executive Dashboard", size="8"),
        rx.text(
            "Charlie Kirk Twitter 数据分析总览",
            font_size="1.2em",
            color="gray"
        ),

        # KPI 卡片组 (6个)
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.text("📝", font_size="2em"),
                    rx.text("总推文数", font_size="0.9em", color="gray"),
                    rx.text(f"{data['total_tweets']:,}", font_size="2em", font_weight="bold", color="#667eea"),
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
                    rx.text("👥", font_size="2em"),
                    rx.text("独立用户", font_size="0.9em", color="gray"),
                    rx.text(f"{data['unique_users']:,}", font_size="2em", font_weight="bold", color="#764ba2"),
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
                    rx.text("💬", font_size="2em"),
                    rx.text("总互动量", font_size="0.9em", color="gray"),
                    rx.text(f"{data['total_engagement']:,}", font_size="1.8em", font_weight="bold", color="#f59e0b"),
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
                    rx.text("🔵", font_size="2em"),
                    rx.text("蓝标比例", font_size="0.9em", color="gray"),
                    rx.text(f"{data['blue_percentage']:.1f}%", font_size="2em", font_weight="bold", color="#3b82f6"),
                    rx.text(f"{data['blue_verified']:,} 条", font_size="0.8em", color="gray"),
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
                    rx.text("📊", font_size="2em"),
                    rx.text("平均互动", font_size="0.9em", color="gray"),
                    rx.text(f"{data['avg_engagement']:.1f}", font_size="2em", font_weight="bold", color="#10b981"),
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
                    rx.text("↩️", font_size="2em"),
                    rx.text("回复率", font_size="0.9em", color="gray"),
                    rx.text(f"{data['reply_rate']:.1f}%", font_size="2em", font_weight="bold", color="#ef4444"),
                    spacing="2"
                ),
                padding="1.5em",
                background="white",
                border_radius="10px",
                box_shadow="0 2px 8px rgba(0,0,0,0.1)",
                text_align="center"
            ),
            columns="3",
            spacing="5",
            width="100%"
        ),

        # 双列：趋势图 + 雷达图
        rx.grid(
            rx.box(
                rx.html(trend_html),
                padding="2em",
                background="white",
                border_radius="10px",
                box_shadow="0 4px 12px rgba(0,0,0,0.1)"
            ),
            rx.box(
                rx.html(radar_html),
                padding="2em",
                background="white",
                border_radius="10px",
                box_shadow="0 4px 12px rgba(0,0,0,0.1)"
            ),
            columns="2",
            spacing="5",
            width="100%"
        ),

        # 语言分布
        rx.box(
            rx.html(lang_pie_html),
            padding="2em",
            background="white",
            border_radius="10px",
            box_shadow="0 4px 12px rgba(0,0,0,0.1)"
        ),

        # 数据概览说明
        rx.box(
            rx.vstack(
                rx.heading("📈 数据概览", size="6"),
                rx.divider(),
                rx.text(
                    f"本仪表板分析了 Charlie Kirk 的 Twitter 互动数据，时间跨度：{data['date_range']}",
                    font_size="1.1em"
                ),
                rx.text(""),
                rx.heading("🔍 核心洞察", size="5"),
                rx.text("🔹 Temporal Dynamics: 9月12日推文量暴增 326 倍，互动量爆发式增长"),
                rx.text("🔹 Network Structure: 21万+ 边，19万+ 节点，呈现典型幂律分布"),
                rx.text("🔹 Content Semantics: 蓝标用户词数 +58%，互动放大 +1200%"),
                rx.text("🔹 Verified Impact: 蓝标认证是传播力的核心放大器"),
                spacing="4",
                align_items="flex-start"
            ),
            padding="2em",
            background="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
            border_radius="10px",
            margin_top="2em"
        ),

        spacing="7",
        width="100%",
        align_items="stretch"
    )
