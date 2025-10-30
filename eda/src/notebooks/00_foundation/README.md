# 00 Foundation - 基础数据准备

## 目的
为所有后续分析提供统一的数据基础。

## 包含文件

### 00_data_intake.ipynb
**核心功能**：
- 加载原始 CSV 数据（tweets + authors）
- 类型规范化（布尔列、时间列）
- **事件时间字段构建**（关键！）
  - `event_time_delta_hours`: 距枪击事件的小时数
  - `time_window`: 事件后时段标签（0-6h, 6-12h, 12-24h, 24-48h, 48-72h）
- 合并作者元数据
- 输出 `tweets_enriched.parquet`

## 事件背景

**Charlie Kirk 暗杀事件**
- 时间：2025年9月10日（推断为 UTC 20:00）
- 地点：犹他州立大学演讲现场
- 受害者：Charlie Kirk（Turning Point USA 创始人，保守派政治活动家）
- 嫌犯：Tyler James Robinson, 22岁，政治动机谋杀

**数据时间窗口**：
- 2025-09-11 23:55 至 2025-09-13 00:12
- 涵盖暗杀事件后 **48-72 小时**的社交媒体反应

## 输出数据

**文件**: `../parquet/tweets_enriched.parquet`

**关键字段**:
- 所有原始推文字段
- 所有作者元数据字段
- `event_time_delta_hours` (Float): 距枪击的小时数
- `time_window` (String): 时段标签

## 使用说明

这个 notebook 必须**最先运行**，所有其他分析都依赖它生成的 `tweets_enriched.parquet`。

```python
# 在 Docker Jupyter 中运行
# 1. 打开 00_data_intake.ipynb
# 2. Run All Cells
# 3. 确认生成 ../parquet/tweets_enriched.parquet
```

## 依赖的两个分析方向

运行本 notebook 后，可以选择：

1. **内容研究分析** (`content_research/`) - **推荐，核心研究方向**
   - 情感、叙事、立场的深度分析
   - 专注于暗杀事件后的公共话语演变

2. **技术指标分析** (`legacy_technical_analysis/`) - 早期探索，已归档
   - 网络结构、话题模型等技术分析
   - 保留用于参考
