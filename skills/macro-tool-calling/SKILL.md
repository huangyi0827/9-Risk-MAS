---
name: macro-tool-calling
type: agent
inputs:
  - snapshot_metrics
  - data_quality
  - tool_results
outputs:
  - macro_finding
policy_version: "local-default"
skills_hash: ""
evidence_prefixes:
  - snapshot_metrics.
  - rules.
  - tool:
tools:
  allowlist:
    - macro_timeseries
    - macro_search
  max_calls: 3
  timeout_ms: 8000
  require_evidence: false
limits:
  max_retries: 1
cost_budget:
  llm_tokens: 1200
  tool_calls: 3
snippets:
  - snippets/evidence_rules.md
---

# 宏观工具型 Agent

用途：使用许可工具评估宏观环境并引用出处。

要求：
- 仅在必要时调用工具。
- 证据必须引用工具输出或 state 指标。
