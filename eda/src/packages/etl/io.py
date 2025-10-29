"""
数据加载与预处理工具。

该模块聚焦于：
- 大型 CSV 的流式读取与类型规范
- 原始数据与元数据的合并
- Parquet 缓存的读写
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, Optional

import polars as pl


# 路径定义：io.py 在 src/packages/etl/，需要回到项目根目录
# src/packages/etl/io.py -> parent -> src/packages/ -> parent -> src/ -> parent -> eda/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "__data" / "charlie-kirk-twitter-dataset"
RAW_TWEETS = DATA_DIR / "for_export_charlie_kirk.csv"
RAW_AUTHORS = DATA_DIR / "well_known_authors_charlie_kirk.csv"
PARQUET_DIR = PROJECT_ROOT / "src" / "notebooks" / "parquet"


def scan_raw_tweets(dtypes: Optional[dict[str, pl.PolarsDataType]] = None) -> pl.LazyFrame:
    """
    使用 Polars scan_csv 流式加载原始推文数据。

    参数
    ----
    dtypes:
        可选的列类型映射，用于覆盖默认推断。
    """
    if not RAW_TWEETS.exists():
        raise FileNotFoundError(f"未找到原始推文文件: {RAW_TWEETS}")

    default_dtypes = {
        "created_at": pl.Utf8,
        "author_id": pl.Utf8,
        "lang": pl.Utf8,
        "isReply": pl.Utf8,
        "author_isBlueVerified": pl.Utf8,
    }
    schema = {**default_dtypes, **(dtypes or {})}
    return pl.scan_csv(RAW_TWEETS, dtypes=schema, ignore_errors=True)


def read_well_known_authors() -> pl.DataFrame:
    """
    读取知名作者信息表，并进行基础清洗（去除重复、规范字段名）。
    """
    if not RAW_AUTHORS.exists():
        raise FileNotFoundError(f"未找到作者元数据文件: {RAW_AUTHORS}")

    df = pl.read_csv(RAW_AUTHORS, ignore_errors=True)
    df = df.unique(subset=["author_userName"], maintain_order=True)
    return df.rename({col: col.strip() for col in df.columns})


def materialize_parquet(lf: pl.LazyFrame, output_path: Path, partitions: Optional[list[str]] = None) -> None:
    """
    将 LazyFrame 实体化为 Parquet 文件，可选按字段分区。
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if partitions:
        lf.sink_parquet(output_path, compression="zstd", partition_by=partitions)
    else:
        lf.sink_parquet(output_path, compression="zstd")


def iter_batches(path: Path, batch_size: int = 100_000) -> Iterator[pl.DataFrame]:
    """
    以指定批大小迭代读取 Parquet 数据。

    说明：Polars 当前尚未在 Python API 中暴露原生的 streaming batch 读取接口，
    因此这里采用 collect 后再切片的方式作为占位实现。若数据规模导致内存压力，
    建议切换为 `pyarrow.parquet.ParquetFile.iter_batches` 等底层方案。
    """
    df = pl.read_parquet(path)
    for batch in df.iter_slices(n_rows=batch_size):
        yield batch


def list_parquet_files() -> Iterable[Path]:
    """
    列出缓存的 Parquet 文件，方便在 Notebook 中快速浏览。
    """
    if not PARQUET_DIR.exists():
        return []
    return sorted(PARQUET_DIR.glob("**/*.parquet"))
