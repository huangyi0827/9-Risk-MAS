决策标准：
- rule_level 优先，report_level 兜底（不要简单取最大 severity）。
- pass：无显著风险或约束。
- warn：风险上升但不触发强制约束。
- restrict：需要在执行前修改方案。
- block：违反硬性约束或包含禁投标的。

输出要求：
- 输出需包含 agent、risk_type、severity、summary、metrics、evidence。
- 缺少证据时不得强行给出确定性结论。
