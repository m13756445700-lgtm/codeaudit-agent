# 现场演示

先按部署文档启动，然后运行 `./scripts/healthcheck.sh`。四组 Demo 共用真实 agent-compose → Engine → 模型 → OctoBus → worker 链路，不需手工切换配置。

| 命令 | 输入 | 关注点 |
|---|---|---|
| `./scripts/demo.sh a` | Python原始SQL拼接 | 实际输入、传播、Sink与CONFIRMED证据 |
| `./scripts/demo.sh b` | Java固定映射/MyBatis | 读取上游映射后REJECTED；候选不等于已确认误报 |
| `./scripts/demo.sh c` | 三文件命令链 | Semgrep无候选时自主调查跨文件数据流 |
| `./scripts/demo.sh d` | 公共flask-video-streaming Git | 非基准任意Git获取、覆盖与未知事实 |

D 不是完整标注的准确率基准，也已经用于验收，不能再声称永久盲测。现场可替换为考官指定的新 URL：`./scripts/demo.sh https://github.com/OWNER/REPO.git`。任意本地路径必须先显式挂载到容器，不自动把主机全盘暴露给沙箱。

观察 stderr 进度事件：repository_intake、understanding、模型动作及判断。输出 audit_id 后导出该次完整工件（替换 AUDIT_ID）：

```bash
mkdir -p audit-output
docker compose --env-file .env --env-file .runtime.env cp \
  octobus:/workspaces/AUDIT_ID ./audit-output/
```

先读 report.md，再检查 findings.json 的 source/data_flow/sink/counter_evidence/unknowns/evidence_gate；查看 coverage.json 的未读文件；查看 tool_calls.jsonl 的模型选择与工具反馈。原始工件可能含私有源码，默认不提交 Git。`--keep-source` 保留重放快照，演示结果保存在本项目数据卷。

然后 `make ablation-test`：同快照比较真实完整静态分析和新 AI 调查。输出在 runs/v2/ablation.json。固定安全候选若静态结果为 NEEDS_REVIEW，必须按此展示，不包装成静态CONFIRMED误报。若模型本次漏报或INCOMPLETE，保留失败输出并解释，不能换历史成功冒充。

“为什么是Agent”：展示未命中规则的C案例仍有假设和调查。“如何排误报”：展示B上游固定映射证据。“OctoBus是否真用”：断开MCP地址应失败、Trace标识octobus-mcp、服务日志有实际调用。“Knowledge贡献”：读取具体决策规则/反例/哈希；历史单次ON/OFF不证明普遍因果。“新机器”：按README用独立数据卷完成启动和本演示。
