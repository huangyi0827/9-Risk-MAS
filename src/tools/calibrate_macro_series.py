from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
import tushare as ts
try:
    import yaml
except ImportError as exc:  # pragma: no cover - optional dependency drift
    raise SystemExit(f"pyyaml is required: {exc}")


def _parse_date(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value)
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _format_tushare_date(value: datetime) -> str:
    return value.strftime("%Y%m%d")


def _format_tushare_year_start(value: datetime) -> str:
    return f"{value.year}0101"


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    v = sorted(values)
    if p <= 0:
        return float(v[0])
    if p >= 1:
        return float(v[-1])
    k = (len(v) - 1) * p
    f = int(k)
    c = min(f + 1, len(v) - 1)
    if f == c:
        return float(v[f])
    return float(v[f] + (v[c] - v[f]) * (k - f))


def _load_config(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if isinstance(data, dict) and "series" in data:
        return data
    if isinstance(data, dict):
        return {"series": data}
    return {"series": {}}


def _fetch_series(
    series: str,
    config: Dict[str, Any],
    asof_date: datetime | None,
) -> Tuple[List[Tuple[datetime, float]], str | None]:
    token = os.getenv("TUSHARE_TOKEN", "").strip()
    if not token:
        return [], "TUSHARE_TOKEN not configured"

    api_name = str(config.get("api") or "").strip()
    if not api_name:
        return [], "macro series config missing api"
    series_param = str(config.get("series_param") or "").strip()
    params: Dict[str, Any] = dict(config.get("params") or {})
    if series_param:
        params[series_param] = config.get("series_value") or series
    if asof_date and "end_date" not in params:
        params["end_date"] = _format_tushare_date(asof_date)
    if asof_date and "start_date" not in params:
        params["start_date"] = _format_tushare_year_start(asof_date)
    fields = str(config.get("fields") or "").strip()
    date_field = str(config.get("date_field") or "").strip()
    value_field = str(config.get("value_field") or "").strip()
    bid_field = str(config.get("bid_field") or "").strip()
    ask_field = str(config.get("ask_field") or "").strip()
    shift_days = int(config.get("date_shift_days") or 0)

    ts.set_token(token)
    pro = ts.pro_api()
    api = getattr(pro, api_name, None)
    if api is None:
        return [], f"tushare api not found: {api_name}"

    try:
        if fields:
            df = api(**params, fields=fields)
        else:
            df = api(**params)
    except Exception as exc:  # pragma: no cover - external API errors
        return [], f"tushare api error: {exc!r}"

    if df is None or getattr(df, "empty", True):
        return [], None

    columns = list(getattr(df, "columns", []))
    if not date_field:
        for candidate in ("date", "trade_date", "month", "year", "quarter", "period"):
            if candidate in columns:
                date_field = candidate
                break
    if not date_field or date_field not in columns:
        return [], "date field not found"

    if not value_field and not (bid_field and ask_field):
        numeric_cols = [c for c in columns if c != date_field]
        value_field = numeric_cols[0] if numeric_cols else ""
    if value_field and value_field not in columns:
        return [], f"value field not found: {value_field}"
    if bid_field and bid_field not in columns:
        return [], f"bid field not found: {bid_field}"
    if ask_field and ask_field not in columns:
        return [], f"ask field not found: {ask_field}"

    rows: List[Tuple[datetime, float]] = []
    for _, row in df.iterrows():
        raw_date = row.get(date_field)
        parsed = _parse_date(raw_date)
        if parsed is None:
            continue
        if shift_days:
            parsed = parsed + timedelta(days=shift_days)
        val = None
        if bid_field and ask_field:
            bid = row.get(bid_field)
            ask = row.get(ask_field)
            try:
                if bid is not None and ask is not None:
                    val = (float(bid) + float(ask)) / 2.0
            except (TypeError, ValueError):
                val = None
        elif value_field:
            try:
                val = float(row.get(value_field))
            except (TypeError, ValueError):
                val = None
        if val is None:
            continue
        rows.append((parsed, float(val)))

    rows.sort(key=lambda item: item[0])
    return rows, None


def _filter_window(
    rows: List[Tuple[datetime, float]],
    asof_date: datetime | None,
    lookback_days: int | None,
) -> List[Tuple[datetime, float]]:
    if not rows:
        return rows
    filtered = rows
    if asof_date:
        filtered = [r for r in filtered if r[0] <= asof_date]
    if lookback_days is not None and asof_date:
        start = asof_date - timedelta(days=lookback_days)
        filtered = [r for r in filtered if r[0] >= start]
    return filtered


def _compute_changes(values: List[float], mode: str, scale: str | None) -> List[float]:
    changes: List[float] = []
    if len(values) < 2:
        return changes
    for i in range(1, len(values)):
        prev = values[i - 1]
        curr = values[i]
        if mode == "abs":
            change = abs(curr - prev)
        else:
            if prev == 0:
                continue
            change = abs((curr - prev) / prev)
        if scale == "bp":
            change = change * 100.0
        changes.append(change)
    return changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate macro series thresholds from Tushare data.")
    parser.add_argument("--asof-date", default=os.getenv("ASOF_DATE", "").strip(), help="as-of date (YYYY-MM-DD)")
    parser.add_argument("--lookback-days", type=int, default=365 * 3, help="lookback window in days")
    parser.add_argument("--warn-pctl", type=float, default=0.9, help="warn percentile")
    parser.add_argument("--restrict-pctl", type=float, default=0.98, help="restrict percentile")
    parser.add_argument("--min-samples", type=int, default=30, help="min changes required to calibrate")
    parser.add_argument("--config", default=os.getenv("MACRO_SERIES_CONFIG", "").strip(), help="macro series config path")
    args = parser.parse_args()

    if args.asof_date:
        asof_date = _parse_date(args.asof_date)
    else:
        asof_date = datetime.now(timezone.utc).replace(tzinfo=None)
    if asof_date is None:
        raise SystemExit("invalid --asof-date")

    base = Path(os.getenv("CSV_DATA_DIR", "")).expanduser() if os.getenv("CSV_DATA_DIR") else Path.cwd() / "cufel_practice_data"
    config_path = Path(args.config).expanduser() if args.config else base / "macro_series.yaml"
    if not config_path.exists():
        raise SystemExit(f"config not found: {config_path}")

    config = _load_config(config_path)
    series_cfg = config.get("series") or {}
    if not isinstance(series_cfg, dict) or not series_cfg:
        raise SystemExit("no macro series configured")

    updated = {}
    for series, cfg in series_cfg.items():
        if not isinstance(cfg, dict):
            continue
        rows, err = _fetch_series(series, cfg, asof_date)
        if err:
            updated[series] = {"error": err}
            continue
        rows = _filter_window(rows, asof_date, args.lookback_days)
        values = [v for _, v in rows]
        mode = str(cfg.get("change_mode") or "pct").strip().lower()
        scale = str(cfg.get("change_scale") or "").strip().lower() or None
        changes = _compute_changes(values, mode, scale)
        if len(changes) < args.min_samples:
            updated[series] = {"error": f"not enough samples: {len(changes)}"}
            continue
        warn = _percentile(changes, args.warn_pctl)
        restrict = _percentile(changes, args.restrict_pctl)
        cfg["warn_pct_change"] = float(warn)
        cfg["restrict_pct_change"] = float(restrict)
        updated[series] = {"warn_pct_change": warn, "restrict_pct_change": restrict, "samples": len(changes)}

    config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(json.dumps({"config_path": str(config_path), "updated": updated}, ensure_ascii=False))


if __name__ == "__main__":
    main()
