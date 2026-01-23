from __future__ import annotations

import argparse
import json
import math
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from .csv_data import market_metrics_by_range


_ROOT = Path(__file__).resolve().parents[2]
_RULES_BASE = Path(os.getenv("CSV_DATA_DIR", "")).expanduser() if os.getenv("CSV_DATA_DIR") else _ROOT / "cufel_practice_data"
_RULES_PATH = _RULES_BASE / "rules.yaml"


def _env_float(name: str, default: str) -> float:
    value = os.getenv(name, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _load_blocklist(path: Path, fallback: List[str]) -> List[str]:
    if not path.exists():
        return list(fallback)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return list(fallback)
    blocklist = (data.get("default") or {}).get("blocklist") or fallback
    return list(blocklist)


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    v = sorted(values)
    if p <= 0:
        return float(v[0])
    if p >= 1:
        return float(v[-1])
    k = (len(v) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(v[int(k)])
    return float(v[f] + (v[c] - v[f]) * (k - f))


def _dirichlet(n: int, rng: random.Random) -> List[float]:
    raw = [rng.gammavariate(1.0, 1.0) for _ in range(n)]
    total = sum(raw) or 1.0
    return [v / total for v in raw]


def _load_market_metrics_range(start_date: str, end_date: str) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
    codes, metrics = market_metrics_by_range(start_date, end_date)
    if not codes:
        raise RuntimeError("no market data available for the window")
    cleaned = {}
    for code, row in metrics.items():
        vol = float(row.get("volatility") or 0.0)
        adv = float(row.get("adv") or 0.0)
        spread = float(row.get("spread_bps") or 0.0)
        if vol <= 0 or adv <= 0:
            continue
        cleaned[code] = {"volatility": vol, "adv": adv, "spread_bps": spread}
    codes = [c for c in codes if c in cleaned]
    if not codes:
        raise RuntimeError("no valid market metrics after filtering")
    return codes, cleaned


def _simulate(
    codes: List[str],
    metrics: Dict[str, Dict[str, float]],
    n: int,
    samples: int,
    seed: str | None,
) -> Dict[str, List[float]]:
    rng = random.Random(seed) if seed else random
    vols: List[float] = []
    spreads: List[float] = []
    advs: List[float] = []
    hhis: List[float] = []
    tops: List[float] = []
    effns: List[float] = []

    if len(codes) < n:
        raise RuntimeError(f"not enough symbols to sample: have={len(codes)} need={n}")

    for _ in range(samples):
        pick = rng.sample(codes, n)
        weights = _dirichlet(n, rng)
        hhi = sum(w * w for w in weights)
        effn = 1.0 / hhi if hhi > 0 else 0.0
        top = max(weights)

        vol = 0.0
        spread = 0.0
        adv = 0.0
        for code, w in zip(pick, weights):
            m = metrics[code]
            vol += w * m["volatility"]
            spread += w * m["spread_bps"]
            adv += w * m["adv"]

        vols.append(vol)
        spreads.append(spread)
        advs.append(adv)
        hhis.append(hhi)
        tops.append(top)
        effns.append(effn)

    return {
        "volatility": vols,
        "spread_bps": spreads,
        "adv": advs,
        "hhi": hhis,
        "top_weight": tops,
        "effective_n": effns,
    }


def _build_rules(
    series: Dict[str, List[float]],
    *,
    high_warn: float,
    high_restrict: float,
    low_warn: float,
    low_restrict: float,
    blocklist: List[str],
) -> Dict[str, Any]:
    return {
        "max_single_weight": _percentile(series["top_weight"], high_restrict),
        "max_hhi": _percentile(series["hhi"], high_restrict),
        "max_portfolio_volatility": _percentile(series["volatility"], high_restrict),
        "max_weighted_spread_bps": _percentile(series["spread_bps"], high_restrict),
        "min_weighted_adv": _percentile(series["adv"], low_restrict),
        "volatility_warn": _percentile(series["volatility"], high_warn),
        "volatility_restrict": _percentile(series["volatility"], high_restrict),
        "spread_warn": _percentile(series["spread_bps"], high_warn),
        "spread_restrict": _percentile(series["spread_bps"], high_restrict),
        "adv_warn": _percentile(series["adv"], low_warn),
        "adv_restrict": _percentile(series["adv"], low_restrict),
        "hhi_warn": _percentile(series["hhi"], high_warn),
        "hhi_restrict": _percentile(series["hhi"], high_restrict),
        "top_weight_warn": _percentile(series["top_weight"], high_warn),
        "top_weight_restrict": _percentile(series["top_weight"], high_restrict),
        "effective_n_warn": _percentile(series["effective_n"], low_warn),
        "effective_n_restrict": _percentile(series["effective_n"], low_restrict),
        "blocklist": list(blocklist),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate rules from ETF history.")
    parser.add_argument("--asof-date", type=str, required=True, help="calibrate with data up to this date (YYYY-MM-DD)")
    parser.add_argument("--n", type=int, default=5, help="portfolio size")
    parser.add_argument("--samples", type=int, default=int(os.getenv("CALIB_SAMPLES", "5000")))
    parser.add_argument("--seed", type=str, default=os.getenv("RANDOM_SEED"))
    args = parser.parse_args()

    try:
        asof = datetime.strptime(args.asof_date, "%Y-%m-%d")
    except ValueError as exc:
        raise SystemExit(f"invalid --asof-date: {exc}") from exc
    start_date = f"{asof.year}-01-01"
    end_date = args.asof_date
    codes, metrics = _load_market_metrics_range(start_date, end_date)
    series = _simulate(codes, metrics, args.n, args.samples, args.seed)

    high_warn = _env_float("CALIB_WARN_PCTL", "0.8")
    high_restrict = _env_float("CALIB_RESTRICT_PCTL", "0.9")
    low_warn = _env_float("CALIB_LOW_WARN_PCTL", "0.2")
    low_restrict = _env_float("CALIB_LOW_RESTRICT_PCTL", "0.1")

    chigh_warn = _env_float("CALIB_CONSERVATIVE_WARN_PCTL", "0.85")
    chigh_restrict = _env_float("CALIB_CONSERVATIVE_RESTRICT_PCTL", "0.95")
    clow_warn = _env_float("CALIB_CONSERVATIVE_LOW_WARN_PCTL", "0.15")
    clow_restrict = _env_float("CALIB_CONSERVATIVE_LOW_RESTRICT_PCTL", "0.05")

    blocklist = _load_blocklist(_RULES_PATH, ["CCC"])

    rules = {
        "default": _build_rules(
            series,
            high_warn=high_warn,
            high_restrict=high_restrict,
            low_warn=low_warn,
            low_restrict=low_restrict,
            blocklist=blocklist,
        ),
        "conservative": _build_rules(
            series,
            high_warn=chigh_warn,
            high_restrict=chigh_restrict,
            low_warn=clow_warn,
            low_restrict=clow_restrict,
            blocklist=blocklist,
        ),
    }

    _RULES_PATH.write_text(yaml.safe_dump(rules, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(json.dumps({"rules_path": str(_RULES_PATH), "profiles": list(rules.keys())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
