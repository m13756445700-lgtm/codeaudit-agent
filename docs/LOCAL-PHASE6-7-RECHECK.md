# Phase 6 / 7 本地新环境核验记录

日期：2026-09-22。基线：CodeAudit Agent BRD+PRD V1.0。

## 结论

| 范围 | 本轮结论 | 实际证据 |
|---|---|---|
| 本地回归 | 通过 | 28 passed in 12.47s |
| Phase 6 OctoBus | 本地 SQL 样例范围通过 | 真实 MCP 12 项检查通过；五个受控方法均调用成功 |
| Phase 7 Agent Compose | 未通过 | Codex 沙箱实际启动；模型请求重复 HTTP 401，90 秒后运行失败 |

不将既有服务器结果替代此次本地核验；不将配置/容器启动成功计为模型联动成功。

## 环境及修复

- Docker Engine 29.8.0，Compose 5.5.1，Linux arm64。
- 固定摘要 OctoBus 二进制；服务运行环境为固定摘要 guest 镜像中的 Python 3.11、Node 22。
- 首次服务实例启动失败：src/main.js 缺执行权限，已修复工作区入口文件权限并重新导入。
- 首次扫描失败：Ubuntu 26.04 Python 3.14 与 protobuf 4.25.9 不兼容。调整本地 Dockerfile 使用 Python 3.11 后，真实扫描与容器 pip check 均通过。
- Docker 共享目录读取出现 I/O 错误；通过打包后复制到容器独立存储完成核验。原始工作区未清空。
- 本地验收服务地址仅绑定 127.0.0.1:19000，管理端口仅绑定 127.0.0.1:17410。端口绑定不替代最终权限/网络隔离验收。

## Phase 6 核验

Service：code-audit-service；Instance：code-audit-local；Capset：code-audit-agent。
仓库：lab；固定 commit：af482b5a62e1af3b8fae3908328f229852986337。

- 缺失令牌、错误令牌：均 HTTP 401。
- tools/list：恰好五个方法。
- InventoryRepository、ScanCandidates、ReadCodeSlice、HashEvidence、RunValidation：全部真实调用成功。
- ScanCandidates：2 个候选。
- 原始 SQL 拼接案例：VERIFIED，返回 Source/Dataflow/Sink/Protection/Reachability/Evidence Integrity 六类字段。
- 参数绑定案例：REJECTED。
- 仓库越界、缺失固定 commit、文件路径越界、超过 100 行读取：均拒绝。
- 服务容器重建后已有 Service/Instance/Capset 成功恢复，再次调用通过；此项不等于主机重启验收。

证据位于 ../runs/local-recheck/：phase6-result.json、tools-list.json、各 MCP 返回 JSON、octobus-access.jsonl、latest-service-runs/。复测入口：scripts/verify_local_mcp.py。

## Phase 7 核验

- 受限 guest 镜像实际构建成功，镜像内 runner 精确补丁通过。
- guest 中 Codex 0.144.1；shell_tool、unified_exec 配置关闭后显示 false。
- apply_patch_freeform 在此版本为 removed；不能用该开关证明写入工具已被禁用。
- Agent Compose 项目校验及 up 成功，实际创建并启动 Codex 沙箱。
- 本次 Run：058b00df8e924dd17a05fd080f8b6b2db5e97d6bfce7ada82b596bfb3e8b6484。
- 模型通道 /llm/openai/v1/responses 重复返回 HTTP 401，运行以 context deadline exceeded 失败（90025ms），没有模型驱动的工具调用完成证据。
- 本地模型后端未配置为已验证的可用接口。宿主 Codex ChatGPT 登录不自动提供 Agent Compose 的模型代理凭据；需明确接口地址、模型和安全注入凭据后复验。401 的具体鉴权层还需在配置后继续确认。

未通过项目：真实 Codex→MCP→Gate 完整链路、模型输出校验器接入运行流程、全部候选覆盖校验、Shell/写入/公网访问负向实测。不得进入 Phase 8 并宣称 Phase 7 已完成。

## 下一步

1. 在本地私有配置文件补齐模型接口和凭据，禁止将密钥发到聊天或写进验收报告。
2. 先验证单次模型响应，再执行完整审计，减少失败重试及 token 消耗。
3. 完成输出一致性和权限负向测试；保存本次运行关联的日志与裁决后更新结论。
