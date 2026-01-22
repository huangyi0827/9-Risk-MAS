---
name: risk-market-assessor
type: chain
inputs:
  - snapshot_metrics
  - policy_profile
outputs:
  - market_finding
policy_version: "local-default"
skills_hash: ""
evidence_prefixes:
  - snapshot_metrics.
  - rules.
  - tool:
tools:
  allowlist: []
  max_calls: 0
  timeout_ms: 0
  require_evidence: true
limits:
  max_retries: 1
cost_budget:
  llm_tokens: 800
  tool_calls: 0
---

# 市场风险评估器

用途：基于确定性指标总结市场风险。

要求：
- 仅使用 snapshot_metrics 作为证据来源。
- 输出结构化结果，包含 severity 与 evidence。
