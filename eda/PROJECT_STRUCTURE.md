# 项目结构说明

## 目录结构

```
eda/
├── __data/                          # 原始数据目录
│   └── charlie-kirk-twitter-dataset/
│       ├── tweets.csv
│       └── authors.csv
│
├── app/                             # Reflex Web 应用
│   ├── app.py                       # 应用入口
│   ├── rxconfig.py                  # Reflex 配置
│   └── pages/                       # 页面模块
│       ├── executive.py             # Executive Dashboard (总览)
│       ├── temporal.py              # Temporal Dynamics (时间序列)
│       ├── network.py               # Network Intelligence (网络分析)
│       └── content.py               # Content Semantics (内容语义)
│
├── config/                          # 配置文件
│   ├── requirements.txt             # Python 依赖列表
│   └── jupyter_server_config.py     # Jupyter Lab 配置
│
├── notebooks/                       # Jupyter 笔记本（按顺序执行）
│   ├── 00_data_intake.ipynb         # 数据摄入与预处理
│   ├── 01_temporal_dynamics.ipynb   # 时间序列分析
│   ├── 02_network_intelligence.ipynb # 网络结构分析
│   ├── 03_content_semantics.ipynb   # 内容语义分析
│   └── parquet/                     # 缓存的 Parquet 数据
│       ├── tweets_enriched.parquet
│       ├── tweets_daily.parquet
│       ├── network_edges.parquet
│       ├── network_centrality.parquet
│       ├── content_analysis.parquet
│       ├── verified_comparison.parquet
│       └── topic_distribution.parquet
│
├── scripts/                         # 构建与启动脚本
│   ├── build.sh                     # Docker 镜像构建脚本
│   └── entrypoint.sh                # Docker 容器启动脚本
│
├── src/                             # 源代码包
│   ├── __init__.py                  # 包初始化
│   └── etl/                         # ETL 数据加工模块
│       ├── __init__.py
│       ├── io.py                    # 数据 I/O (读取/写入/流式)
│       ├── analysis.py              # 核心分析变换
│       └── profiling.py             # 数据质量分析
│
├── Dockerfile                       # Docker 镜像定义
├── docker-compose.yml               # Docker Compose 服务编排
├── .dockerignore                    # Docker 构建排除规则
├── CLAUDE.md                        # Claude Code 项目指南
├── DOCKER.md                        # Docker 部署文档
├── README.md                        # 项目主文档
└── PROJECT_STRUCTURE.md             # 本文件
```

## 核心模块说明

### 1. 数据处理层 (`src/etl/`)

**ETL Pipeline - Extract, Transform, Load**

- **`io.py`**: 数据 I/O 层
  - `scan_raw_tweets()`: 懒加载 CSV
  - `read_well_known_authors()`: 加载作者元数据
  - `materialize_parquet()`: Parquet 缓存
  - `iter_batches()`: 流式批处理

- **`analysis.py`**: 核心分析变换
  - `TimeSeriesProfile`: 时间序列分析类
  - `build_time_series()`: 时间聚合
  - `prepare_network_projection()`: 网络构建
  - `enrich_with_authors()`: 作者数据关联

- **`profiling.py`**: 数据质量分析
  - `missingness_summary()`: 缺失值分析
  - `duplicate_check()`: 重复检查
  - `engagement_distribution()`: 互动统计

### 2. 分析层 (`notebooks/`)

**必须按顺序执行 (00 → 01 → 02 → 03)**

1. **00_data_intake.ipynb**: 数据摄入
   - 读取原始 CSV
   - 类型转换与规范化
   - 作者数据关联
   - 生成 `tweets_enriched.parquet`

2. **01_temporal_dynamics.ipynb**: 时间序列分析
   - 每日/小时级聚合
   - 异常检测（326x 增长）
   - 生成 `tweets_daily.parquet`

3. **02_network_intelligence.ipynb**: 网络分析
   - 回复关系网络构建
   - 度中心性计算
   - 幂律分布验证
   - 生成 `network_edges.parquet`, `network_centrality.parquet`

4. **03_content_semantics.ipynb**: 内容语义分析
   - BERTopic 主题建模
   - 蓝标 vs 非蓝标对比
   - 生成 `content_analysis.parquet`, `verified_comparison.parquet`, `topic_distribution.parquet`

### 3. 可视化层 (`app/`)

**Reflex Web Dashboard - 交互式数据可视化**

- **Executive Dashboard** (`executive.py`):
  - 6 个 KPI 卡片
  - 推文量趋势图
  - 蓝标雷达对比图
  - 语言分布饼图

- **Temporal Dynamics** (`temporal.py`):
  - 时间序列双轴面积图（推文量 + 互动量）
  - 小时级活动热力图
  - 蓝标 vs 非蓝标散点图

- **Network Intelligence** (`network.py`):
  - 度分布对数图（幂律分布）
  - Top 20 影响力节点排行
  - 中心性分布直方图

- **Content Semantics** (`content.py`):
  - 蓝标对比分组柱状图
  - 主题互动散点图（词数 vs 互动，气泡大小 = 推文数）
  - Top 20 主题分布

## 数据流

```
原始 CSV (__data/)
    ↓
[00_data_intake.ipynb]
    ↓
tweets_enriched.parquet (notebooks/parquet/)
    ↓
[01/02/03 notebooks] ←── src/etl/* (ETL 模块)
    ↓
specialized parquets (daily, network, content, etc.)
    ↓
[Reflex Dashboard (app/)] ←── Plotly 可视化
    ↓
浏览器访问 (localhost:8700)
```

## 技术栈

- **数据处理**: Polars (LazyFrame), Pandas, DuckDB
- **可视化**: Plotly (graph_objects + express)
- **网络分析**: NetworkX
- **NLP**: BERTopic, spaCy, sentence-transformers
- **机器学习**: scikit-learn, UMAP
- **Web 框架**: Reflex
- **开发工具**: Jupyter Lab, Docker, uv (包管理)

## 部署方式

### 本地开发

```bash
# 启动 Reflex Dashboard
cd app && reflex run

# 启动 Jupyter Lab
jupyter lab
```

### Docker 部署

```bash
# 构建镜像
./scripts/build.sh

# 方式 A: 仅 Jupyter
docker-compose up jupyter

# 方式 B: 仅 Dashboard
docker-compose up dashboard

# 方式 C: 全部服务
docker-compose up eda
```

详见 `DOCKER.md` 文档。
