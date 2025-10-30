# Notebooks - Charlie Kirk 暗杀事件社交媒体分析

## 🎯 研究主题

**Charlie Kirk 政治暗杀事件后 72 小时的社交媒体舆论演变研究**

这不是简单的 Twitter 数据分析，而是一个**政治传播学研究**，专注于分析推文**内容**（情感、叙事、立场），而非技术指标。

## 📋 项目结构

```
notebooks/
├── README.md                          (本文件)
├── parquet/                           (数据缓存目录)
│
├── 00_foundation/                     (基础数据准备)
│   ├── README.md
│   └── 00_data_intake.ipynb          ✅ 必须最先运行
│
├── content_research/                  (核心研究方向 ⭐)
│   ├── README.md
│   ├── 01_content_semantics.ipynb    (情感+叙事+立场分析)
│   └── 02_temporal_evolution.ipynb   (小时级演变追踪)
│
└── legacy_technical_analysis/         (早期技术分析，已归档)
    ├── README.md
    └── 02_network_intelligence.ipynb  (网络结构分析)
```

## 🚀 快速开始

### 执行顺序（必须按顺序）

**Step 1: 基础数据准备**
```bash
# 打开 Jupyter Lab (Docker 或本地)
jupyter lab

# 运行基础 notebook
00_foundation/00_data_intake.ipynb
```
**输出**：`parquet/tweets_enriched.parquet`（包含事件时间字段）

**Step 2: 内容研究分析（核心）**
```bash
# 内容语义分析
content_research/01_content_semantics.ipynb

# 时间演变分析
content_research/02_temporal_evolution.ipynb
```
**输出**：
- `content_analysis.parquet` - 情感、叙事、立场数据
- `emotion_evolution.parquet` - 情感演变
- `narrative_evolution.parquet` - 叙事演变
- `representative_tweets.parquet` - 代表性推文
- `tweets_hourly.parquet` - 小时级时间序列
- `narrative_hourly.parquet` - 叙事小时分布

**Step 3: 可视化展示**
```bash
# 启动 Reflex Dashboard
cd ../../app/eda
reflex run
```
访问 http://localhost:8700 查看完整分析报告。

## 📊 研究背景

### 事件概要
- **时间**：2025年9月10日（UTC 20:00 推断）
- **地点**：犹他州立大学演讲现场
- **受害者**：Charlie Kirk（Turning Point USA 创始人，保守派政治活动家）
- **嫌犯**：Tyler James Robinson, 22岁，政治动机谋杀

### 数据集
- **推文数量**：108万+
- **时间窗口**：2025-09-11 23:55 至 2025-09-13 00:12（事件后 48-72 小时）
- **采样策略**：按时间窗口分层采样 10,000 条用于深度分析
- **语言**：英文

## 🔬 核心分析维度

### 1. 多维度情感分析
使用 HuggingFace transformers 进行 6 维情感分类：
- 😢 Sadness (悲伤)
- 😡 Anger (愤怒)
- 😨 Fear (恐惧)
- 😲 Surprise (惊讶)
- 😊 Joy (喜悦)
- ❤️ Love (爱)

### 2. 叙事框架识别
基于语义相似度识别 6 种核心叙事：
1. **Political Violence** - 政治暴力受害者叙事
2. **Consequences** - 言论后果反思叙事
3. **Polarization** - 政治极化担忧叙事
4. **Free Speech** - 言论自由捍卫叙事
5. **Conspiracy** - 阴谋论怀疑叙事
6. **Memorial** - 纪念与遗产叙事

### 3. 政治立场检测
- Conservative (保守派)
- Liberal (自由派)
- Neutral (中立)

### 4. 时间演变追踪
- **小时级粒度**（不是日级！）
- 追踪 72 小时内情感和叙事的快速变化
- 识别关键时间节点（震惊期、悲伤期、政治化期）

## 🛠️ 技术栈

- **数据处理**：Polars (LazyFrame, 高效内存管理)
- **情感分析**：HuggingFace transformers (`j-hartmann/emotion-english-distilroberta-base`)
- **语义理解**：sentence-transformers (`all-MiniLM-L6-v2`)
- **相似度计算**：scikit-learn (cosine similarity)
- **可视化**：Plotly (dark theme)
- **Web 框架**：Reflex

## 📁 数据文件说明

### 基础数据
- `tweets_enriched.parquet` (58MB) - 完整推文 + 作者元数据 + 事件时间字段

### 内容分析数据
- `content_analysis.parquet` (371KB) - 10K 采样推文的完整分析
- `emotion_evolution.parquet` (2.7KB) - 5个时间窗口的情感统计
- `narrative_evolution.parquet` (1.3KB) - 5个时间窗口的叙事分布
- `representative_tweets.parquet` - 每种叙事的代表性推文

### 时间序列数据
- `tweets_hourly.parquet` - 小时级推文量 + 情感得分
- `narrative_hourly.parquet` - 小时级叙事分布

### Legacy 数据（归档）
- `network_centrality.parquet` - 网络中心性数据
- `network_edges.parquet` - 网络边关系
- `tweets_daily.parquet` - 日级统计（已被小时级替代）

## 🔑 关键字段说明

### 事件时间字段（来自 00_data_intake）
- `event_time_delta_hours` (Float) - 距枪击事件的小时数
- `time_window` (String) - 时段标签
  - `0-6h` - 初始震惊期
  - `6-12h` - 悲伤扩散期
  - `12-24h` - 情感发酵期
  - `24-48h` - 政治化转变期
  - `48-72h` - 反思与叙事固化期

### 情感字段（来自 01_content_semantics）
- `emotion_sadness` - 悲伤强度 (0-1)
- `emotion_anger` - 愤怒强度 (0-1)
- `emotion_fear` - 恐惧强度 (0-1)
- `emotion_surprise` - 惊讶强度 (0-1)
- `emotion_joy` - 喜悦强度 (0-1)
- `emotion_love` - 爱意强度 (0-1)
- `primary_emotion` - 主导情感

### 叙事字段
- `narrative_political_violence` - 政治暴力叙事得分
- `narrative_consequences` - 言论后果叙事得分
- `narrative_polarization` - 政治极化叙事得分
- `narrative_free_speech` - 言论自由叙事得分
- `narrative_conspiracy` - 阴谋论叙事得分
- `narrative_memorial` - 纪念叙事得分
- `primary_narrative` - 主导叙事
- `narrative_confidence` - 叙事置信度

### 立场字段
- `political_stance` - 政治立场 (conservative/liberal/neutral)

## 🎓 研究问题

本研究试图回答：

1. **情感轨迹**：从震惊到悲伤到愤怒到政治化，情感如何演变？
2. **叙事竞争**："受害者"叙事 vs "后果"叙事，谁占上风？
3. **政治鸿沟**：保守派和自由派的情感与叙事差异有多大？
4. **舆论操纵**：是否有组织化的叙事推动？
5. **社会撕裂**：这个事件加剧了美国社会撕裂还是短暂团结？
6. **暴力的回响**：人们对政治暴力的态度是谴责还是理解？

## 💡 与早期分析的区别

| 维度 | 早期技术分析 (Legacy) | 当前内容研究 (Core) |
|------|---------------------|-------------------|
| **研究重点** | Twitter 技术指标 | 推文内容语义 |
| **关键指标** | 网络结构、蓝标用户 | 情感、叙事、立场 |
| **时间粒度** | 日级 | 小时级 |
| **分析方法** | 网络分析、统计描述 | NLP、语义理解 |
| **研究价值** | 技术探索 | 政治传播学洞察 |

## 🐳 Docker 环境

```bash
# 启动 Jupyter Lab (端口 8888)
docker-compose up jupyter

# 访问
http://localhost:8888
# 无需 token，已配置免密登录
```

## 📚 参考文档

- `00_foundation/README.md` - 基础数据准备说明
- `content_research/README.md` - 内容研究详细说明
- `legacy_technical_analysis/README.md` - 早期分析归档说明
- `../../RESEARCH_REDESIGN.md` - 研究框架重构方案

## 🤝 后续工作

所有分析结果最终汇总到 **Reflex Dashboard**，展示：
- 研究背景与事件时间线
- 情感演变可视化（6大情感 x 72小时）
- 叙事框架分析图表
- 政治立场对比
- 代表性推文展示

---

**核心研究方向**: `content_research/`
**当前状态**: ETL 完成，Dashboard 开发中
