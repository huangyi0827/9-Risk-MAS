from __future__ import annotations

import os
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd


_ROOT = Path(__file__).resolve().parents[2]


def _data_dir() -> Path:
    configured = os.getenv("CSV_DATA_DIR", "").strip()
    if configured:
        return Path(configured)
    return _ROOT / "cufel_practice_data"


def _load_csv(path: Path, *, usecols: Iterable[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, usecols=usecols)


@lru_cache(maxsize=1)
def load_etf_prices() -> pd.DataFrame:
    path = _data_dir() / "etf_2025_data.csv"
    df = _load_csv(path)
    if df.empty:
        return df
    df = df.copy()
    df["code"] = df["code"].astype(str)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ("open", "high", "low", "close", "vol", "amount"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["date", "code"])
    return df


@lru_cache(maxsize=1)
def load_etf_basic() -> pd.DataFrame:
    path = _data_dir() / "sampled_etf_basic.csv"
    df = _load_csv(path)
    if df.empty:
        return df
    df = df.copy()
    df["code"] = df["code"].astype(str)
    return df


@lru_cache(maxsize=1)
def load_compliance_docs() -> pd.DataFrame:
    path = _data_dir() / "csrc_2025.csv"
    df = _load_csv(path)
    if df.empty:
        return df
    df = df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ("title", "content", "from"):
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df


@lru_cache(maxsize=1)
def load_macro_docs() -> pd.DataFrame:
    path = _data_dir() / "govcn_2025.csv"
    df = _load_csv(path)
    if df.empty:
        return df
    df = df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ("title", "content", "industry_name"):
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df


def security_master_codes() -> Tuple[set, str]:
    basic = load_etf_basic()
    if not basic.empty and "code" in basic.columns:
        return set(basic["code"].dropna().astype(str)), "sampled_etf_basic.csv"
    prices = load_etf_prices()
    if not prices.empty:
        return set(prices["code"].dropna().astype(str)), "etf_2025_data.csv"
    return set(), "missing"


def sample_universe(asof_date: str, size: int, seed: str | None) -> List[str]:
    df = load_etf_prices()
    if df.empty:
        return []
    if asof_date:
        cutoff = pd.to_datetime(asof_date, errors="coerce")
        if pd.notna(cutoff):
            df = df[df["date"] <= cutoff]
    codes = list(dict.fromkeys(df["code"].dropna().astype(str).tolist()))
    if not codes:
        return []
    rng = random.Random(seed)
    if size >= len(codes):
        return codes
    return rng.sample(codes, size)


def lookback_start_date(asof_date: str, lookback_days: int) -> str:
    if not asof_date:
        return ""
    cutoff = pd.to_datetime(asof_date, errors="coerce")
    if pd.isna(cutoff):
        return ""
    return (cutoff - pd.Timedelta(days=int(lookback_days))).date().isoformat()


def previous_trading_date(asof_date: str) -> str:
    if not asof_date:
        return ""
    df = load_etf_prices()
    if df.empty or "date" not in df.columns:
        return asof_date
    cutoff = pd.to_datetime(asof_date, errors="coerce")
    if pd.isna(cutoff):
        return asof_date
    prior = df[df["date"] < cutoff]
    if prior.empty:
        return asof_date
    latest = prior["date"].max()
    if pd.isna(latest):
        return asof_date
    return str(latest.date())


def market_metrics(
    codes: Iterable[str],
    start_date: str | None,
    end_date: str | None,
) -> Dict[str, Dict[str, float]]:
    code_set = {str(c) for c in codes if str(c).strip()}
    if not code_set:
        return {}
    df = load_etf_prices()
    if df.empty:
        return {}
    df = df[df["code"].isin(code_set)]
    if start_date:
        start = pd.to_datetime(start_date, errors="coerce")
        if pd.notna(start):
            df = df[df["date"] >= start]
    if end_date:
        end = pd.to_datetime(end_date, errors="coerce")
        if pd.notna(end):
            df = df[df["date"] <= end]
    if df.empty:
        return {}

    df = df.sort_values(["code", "date"])
    df["ret"] = df.groupby("code")["close"].pct_change()
    close = df["close"].replace(0, np.nan)
    df["spread_bps"] = (df["high"] - df["low"]) / close * 10000

    grouped = df.groupby("code")
    volatility = grouped["ret"].std(ddof=0).fillna(0.0)
    adv = grouped["amount"].mean().fillna(0.0)
    spread_bps = grouped["spread_bps"].mean().fillna(0.0)

    metrics = {}
    for code in code_set:
        if code not in volatility.index:
            continue
        metrics[code] = {
            "volatility": float(volatility.get(code, 0.0)),
            "adv": float(adv.get(code, 0.0)),
            "spread_bps": float(spread_bps.get(code, 0.0)),
        }
    return metrics


def market_metrics_by_year(year: int) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    df = load_etf_prices()
    if df.empty:
        return [], {}
    df = df[(df["date"] >= start) & (df["date"] <= end)]
    if df.empty:
        return [], {}
    codes = list(dict.fromkeys(df["code"].dropna().astype(str).tolist()))
    metrics = market_metrics(codes, start, end)
    codes = [c for c in codes if c in metrics]
    return codes, metrics


def market_metrics_by_range(start_date: str, end_date: str) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
    df = load_etf_prices()
    if df.empty:
        return [], {}
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    if df.empty:
        return [], {}
    codes = list(dict.fromkeys(df["code"].dropna().astype(str).tolist()))
    metrics = market_metrics(codes, start_date, end_date)
    codes = [c for c in codes if c in metrics]
    return codes, metrics


def macro_docs_available() -> bool:
    df = load_macro_docs()
    return not df.empty


def compliance_docs_available() -> bool:
    df = load_compliance_docs()
    return not df.empty


def macro_search_hits(query: str, limit: int = 5, asof_date: str | None = None) -> List[Dict[str, Any]]:
    df = load_macro_docs()
    if df.empty or not query:
        return []
    if asof_date and "date" in df.columns:
        cutoff = pd.to_datetime(asof_date, errors="coerce")
        if pd.notna(cutoff):
            df = df[df["date"] <= cutoff]
    q = query.lower()
    title = df.get("title", pd.Series([], dtype=str)).astype(str).str.lower()
    content = df.get("content", pd.Series([], dtype=str)).astype(str).str.lower()
    mask = title.str.contains(q, na=False) | content.str.contains(q, na=False)
    hits = df[mask].head(limit)
    return [{"series": str(row.get("title") or "")} for _, row in hits.iterrows()]


def compliance_search_hits(query: str, limit: int = 5) -> List[str]:
    df = load_compliance_docs()
    if df.empty or not query:
        return []
    q = query.lower()
    title = df.get("title", pd.Series([], dtype=str)).astype(str).str.lower()
    content = df.get("content", pd.Series([], dtype=str)).astype(str).str.lower()
    mask = title.str.contains(q, na=False) | content.str.contains(q, na=False)
    hits = df[mask].head(limit)
    return [str(row.get("content") or "") for _, row in hits.iterrows()]


def macro_latest_date(asof_date: str | None = None) -> str:
    df = load_macro_docs()
    if df.empty or "date" not in df.columns:
        return ""
    if asof_date:
        cutoff = pd.to_datetime(asof_date, errors="coerce")
        if pd.notna(cutoff):
            df = df[df["date"] <= cutoff]
            if df.empty:
                return ""
    latest = df["date"].max()
    if pd.isna(latest):
        return ""
    return str(latest.date())
