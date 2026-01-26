# Risk-MAS 练习用空心化模板（轻量版）

> 说明：仅保留函数/类/字段骨架与返回结构，避免限定实现方式。

---

## 1) 状态板块（state.py）

```python
from typing import TypedDict, Dict, List, Any, Optional

class Intent(TypedDict):
    date: str
    mode: str
    targets: Dict[str, float]

class Context(TypedDict, total=False):
    current_positions: Dict[str, float]
    current_positions_date: str
    universe: List[str]
    account_type: str
    jurisdiction: str
    policy_profile: str
    aum: float

class RiskState(TypedDict, total=False):
    intent: Intent
    context: Context
    normalized: Dict[str, Any]
    validation: Dict[str, Any]
    data_quality: Dict[str, Any]
    snapshot_metrics: Dict[str, Any]
    # 其余 slot 由学员补充

def new_state(intent: Intent, context: Optional[Context] = None) -> RiskState:
    return {"intent": intent, "context": context or {}}
```

---

## 2) 输入规范化（validate.py）

```python
from typing import Dict, Any, Tuple
from ..state import RiskState

def validate_and_normalize(state: RiskState) -> Dict[str, Any]:
    """
    输入：RiskState
    输出：normalized + validation
    """
    # TODO: 校验 intent/context
    # TODO: 生成 asof_date / universe / target_weights
    return {
        "normalized": {},
        "validation": {"is_valid": True, "errors": [], "warnings": []},
    }
```

---

## 3) 数据与指标（csv_data.py / data_quality.py / snapshot.py）

```python
# csv_data.py
import pandas as pd
from typing import Dict, Iterable, List, Any, Tuple

def load_etf_prices() -> pd.DataFrame: ...
def load_etf_basic() -> pd.DataFrame: ...
def load_macro_docs() -> pd.DataFrame: ...
def load_compliance_docs() -> pd.DataFrame: ...

def security_master_codes() -> Tuple[set, str]: ...
def previous_trading_date(asof_date: str) -> str: ...
def lookback_start_date(asof_date: str, lookback_days: int) -> str: ...

def market_metrics(
    codes: Iterable[str],
    start_date: str | None,
    end_date: str | None,
) -> Dict[str, Dict[str, float]]:
    # TODO: volatility / adv / spread_bps
    return {}

def macro_search_hits(query: str, limit: int = 5, asof_date: str | None = None) -> List[Dict[str, Any]]: ...
def compliance_search_hits(query: str, limit: int = 5) -> List[str]: ...
def macro_latest_date(asof_date: str | None = None) -> str: ...
```

```python
# data_quality.py
from typing import Dict, Any
from ..state import RiskState

def check_data_quality(state: RiskState) -> Dict[str, Any]:
    """
    输出：data_quality + data_gaps
    """
    return {"data_quality": {}, "data_gaps": []}
```

```python
# snapshot.py
from typing import Dict, Any
from ..state import RiskState

def risk_snapshot_bundle(state: RiskState) -> Dict[str, Any]:
    """
    输出：snapshot_metrics（vol/HHI/ADV/spread + delta 指标）
    """
    return {"snapshot_metrics": {}}
```

---

## 4) 编排与汇总（graph.py / gatekeeper.py / supervisor.py / reducer.py）

```python
# graph.py
def build_graph():
    """组装主流程图"""
    ...
```

```python
# gatekeeper.py
from typing import Dict, Any
from ..state import RiskState

def gatekeeper_chain(state: RiskState) -> Dict[str, Any]:
    return {"candidate_nodes": [], "gatekeeper_used": True, "gatekeeper_rationale": "ok"}
```

```python
# supervisor.py
from typing import Dict, Any
from ..state import RiskState

def supervisor_chain(state: RiskState, llm) -> Dict[str, Any]:
    return {"supervisor_used": True, "supervisor_rationale": "...", "supervisor_model": "..."}
```

```python
# reducer.py
from typing import Dict, Any
from ..state import RiskState

def reducer_chain(state: RiskState) -> Dict[str, Any]:
    return {"findings": [], "risk_report": {}}
```

---

## 5) 分析链路（market.py / concentration.py / diversification.py / liquidity.py）

```python
# market.py
from typing import Dict, Any
from ..state import RiskState

def market_chain(state: RiskState) -> Dict[str, Any]:
    return {"finding_market": {"agent": "MarketRiskChain", "risk_type": "market"}}
```

```python
# concentration.py
from typing import Dict, Any
from ..state import RiskState

def concentration_chain(state: RiskState) -> Dict[str, Any]:
    return {"finding_concentration": {"agent": "ConcentrationChain", "risk_type": "concentration"}}
```

```python
# diversification.py
from typing import Dict, Any
from ..state import RiskState

def diversification_chain(state: RiskState) -> Dict[str, Any]:
    return {"finding_diversification": {"agent": "DiversificationChain", "risk_type": "diversification"}}
```

```python
# liquidity.py
from typing import Dict, Any
from ..state import RiskState

def liquidity_chain(state: RiskState) -> Dict[str, Any]:
    return {"finding_liquidity": {"agent": "LiquidityChain", "risk_type": "liquidity"}}
```

---

## 6) Agent 与工具（macro_agent.py / compliance_agent.py / agent_utils.py / prompts.py）

```python
# agent_utils.py
from typing import Callable, Dict, Any

def wrap_tool(name: str, fn: Callable[..., Dict[str, Any]]):
    """工具封装（留空细节）"""
    ...
```

```python
# macro_agent.py
from typing import Dict, Any

def macro_timeseries(series: str) -> Dict[str, Any]: ...
def macro_search(query: str) -> Dict[str, Any]: ...

def run_macro_agent(state: Dict[str, Any], llm) -> Dict[str, Any]:
    return {"finding_macro": {"agent": "MacroToolCallingAgent", "risk_type": "macro"}}
```

```python
# compliance_agent.py
from typing import Dict, Any

def compliance_search(query: str) -> Dict[str, Any]: ...

def run_compliance_agent(state: Dict[str, Any], llm) -> Dict[str, Any]:
    return {"finding_compliance": {"agent": "ComplianceToolCallingAgent", "risk_type": "compliance"}}
```

```python
# prompts.py
MACRO_SYSTEM = "..."
COMPLIANCE_SYSTEM = "..."
```

---

## 7) 阈值板块（calibrate_rules.py / calibrate_macro_series.py）

```python
def calibrate_rules(asof_date: str, n: int) -> Dict[str, Any]:
    return {}

def calibrate_macro_series(asof_date: str, config_path: str) -> Dict[str, Any]:
    return {}
```

---

## 8) 规则与决策（decision.py / solver.py）

```python
from typing import Dict, Any, List

def decision_engine(state: Dict[str, Any]) -> Dict[str, Any]:
    return {"decision": {"decision": "pass", "rule_level": 0, "report_level": 0}}

def evaluate_constraints(metrics: Dict[str, Any], rules: Dict[str, Any]) -> List[Dict[str, Any]]:
    return []
```

```python
def constraint_solver(state: Dict[str, Any]) -> Dict[str, Any]:
    return {"recommended_actions": []}
```

---

## 9) Skills 板块（SKILL.md / output.schema.json / tool_interfaces.yaml / skills_runtime.py）

```text
skills/
├── <skill-name>/SKILL.md
├── <skill-name>/output.schema.json
├── snippets/evidence_rules.md
└── tools/tool_interfaces.yaml
```

```python
def load_skill(skill_name: str) -> Dict[str, Any]: ...
def build_prompt(skill: Dict[str, Any], snippets: Dict[str, str]) -> str: ...
def validate_output(schema: Dict[str, Any], output: Dict[str, Any]) -> bool: ...
```

---

## 10) 审计与可追溯（audit.py）

```python
from typing import Dict, Any

def _hash_payload(payload: Dict[str, Any]) -> str: ...

def audit_log(state: Dict[str, Any]) -> Dict[str, Any]:
    return {"audit": {"ruleset_version": "...", "tool_calls": [], "trace_id": "..."}}
```
