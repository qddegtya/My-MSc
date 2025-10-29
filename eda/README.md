# Charlie Kirk Twitter Data EDA

> 全栈数据分析项目：从原始推文数据到交互式可视化仪表板

## 项目概览

本项目对 Charlie Kirk 的 Twitter 数据集进行探索性数据分析（EDA），涵盖：
- 📊 **508,954 条推文** 分析
- 👥 **4,242 位用户** 互动网络
- ⏱️ **3天时间窗口** (Sep 11-13, 2025)
- 🔵 **蓝标认证效应** 深度研究

### 核心发现

1. **时间序列异常**: 9月12日推文量暴增 **326倍** (1,542 → 503,057)
2. **蓝标优势**: 蓝标用户词数 **+58%**，互动放大 **+1200%**
3. **网络结构**: 21.3万边，19万节点，典型幂律分布（富者愈富）
4. **主题建模**: 49个主题，BERTopic 语义聚类

## 快速开始

### 方式 1: Docker 部署（推荐）
./
```bash
# 构建镜像
./scripts/build.sh

# 启动完整服务（Jupyter + Dashboard）
docker-compose up eda

# 访问地址
# Jupyter Lab: http://localhost:8888
# Dashboard: http://localhost:8700
```

### 方式 2: 本地开发

```bash
# 安装依赖
pip install -r config/requirements.txt
python -m spacy download en_core_web_md

# 启动 Jupyter
jupyter lab

# 启动 Dashboard
cd src/app && reflex run
```

## 项目结构

```
eda/
├── __data/           # 原始数据
├── config/           # 配置文件
├── scripts/          # 构建与启动脚本
└── src/              # 所有源码
    ├── app/          # Reflex Web 应用
    │   ├── assets/   # 静态资源
    │   └── pages/    # 页面模块
    ├── notebooks/    # Jupyter 分析笔记本
    │   └── parquet/  # 缓存数据
    └── packages/     # Python 包
        └── etl/      # ETL 数据加工
```

详细结构见 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

## 使用流程

### 1. 数据准备

确保原始数据在 `__data/charlie-kirk-twitter-dataset/`:
- `tweets.csv`: 推文数据
- `authors.csv`: 作者元数据

### 2. 运行分析笔记本（按顺序）

```bash
jupyter lab

# 在 notebooks/ 目录下依次运行：
# 00_data_intake.ipynb         → 生成 tweets_enriched.parquet
# 01_temporal_dynamics.ipynb   → 时间序列分析
# 02_network_intelligence.ipynb → 网络结构分析
# 03_content_semantics.ipynb   → 内容语义分析
```

### 3. 启动可视化仪表板

```bash
cd src/app
reflex run

# 访问 http://localhost:8700
```

## Dashboard 功能

### 📊 Executive Dashboard
- 6个核心 KPI 指标
- 推文量趋势可视化
- 蓝标 vs 非蓝标雷达对比
- 语言分布分析

### 📈 Temporal Dynamics
- 时间序列双轴面积图
- 小时级活动热力图
- 互动量散点分析

### 🕸️ Network Intelligence
- 度分布对数图（幂律验证）
- Top 20 影响力节点
- 中心性分布统计

### 📝 Content Semantics
- 蓝标语言策略对比
- 主题互动效能分析
- Top 20 主题分布

## 技术栈

**数据处理**
- Polars (高性能 DataFrame)
- Pandas (数据转换)
- DuckDB (SQL 分析)

**可视化**
- Plotly (交互式图表)
- Reflex (Web 框架)

**分析工具**
- NetworkX (网络分析)
- BERTopic (主题建模)
- spaCy (NLP 处理)

**开发工具**
- Docker (容器化)
- uv (快速包管理)
- Jupyter Lab

## 文档

- [DOCKER.md](./DOCKER.md) - Docker 部署详细说明
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 完整目录结构

## 依赖管理

所有依赖定义在 `config/requirements.txt`，使用 **uv** 作为包管理器（速度提升 10-100x）：

```bash
# 使用 uv 安装依赖
uv pip install -r config/requirements.txt

# 或使用传统 pip
pip install -r config/requirements.txt
```

## 数据流

```
Raw CSV (__data/)
    ↓
src/packages/etl/ (ETL 模块)
    ↓
src/notebooks/ (分析笔记本)
    ↓
src/notebooks/parquet/ (缓存)
    ↓
src/app/ (Reflex Dashboard)
    ↓
Browser (localhost:8700)
```

## 许可证

MIT License
