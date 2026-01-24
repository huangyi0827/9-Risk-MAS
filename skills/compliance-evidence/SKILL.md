---
name: compliance-evidence
type: agent
inputs:
  - normalized
  - snapshot_metrics
  - tool_results
outputs:
  - finding_compliance
policy_version: "local-default"
skills_hash: ""
evidence_prefixes:
  - snapshot_metrics.
  - rules.
  - "tool:"
tools:
  allowlist:
    - policy_search
    - allowlist_check
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
  - snippets/decision_rubric.md
---

# 合规证据采集器

用途：评估合规风险并引用权威证据。

要求：
- 仅引用带 provenance 的工具输出或明确的规则引用。
- 有 policy_ids 时必须给出。
- 输出必须为单个 JSON，对象字段名使用英文 key：`severity`、`summary`、`evidence`、`recommendations`、`policy_ids`。
- 所有自然语言字段必须为中文。
