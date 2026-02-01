from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import math

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - optional dependency drift
    ChatOpenAI = None

from .graph import build_graph
from .state import new_state
from .tools.csv_data import sample_universe
from .config import RuntimeConfig, DEFAULT_CONFIG


def _load_llm(config: RuntimeConfig | None = None):
    cfg = config or DEFAULT_CONFIG
    api_key = cfg.openai_api_key
    if not api_key or ChatOpenAI is None:
        return None
    model = cfg.llm_model
    if not model:
        return None
    kwargs = {"model": model, "temperature": 0, "api_key": api_key}
    if cfg.openai_base_url:
        kwargs["base_url"] = cfg.openai_base_url
    return ChatOpenAI(**kwargs)


def _random_weights(codes: List[str], seed: str | None = None) -> Dict[str, float]:
    rng = random.Random(seed) if seed else random
    raw = [rng.random() for _ in codes]
    total = sum(raw) or 1.0
    return {c: v / total for c, v in zip(codes, raw)}


def _sample_universe_from_csv(
    asof_date: str, size: int, seed: str | None, config: RuntimeConfig
) -> List[str]:
    return sample_universe(asof_date, size, seed, config)


def _sample_case(profile: str, config: RuntimeConfig) -> Dict[str, Any]:
    asof_env = config.asof_date
    if asof_env:
        asof_date = asof_env
    else:
        asof_date = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    size = int(config.sample_universe_size)
    seed = config.random_seed
    universe = _sample_universe_from_csv(asof_date, size, seed, config)
    if not universe:
        universe = ["513090", "518880", "588200"]

    current_weights = _random_weights(universe, seed=seed)
    target_weights = _random_weights(universe, seed=None if seed is None else f"{seed}-target")

    intent = {
        "date": asof_date,
        "mode": "target",
        "targets": target_weights,
    }
    context = {
        "current_positions": current_weights,
        "current_positions_date": asof_date,
        "universe": universe,
        "account_type": "brokerage",
        "jurisdiction": "CN",
        "policy_profile": profile,
    }
    if config.default_aum is not None:
        context["aum"] = float(config.default_aum)

    return {"intent": intent, "context": context}


def _format_table(headers, rows):
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    line = "+".join("-" * (w + 2) for w in widths)
    def fmt_row(row):
        return "|".join(f" {str(cell).ljust(widths[i])} " for i, cell in enumerate(row))
    out = [line, fmt_row(headers), line]
    out.extend(fmt_row(r) for r in rows)
    out.append(line)
    return "\n".join(out)


def _format_num(value, digits: int = 5):
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.{digits}f}"
    return value


def _shorten(value: Any, limit: int = 120) -> str:
    text = "" if value is None else str(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _evidence_refs(evidence: List[Dict[str, Any]] | None, max_items: int = 4) -> str:
    refs: List[str] = []
    for item in (evidence or []):
        ref = item.get("ref")
        if isinstance(ref, str) and ref:
            refs.append(ref)
    if not refs:
        return "none"
    if len(refs) <= max_items:
        return ",".join(refs)
    return ",".join(refs[:max_items]) + f"...(+{len(refs) - max_items})"


def _build_minimal_view(result: Dict[str, Any]) -> Dict[str, Any]:
    findings = result.get("findings") or []
    audit = result.get("audit") or {}
    compliance_meta = audit.get("compliance_blocklist_meta") or {}
    return {
        "decision": (result.get("decision") or {}).get("decision"),
        "binding_constraints": result.get("binding_constraints") or [],
        "recommended_actions": result.get("recommended_actions") or [],
        "findings_summary": [
            {
                "risk_type": f.get("risk_type"),
                "severity": f.get("severity"),
                "summary": f.get("summary"),
            }
            for f in findings
        ],
        "compliance_blocklist_soft": audit.get("compliance_blocklist_soft") or [],
        "compliance_industry_hits": compliance_meta.get("industry_hits") or [],
        "trace_id": audit.get("trace_id"),
        "llm_used": audit.get("llm_used"),
        "llm_model": audit.get("llm_model"),
        "supervisor_used": result.get("supervisor_used"),
        "supervisor_rationale": result.get("supervisor_rationale"),
    }


def _build_payload(result: Dict[str, Any], minimal_view: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "user_view": minimal_view,
        "decision": result.get("decision"),
        "risk_report": result.get("risk_report"),
        "binding_constraints": result.get("binding_constraints"),
        "recommended_actions": result.get("recommended_actions"),
        "audit": result.get("audit"),
    }


def _recommendation_summary(minimal_view: Dict[str, Any]) -> str:
    recs = minimal_view.get("recommended_actions") or []
    rec_summary = ""
    if recs:
        first = recs[0] if isinstance(recs, list) else recs
        action = first.get("action") if isinstance(first, dict) else ""
        rationale = first.get("rationale") if isinstance(first, dict) else ""
        if action or rationale:
            rec_summary = f"{action}: {rationale}".strip(": ")
        if isinstance(first, dict) and first.get("target_weights"):
            weights = first.get("target_weights") or {}
            parts = []
            for code in sorted(weights.keys()):
                val = _format_num(weights.get(code))
                parts.append(f"{code}={val}")
            if parts:
                rec_summary = f"{rec_summary} | {', '.join(parts)}".strip()
    decision_value = minimal_view.get("decision")
    if decision_value == "block":
        rec_summary = "需人工介入"
    elif decision_value in {"pass", "warn"}:
        rec_summary = "none"
    return rec_summary


def _rules_current_values(result: Dict[str, Any], rules_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    snapshot = result.get("snapshot_metrics") or {}
    normalized = result.get("normalized") or {}
    targets = normalized.get("target_weights") or {}
    blocklist = result.get("compliance_blocklist") or rules_snapshot.get("blocklist") or []
    blocked = [c for c, w in targets.items() if c in blocklist and float(w) > 0]

    mapping = {
        "max_single_weight": snapshot.get("top_weight"),
        "top_weight_warn": snapshot.get("top_weight"),
        "top_weight_restrict": snapshot.get("top_weight"),
        "max_hhi": snapshot.get("hhi"),
        "hhi_warn": snapshot.get("hhi"),
        "hhi_restrict": snapshot.get("hhi"),
        "max_portfolio_volatility": snapshot.get("portfolio_volatility"),
        "volatility_warn": snapshot.get("portfolio_volatility"),
        "volatility_restrict": snapshot.get("portfolio_volatility"),
        "max_weighted_spread_bps": snapshot.get("weighted_spread_bps"),
        "spread_warn": snapshot.get("weighted_spread_bps"),
        "spread_restrict": snapshot.get("weighted_spread_bps"),
        "min_weighted_adv": snapshot.get("weighted_adv"),
        "adv_warn": snapshot.get("weighted_adv"),
        "adv_restrict": snapshot.get("weighted_adv"),
        "effective_n_warn": snapshot.get("effective_n"),
        "effective_n_restrict": snapshot.get("effective_n"),
        "max_turnover": snapshot.get("turnover"),
        "max_position_delta": snapshot.get("max_position_delta"),
        "max_adv_ratio": snapshot.get("max_adv_ratio"),
        "max_delta_hhi": snapshot.get("delta_hhi"),
        "max_delta_volatility": snapshot.get("delta_portfolio_volatility"),
    }
    mapping["blocklist"] = ",".join(blocked) if blocked else "none"
    return mapping


def _rule_status(rule_key: str, threshold, current, blocked: bool) -> tuple[str, bool]:
    if current in ("", None):
        return "", False
    if rule_key == "blocklist":
        return ("未达标" if blocked else "达标", blocked)
    try:
        cur = float(current)
        thr = float(threshold)
    except (TypeError, ValueError):
        return "", False
    if rule_key.startswith("min_") or rule_key.startswith("adv_") or rule_key.startswith("effective_n_"):
        failed = cur < thr
    else:
        failed = cur > thr
    return ("未达标" if failed else "达标", failed)



def _print_tables(result: Dict[str, Any], minimal_view: Dict[str, Any]) -> None:
    audit = result.get("audit") or {}
    nodes_to_run = ",".join(audit.get("nodes_to_run") or [])
    rec_summary = _recommendation_summary(minimal_view)
    summary_rows = [
        ("decision", minimal_view.get("decision")),
        ("recommendation", rec_summary),
        ("llm_used", minimal_view.get("llm_used")),
        ("llm_model", minimal_view.get("llm_model") or ""),
        ("trace_id", minimal_view.get("trace_id") or ""),
    ]
    print(_format_table(["KEY", "VALUE"], summary_rows))
    print()

    finding_rows = [
        (f.get("risk_type"), f.get("severity"), f.get("summary"))
        for f in (minimal_view.get("findings_summary") or [])
    ]
    if finding_rows:
        print(_format_table(["RISK", "SEVERITY", "SUMMARY"], finding_rows))
        print()

    skills_used = audit.get("skills_used") or []
    tool_summary = audit.get("tool_call_summary") or {}
    compliance_meta = audit.get("compliance_blocklist_meta") or {}
    soft_blocklist = audit.get("compliance_blocklist_soft") or []
    industry_hits = compliance_meta.get("industry_hits") or []
    audit_rows = [
        ("policy_profile", audit.get("policy_profile") or ""),
        ("supervisor_result", nodes_to_run),
        ("supervisor_rationale", audit.get("supervisor_rationale") or ""),
        ("skills_used", len(skills_used)),
        ("tool_calls", tool_summary.get("count", 0)),
        ("tool_errors", tool_summary.get("errors", 0)),
        ("compliance_industry_hits", ",".join(industry_hits) if industry_hits else "none"),
        ("compliance_blocklist_soft", ",".join(soft_blocklist) if soft_blocklist else "none"),
    ]
    print(_format_table(["AUDIT", "VALUE"], audit_rows))
    print()

    rules_snapshot = audit.get("rules_snapshot") or {}
    compliance_blocklist = result.get("compliance_blocklist")
    if compliance_blocklist is not None:
        rules_snapshot = dict(rules_snapshot)
        rules_snapshot["blocklist"] = compliance_blocklist
    if rules_snapshot:
        current_map = _rules_current_values(result, rules_snapshot)
        blocked = current_map.get("blocklist") not in {"", "none"}
        rules_rows = []
        for key in sorted(rules_snapshot.keys()):
            val = rules_snapshot.get(key)
            if isinstance(val, list):
                val = ",".join(str(x) for x in val)
            current = current_map.get(key, "")
            val_fmt = _format_num(val)
            cur_fmt = _format_num(current)
            _status, failed = _rule_status(key, val_fmt, cur_fmt, blocked)
            icon = "⛔️" if (key == "blocklist" and failed) else ("⚠️" if failed else "✅")
            rules_rows.append((failed, key, val_fmt, cur_fmt, icon))
        rules_rows.sort(key=lambda item: (not item[0], item[1]))
        print(
            _format_table(
                ["RULE_KEY", "VALUE", "CURRENT", "STATUS"],
                [(k, v, c, s) for _, k, v, c, s in rules_rows],
            )
        )
        print()

    findings = result.get("findings") or []
    agent_reason_rows = []
    has_macro = False
    for finding in findings:
        risk_type = finding.get("risk_type")
        if risk_type not in {"macro", "compliance"}:
            continue
        if risk_type == "macro":
            has_macro = True
        summary = _shorten(finding.get("summary") or "")
        evidence = _shorten(_evidence_refs(finding.get("evidence")))
        recs = finding.get("recommendations") or []
        if isinstance(recs, list):
            rec_text = "; ".join(str(r) for r in recs if r)
        else:
            rec_text = str(recs)
        rec_text = _shorten(rec_text or "none")
        agent_reason_rows.append((risk_type, summary, evidence, rec_text))
    if not has_macro:
        agent_reason_rows.append(("macro", "未运行", "原因来自 supervisor_rationale", "none"))
    if agent_reason_rows:
        print(_format_table(["AGENT", "SUMMARY", "EVIDENCE", "RECOMMENDATIONS"], agent_reason_rows))
        print()


def _print_json(payload: Dict[str, Any], pretty: bool) -> None:
    if pretty:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single risk assessment case.")
    parser.add_argument("--profile", default="default", help="policy profile name")
    parser.add_argument("--pretty", action="store_true", help="pretty JSON output (with -JSON)")
    parser.add_argument("--table", action="store_true", help="print user view as tables")
    parser.add_argument("--json", "-JSON", action="store_true", help="print JSON output")
    args = parser.parse_args()

    config = RuntimeConfig.from_env()
    case = _sample_case(args.profile, config)
    state = new_state(case["intent"], case["context"])

    llm = _load_llm(config)
    graph = build_graph(llm=llm, config=config)
    result = graph.invoke(state)

    minimal_view = _build_minimal_view(result)
    payload = _build_payload(result, minimal_view)

    show_table = args.table or not args.json
    show_json = args.json

    if show_table:
        _print_tables(result, minimal_view)

    if show_json:
        _print_json(payload, args.pretty)


if __name__ == "__main__":
    main()
