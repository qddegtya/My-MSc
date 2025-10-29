"""
EDA Project Source Code

包含:
- app: Reflex Web 应用
- notebooks: Jupyter 分析笔记本
- packages: Python 包集合
  - etl: ETL 数据加工模块
"""

from .packages.etl import io, profiling, analysis  # noqa: F401

__all__ = ["io", "profiling", "analysis"]

