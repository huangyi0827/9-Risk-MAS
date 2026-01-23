from __future__ import annotations

import datetime as dt
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


def main() -> None:
    codes = ["159213", "159959", "511960", "516310", "561180"]
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
        "policy_profile": "default",
        "aum": 1000000.0,
    }

    asof_date = previous_trading_date(intent["date"])
    calibrate_rules(asof_date, len(intent["targets"]))
    calibrate_macro_series(asof_date)

    mas = RiskMAS(output="table")
    result = mas.run(intent=intent, context=context)
    if isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
