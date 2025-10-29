# Notebooks 使用说明

## 重要：路径配置

由于项目重构，notebooks 现在位于 `src/notebooks/` 目录下。

### 方式 1: 使用 init.py（推荐）

在每个 notebook 的**第一个代码单元格**添加：

```python
import init  # 自动配置项目路径
from src import io, analysis, profiling
```

### 方式 2: 手动配置路径

如果不想使用 init.py，可以手动添加：

```python
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path.cwd().parent.parent))

from src import io, analysis, profiling
```

### 方式 3: 从项目根目录启动（最简单）

如果你从项目根目录启动 Jupyter Lab：

```bash
# 在项目根目录 (eda/) 执行
jupyter lab
```

那么可以直接使用：

```python
from src import io, analysis, profiling
```

## 数据路径

所有数据路径已自动配置：

- **原始数据**: `__data/charlie-kirk-twitter-dataset/`
- **缓存数据**: `src/notebooks/parquet/`

模块 `src.packages.etl.io` 中的常量已自动处理路径解析。

## 执行顺序

必须按顺序运行：

1. **00_data_intake.ipynb** - 生成 `parquet/tweets_enriched.parquet`
2. **01_temporal_dynamics.ipynb** - 时间序列分析
3. **02_network_intelligence.ipynb** - 网络结构分析
4. **03_content_semantics.ipynb** - 内容语义分析

## Docker 环境

在 Docker 容器中，路径已自动配置，无需额外设置：

```bash
docker-compose up jupyter
# 访问 http://localhost:8888
```
