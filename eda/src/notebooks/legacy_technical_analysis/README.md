# Legacy Technical Analysis - 早期技术指标分析（归档）

## 说明

这个目录包含**早期探索阶段**的技术指标分析 notebooks。

这些分析关注的是 Twitter 平台的**技术特征**（时间序列统计、网络结构、话题模型），而非推文**内容语义**。

## 为何归档？

在深入理解数据背景后，我们发现：

- **研究重点变化**：从 Twitter 技术分析 → 政治暗杀事件内容研究
- **分析维度变化**：从网络结构、蓝标用户、统计指标 → 情感、叙事、政治立场
- **时间粒度变化**：从日级分析 → 小时级演变追踪
- **方法变化**：从统计描述 → 深度NLP语义理解

**新的核心研究方向**在 `content_research/` 目录下。

## 保留原因

1. **技术完整性**：代码和方法仍然有效，可供参考
2. **对比价值**：展示研究方向的演进过程
3. **可复用性**：这些分析方法可应用于其他项目
4. **历史记录**：保留完整的探索历程

## 包含文件

### 01_temporal_dynamics.ipynb（旧版本）
**分析内容**：
- 日级推文量时间序列
- 滚动平均和异常检测
- 推文量与互动量的双轴图表

**技术栈**：
- Polars 数据聚合
- 简单统计分析

**输出文件**：
- `tweets_daily.parquet` - 日级统计数据
- `tweets_rolling.parquet` - 滚动窗口数据
- `tweets_anomalies.parquet` - 异常检测结果

**局限性**：
- 日级粒度太粗，无法捕捉事件后的快速情感变化
- 仅统计推文数量，未分析内容
- 缺少事件时间字段

**新版本**：`content_research/02_temporal_evolution.ipynb`
- 小时级粒度（72小时详细追踪）
- 包含6大情感的演变分析
- 叙事框架的时间分布

---

### 02_network_analysis.ipynb
**分析内容**：
- 构建推文互动网络（转发、回复关系）
- 计算网络中心性指标（度中心性、介数中心性、接近中心性）
- 网络度分布分析
- 识别关键意见领袖（KOL）

**技术栈**：
- NetworkX 图论分析
- 中心性算法

**输出文件**：
- `network_centrality.parquet` - 节点中心性数据
- `network_edges.parquet` - 边关系数据

**局限性**：
- 仅分析网络结构，未涉及内容语义
- 未区分不同政治立场的网络社区
- 缺少叙事传播路径分析
- KOL影响力分析未结合其推文内容

**潜在改进**：
如果未来需要分析**叙事传播网络**，可以结合：
- 本 notebook 的网络分析方法
- `content_research/` 的叙事识别结果
- 追踪不同叙事框架如何在网络中传播

---

### 03_content_semantics.ipynb（旧版本）
**分析内容**：
- BERTopic 话题建模
- 基础情感分析（正负面）
- 可读性和文本统计
- 蓝标 vs 非蓝标用户对比

**技术栈**：
- BERTopic (主题提取)
- TextBlob (基础情感)
- textstat (可读性指标)

**输出文件**：
- `topic_distribution.parquet` - 话题分布
- `verified_comparison.parquet` - 蓝标对比数据

**局限性**：
- 话题建模是无监督的，缺少针对性的叙事框架
- 情感分析仅分正负面，太粗糙
- 未检测政治立场
- 关注蓝标用户而非内容本身

**新版本**：`content_research/01_content_semantics.ipynb`
- **6维情感分析**（sadness, anger, fear, surprise, joy, love）
- **6种叙事框架**（基于语义相似度，而非无监督话题）
- **政治立场检测**（conservative, liberal, neutral）
- **代表性推文提取**（每种叙事的典型案例）
- 完全聚焦于**暗杀事件相关内容**

---

## 使用说明

这些 notebooks **可以运行**，但**不是当前研究的核心**。

### 如果你想运行
1. 确保已运行 `00_foundation/00_data_intake.ipynb`
2. 打开相应 notebook
3. 结果仅供参考，**不会**用于最终 Dashboard

### 路径说明
这些旧版本 notebooks 的路径可能还是 `parquet/`，需要改为 `../parquet/` 才能正常运行。

## 技术分析 vs 内容研究对比

| 维度 | Legacy 技术分析 | Content 内容研究 |
|------|---------------|-----------------|
| **研究重点** | Twitter 技术指标 | 推文内容语义 |
| **关键指标** | 网络结构、蓝标用户、推文量 | 情感、叙事、立场 |
| **时间粒度** | 日级（3个数据点） | 小时级（72个数据点） |
| **分析方法** | 统计描述、图论 | NLP、语义理解、情感分类 |
| **研究价值** | 技术探索 | 政治传播学洞察 |
| **事件关联** | 无事件时间字段 | 完整的事件时间框架 |

## 未来可能的应用

虽然这些分析已归档，但方法仍有价值：

- **网络社区检测**：识别保守派 vs 自由派的网络社区结构
- **叙事传播分析**：结合 02_network 和 content_research 的叙事数据
- **KOL 立场分析**：分析关键意见领袖的政治立场和叙事倾向
- **时间对比研究**：对比暗杀事件前后的网络结构变化

## 数据文件清理建议

以下 parquet 文件是旧分析生成的，可以保留或删除：

**可以删除**（已被新分析替代）：
- `tweets_daily.parquet` - 被 `tweets_hourly.parquet` 替代
- `tweets_rolling.parquet` - 不再需要
- `tweets_anomalies.parquet` - 不再需要
- `verified_comparison.parquet` - 已被立场分析替代
- `topic_distribution.parquet` - 已被叙事框架替代

**可以保留**（如需网络分析）：
- `network_centrality.parquet`
- `network_edges.parquet`

---

**当前核心研究方向**: 请转向 `content_research/` 目录
**当前状态**: Legacy notebooks 已归档，仅供参考
