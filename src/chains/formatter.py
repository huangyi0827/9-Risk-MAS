from __future__ import annotations

import json
from typing import Any, Dict


def format_output(decision: Dict[str, Any], report: Dict[str, Any]) -> str:
    payload = {
        "decision": decision,
        "risk_report": report,
    }
    return json.dumps(payload, indent=2, sort_keys=True)
