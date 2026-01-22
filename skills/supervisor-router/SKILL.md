---
name: supervisor-router
type: chain
inputs:
  - candidates
  - validation
  - data_quality
  - snapshot_metrics
  - rule_findings
  - policy_profile
outputs:
  - nodes_to_run
  - rationale
policy_version: "local-default"
skills_hash: ""
tools:
  allowlist: []
  max_calls: 0
  timeout_ms: 0
  require_evidence: false
limits:
  max_retries: 1
cost_budget:
  llm_tokens: 1000
  tool_calls: 0
snippets:
  - snippets/decision_rubric.md
---

# 调度路由器

用途：基于当前上下文与风险信号决定运行哪些分析节点。

规则：
- 只能从提供的候选列表中选择。
- 除非有明确理由，否则必须保留合规节点。
