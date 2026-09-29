# 架构与可检查的 Agent 行为

唯一生产入口 `agent.cli → agent.v2.cli`。Intake 获取仓库后，Engine 将导航摘要交给真实模型。模型 function calls 是下一动作来源：submit_plan、hypothesis、use_tool、submit_decision、finish。没有固定的“先扫描，再逐项转述”脚本。

`use_tool` 受名字/参数/范围约束，传输层把 audit_id 和动作送到 OctoBus ExecuteTool。Node SDK bridge 根据固定 allowlist 路由到独立 repo-tools 或 static-analysis worker。repo-tools 提供文件/范围读取、搜索、词法符号/调用导航、依赖摘要、Git diff、判断知识；static-analysis 以固定参数执行 Semgrep，不执行仓库 build/test/hooks。

Engine 不接受目标文件中的指令作为系统权限。快照只读，读取证据有路径、行数、大小及哈希边界；模型读记录用于 Gate。知识工具返回版本/哈希，不只是 README 中的一段百科。Git parent/initial diff 有单独完整性检查；ZIP/local 无基线就明确 unavailable。

## 判断和证据

模型负责 Source、传播/变换、Sink、输入控制、Validation/Sanitization、Reachability、Security Boundary、攻击条件、严重度、反证、Unknown、Confidence 和修复。Gate 校验字段类型、源码引用和已读记录，能将不充分的结论降级为 INSUFFICIENT_EVIDENCE，不能确认新的漏洞。哈希一致不代表语义因果正确，仍需人工复核。

实际覆盖由工具读记录独立计算，包含文件总数、已读文件、行数和未读列表。finish 只表示预算内调查完成；不会由模型一句“读完了”替换真实覆盖。JSON 工件是完整机器证据，Markdown 是入口。

## agent-compose 的真实角色

独立 daemon 创建 Docker 沙箱，执行 scripts/run-agent.py → 同一 Engine。daemon 会设置 provider 模型代理环境，因此操作员模型凭据用 CODEAUDIT_LLM_* 传给 launcher，再显式映射；不让运行框架的代理配置意外替换审计模型。provider 字段不是安全判定实现。

## 静态对照为何仍保留旧模块

`agent/v2/static_baseline.py` 仅由验收脚本/测试导入，调用已验证的 analysis + report + validator 及四种语义分析器。preflight、evidence、knowledge 是它的传递依赖。评估适配器以完整快照哈希替代原 Git/framework inventory，分析器和 Gate 保持原样，结果包括 VERIFIED/REJECTED/NEEDS_REVIEW 及建议。

这些模块是正式公平对照，不是生产 fallback。旧 agent.service、配置/日志服务、workflow、旧提示词、旧 OctoBus 包和旧部署已退出发布。模块保留原路径是为了避免发布期改变稳定语义。

## 审查证据

现场检查 audit_plan.json、tool_calls.jsonl、findings.json、coverage.json 和 report.md；不同输入应有实际不同的计划/动作，跨文件发现必须引用真实文件。对照同一快照的静态信号与完整静态 verdict。单次 LLM 输出有随机性，不能仅以 API 成功作为正确性验收。
