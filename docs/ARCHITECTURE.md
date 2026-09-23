# 架构与证据责任边界

版本1.0；2026-09-23；用于代码评审。

| 层 | 实现 | 责任 |
|---|---|---|
| 模型规划 | agent-compose.yml、agent/prompts/ | 调用和解释，不自行裁决 |
| 能力入口 | octobus/code-audit-service/ | 输入约束、进程边界、五方法 |
| 资产与候选 | agent/preflight.py、scanner/ | 固定Commit、实际Semgrep，候选不是漏洞 |
| 专项证明 | analyzer.py、command_analyzer.py、command_flow.py、ssrf_analyzer.py、path_analyzer.py | 有界数据流、保护和可达性分析 |
| 知识 | knowledge/java-spring/ | 保护规则、误报规则及版本 |
| 证据 | agent/evidence/ | 文件行号、内容哈希、Commit绑定 |
| Gate | agent/validator/gate.py | 独立读取和重新核验证据 |
| 报告 | agent/report.py、schemas/ | Finding JSON及Markdown |
| 会话验收 | agent/workflow/validation.py | 真调用、候选覆盖、结果与可信记录一致 |

五个方法为InventoryRepository、ScanCandidates、ReadCodeSlice、HashEvidence、RunValidation。共享JSON字符串契约；repository、commit、file、line、end_line按具体方法限制，拒绝未知字段及越界输入。

VERIFIED需要Source、Dataflow、Sink、Protection、Reachability、Evidence Integrity六类证据。Schema只验证结构，不能证明漏洞。模型输出与服务可信记录不一致时会话验收失败。

下一步评审：先检查一对正反例，再阅读Gate和负向测试，最后对照实际模型调用摘录。
