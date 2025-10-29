"""
Temporal Analysis - 时间序列深度分析页面

核心洞察：
- 9月12日推文量暴增 326 倍（1,542 → 503,057）
- 小时级活动模式
- 互动量随时间的爆发性增长
"""

import reflex as rx
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


# 获取项目根目录的 parquet 路径
PARQUET_DIR = Path(__file__).parent.parent.parent.parent / "notebooks" / "parquet"


def load_temporal_data() -> dict:
    """加载时间序列数据并计算关键指标"""
    try:
        # 加载完整推文数据用于小时级分析
        df_full = pl.read_parquet(str(PARQUET_DIR / "tweets_enriched.parquet"))

        # 加载每日统计
        daily_df = pl.read_parquet(str(PARQUET_DIR / "tweets_daily.parquet"))

        # 计算增长率
        if daily_df.height >= 2:
            growth_rate = (daily_df[1, "tweet_count"] / daily_df[0, "tweet_count"]) if daily_df[0, "tweet_count"] > 0 else 0
        else:
            growth_rate = 0

        # 小时级聚合
        hourly_df = df_full.with_columns(
            pl.col("createdAt").str.to_datetime("%Y-%m-%d %H:%M:%S%:z").dt.hour().alias("hour"),
            pl.col("createdAt").str.to_datetime("%Y-%m-%d %H:%M:%S%:z").dt.date().alias("date")
        ).group_by(["date", "hour"]).agg([
            pl.len().alias("tweet_count")
        ]).sort(["date", "hour"])

        return {
            "daily_df": daily_df,
            "hourly_df": hourly_df,
            "df_full": df_full,
            "total_days": daily_df.height,
            "growth_rate": growth_rate,
            "peak_date": str(daily_df.sort("tweet_count", descending=True)[0, "event_date"]),
            "peak_count": int(daily_df.sort("tweet_count", descending=True)[0, "tweet_count"]),
        }
    except Exception as e:
        return {
            "error": str(e),
            "daily_df": None,
            "hourly_df": None,
            "df_full": None,
            "total_days": 0,
            "growth_rate": 0,
            "peak_date": "N/A",
            "peak_count": 0,
        }


def create_time_series_chart(daily_df: pl.DataFrame) -> str:
    """创建时间序列双轴面积图"""

    # 转换为 pandas 以便 Plotly 处理
    daily_pd = daily_df.to_pandas()

    # 创建双轴图
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]]
    )

    # 添加推文量（左轴）
    fig.add_trace(
        go.Scatter(
            x=daily_pd["event_date"],
            y=daily_pd["tweet_count"],
            name="推文量",
            fill='tozeroy',
            line=dict(color='#667eea', width=2),
            fillcolor='rgba(102, 126, 234, 0.3)'
        ),
        secondary_y=False
    )

    # 添加互动量（右轴）
    fig.add_trace(
        go.Scatter(
            x=daily_pd["event_date"],
            y=daily_pd["total_engagement"],
            name="总互动量",
            fill='tozeroy',
            line=dict(color='#764ba2', width=2),
            fillcolor='rgba(118, 75, 162, 0.2)'
        ),
        secondary_y=True
    )

    # 标注峰值
    peak_idx = daily_pd["tweet_count"].idxmax()
    fig.add_annotation(
        x=daily_pd.iloc[peak_idx]["event_date"],
        y=daily_pd.iloc[peak_idx]["tweet_count"],
        text=f"🔥 爆发！<br>{daily_pd.iloc[peak_idx]['tweet_count']:,} 条推文",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#ff6b6b",
        bgcolor="#ffe66d",
        bordercolor="#ff6b6b",
        borderwidth=2,
        font=dict(size=12, color="#000")
    )

    # 布局优化
    fig.update_xaxes(title_text="日期", showgrid=True)
    fig.update_yaxes(title_text="推文数量", secondary_y=False, showgrid=True)
    fig.update_yaxes(title_text="总互动量", secondary_y=True, showgrid=False)

    fig.update_layout(
        title={
            'text': "推文量与互动量时间序列<br><sub>发现异常爆发模式</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="time_series_chart")


def create_hourly_heatmap(hourly_df: pl.DataFrame) -> str:
    """创建小时级活动热力图"""

    # 准备数据透视表
    hourly_pd = hourly_df.to_pandas()
    pivot_data = hourly_pd.pivot(index='hour', columns='date', values='tweet_count').fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=[str(d) for d in pivot_data.columns],
        y=pivot_data.index,
        colorscale='YlOrRd',
        text=pivot_data.values,
        texttemplate='%{text:,.0f}',
        textfont={"size": 10},
        colorbar=dict(title="推文数")
    ))

    fig.update_layout(
        title={
            'text': "小时级推文活动热力图<br><sub>识别高活跃时段</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="日期",
        yaxis_title="小时 (UTC)",
        height=500,
        template='plotly_white'
    )

    fig.update_yaxes(dtick=1)

    return fig.to_html(include_plotlyjs='cdn', div_id="hourly_heatmap")


def create_engagement_scatter(df_full: pl.DataFrame) -> str:
    """创建互动散点图（时间 vs 互动量，按蓝标着色）"""

    # 采样数据（避免过多点）
    sample_size = min(5000, df_full.height)
    df_sample = df_full.sample(n=sample_size, seed=42).with_columns(
        pl.col("createdAt").str.to_datetime("%Y-%m-%d %H:%M:%S%:z").alias("datetime"),
        (pl.col("retweetCount") + pl.col("likeCount") + pl.col("replyCount")).alias("total_engagement")
    )

    df_pd = df_sample.to_pandas()

    # 按蓝标分组
    verified = df_pd[df_pd["author_isBlueVerified_right"] == True]
    non_verified = df_pd[df_pd["author_isBlueVerified_right"] != True]

    fig = go.Figure()

    # 非蓝标
    fig.add_trace(go.Scatter(
        x=non_verified["datetime"],
        y=non_verified["total_engagement"],
        mode='markers',
        name='非蓝标',
        marker=dict(
            size=5,
            color='rgba(150, 150, 150, 0.3)',
            line=dict(width=0)
        )
    ))

    # 蓝标
    fig.add_trace(go.Scatter(
        x=verified["datetime"],
        y=verified["total_engagement"],
        mode='markers',
        name='🔵 蓝标',
        marker=dict(
            size=8,
            color='rgba(102, 126, 234, 0.7)',
            line=dict(width=0.5, color='white')
        )
    ))

    fig.update_layout(
        title={
            'text': "推文互动散点图<br><sub>蓝标 vs 非蓝标的传播差异</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="创建时间",
        yaxis_title="总互动量",
        yaxis_type="log",
        hovermode='closest',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="engagement_scatter")


def temporal_page() -> rx.Component:
    """时间序列分析页面"""
    data = load_temporal_data()

    # 错误处理
    if "error" in data and data["error"]:
        return rx.vstack(
            rx.heading("📈 Temporal Dynamics", size="8"),
            rx.box(
                rx.text(f"⚠️ 数据加载错误: {data['error']}", color="red"),
                padding="2em",
                background="#fee",
                border_radius="10px"
            ),
            spacing="5"
        )

    # 生成图表
    time_series_html = create_time_series_chart(data["daily_df"]) if data["daily_df"] is not None else ""
    hourly_heatmap_html = create_hourly_heatmap(data["hourly_df"]) if data["hourly_df"] is not None else ""
    engagement_scatter_html = create_engagement_scatter(data["df_full"]) if data["df_full"] is not None else ""

    return rx.vstack(
        # 标题
        rx.heading("📈 Temporal Dynamics", size="8"),
        rx.text(
            "时间序列深度分析：揭示推文活动的异常爆发模式",
            font_size="1.1em",
            color="gray"
        ),

        # KPI 卡片
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.text("分析天数", font_size="0.9em", color="gray"),
                    rx.text(f"{data['total_days']}", font_size="2.5em", font_weight="bold", color="#667eea"),
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
                    rx.text("峰值日期", font_size="0.9em", color="gray"),
                    rx.text(data['peak_date'], font_size="1.3em", font_weight="bold", color="#764ba2"),
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
                    rx.text("峰值推文量", font_size="0.9em", color="gray"),
                    rx.text(f"{data['peak_count']:,}", font_size="2em", font_weight="bold", color="#ff6b6b"),
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
                    rx.text("增长倍数", font_size="0.9em", color="gray"),
                    rx.text(f"{data['growth_rate']:.0f}x" if data['growth_rate'] > 0 else "N/A", font_size="2.5em", font_weight="bold", color="#f59e0b"),
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

        # 图表 1: 时间序列
        rx.box(
            rx.html(time_series_html),
            width="100%",
            padding="2em",
            background="white",
            border_radius="10px",
            box_shadow="0 4px 12px rgba(0,0,0,0.1)"
        ),

        # 图表 2: 小时热力图
        rx.box(
            rx.html(hourly_heatmap_html),
            width="100%",
            padding="2em",
            background="white",
            border_radius="10px",
            box_shadow="0 4px 12px rgba(0,0,0,0.1)"
        ),

        # 图表 3: 互动散点图
        rx.box(
            rx.html(engagement_scatter_html),
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
                    f"📊 数据显示：9月12日推文量从前一天的 1,542 条暴增至 {data['peak_count']:,} 条，增长 {data['growth_rate']:.0f} 倍",
                    font_size="1.1em"
                ),
                rx.text(
                    "💡 这种异常爆发可能与重大事件、热点话题或网络行为模式变化有关",
                    color="gray"
                ),
                rx.text(
                    "🔵 散点图显示：蓝标用户的推文互动量显著高于非蓝标用户，暗示认证身份对传播力的放大效应",
                    color="gray"
                ),
                spacing="4",
                align_items="flex-start"
            ),
            padding="2em",
            background="linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
            border_radius="10px",
            margin_top="2em"
        ),

        spacing="7",
        width="100%",
        align_items="stretch"
    )
