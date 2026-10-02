# 集中验收失败后的整改

## 已开发：判断依据契约

集中验收 job91 引用了真实 import 行，但错误声称快照存在 leading-slash 防护，且未经证据确认便限定为 Linux。新增 defense_claims 将每项防护主张绑定实际读取的实现引用及适用限制；environment_assumptions 记录前提、verified/unknown、引用和是否影响结论。影响结论的未知前提要求 INSUFFICIENT_EVIDENCE。REJECTED 必须提供 counter_evidence，防护及反证不得只引用依赖导入行。

Gate 只检查证据契约和引用，不证明自然语言主张蕴含于代码。模型遗漏某个前提、选择无关但真实的实现行，仍可能通过。它不能修复漏报，也不能代替独立语义复核。不得将新 Gate 追溯用于改写既有失败结果。

新增字段是新候选的输出契约；旧结果保持原样，不进行批量重写。引用检查失败仍只降为 INSUFFICIENT_EVIDENCE，不生成漏洞结论。

## 离线验证

2026-10-02：39 passed in 0.46s，命令：

```sh
.internal/review-venv/bin/python -m pytest -q tests/test_v2_tools_gate.py tests/test_v2_rev.py tests/test_v2_ledger.py tests/test_consolidated_acceptance.py tests/test_acceptance_review.py
```

新增7项测试覆盖虚构 guard 引用、import 伪防护、四种判断状态下的未知关键平台前提、无证据的 verified 前提。尚未运行新候选全量 Linux 测试或付费模型验证。

## next_task

1. 从已保存 job91 原始判定建立固定失败回放，区分契约拦截与真实语义纠错；补充“引用真实但无关代码”的已知限制用例。
2. 开发有界分段调查与结束前反证复核：保留模型选题和判断，每段保存证据、未解问题及覆盖；避免重复结算与无目的重复读取，明确保留未调查范围。不能通过增加预算或自动提升 PARTIAL 掩盖问题。
3. 开发完成后跑全量离线 Linux 回归，再冻结小规模失败案例验收协议。模型服务恢复后先验证这些案例，再决定是否扩大集中验收。
4. 独立案例、项目知识相对 generic 的独特收益仍待证明。只有验收通过才推送 GitHub / 更新部署。

本轮没有付费调用、GitHub 推送或生产部署。生产与远程保持91c9e7a；集中验收失败状态不变。
