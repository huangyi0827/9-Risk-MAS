---
name: liquidity-execution-assessor
type: chain
inputs:
  - snapshot_metrics
  - policy_profile
outputs:
  - liquidity_finding
policy_version: "local-default"
skills_hash: ""
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

# 流动性执行评估器

用途：评估流动性风险与执行可行性。

要求：
- 使用加权点差与 ADV 指标作为证据。
- 输出清晰的 severity 与建议。
