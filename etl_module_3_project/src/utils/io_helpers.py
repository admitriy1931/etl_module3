"""I/O helpers: read from path / URL / fallback sample."""

import os
import json
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from lxml import etree

from utils.logger import get_logger

log = get_logger(__name__)


def resolve_source(
    env_path_key: str,
    env_url_key: str,
    sample_filename: str,
    sample_dir: Path,
) -> str:
    """Return a local file path: env path > download from URL > sample fallback."""
    path_val = os.getenv(env_path_key, "").strip()
    url_val = os.getenv(env_url_key, "").strip()

    if path_val and Path(path_val).exists():
        log.info("Using source file from env path: %s", path_val)
        return path_val

    if url_val:
        dest = sample_dir / f"downloaded_{sample_filename}"
        log.info("Downloading source from URL: %s -> %s", url_val, dest)
        resp = requests.get(url_val, timeout=60)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        return str(dest)

    fallback = sample_dir / sample_filename
    if fallback.exists():
        log.info("Using sample fallback: %s", fallback)
        return str(fallback)

    raise FileNotFoundError(
        f"No source found: env vars {env_path_key}/{env_url_key} empty, "
        f"sample {fallback} does not exist."
    )


def read_json_file(path: str) -> dict:
    """Read a JSON file and return parsed dict."""
    log.info("Reading JSON from %s", path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def read_xml_file(path: str) -> etree._Element:
    """Read an XML file and return lxml root element."""
    log.info("Reading XML from %s", path)
    tree = etree.parse(path)
    return tree.getroot()


def read_csv_file(path: str, **kwargs) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    log.info("Reading CSV from %s", path)
    df = pd.read_csv(path, **kwargs)
    log.info("Read %d rows, %d columns", len(df), len(df.columns))
    if df.empty:
        raise ValueError(f"CSV file is empty: {path}")
    return df


def save_dataframe(df: pd.DataFrame, path: str, fmt: str = "csv") -> None:
    """Save a DataFrame to disk."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "csv":
        df.to_csv(p, index=False)
    elif fmt == "parquet":
        df.to_parquet(p, index=False)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    log.info("Saved %d rows to %s", len(df), p)
