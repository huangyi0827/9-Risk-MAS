证据规范：
- 仅能引用明确指标或工具输出，严禁臆测。
- 允许的 ref 前缀应来自对应 skill 的 evidence_prefixes（通常为 snapshot_metrics.*, rules.*, tool:*）。
- 使用形式：snapshot_metrics.xxx 或 tool:macro_timeseries。
- tool:* 必须带 provenance（source/timestamp/params_hash）。
- evidence 为空时必须降低结论强度并说明不确定。
