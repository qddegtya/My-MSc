"""
Charlie Kirk 暗杀事件社交媒体舆论分析报告
Tableau Public 专业风格数据报告
"""

import reflex as rx
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# 数据目录
PARQUET_DIR = Path(__file__).parent.parent.parent.parent.parent / "src" / "notebooks" / "parquet"

# 映射字典
NARRATIVE_CN = {
    'political_violence': '政治暴力受害者',
    'consequences': '言论后果反思',
    'polarization': '政治极化担忧',
    'free_speech': '言论自由捍卫',
    'conspiracy': '阴谋论怀疑',
    'memorial': '纪念与遗产'
}

EMOTION_CN = {
    'sadness': '悲伤', 'anger': '愤怒', 'fear': '恐惧',
    'surprise': '惊讶', 'joy': '喜悦', 'love': '爱意'
}

STANCE_CN = {'conservative': '保守派', 'liberal': '自由派', 'neutral': '中立'}

# Tableau 专业配色
COLORS = {
    'blue': '#4E79A7', 'orange': '#F28E2B', 'red': '#E15759',
    'teal': '#76B7B2', 'green': '#59A14F', 'yellow': '#EDC948',
    'purple': '#B07AA1', 'pink': '#FF9DA7', 'brown': '#9C755F',
    'gray': '#BAB0AC'
}


def load_all_data() -> dict:
    """加载所有分析数据"""
    try:
        tweets_df = pl.read_parquet(str(PARQUET_DIR / "tweets_enriched.parquet"))
        content_df = pl.read_parquet(str(PARQUET_DIR / "content_analysis.parquet"))
        emotion_evo = pl.read_parquet(str(PARQUET_DIR / "emotion_evolution.parquet"))
        narrative_evo = pl.read_parquet(str(PARQUET_DIR / "narrative_evolution.parquet"))
        hourly_df = pl.read_parquet(str(PARQUET_DIR / "tweets_hourly.parquet"))

        # 【优化新增】加载作者画像数据（如果存在）
        try:
            author_prof = pl.read_parquet(str(PARQUET_DIR / "author_profiling.parquet"))
            top_50 = pl.read_parquet(str(PARQUET_DIR / "top_50_influencers.parquet"))
        except:
            author_prof = None
            top_50 = None

        return {
            "tweets_df": tweets_df,
            "content_df": content_df,
            "emotion_evo": emotion_evo,
            "narrative_evo": narrative_evo,
            "hourly_df": hourly_df,
            "author_prof": author_prof,
            "top_50": top_50,
            "total_tweets": tweets_df.height,
            "total_sampled": content_df.height,
            "date_range": f"{str(tweets_df['createdAt'].min())[:10]} ~ {str(tweets_df['createdAt'].max())[:10]}",
        }
    except Exception as e:
        return {"error": str(e)}


def kpi_card(icon: str, label: str, value: str, color: str) -> rx.Component:
    """KPI指标卡片"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(icon, font_size="2em"),
                rx.spacer(),
            ),
            rx.text(value, font_size="2em", font_weight="700", color=color),
            rx.text(label, font_size="0.9em", color="#666"),
            spacing="1",
            align_items="flex_start",
        ),
        padding="1.2em",
        background="white",
        border_radius="8px",
        box_shadow="0 1px 3px rgba(0,0,0,0.1)",
        width="100%",
    )


def chart_box(title: str, chart_html: str, height: str = "auto") -> rx.Component:
    """图表容器"""
    return rx.box(
        rx.vstack(
            rx.text(title, font_size="1em", font_weight="600", color="#333", margin_bottom="0.5em"),
            rx.html(chart_html),
            spacing="0",
            align_items="flex_start",
            width="100%",
        ),
        padding="1.2em",
        background="white",
        border_radius="6px",
        box_shadow="0 1px 3px rgba(0,0,0,0.1)",
        width="100%",
        height=height,
    )


def create_emotion_line(emotion_evo: pl.DataFrame) -> str:
    """情感演变折线图"""
    df = emotion_evo.to_pandas()
    fig = go.Figure()

    emotions = ['sadness', 'anger', 'fear', 'surprise', 'joy', 'love']
    colors = [COLORS['red'], COLORS['orange'], COLORS['yellow'], COLORS['purple'], COLORS['green'], COLORS['pink']]

    for idx, emotion in enumerate(emotions):
        col = f'avg_{emotion}'
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['time_window'], y=df[col],
                name=EMOTION_CN[emotion],
                line=dict(color=colors[idx], width=2.5),
                mode='lines+markers',
                marker=dict(size=8),
            ))

    fig.update_layout(
        template='plotly_white',
        height=280,
        font=dict(family='Arial', size=11),
        xaxis=dict(title='', showgrid=True, gridcolor='#E5E5E5'),
        yaxis=dict(title='强度', showgrid=True, gridcolor='#E5E5E5'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=30, b=30, l=50, r=10),
        hovermode='x unified',
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="emotion_line")


def create_narrative_pie(content_df: pl.DataFrame) -> str:
    """叙事饼图"""
    counts = content_df.group_by('primary_narrative').agg(pl.len().alias('count')).sort('count', descending=True).to_pandas()
    labels = [NARRATIVE_CN.get(n, n) for n in counts['primary_narrative'] if n in NARRATIVE_CN]
    values = [counts[counts['primary_narrative'] == n]['count'].values[0] for n in counts['primary_narrative'] if n in NARRATIVE_CN]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.5,
        marker=dict(colors=[COLORS['blue'], COLORS['orange'], COLORS['green'], COLORS['red'], COLORS['yellow'], COLORS['purple']]),
        textinfo='label+percent', textfont=dict(size=11),
    )])

    fig.update_layout(
        template='plotly_white',
        height=280,
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="narrative_pie")


def create_stance_bar(content_df: pl.DataFrame) -> str:
    """立场柱状图"""
    counts = content_df.group_by('political_stance').agg(pl.len().alias('count')).to_pandas()
    labels = [STANCE_CN.get(s, s) for s in counts['political_stance']]

    fig = go.Figure(data=[go.Bar(
        x=labels, y=counts['count'],
        marker_color=[COLORS['red'], COLORS['gray'], COLORS['blue']],
        text=counts['count'].apply(lambda x: f'{x:,}'),
        textposition='outside',
    )])

    fig.update_layout(
        template='plotly_white',
        height=280,
        font=dict(size=11),
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(title='推文数', showgrid=True, gridcolor='#E5E5E5'),
        margin=dict(t=10, b=30, l=50, r=10),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="stance_bar")


def create_hourly_bar(hourly_df: pl.DataFrame) -> str:
    """小时级推文量"""
    df = hourly_df.to_pandas()

    fig = go.Figure(data=[go.Bar(
        x=df['hour'], y=df['tweet_count'],
        marker_color=COLORS['blue'], marker_opacity=0.8,
    )])

    fig.update_layout(
        template='plotly_white',
        height=280,
        font=dict(size=11),
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(title='推文数', showgrid=True, gridcolor='#E5E5E5'),
        margin=dict(t=10, b=30, l=50, r=10),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="hourly_bar")


def create_emotion_heatmap(emotion_evo: pl.DataFrame) -> str:
    """情感热力图"""
    df = emotion_evo.to_pandas()
    emotions = ['sadness', 'anger', 'fear', 'surprise', 'joy', 'love']
    emotion_labels = [EMOTION_CN[e] for e in emotions]

    z_data = []
    for emotion in emotions:
        col = f'avg_{emotion}'
        if col in df.columns:
            z_data.append(df[col].values)

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=df['time_window'].values,
        y=emotion_labels,
        colorscale='RdYlBu_r',
        showscale=True,
    ))

    fig.update_layout(
        template='plotly_white',
        height=280,
        font=dict(size=11),
        margin=dict(t=10, b=30, l=60, r=40),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="emotion_heat")


def create_narrative_area(narrative_evo: pl.DataFrame) -> str:
    """叙事堆叠面积图"""
    df = narrative_evo.to_pandas()
    narratives = ['political_violence', 'consequences', 'polarization', 'free_speech', 'conspiracy', 'memorial']
    colors = [COLORS['blue'], COLORS['orange'], COLORS['green'], COLORS['red'], COLORS['yellow'], COLORS['purple']]

    fig = go.Figure()

    for idx, narrative in enumerate(narratives):
        narrative_data = df[df['primary_narrative'] == narrative]
        if not narrative_data.empty:
            fig.add_trace(go.Scatter(
                x=narrative_data['time_window'],
                y=narrative_data['count'],
                name=NARRATIVE_CN[narrative],
                fill='tonexty',
                line=dict(color=colors[idx], width=0),
                stackgroup='one',
            ))

    fig.update_layout(
        template='plotly_white',
        height=280,
        font=dict(size=11),
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(title='推文数', showgrid=True, gridcolor='#E5E5E5'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=30, b=30, l=50, r=10),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="narrative_area")


def create_dual_axis(hourly_df: pl.DataFrame) -> str:
    """推文量与情感双轴"""
    df = hourly_df.to_pandas()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=df['hour'], y=df['tweet_count'], name='推文量', marker_color=COLORS['blue'], opacity=0.5),
        secondary_y=False
    )

    if 'avg_sadness' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['hour'], y=df['avg_sadness'], name='悲伤', line=dict(color=COLORS['red'], width=2.5), mode='lines+markers'),
            secondary_y=True
        )

    fig.update_xaxes(title_text="", showgrid=False)
    fig.update_yaxes(title_text="推文数", secondary_y=False, showgrid=True, gridcolor='#E5E5E5')
    fig.update_yaxes(title_text="情感强度", secondary_y=True, showgrid=False)

    fig.update_layout(
        template='plotly_white',
        height=280,
        font=dict(size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=30, b=30, l=50, r=50),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="dual_axis")


def create_stance_radar(content_df: pl.DataFrame) -> str:
    """立场情感雷达图"""
    stance_emotion = content_df.group_by('political_stance').agg([
        pl.col('emotion_sadness').mean().alias('sadness'),
        pl.col('emotion_anger').mean().alias('anger'),
        pl.col('emotion_fear').mean().alias('fear'),
        pl.col('emotion_surprise').mean().alias('surprise'),
        pl.col('emotion_joy').mean().alias('joy'),
        pl.col('emotion_love').mean().alias('love'),
    ]).to_pandas()

    fig = go.Figure()

    emotions = ['sadness', 'anger', 'fear', 'surprise', 'joy', 'love']
    emotion_labels = [EMOTION_CN[e] for e in emotions]

    for _, row in stance_emotion.iterrows():
        stance = row['political_stance']
        if stance in ['conservative', 'liberal']:
            values = [row[e] for e in emotions] + [row[emotions[0]]]
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=emotion_labels + [emotion_labels[0]],
                fill='toself',
                name=STANCE_CN[stance],
                line=dict(width=2),
                opacity=0.6
            ))

    fig.update_layout(
        template='plotly_white',
        polar=dict(radialaxis=dict(visible=True, range=[0, 0.5]), bgcolor='#F9FAFB'),
        height=280,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        margin=dict(t=30, b=50, l=50, r=50),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="stance_radar")


def create_narrative_bar_comparison(content_df: pl.DataFrame) -> str:
    """叙事立场对比图"""
    matrix = content_df.group_by(['political_stance', 'primary_narrative']).agg(pl.len().alias('count')).to_pandas()

    fig = go.Figure()

    stances = ['conservative', 'liberal']
    narratives = ['political_violence', 'memorial', 'consequences']

    for stance in stances:
        counts = []
        for narrative in narratives:
            val = matrix[(matrix['political_stance'] == stance) & (matrix['primary_narrative'] == narrative)]
            counts.append(val['count'].values[0] if not val.empty else 0)

        fig.add_trace(go.Bar(
            name=STANCE_CN[stance],
            x=[NARRATIVE_CN[n] for n in narratives],
            y=counts,
            marker_color=COLORS['red'] if stance == 'conservative' else COLORS['blue']
        ))

    fig.update_layout(
        template='plotly_white',
        barmode='group',
        height=280,
        font=dict(size=11),
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(title='推文数', showgrid=True, gridcolor='#E5E5E5'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=30, b=30, l=50, r=10),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="narrative_comparison")


def create_engagement_scatter(content_df: pl.DataFrame) -> str:
    """互动量散点图"""
    df = content_df.to_pandas().head(500)

    fig = go.Figure(data=go.Scatter(
        x=df['likeCount'],
        y=df['retweetCount'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['emotion_sadness'],
            colorscale='RdYlBu_r',
            showscale=True,
            colorbar=dict(title="悲伤强度"),
            opacity=0.6
        ),
        text=df['primary_narrative'].apply(lambda x: NARRATIVE_CN.get(x, x)),
        hovertemplate='<b>%{text}</b><br>点赞: %{x}<br>转发: %{y}<extra></extra>'
    ))

    fig.update_layout(
        template='plotly_white',
        height=280,
        font=dict(size=11),
        xaxis=dict(title='点赞数', type='log', showgrid=True, gridcolor='#E5E5E5'),
        yaxis=dict(title='转发数', type='log', showgrid=True, gridcolor='#E5E5E5'),
        margin=dict(t=10, b=40, l=50, r=60),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="engagement_scatter")


def create_stance_improvement_bar(content_df: pl.DataFrame) -> str:
    """【优化新增】立场分类改进对比图"""
    # 如果有author_stance_prelabel，计算改进效果
    if 'author_stance_prelabel' not in content_df.columns:
        return ""

    # 统计有bio立场的作者推文分布
    with_bio = content_df.filter(pl.col('author_stance_prelabel') != 'neutral')

    # 对比bio预标注 vs 最终立场
    bio_dist = with_bio.group_by('author_stance_prelabel').agg(pl.len().alias('count')).to_pandas()
    final_dist = with_bio.group_by('political_stance').agg(pl.len().alias('count')).to_pandas()

    fig = go.Figure()

    stances = ['conservative', 'liberal', 'neutral']
    for idx, (df, name) in enumerate([(bio_dist, 'Bio预标注'), (final_dist, '混合分类')]):
        counts = [df[df.iloc[:, 0] == s]['count'].values[0] if len(df[df.iloc[:, 0] == s]) > 0 else 0 for s in stances]
        fig.add_trace(go.Bar(
            name=name,
            x=[STANCE_CN[s] for s in stances],
            y=counts,
            text=counts,
            textposition='outside',
            marker_color=COLORS['gray'] if idx == 0 else COLORS['blue']
        ))

    fig.update_layout(
        template='plotly_white',
        barmode='group',
        height=280,
        font=dict(size=11),
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(title='推文数', showgrid=True, gridcolor='#E5E5E5'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=30, b=30, l=50, r=10),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="stance_improvement")


def create_author_influence_stance(author_prof: pl.DataFrame) -> str:
    """【优化新增】影响力分层立场分布"""
    if author_prof is None:
        return ""

    df = author_prof.to_pandas()

    # 【修复】使用实际数据中的分层值
    tiers = ['Mega (1M+)', 'High (100K-1M)', 'Medium (10K-100K)']
    stances = ['conservative', 'liberal', 'neutral']

    fig = go.Figure()

    for stance in stances:
        counts = []
        for tier in tiers:
            val = df[(df['influence_tier'] == tier) & (df['bio_stance'] == stance)]
            counts.append(len(val) if not val.empty else 0)

        fig.add_trace(go.Bar(
            name=STANCE_CN[stance],
            x=tiers,
            y=counts,
            marker_color=COLORS['red'] if stance == 'conservative' else (COLORS['blue'] if stance == 'liberal' else COLORS['gray'])
        ))

    fig.update_layout(
        template='plotly_white',
        barmode='stack',
        height=280,
        font=dict(size=11),
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(title='作者数', showgrid=True, gridcolor='#E5E5E5'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=30, b=30, l=50, r=10),
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="influence_stance")


def create_top_influencers_table(top_50: pl.DataFrame) -> str:
    """【优化新增】Top 10影响力作者表格 - 使用 Plotly Table"""
    if top_50 is None:
        return ""

    df = top_50.head(10).to_pandas()

    # 准备表格数据
    ranks = [f"#{i+1}" for i in range(len(df))]
    author_ids = [f"用户{str(row['pseudo_author_userName'])[:12]}" for _, row in df.iterrows()]
    followers = [f"{row['followers']:,}" for _, row in df.iterrows()]
    tweet_counts = [str(row['tweet_count']) for _, row in df.iterrows()]
    bio_stances = [STANCE_CN.get(row.get('bio_stance', 'neutral'), '中立') for _, row in df.iterrows()]
    tweet_stances = [STANCE_CN.get(row.get('tweet_stance_mode', 'neutral'), '中立') for _, row in df.iterrows()]
    consistencies = [row.get('stance_consistency', '-') for _, row in df.iterrows()]

    # 创建 Plotly 表格
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>排名</b>', '<b>作者ID</b>', '<b>Followers</b>', '<b>推文数</b>',
                    '<b>Bio立场</b>', '<b>推文立场</b>', '<b>一致性</b>'],
            fill_color=COLORS['blue'],
            align='center',
            font=dict(color='white', size=13, family='Arial'),
            height=35
        ),
        cells=dict(
            values=[ranks, author_ids, followers, tweet_counts, bio_stances, tweet_stances, consistencies],
            fill_color=[['#f9fafb', 'white'] * 5],  # 交替行颜色
            align=['center', 'left', 'right', 'right', 'center', 'center', 'center'],
            font=dict(color='#333', size=12, family='Arial'),
            height=30
        )
    )])

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=380,
    )

    return fig.to_html(include_plotlyjs='cdn', div_id="top_influencers_table")


def get_rep_tweets(content_df: pl.DataFrame) -> list[dict]:
    """获取代表性推文"""
    tweets = []
    narratives = ['political_violence', 'memorial', 'consequences']

    for narrative in narratives:
        top = content_df.filter(pl.col('primary_narrative') == narrative).sort(f'narrative_{narrative}', descending=True).head(1)
        if top.height > 0:
            row = top.to_dicts()[0]
            tweets.append({
                'narrative': NARRATIVE_CN[narrative],
                'text': row['text'][:150] + '...' if len(row['text']) > 150 else row['text'],
                'stance': STANCE_CN.get(row.get('political_stance', 'neutral'), '中立'),
            })
    return tweets


def tweet_card(tweet: dict) -> rx.Component:
    """推文卡片"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.badge(tweet['narrative'], color_scheme="blue", size="1"),
                rx.badge(tweet['stance'], color_scheme="gray", size="1", variant="outline"),
                spacing="2",
            ),
            rx.text(f'"{tweet["text"]}"', font_size="0.9em", color="#555", line_height="1.5", font_style="italic"),
            spacing="2",
            align_items="flex_start",
        ),
        padding="1em",
        background="white",
        border_left=f"3px solid {COLORS['blue']}",
        border_radius="4px",
        box_shadow="0 1px 2px rgba(0,0,0,0.08)",
        margin_bottom="0.8em",
    )


def report_page() -> rx.Component:
    """报告页面"""
    data = load_all_data()

    if "error" in data:
        return rx.center(
            rx.text(f"数据加载错误: {data['error']}", color="red.500", font_size="1.1em"),
            min_height="100vh",
            background="#F3F4F6",
        )

    # 生成图表
    emotion_line = create_emotion_line(data["emotion_evo"])
    narrative_pie = create_narrative_pie(data["content_df"])
    stance_bar = create_stance_bar(data["content_df"])
    hourly_bar = create_hourly_bar(data["hourly_df"])
    emotion_heat = create_emotion_heatmap(data["emotion_evo"])
    narrative_area = create_narrative_area(data["narrative_evo"])
    dual_axis = create_dual_axis(data["hourly_df"])
    stance_radar = create_stance_radar(data["content_df"])
    narrative_comparison = create_narrative_bar_comparison(data["content_df"])
    engagement_scatter = create_engagement_scatter(data["content_df"])

    # 【优化新增】作者画像相关图表
    stance_improvement = create_stance_improvement_bar(data["content_df"])
    influence_stance = create_author_influence_stance(data["author_prof"])
    top_influencers_table = create_top_influencers_table(data["top_50"])

    rep_tweets = get_rep_tweets(data["content_df"])

    return rx.box(
        rx.vstack(
            # ==================== 顶部标题栏 ====================
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Charlie Kirk 遇刺事件社交媒体舆论分析", size="8", color="#333333", font_weight="700"),
                        rx.text("2025 年 9 月 10 日遇刺事件后 72 小时公共（Twitter）话语演变研究", font_size="1.1em", color="#666666"),
                        rx.text(f"数据来源: Twitter/X | {data['date_range']} | NLP 情感分析", font_size="0.9em", color="#666666"),
                        spacing="1",
                        align_items="flex_start",
                    ),
                    spacing="4",
                    align_items="center",
                    width="100%",
                ),
                width="100%",
                padding="1.8em 2em",
                background="white",
                border_radius="6px",
                box_shadow="0 1px 3px rgba(0,0,0,0.1)",
                margin_bottom="1.5em",
            ),

            # ==================== KPI 卡片 ====================
            rx.grid(
                kpi_card("📊", "总推文数", f"{data['total_tweets']:,}", COLORS['blue']),
                kpi_card("🔍", "分析样本", f"{data['total_sampled']:,}", COLORS['orange']),
                kpi_card("⏱️", "时间跨度", "72 小时", COLORS['green']),
                kpi_card("❤️", "情感维度", "6 维", COLORS['red']),
                columns="4",
                spacing="3",
                width="100%",
                margin_bottom="1.5em",
            ),

            # ==================== 核心图表区（2x2 grid）====================
            rx.grid(
                chart_box("情感演变趋势", emotion_line),
                chart_box("叙事框架分布", narrative_pie),
                chart_box("政治立场分布", stance_bar),
                chart_box("小时级推文活跃度", hourly_bar),
                columns="2",
                spacing="3",
                width="100%",
                margin_bottom="1.5em",
            ),

            # ==================== 深度分析区（2x3 grid）====================
            rx.grid(
                chart_box("情感强度热力图", emotion_heat),
                chart_box("叙事时间演变", narrative_area),
                chart_box("推文量与情感双轴", dual_axis),
                chart_box("立场情感对比雷达", stance_radar),
                chart_box("叙事立场交叉对比", narrative_comparison),
                chart_box("互动量与情感分布", engagement_scatter),
                columns="2",
                spacing="3",
                width="100%",
                margin_bottom="1.5em",
            ),

            # ==================== 【优化新增】作者画像分析区 ====================
            rx.cond(
                data["author_prof"] is not None,
                rx.vstack(
                    # 图表区
                    rx.grid(
                        rx.cond(
                            stance_improvement != "",
                            chart_box("立场分类改进对比", stance_improvement),
                            rx.box(),
                        ),
                        rx.cond(
                            influence_stance != "",
                            chart_box("影响力分层立场分布", influence_stance),
                            rx.box(),
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                        margin_bottom="1.5em",
                    ),
                    spacing="0",
                    width="100%",
                ),
                rx.box(),
            ),

            # ==================== Top 50 作者 & 代表性推文（并排）====================
            rx.grid(
                # Top 10 高影响力作者
                rx.cond(
                    top_influencers_table != "",
                    chart_box("Top 10 高影响力作者", top_influencers_table),
                    rx.box(),
                ),
                # 代表性推文
                rx.box(
                    rx.vstack(
                        rx.text("代表性推文", font_size="1.2em", font_weight="600", color="#333", margin_bottom="0.8em"),
                        *[tweet_card(t) for t in rep_tweets],
                        spacing="0",
                        align_items="flex_start",
                    ),
                    padding="1.5em",
                    background="white",
                    border_radius="6px",
                    box_shadow="0 1px 3px rgba(0,0,0,0.1)",
                    width="100%",
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),

            spacing="0",
            width="100%",
            padding="1.5em",
        ),
        background="#F9F9F9",
        min_height="100vh",
        width="100%",
    )
