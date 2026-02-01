from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

from langchain.agents import create_agent
import yaml
from .agent_utils import extract_tool_calls, last_ai_content, wrap_tool
from ..state import RiskState, Finding
from ..tools.csv_data import macro_search_hits
from ..skills_runtime import load_skill, build_system_prompt, filter_tools, validate_output
from ..config import RuntimeConfig, DEFAULT_CONFIG
import tushare as ts

def _provenance(source: str, params: Dict[str, Any]) -> Dict[str, Any]:
    payload = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return {
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "params_hash": hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],
    }


_ROOT = Path(__file__).resolve().parents[2]


def _macro_series_path(config: RuntimeConfig) -> Path:
    if config.macro_series_config:
        return Path(config.macro_series_config).expanduser()
    base = Path(config.csv_data_dir).expanduser() if config.csv_data_dir else _ROOT / "cufel_practice_data"
    return base / "macro_series.yaml"


@lru_cache(maxsize=8)
def _load_macro_series_config(path_str: str) -> Dict[str, Any]:
    path = Path(path_str)
    if not path.exists():
        raise SystemExit(f"macro series config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or "series" not in data or not isinstance(data.get("series"), dict):
        raise SystemExit("macro series config must include a 'series' mapping")
    if not data["series"]:
        raise SystemExit("macro series config 'series' is empty")
    return data["series"]


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


def _format_tushare_date(value: str) -> str:
    parsed = _parse_date(value)
    if not parsed:
        return ""
    return parsed.strftime("%Y%m%d")


def _format_tushare_year_start(value: str) -> str:
    parsed = _parse_date(value)
    if not parsed:
        return ""
    return f"{parsed.year}0101"


def _tushare_timeseries_from_config(
    series: str, config: Dict[str, Any], asof_date: str, runtime: RuntimeConfig
) -> Tuple[Dict[str, Any], str | None]:
    """Fetch timeseries from Tushare API.

    Args:
        series: Series identifier
        config: Series configuration from macro_series.yaml
        asof_date: Reference date for data alignment (thread-safe parameter)
    """
    token = runtime.tushare_token
    if not token:
        raise SystemExit("TUSHARE_TOKEN not configured")

    api_name = str(config.get("api") or "").strip()
    if not api_name:
        return {}, "macro series config missing api"
    series_param = str(config.get("series_param") or "").strip()
    params: Dict[str, Any] = dict(config.get("params") or {})
    if series_param:
        params[series_param] = config.get("series_value") or series
    if asof_date and "end_date" not in params:
        end_date = _format_tushare_date(asof_date)
        if end_date:
            params["end_date"] = end_date
    if asof_date and "start_date" not in params:
        start_date = _format_tushare_year_start(asof_date)
        if start_date:
            params["start_date"] = start_date
    fields = str(config.get("fields") or "").strip()
    date_field = str(config.get("date_field") or "").strip()
    value_field = str(config.get("value_field") or "").strip()
    bid_field = str(config.get("bid_field") or "").strip()
    ask_field = str(config.get("ask_field") or "").strip()
    shift_days = int(config.get("date_shift_days") or 0)
    stale_days = config.get("stale_days")

    ts.set_token(token)
    pro = ts.pro_api()
    api = getattr(pro, api_name, None)
    if api is None:
        return {}, f"tushare api not found: {api_name}"

    try:
        if fields:
            df = api(**params, fields=fields)
        else:
            df = api(**params)
    except Exception as exc:  # pragma: no cover - external API errors
        return {}, f"tushare api error: {exc!r}"

    if df is None or getattr(df, "empty", True):
        return {"series": series, "values": []}, None

    columns = list(getattr(df, "columns", []))
    if not date_field:
        return {}, "date field is required in config"
    if value_field and value_field not in columns:
        return {}, f"value field not found: {value_field}"
    if bid_field and bid_field not in columns:
        return {}, f"bid field not found: {bid_field}"
    if ask_field and ask_field not in columns:
        return {}, f"ask field not found: {ask_field}"
    if not value_field and not (bid_field and ask_field):
        return {}, "value_field or bid_field+ask_field is required in config"

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

    if not rows:
        return {"series": series, "values": []}, None

    rows.sort(key=lambda item: item[0])
    asof_dt = _parse_date(asof_date)
    if asof_dt:
        rows = [r for r in rows if r[0] <= asof_dt]
    if not rows:
        return {"series": series, "values": []}, None

    aligned_date, aligned_value = rows[-1]
    stale = None
    stale_diff = None
    if asof_dt and stale_days is not None:
        stale_diff = (asof_dt.date() - aligned_date.date()).days
        try:
            stale_threshold = int(stale_days)
            stale = stale_diff > stale_threshold
        except (TypeError, ValueError):
            stale = None

    values = [(r[0].date().isoformat(), r[1]) for r in rows[-5:]]
    payload = {
        "series": series,
        "values": values,
        "aligned_date": aligned_date.date().isoformat(),
        "aligned_value": aligned_value,
    }
    if stale is not None:
        payload["stale"] = stale
    if stale_diff is not None:
        payload["stale_days"] = stale_diff
    return payload, None


def _macro_timeseries_impl(series: str, asof_date: str, runtime: RuntimeConfig) -> Dict[str, Any]:
    """Return simplified macro time series samples.

    Args:
        series: Series identifier
        asof_date: Reference date for data alignment (thread-safe parameter)
    """
    config = _load_macro_series_config(str(_macro_series_path(runtime))).get(series)
    if not config:
        return {
            "series": series,
            "values": [],
            "provenance": _provenance("tushare", {"series": series, "error": "series not configured"}),
        }

    payload, err = _tushare_timeseries_from_config(series, config, asof_date, runtime)
    if err:
        return {
            "series": series,
            "values": [],
            "provenance": _provenance("tushare", {"series": series, "error": err}),
        }

    return {
        **payload,
        "provenance": _provenance(
            "tushare",
            {"series": series, "rows": len(payload.get("values") or []), "asof_date": asof_date or None},
        ),
    }


def _macro_search_impl(query: str, asof_date: str, runtime: RuntimeConfig) -> Dict[str, Any]:
    """Lightweight search over macro documents.

    Args:
        query: Search query string
        asof_date: Reference date for filtering results (thread-safe parameter)
    """
    hits = macro_search_hits(query, limit=5, asof_date=asof_date or None, config=runtime)
    return {
        "query": query,
        "hits": hits,
        "provenance": _provenance(
            "macro_docs",
            {"query": query, "hits": len(hits), "asof_date": asof_date or None},
        ),
    }


# FIX: Removed global variable _CURRENT_ASOF_DATE and _set_asof_date function
# asof_date is now passed as a parameter to all functions that need it


def _create_tools_with_asof_date(asof_date: str, runtime: RuntimeConfig):
    """Create tool instances bound to a specific asof_date.

    This factory function creates thread-safe tool instances by capturing
    asof_date in a closure instead of using a global variable.

    Args:
        asof_date: Reference date to bind to the tools

    Returns:
        Tuple of (macro_timeseries_tool, macro_search_tool)
    """
    def timeseries_impl(series: str) -> Dict[str, Any]:
        return _macro_timeseries_impl(series, asof_date, runtime)

    def search_impl(query: str) -> Dict[str, Any]:
        return _macro_search_impl(query, asof_date, runtime)

    return (
        wrap_tool("macro_timeseries", timeseries_impl),
        wrap_tool("macro_search", search_impl),
    )


def _fallback_finding(severity: int) -> Finding:
    sev = int(severity)
    summary = "宏观环境平稳" if sev == 0 else "宏观环境波动"
    return {
        "agent": "MacroToolCallingAgent",
        "risk_type": "macro",
        "severity": sev,
        "summary": summary,
        "metrics": {"macro_severity": sev},
        "evidence": [{"ref": "snapshot_metrics.macro_severity", "value": sev}],
        "recommendations": ["关注宏观指标"],
    }


def _llm_model_name(llm) -> str:
    return str(getattr(llm, "model_name", None) or getattr(llm, "model", None) or "")


def _prefetch_macro_timeseries(
    asof_date: str, runtime: RuntimeConfig
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    series_cfg = _load_macro_series_config(str(_macro_series_path(runtime)))
    series_list = list(series_cfg.keys())
    if not series_list:
        raise SystemExit("macro series config contains no series")

    tool_calls: List[Dict[str, Any]] = []
    results: Dict[str, Any] = {}
    for series in series_list:
        start = time.monotonic()
        error = None
        try:
            output = _macro_timeseries_impl(series, asof_date, runtime)
        except Exception as exc:  # pragma: no cover - runtime tool errors
            error = repr(exc)
            output = {"error": error}
        latency_ms = int((time.monotonic() - start) * 1000)
        if isinstance(output, dict):
            output.setdefault("tool_meta", {})
            output["tool_meta"].update({"latency_ms": latency_ms, "error": error})
        tool_calls.append(
            {
                "tool": "macro_timeseries",
                "input": {"series": series},
                "output": output,
                "latency_ms": latency_ms,
                "error": error,
            }
        )
        results[series] = output
    return tool_calls, {"macro_timeseries": results}


def _coerce_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _nlp_severity_from_score(score: float | None) -> int:
    if score is None:
        return 0
    if score >= 70:
        return 2
    if score >= 60:
        return 1
    if score >= 40:
        return 0
    if score >= 30:
        return 1
    return 2


def _nlp_severity_from_tool_calls(tool_calls: List[Dict[str, Any]]) -> int | None:
    found = False
    severity = 0
    for call in tool_calls:
        if call.get("tool") != "macro_search":
            continue
        output = call.get("output")
        if not isinstance(output, dict):
            continue
        hits = output.get("hits") or []
        if not isinstance(hits, list):
            continue
        for hit in hits:
            if not isinstance(hit, dict):
                continue
            score = _coerce_float(hit.get("sentiment_score"))
            if score is None:
                continue
            found = True
            severity = max(severity, _nlp_severity_from_score(score))
    if not found:
        return None
    return severity


def _blend_severity(macro_severity: int, nlp_severity: int | None, runtime: RuntimeConfig) -> int:
    if nlp_severity is None:
        return int(macro_severity)
    weight = float(runtime.macro_severity_weight)
    blended = round(weight * float(macro_severity) + (1.0 - weight) * float(nlp_severity))
    return max(0, min(3, int(blended)))


def _compute_macro_severity(tool_results: Dict[str, Any], runtime: RuntimeConfig) -> int:
    series_results = tool_results.get("macro_timeseries") or {}
    if not isinstance(series_results, dict):
        return 0
    config = _load_macro_series_config(str(_macro_series_path(runtime)))
    severity = 0
    for series, output in series_results.items():
        if not isinstance(output, dict):
            continue
        values = output.get("values") or []
        if not values:
            severity = max(severity, 1)
            continue
        if output.get("stale") is True:
            severity = max(severity, 1)
        if len(values) >= 2:
            prev_val = _coerce_float(values[-2][1] if isinstance(values[-2], (list, tuple)) else None)
            last_val = _coerce_float(values[-1][1] if isinstance(values[-1], (list, tuple)) else None)
            if prev_val is None or last_val is None:
                continue
            cfg = config.get(series) or {}
            warn_pct = _coerce_float(cfg.get("warn_pct_change"))
            restrict_pct = _coerce_float(cfg.get("restrict_pct_change"))
            mode = str(cfg.get("change_mode") or "pct").strip().lower()
            scale = str(cfg.get("change_scale") or "").strip().lower() or None
            if mode == "abs":
                change = abs(last_val - prev_val)
            else:
                if prev_val == 0:
                    continue
                change = abs((last_val - prev_val) / prev_val)
            if scale == "bp":
                change = change * 100.0
            if restrict_pct is not None and change >= restrict_pct:
                severity = max(severity, 2)
            elif warn_pct is not None and change >= warn_pct:
                severity = max(severity, 1)
    return severity


def run_macro_agent(state: RiskState, llm, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """运行宏观 Agent：先取时序并计算 severity，必要时再补文本上下文。"""
    runtime = config or DEFAULT_CONFIG
    normalized = state.get("normalized") or {}
    asof_date = str(normalized.get("asof_date") or "")

    data_quality = state.get("data_quality") or {}
    if not (data_quality.get("macro") or {}).get("timeseries_available", False):
        snapshot = state.get("snapshot_metrics") or {}
        return {
            "finding_macro": _fallback_finding(int(snapshot.get("macro_severity", 0))),
            "tool_calls_macro": [],
            "llm_used_macro": False,
            "llm_model_macro": "",
            "snapshot_metrics": snapshot,
        }

    prefetched_calls, prefetched_results = _prefetch_macro_timeseries(asof_date, runtime)
    macro_severity = _compute_macro_severity(prefetched_results, runtime)
    snapshot = state.get("snapshot_metrics") or {}
    updated_snapshot = dict(snapshot)
    updated_snapshot["macro_severity"] = macro_severity
    updated_snapshot["macro_severity_timeseries"] = macro_severity

    if llm is None:
        return {
            "finding_macro": _fallback_finding(macro_severity),
            "tool_calls_macro": prefetched_calls,
            "llm_used_macro": False,
            "llm_model_macro": "",
            "snapshot_metrics": updated_snapshot,
        }

    skill = load_skill("macro-tool-calling")
    macro_timeseries, macro_search = _create_tools_with_asof_date(asof_date, runtime)
    tools = filter_tools([macro_timeseries, macro_search], skill.allowlist)
    if not tools:
        return {
            "finding_macro": _fallback_finding(macro_severity),
            "tool_calls_macro": prefetched_calls,
            "llm_used_macro": False,
            "llm_model_macro": "",
            "snapshot_metrics": updated_snapshot,
        }

    system_prompt = build_system_prompt("", skill)
    agent = create_agent(llm, tools, system_prompt=system_prompt)

    payload = {
        "snapshot_metrics": updated_snapshot,
        "data_quality": state.get("data_quality") or {},
        "tool_results": prefetched_results,
    }
    user_payload = json.dumps(payload, separators=(",", ":"))
    result = agent.invoke({"messages": [{"role": "user", "content": f"Input state: {user_payload}"}]})
    llm_model = _llm_model_name(llm)

    messages = result.get("messages", []) if isinstance(result, dict) else []
    tool_calls = list(prefetched_calls)
    tool_calls.extend(extract_tool_calls(messages))

    output = last_ai_content(messages)
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        parsed = {}

    errors = validate_output(skill, parsed)
    if errors:
        tool_calls.append({"tool": "schema_validation", "errors": errors, "skill": skill.name})
        nlp_severity = _nlp_severity_from_tool_calls(tool_calls)
        final_severity = _blend_severity(macro_severity, nlp_severity, runtime)
        final_snapshot = dict(updated_snapshot)
        if nlp_severity is not None:
            final_snapshot["macro_nlp_severity"] = nlp_severity
        final_snapshot["macro_severity_final"] = final_severity
        final_snapshot["macro_severity"] = final_severity
        return {
            "finding_macro": _fallback_finding(final_severity),
            "tool_calls_macro": tool_calls,
            "llm_used_macro": True,
            "llm_model_macro": llm_model,
            "snapshot_metrics": final_snapshot,
        }

    nlp_severity = _nlp_severity_from_tool_calls(tool_calls)
    final_severity = _blend_severity(macro_severity, nlp_severity, runtime)
    final_snapshot = dict(updated_snapshot)
    if nlp_severity is not None:
        final_snapshot["macro_nlp_severity"] = nlp_severity
    final_snapshot["macro_severity_final"] = final_severity
    final_snapshot["macro_severity"] = final_severity

    metrics = parsed.get("metrics") if isinstance(parsed, dict) else {}
    if not isinstance(metrics, dict):
        metrics = {}
    metrics["macro_severity_timeseries"] = macro_severity
    if nlp_severity is not None:
        metrics["macro_nlp_severity"] = nlp_severity
    metrics["macro_severity_final"] = final_severity

    finding: Finding = {
        "agent": "MacroToolCallingAgent",
        "risk_type": "macro",
        "severity": int(final_severity),
        "summary": parsed.get("summary", ""),
        "evidence": parsed.get("evidence", []),
        "metrics": metrics,
        "recommendations": parsed.get("recommendations", []),
    }

    return {
        "finding_macro": finding,
        "tool_calls_macro": tool_calls,
        "llm_used_macro": True,
        "llm_model_macro": llm_model,
        "snapshot_metrics": final_snapshot,
    }
