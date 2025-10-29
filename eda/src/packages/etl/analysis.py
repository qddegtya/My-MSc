"""
高级分析入口：时间序列、网络结构与语义建模的占位实现。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import polars as pl


@dataclass
class TimeSeriesProfile:
    """
    时间序列分析结果的结构化容器。
    """

    daily_counts: pl.DataFrame
    rolling_metrics: pl.DataFrame
    anomalies: pl.DataFrame


def build_time_series(df: pl.DataFrame, date_col: str, value_col: str) -> TimeSeriesProfile:
    """
    基于每日聚合构建时间序列指标。当前实现聚焦于骨架，后续在 Notebook 中扩展。
    """
    daily = (
        df.with_columns(pl.col(date_col).str.to_datetime(time_zone="UTC").dt.date().alias("event_date"))
        .group_by("event_date")
        .agg(pl.count().alias("tweet_count"), pl.col(value_col).sum().alias("total_engagement"))
        .sort("event_date")
    )

    rolling = (
        daily.sort("event_date")
        .with_columns(
            pl.col("tweet_count").rolling_mean(window_size=7).alias("tweet_count_ma7"),
            pl.col("total_engagement").rolling_mean(window_size=7).alias("engagement_ma7"),
        )
        .drop_nulls()
    )

    anomalies = rolling.filter(
        (pl.col("tweet_count") > pl.col("tweet_count_ma7") * 3)
        | (pl.col("total_engagement") > pl.col("engagement_ma7") * 3)
    )

    return TimeSeriesProfile(daily_counts=daily, rolling_metrics=rolling, anomalies=anomalies)


def prepare_network_projection(df: pl.DataFrame, source_col: str, target_col: str) -> pl.DataFrame:
    """
    构建回复/引用网络的边列表。保留基础权重供 NetworkX 等库使用。
    """
    edges = (
        df.drop_nulls(subset=[source_col, target_col])
        .group_by([source_col, target_col])
        .count()
        .rename({"count": "weight"})
        .filter(pl.col(source_col) != pl.col(target_col))
    )
    return edges


def normalize_boolean_columns(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    """
    将字符串形式的布尔列转换为 Polars Boolean。
    """
    cleaned = df.clone()
    for col in columns:
        if col not in cleaned.columns:
            continue
        cleaned = cleaned.with_columns(
            pl.when(pl.col(col).cast(pl.Utf8).str.to_lowercase().is_in(["true", "1"]))
            .then(True)
            .when(pl.col(col).cast(pl.Utf8).str.to_lowercase().is_in(["false", "0"]))
            .then(False)
            .otherwise(None)
            .alias(col)
        )
    return cleaned


def enrich_with_authors(
    tweets: pl.DataFrame,
    authors: pl.DataFrame,
    on: str = "author_id",
    suffix: Optional[str] = "_author",
) -> pl.DataFrame:
    """
    将推文表与作者表合并，默认使用左连接保留所有推文。
    """
    if on not in tweets.columns or on not in authors.columns:
        raise ValueError(f"无法基于字段 {on} 进行合并，请确认数据列。")
    return tweets.join(authors, on=on, how="left", suffix=suffix)

