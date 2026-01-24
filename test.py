from __future__ import annotations

import datetime as dt
import csv
import json
import random
from typing import Dict, List

from src import RiskMAS
from src.tools.calibrate_rules import calibrate_rules
from src.tools.calibrate_macro_series import calibrate_macro_series
from src.tools.csv_data import previous_trading_date


def _random_weights(codes: List[str], seed: int) -> Dict[str, float]:
    rng = random.Random(seed)
    raw = [rng.random() for _ in codes]
    total = sum(raw) or 1.0
    return {c: v / total for c, v in zip(codes, raw)}


def _write_positions_csv(path: str, date: str, weights: Dict[str, float], note: str = "") -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "code", "weight"])
        if note:
            writer.writerow([date, note, ""])
            return
        for code in sorted(weights.keys()):
            writer.writerow([date, code, weights.get(code)])


def main() -> None:
    codes = ["159213", "159959", "511960", "516310",'561180']
    base_date = dt.date(2025, 11, 15)
    intent_date = base_date + dt.timedelta(days=1)

    current_weights = _random_weights(codes, seed=28)
    target_weights = _random_weights(codes, seed=21)

    intent = {
        "date": intent_date.isoformat(),
        "mode": "target",
        "targets": target_weights,
    }
    context = {
        "current_positions": current_weights,
        "current_positions_date": base_date.isoformat(),
        "universe": codes,
        "account_type": "brokerage",
        "jurisdiction": "CN",
        "policy_profile": "conservative",
        "aum": 1000000.0,
    }

    asof_date = previous_trading_date(intent["date"])
    calibrate_rules(asof_date, len(intent["targets"]))
    calibrate_macro_series(asof_date)

    mas = RiskMAS(output="table")
    result = mas.run_raw(intent=intent, context=context)

    decision = (result.get("decision") or {}).get("decision")
    intent_date = intent.get("date") or ""
    intent_targets = intent.get("targets") or {}
    _write_positions_csv("intent_positions.csv", intent_date, intent_targets)
    if decision in {"pass", "warn"}:
        _write_positions_csv("post_risk_positions.csv", intent_date, intent_targets)
    elif decision == "restrict":
        recs = result.get("recommended_actions") or []
        rec = recs[0] if recs else {}
        rec_targets = rec.get("target_weights") or {}
        note = "" if rec_targets else "未生成调仓建议"
        _write_positions_csv("post_risk_positions.csv", intent_date, rec_targets, note=note)
    elif decision == "block":
        _write_positions_csv("post_risk_positions.csv", intent_date, {}, note="交易不通过，需人为干预")

    table_output = mas.run(intent=intent, context=context, output="table")
    if isinstance(table_output, str):
        print(table_output)
    else:
        print(json.dumps(table_output, indent=2, ensure_ascii=False))

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
