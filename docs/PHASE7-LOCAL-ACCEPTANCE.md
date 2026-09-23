# Phase 7 本地验收报告

版本：V1.0；日期：2026-09-22；需求基线：CodeAudit Agent BRD+PRD V1.0。

## 结论

**Phase 7 在本地 Docker、当前 SQL 样例及已配置 DeepSeek 接口范围内通过。**
本轮验证 Codex Agent 经 OctoBus 调用受控方法，Evidence Gate 独立给出裁决，运行后校验器验证最终输出。未以模型文字或单独退出码替代工具执行证据。

| 项目 | 实测结果 |
|---|---|
| 模型接口 | Responses API 探测 HTTP 200，completed |
| Agent Compose | Codex 实际运行成功，用时 28.113 秒 |
| 模型 | deepseek-flash；Agent provider 保持 codex |
| 工具调用 | 8 次受控 MCP 方法调用，全部 HTTP 200 |
| 候选覆盖 | 2/2；每个均有读取、哈希、验证调用 |
| Gate 裁决 | 原始 SQL 拼接 VERIFIED；参数绑定 REJECTED |
| 最终输出 | 原始 JSON；与当前会话实际工具响应及服务端保存结果完全一致 |
| 权限负向 | 无终端/写入/网页工具执行事件；测试文件实际不存在；有效策略 read-only / restricted network |
| 回归 | 37 passed in 7.83s |
| 最终镜像 | runner SHA256 与成功会话一致 |

## 证据索引

- 成功 Run ID：`5698e0cd6a327085ff5c78219f876c4eab31c3e0c6a951bee501a29306aab4da`。
- 固定仓库 commit：`af482b5a62e1af3b8fae3908328f229852986337`。
- `../runs/local-recheck/phase7/result.json`：验收运行入口和结果。
- 对应 attempt 目录：`run.json`、`sessions/`、`trusted-runs/`、`verified-output.json`。
- `audit-correlated.json` / `audit-result.json`：3 条初始化/目录事件及8次受控方法调用；与成功运行时间对应。
- `permission-run.json` / `permission-sessions/` / `permission-result.json`：权限负向用例、实际执行记录和文件不存在检查。
- `runner-integrity.json`：成功沙箱和最终镜像 runner 字节一致性。
- `regression.txt`：最终完整回归结果。

## 本轮修复

1. 模型通道：加载用户提供的本地凭据和 Responses API 配置，消除之前的401问题。真实凭据仅存在私有配置中。
2. MCP授权：Codex无交互模式原先取消工具调用；现在显式列出五个受控工具，并仅为这五个工具配置批准策略。保持Shell和网页工具关闭，文件系统只读。
3. 参数契约：明确使用 file、line、可选 end_line；禁止模型猜测 start_line/path 等字段，要求串行调用，避免无效请求和并发冲突。
4. 输出验证：新增 verify_session；使用宿主收集的实际 Codex 事件检查调用，绑定 repository/commit、候选覆盖和本次验证run_id，并与服务端文件逐字段比较。
5. 有限重试：实际运行脚本最多两次尝试；失败会留存并返回失败，不能据此生成成功结果。
6. 部署参数：guest构建允许通过 CODEAUDIT_MCP_TOOL_PREFIX 指定已核验实例的工具前缀；默认是本地实例，迁移前需匹配服务目录，不能宽泛批准全部工具。

## 失败记录与处理

- 首次接入模型后的运行中，工具被取消；修复专用MCP授权后重新执行。
- 第二次运行中 ReadCodeSlice 使用错误字段而失败，最终回复有额外文字；该次未通过验收。参数说明及严格输出校验补齐后，成功运行通过所有检查。
- 完整回归曾出现1项Semgrep扫描失败（36通过），当时错误记录未给出详细原因；独立扫描随后无错误，相关15项测试通过，最终完整37项通过。保留该记录，不将一次通过视为共享目录稳定性已充分证明。

## 边界

- 验收仅覆盖当前两个 SQL 测试候选，不能推导为全部Java框架或全部漏洞类型已支持。
- 权限测试针对Agent暴露能力、实际调用事件、文件结果和有效沙箱策略。**不是容器级公网防火墙或完整沙箱逃逸验收**；模型代理和MCP自身仍需要网络连接。
- guest中Codex为0.144.1；仍提示deepseek-flash模型metadata缺失，但本次调用和结果校验通过。
- 独立 sandbox 子进程探测遇到 bwrap namespace权限限制并拒绝启动；本轮没有通过放开容器特权绕过该限制。
- 未替代服务器部署、主机重启恢复、最终生产权限配置验收。
- Phase8–10尚未完成；本轮未擅自推进漏洞类型扩展。

## 复测与下一步

已有本地服务及私有配置就绪时，使用项目虚拟环境执行 `scripts/run_phase7_verification.py`（设置 PYTHONPATH 指向项目根目录），脚本运行真实Agent并验证结果。私有配置、令牌及runs目录不应提交或对外分享。

下一阶段按BRD推进Command Injection，再处理SSRF、Path Traversal；每阶段先测试并报告后继续。

配置参考：[OpenAI MCP工具授权文档](https://learn.chatgpt.com/docs/extend/mcp)、[DeepSeek Responses API](https://api-docs.deepseek.com/zh-cn/guides/responses_api/)。
