"""
ETL (Extract, Transform, Load) Module

数据加工管道:
- io: 数据 I/O 层 (读取、写入、流式处理)
- analysis: 核心分析变换 (时间序列、网络分析、特征工程)
- profiling: 数据质量分析 (缺失值、重复值、分布统计)
"""

from . import io, analysis, profiling

__all__ = ["io", "analysis", "profiling"]
