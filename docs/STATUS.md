# 实施状态

> 最新结论（2026-09-23）：Phase1–10在BRD及已确认勘误的限定范围内验收通过。全量回归121项通过；服务器12/12案例通过，整机重启后SSH、三个服务、四类MCP回归及真实模型调用通过。下方早期表格和记录为历史，最终证据见PHASE10-SERVER-ACCEPTANCE.md及ACCEPTANCE-MATRIX.md。

需求基线：docs/BRD-PRD.md，原文 SHA256 见 BASELINE.sha256。

| Phase | 状态 | 证据 |
|---|---|---|
| 1 Skeleton | 本地测试通过 | pytest：5 passed；配置越界/符号链接、日志字段、Schema、CLI |
| 2 Static Scan | 实施及测试中 | 真实 Semgrep 安装与 TC01/02 扫描 |
| 3–10 | 未完成 | 不计入交付完成率 |

尚未进行 Java 构建、云端部署、Codex 联动、OctoBus 注册、重启恢复。当前无 Java Runtime。既有 Calculator/OpenCode 测试不能替代 CodeAudit 验收。

## 2026-09-21 工作区接续核查（以本节为当前口径）

- 已保留 CLI 新增的 preflight、analyzer、evidence/model、validator/gate、report 及 audit CLI；这些文件修改时间为 2026-09-18 17:26–17:28。
- 本轮实际运行现有测试：6 passed，1 failed（146.34 秒）。真实 Semgrep 候选扫描两次尝试后 SCAN_FAILED；不能沿用此前7项通过作为当前环境结论。
- 额外负向探测：不存在文件的引用配合自报 integrity PASS 和匹配摘要，Gate 返回 VERIFIED。该项不符合需求，Phase4 未验收。
- analyzer 当前通过同名参数建立 source/sink 配对，尚未验证真实跨函数连接；Phase3 未验收。
- 当前仅发现两个测试文件；新增模块没有对应验收测试。工作目录未发现 Git 元数据，无法用提交差异确认CLI进度。
- 接续顺序：定位扫描失败 → 补证据真实性/断链负向测试 → 修复流水线和Gate → 按Phase报告后推进。复用已有代码，避免重建骨架或重复阅读完整BRD。

## 2026-09-22 接续（最新口径）
- Phase2：修复改变HOME导致的Semgrep启动超时；真实扫描测试2通过。
- Phase3：固定commit、AST有限跨函数追踪、篡改与断链负向测试6通过。
- Phase4：独立复读与重分析Gate，专项8通过；不再接受自报PASS。
- Phase5：知识开关对照通过；累计本地回归曾为24通过。
- Phase6：用户明确确认“已经验证完成”；保留该确认，不冒充本轮独立云端复验。
- Phase7：新增Codex项目配置、受限guest补丁、模型结果一致性模块；本轮相关测试6通过。远端构建、Codex实际MCP调用、权限负向验收待执行，见 PHASE7-RUNBOOK.md。
- Phase8–10：未开始/未验收，不计完成。
- 本轮最终回归：28 passed in 7.68s；pip check 无依赖冲突。此为本地测试，不替代Phase7服务器验收。

## 2026-09-22 本地 Docker 重新核验（最新口径）
- Phase6：真实 OctoBus MCP 12项检查通过，五方法成功，SQL正例VERIFIED/绑定负例REJECTED；见 LOCAL-PHASE6-7-RECHECK.md。
- Phase7：受限镜像构建与实际沙箱启动通过；模型请求401，90秒超时失败，整体未通过。尚需模型配置、结果校验接入和权限负向测试。
- 回归28通过；容器pip check通过。未推进Phase8。

## 2026-09-22 Phase7最终本地验收
- 成功Run：5698e0cd6a327085ff5c78219f876c4eab31c3e0c6a951bee501a29306aab4da。
- 8次受控方法调用全部HTTP200；2/2候选覆盖；最终JSON与真实Gate输出一致。
- 1 VERIFIED、1 REJECTED；权限能力负向检查通过，非容器级防火墙验收。
- 最终回归37 passed in 7.83s；Phase8–10未完成。

## 2026-09-23 Phase8 Command 首批本地验证
- 原TC-05语义勘误已获用户明确同意；原BRD未改。详见 PHASE8-COMMAND-ERRATUM.md。
- 新增Command候选规则、有限AST参数证明、类别路由；Gate独立复读并核验类别与六类证据。
- 修正正例VERIFIED、固定映射负例REJECTED、原单字符串样例NEEDS_REVIEW。
- 真实Semgrep找到3个Command候选，受控RunValidation Python入口结论一致。
- 最终全量回归58 passed in 15.63s；Java17无网络隔离语义探测通过。日志在 runs/phase8-command/。
- 首次扫描测试失败，直接复查无扫描错误，后续两轮回归通过；未认定根因。
- Phase8仍未完成：跨方法Command、实际容器联调、SSRF、Path Traversal待做；没有把本地结果当成OctoBus/Codex验收。

## 2026-09-23 Phase8 实际服务联调
- codeaudit-octobus:phase8 镜像已构建并部署到本地；此前容器停止并保留为 codeaudit-local-octobus-phase7-backup。
- SQL原有12项MCP检查通过；Command三候选读取、摘要、验证全部完成，结论为VERIFIED/NEEDS_REVIEW/REJECTED。
- Codex/DeepSeek单次Run bac57466885fcfe699de9ef5cd53e797b947e4305e2381f26b50bd4a9b269963 未通过严格验收。模型有一次越界读文件，工具返回CONTROLLED_METHOD_FAILED；校验器拒绝该会话，没有降低标准。
- 已收紧下一次执行提示为逐候选原始行号、单行读取；尚未重跑，未宣称修复已验证。
- Phase8仍未完成，下一步先重验模型会话，再补跨方法Command及SSRF/Path Traversal。

## 2026-09-23 模型复验及Command跨方法验证（最新）
- 模型复验通过：Run 61360ffa71d2f0f174147233b61b91d7e9afc342fdf2c9fc67c13437a5e96780；17次真实MCP调用，5个候选全部覆盖，最终JSON与可信工具记录一致。2 VERIFIED、2 REJECTED、1 NEEDS_REVIEW。
- 上述模型验收对应原 phase8 镜像，不冒充后续跨方法版本的模型验收。
- 新增最多6层、唯一静态类型解析的Command跨方法证明。动态实例分派、未知过滤及歧义保持NEEDS_REVIEW。
- 新增14项跨方法测试；最终全量72 passed in 18.58s。
- phase8-flow镜像已部署；SQL的12项MCP检查、Command三候选验证、跨文件Controller→CommandRunner的真实五方法调用全部通过。
- 证据：runs/phase8-command/agent-recheck/summary.json、static-flow-regression.txt、static-flow-mcp-result.json。旧容器均保留为停止状态，未并发使用数据卷。
- Phase8仍在实施；SSRF、Path Traversal尚未完成。下一批按BRD继续SSRF，不扩大为通用Java静态分析器。

## 2026-09-23 SSRF首批验证（最新）
- SSRF分析、规则、类别路由已接入；TC-07 VERIFIED、TC-08 REJECTED、前缀检查NEEDS_REVIEW。
- 全量95 passed in 28.29s；真实MCP验证及SQL/Command/跨文件调用回归通过。
- 真实Codex/DeepSeek Run 73f5d510128b93a2a9c5a2e144e115b4e42203100ff14a1a7e1e7105560b7567 验收通过，17次真实调用，5个候选覆盖，最终JSON与可信工具结果一致。
- 当前镜像codeaudit-octobus:phase8-ssrf。首轮扫描退出-9，后续分开构建与测试后通过，根因未确认。
- SSRF支持边界及DNS/重定向限制见PHASE8-SSRF-ACCEPTANCE.md；未进行任意外部HTTP探测。
- Phase8仍未整体完成，下一步实施Path Traversal，之后做四类漏洞汇总验收。

## 2026-09-23 Path Traversal首批实现（安全负例待确认）
- 新增Files.readString候选规则与路径数据流分析；TC-09危险正例的六类证据及独立Gate验证通过。
- 新增14项路径测试；全量109 passed in 140.20s。
- Java17无网络隔离探测证实：normalize+startsWith仍可经符号链接读到基目录外；toRealPath后边界检查拒绝该路径。见runs/phase8-path/java17-probe.txt。
- 已请求用户确认TC-10验收勘误，尚未收到答复。原BRD未改；安全负例未实施/验收，不计Phase8完成。
- 运行中容器保持phase8-ssrf；新增Path能力仅本地测试通过，真实MCP/模型联调待安全负例补齐后执行。
- 具体边界见PHASE8-PATH-REVIEW.md。

## 2026-09-23 Phase8–10汇总（取代以上历史待办状态）

- 用户已确认TC-10验收勘误，原BRD保持不变。真实路径边界负例已实施；原normalize样例保持NEEDS_REVIEW。并发文件系统变更不在该静态证明保证范围内。
- Phase8限定场景通过：最终全量回归121 passed in 56.66s；SQL、Command、SSRF和Path真实MCP回归通过。Path模型Run `a2a274853ac075aaeb405a0bebb051f2c850fbbe0392d39c32c86d08ee2daca6`通过，17次真实MCP调用覆盖5个候选。
- Phase9通过：Linux OctoBus容器内12/12 BRD验收案例通过，详见ACCEPTANCE-MATRIX.md及runs/phase9-container-evidence/。此前macOS扫描退出-9的失败记录保留，未认定根因。
- Phase10本地部分通过：Java17/Maven实际构建Demo，隔离容器启动及3项HTTP检查通过；OctoBus和Agent Compose重启后的四类MCP回归通过。
- 重启后的模型验收通过：Run `98bf59ccc2f7e87d503d040061d1d12cd17dc45e723cd9880e4ce243ff88bd1e`，SQL结果VERIFIED/REJECTED。证据见runs/phase10-local/recovery-agent/result.json。
- Phase10仍未完成：目标服务器资源、部署、整机重启恢复和SSH验收待执行。已请求服务器地址或SSH别名及用户名，等待用户补充。当前不能宣称V1.0所有交付条件完成。
- 下一步仅推进PHASE10-LOCAL-ACCEPTANCE.md列出的服务器验收，不扩大功能范围，也不重复已通过的模型测试。

## 2026-09-23 Phase10服务器验收完成

- 服务器资源符合目标规格；独立CodeAudit部署完成，原服务保留。
- 服务器12/12案例、四类真实MCP、Java Demo三项接口、重启前模型会话通过。
- 用户授权一次整机重启；启动标识变化，SSH重新登录，三个新增容器自动恢复。
- 重启后Demo三项接口、四类MCP回归及真实模型会话通过。Run：cb1b878c2ea7efb28e0829d7fcf52d3c8b7af45ac96d7d7d3ee2e75f6b0e87ba。
- 本阶段修改仅为验证脚本环境参数与部署恢复定义；服务器实际调用已验证。未重复运行无代码变更的121项核心回归。
- 证据已同步至runs/phase10-server/evidence；最终范围、失败记录与恢复说明见PHASE10-SERVER-ACCEPTANCE.md。
