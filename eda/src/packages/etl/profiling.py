"""
数据质量与概况分析工具。
"""

from __future__ import annotations

from typing import Iterable

import polars as pl


def missingness_summary(df: pl.DataFrame, key_columns: Iterable[str]) -> pl.DataFrame:
    """
    统计各列缺失率与缺失计数。
    """
    total = df.height
    stats = []
    for col in df.columns:
        nulls = df[col].null_count()
        stats.append(
            {
                "column": col,
                "null_count": nulls,
                "null_ratio": nulls / total if total else 0.0,
                "is_key": col in key_columns,
            }
        )
    return pl.DataFrame(stats).sort("null_ratio", descending=True)


def duplicate_check(df: pl.DataFrame, subset: Iterable[str]) -> pl.DataFrame:
    """
    基于指定键检查是否存在重复行。
    """
    dupes = df.group_by(subset).count().filter(pl.col("count") > 1)
    return dupes.sort("count", descending=True)


def engagement_distribution(df: pl.DataFrame, engagement_cols: list[str]) -> pl.DataFrame:
    """
    计算互动指标的分布统计。
    """
    summaries = []
    for col in engagement_cols:
        if col not in df.columns:
            continue
        series = df[col].cast(pl.Float64)
        summaries.append(
            {
                "metric": col,
                "mean": series.mean(),
                "median": series.median(),
                "std": series.std(),
                "p95": series.quantile(0.95),
                "max": series.max(),
                "non_zero_ratio": (series > 0).sum() / df.height if df.height else 0.0,
            }
        )
    return pl.DataFrame(summaries)

