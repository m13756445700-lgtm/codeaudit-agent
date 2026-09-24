# 实践判据、来源与知识影响

这里记录的是本项目实施中的真实实验与通用审计知识，不宣称个人客户项目或历史工单积累。是否符合原题§5.2对实践深度的评定由考官判断。

| 判据 | 依据与已发生实验 | 执行位置 | 可复核材料 |
|---|---|---|---|
| 参数名一致不能证明Source到Sink | 固定正反例与类型/调用解析负向测试 | agent/analyzer.py | tests/functional/test_pipeline.py、test_gate_integrity.py |
| 有限映射是保护，但无证据时不能推定安全 | 同Commit启停ALLOWLIST知识，状态发生变化 | agent/analyzer.py、knowledge/loader.py | evidence/review/cases/TC-12.json |
| Runtime.exec单字符串不能简单等同shell注入 | Java argv探针及TC-05勘误 | agent/command_analyzer.py | scripts/probes/CommandArgvProbe.java、PHASE8-COMMAND-ERRATUM.md |
| normalize边界不足以排除符号链接逃逸 | Java真实路径探针及TC-10勘误 | agent/path_analyzer.py | scripts/probes/PathBoundaryProbe.java、PHASE8-PATH-ERRATUM.md |
| 工具退出成功不等于模型真实完成业务 | 实施中出现仅输出文本的失败；增加会话和可信结果核对 | agent/workflow/validation.py | TROUBLESHOOTING.md、evidence/review/model/ |

运行态边界：知识文件目前主要提供版本与规则开关，具体安全语义由程序执行；不能声称修改任意描述即可自动生成新分析策略。语义探针在代码中可查，原始实验日志受控保存；公开摘要与完整原始记录应区分。

答辩时展示一条规则的输入、可执行判断、输出及反例，再展示移除规则的对照；不要只念OWASP概念或枚举配置。
