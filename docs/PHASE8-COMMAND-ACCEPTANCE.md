# Command Injection 首批验收记录

日期：2026-09-23。范围：Java/Spring受控样例，既有SQL能力回归。

## 结论

首批Command能力、本地OctoBus联调和一次真实模型审计已通过。Phase8整体尚未完成；SSRF及Path Traversal待实施。

## 验证结果

| 验证层 | 实际结果 | 证据 |
|---|---|---|
| 本地回归 | 72项全部通过，18.58秒 | runs/phase8-command/static-flow-regression.txt |
| 原SQL MCP回归 | 12项通过 | runs/local-recheck/phase6-result.json |
| Command三候选MCP | VERIFIED、NEEDS_REVIEW、REJECTED，与Gate一致 | runs/phase8-command/mcp-result.json |
| 跨文件静态调用MCP | Controller→CommandRunner，VERIFIED，证据包含实参与形参 | runs/phase8-command/static-flow-mcp-result.json |
| Codex/DeepSeek会话 | 17次真实调用，5个候选覆盖，最终JSON完全匹配 | runs/phase8-command/agent-recheck/summary.json |

模型成功Run：`61360ffa71d2f0f174147233b61b91d7e9afc342fdf2c9fc67c13437a5e96780`。

## 版本与范围边界

模型复验对应 `codeaudit-octobus:phase8`：三个Command候选及两个SQL候选。后续跨方法实现对应 `codeaudit-octobus:phase8-flow`，已独立完成本地回归及真实MCP验证，未再消耗模型额度重跑跨方法会话。

跨方法仅支持唯一解析的public static调用链，最多6层。重载、动态分派、断链、未知过滤等均保留NEEDS_REVIEW。测试目录调用链不作生产可达。没有运行被审计样例中的危险命令。

TC-05采用用户已确认的勘误，详见 PHASE8-COMMAND-ERRATUM.md。原BRD保留。

## 失败记录与修正

前次模型Run有一次越界读取，严格验收失败。此次仅调整执行提示：逐候选使用原始行号、单行读取、不猜测文件长度。Gate与会话验收规则均未放宽。失败原始记录保留。

## 下一步

按BRD实施SSRF的正负样例、地址解析及保护规则证明，先测试后报告；随后实施Path Traversal。不得以当前Command结果宣称全部Phase8已完成。
