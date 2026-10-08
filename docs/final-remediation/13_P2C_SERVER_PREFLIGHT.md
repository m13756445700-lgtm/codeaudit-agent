# P2-C 服务器发布预检报告

版本：1.0｜日期：2026-10-08｜范围：最终 main、本地隔离构建、8.130.121.3 只读调查。

## 1. 验收结论

**P2C_PREFLIGHT_GATE = CONDITIONAL；当前不具备安全切换条件。** 最终源码与新镜像身份一致，252 项回归、Schema、构建和隔离 Smoke 通过。现有服务正常，但完整数据备份及恢复验证缺失、考官实际 SSH 登录未验证、现有运行应用版本无法追溯到 Git commit。未部署、未停止服务、未创建备份、未运行付费审计。

## 2. 必填状态

```text
GITHUB_MAIN_SHA: 567a9aeed8429866c8e8cd551ddb596627bdd7ae
SERVER_SOURCE_SHA: INCONCLUSIVE
SERVER_CURRENT_IMAGE_ID: sha256:a56bb11d00d0763b1978e09e5c9a05fc78ebf1cf97739b61c85f885a4ede1b36
SERVER_CURRENT_OCI_REVISION: e14c4dbd5e3b0dec6178073902d67d2765390427
FINAL_SOURCE_SHA: 567a9aeed8429866c8e8cd551ddb596627bdd7ae
FINAL_IMAGE_ID: sha256:1b207430a18eac15161663504911263030cc3ece4b4690153556d954c66163e6
FINAL_IMAGE_OCI_REVISION: 567a9aeed8429866c8e8cd551ddb596627bdd7ae
FINAL_IMAGE_REGISTRY_DIGEST: NOT_AVAILABLE_PRE_PUSH
SERVER_ENVIRONMENT: PASS
COMPOSE_VALIDATION: PASS
BACKUP_READINESS: FAIL
ROLLBACK_READINESS: CONDITIONAL
IMAGE_SMOKE_STATUS: PASS
EXAMINER_ACCESS_READINESS: CONDITIONAL
P0_REAL_POST_REJECTION: INCONCLUSIVE
UNIQUE_KNOWLEDGE_BENEFIT: NOT_ESTABLISHED
SERVER_DEPLOYMENT: NOT_STARTED
P2C_PREFLIGHT_GATE: CONDITIONAL
DEPLOYMENT_AUTHORIZED: NO
```

当前 OCI revision 是上游组件继承的标记，不能证明 CodeAudit 应用的源码版本。它不同于最终 main，但这是待替换的现有运行镜像；新构建的候选镜像与 main 完全一致。当前运行服务不能标记为“最终 main V2”。

## 3. 已执行验证与证据

所有路径相对于仓库根目录：`evaluation/final-remediation/p2-server-preflight/`。命令、时间、退出码见 `local-build/steps.json`、`server-operation.json`、`server-inventory.json`、`reviewer-readonly.json`；结果字段见 `result.json`。

| 检查 | 实际结果 | 证据 |
|---|---|---|
| GitHub main / 合并后 CI | main=567a9aeed8429866c8e8cd551ddb596627bdd7ae；run 37741956460 success | main-final.json、github-main-ci.json |
| 干净源码 | 新 clone，精确提交与 Git Tree 校验；未取用原工作区未提交内容 | local-build/clean-source.json、source-import.json、checkout.log |
| 网络替代取源 | GitHub 签名 payload 重构 merge commit，经 Git 对象哈希确认为目标 SHA；首次错误重构被拒绝，未作为有效源码 | local-build/source-import-attempts.json、source-import.json、import_final_main.log |
| Git Tree | 992a882b8c14dd4b0d0bfa3f029045938ec49d82 | local-build/release-manifest.json |
| Python / Semgrep / 回归 | 新 venv；Semgrep 1.99；252 passed；无付费模型重跑 | local-build/pytest.log、semgrep.log、dependency-resolutions.log |
| Schema | 退出码 0 | local-build/schema.log |
| 镜像 | --no-cache、linux/amd64、BUILD_SHA=最终 main；Image ID 和 OCI 已读取 | local-build/docker-build.log、image-inspect.log、release-manifest.json |
| 隔离 Smoke | 应用导入、CLI、两个 MCP 工具服务健康、OctoBus status 均通过 | local-build/docker-smoke.log |
| Compose | 本地占位配置及服务器现有真实配置均成功解析；不输出配置值 | local-build/compose-config.log、server-inventory.json |
| 考官只读入口 | status/projects/triggers/methods/runs 全部退出 0，report 可读取 | reviewer-readonly.json |
| 备份调查 | 找到历史报告包和旧配置包，未找到可验证的完整当前数据库/OctoBus备份 | backup-archive-review.json、reviewer-readonly.json |

Smoke 在本地 Docker Desktop 使用 amd64 模拟运行，未验证服务器原生运行。容器使用 `--network none`、容器内临时数据，不挂载生产卷、不绑定服务器端口；临时 Smoke 容器已由脚本清理。Smoke 证明基础组件启动，不证明端到端编排、真实模型或重启恢复。

main CI：[真实运行记录](https://github.com/m13756445700-lgtm/codeaudit-agent/actions/runs/37741956460)。本地构建器中的 `GITHUB_ACTIONS=NOT_RUN` 表示该构建器没有启动新 workflow，并不覆盖另行读取的 main CI success。

## 4. 服务器现状与版本边界

Ubuntu 22.04.5 LTS / x86_64；4 CPU；内存 7,888,076,800 字节，调查时可用 6,851,272,704 字节；根分区 41,882,943,488 字节，剩余 22,916,362,240 字节，使用率 43%。Docker 29.8.1，Compose 5.5.1；Daemon 可响应；Asia/Shanghai、NTP 已同步；负载 0.04/0.09/0.08。容量是本次观测值，复制备份和双份数据卷前需重新估算空间。

服务器有 **两个正在运行的 Compose 项目**，不能全局停机或清理：

| 项目 | 运行组件 | 应用镜像身份 | 状态 |
|---|---|---|---|
| codeaudit-github | agent-compose、octobus、repo-tools、static-analysis | 后三者 sha256:a56bb11d00d0763b1978e09e5c9a05fc78ebf1cf97739b61c85f885a4ede1b36 | 四个服务 healthy |
| codeaudit-submit20 | octobus、repo-tools、static-analysis | sha256:79185994f47847bc20a4ca55a3084fd3db80a5cdb589e76577e6fe5768841fe8 | 三个服务 healthy |

主验收入口的 controller 使用上游 pinned image `ghcr.io/chaitin/agent-compose@sha256:3117226250256b03d25815bd1bb584ade5ac225b83f55d527be122b8b75a61e8`。历史 auditor guest 镜像另为 `sha256:a7ad2a637412283936446e6899d81bb65d6fb5f6603234e5f6909a82997ee48e`、OCI 未设置。Mutable tag `codeaudit-final:2.0` 的现有服务与历史 guest 并非同一 Image ID，回滚必须分别保留。上游 OCI revision 不可当作应用 SHA。

服务器 `/opt/codeaudit-v2`、`/root/codeaudit-submit-20261007` 均非 Git 工作树，SERVER_SOURCE_SHA 无法核验。`/opt/codeaudit-v2/docker-compose.yml` SHA256 与最终 main 对应文件一致；**单个配置文件一致不代表全套应用源码一致**。controller 的创建标签仍指向 `/root/codeaudit-v2-github-acceptance/docker-compose.yml`，该路径当前不存在；现有 reviewer 通过 `/opt/codeaudit-v2` 的同名项目读取正在运行的 controller。

服务器 SSH 22 对外监听；主 daemon 17422、MCP 19015 绑定 172.17.0.1，不是公网发布。未修改端口、防火墙或 SSH。组件启动时间、挂载、健康和 restart policy 详见资产记录。controller 的 Docker socket 挂载仅供编排；考官不能直接写 socket。

`.env` / `.runtime.env` 均 root:0600；仅记录配置位置、变量名和是否填入。LLM 和两个服务认证变量存在，不代表上游模型服务已真实连通。本轮未验证模型调用。

## 5. 数据保护与回滚

主项目数据卷：`codeaudit-github-agent-data`（controller /data、审计 /workspaces）和 `codeaudit-github_octobus-data`（OctoBus /var/lib/octobus）。另一个 submit20 项目的两个数据卷必须一并保留。主卷包括 `data.db`、`data.db-wal`、`data.db-shm`、logs、sandboxes、work 和配置；观测到审计目录 149、run_summary 148、report 148。数量只代表文件存在，不代表每次审计成功或完整。

现有 `/root/consolidated-01-audits.tgz` 含 110 个 report、无数据库；`/root/codeaudit-submit-20261007/previous-deployment.tgz` 含旧 Compose/Agent 配置、无数据库。已只读读取目录清单和 SHA256，未解包或恢复。旧 tar 日志不构成备份成功证明。调查范围为 `/root`、`/opt`、`/var/backups`、`/data` 有限深度；不排除范围外/外部备份，但尚无可验证证据。

| 回滚条件 | 状态 | 发布前补齐动作 |
|---|---|---|
| 当前服务及 guest 镜像仍在服务器 | YES | 分别归档不可变身份和导出清单；不能仅保留 mutable tag |
| 当前配置可读取 | PARTIAL | 完整保存有效配置、权限、项目/卷/路径映射；旧 controller 标签路径缺失需明确替代 |
| 当前完整一致数据备份 | NO，BACKUP_READINESS=FAIL | 经单独授权取得数据库一致备份、OctoBus 状态、审计报告、配置；核验清单和哈希 |
| 恢复演练 | NOT_RUN | 在独立卷完成恢复、数据库检查、历史项目/调度/报告核对 |
| 数据向后兼容 | INCONCLUSIVE | 使用旧数据副本验证新版本；保留旧卷，不能宣称无损回滚 |
| V1 tag 对应运行镜像 | INCONCLUSIVE | Git 回滚入口已保留，但无法将现有镜像映射到 V1 commit |

SQLite WAL 存在，不能把单独复制 `data.db` 或未证明一致性的在线 tar 当成可恢复数据库备份。后续备份方式和维护窗口需审批；本轮没有创建快照。

## 6. 考官入口

codeaudit-reviewer 仅属于自身组；sudo 仅允许 root-owned `/usr/local/bin/codeaudit-review`。wrapper SHA256 与提交中的 `scripts/reviewer.py` 一致。五个只读子命令和报告读取均成功；账号不能读取两个敏感环境文件、不能写 Docker socket 或 wrapper（test 退出 1 属于预期拒绝）。

SSH 目录 0700、authorized_keys 0600、uid 1000。**实际考官 SSH 登录 NOT_RUN**：本次使用用户指定的 root 私钥，只在服务器通过 runuser 模拟考官执行只读命令。这不证明考官密钥能登录，也未证明所有环境输入/命令参数安全性；本轮权限检查范围是现有组、sudo 白名单、文件和 socket 边界。

现有调度 daily-v2-audit enabled；最近十次记录包括两次 failed，已如实保留。scheduler succeeded 不能直接推导模型参与、审计结论正确或最终 main 验收通过。OctoBus method list 有一个聚合 ExecuteTool 入口，不代表已完成每个 MCP 方法的真实调用。

## 7. 阻塞清单与下一步

1. 发布负责人：补齐完整一致备份及独立恢复演练；未完成前禁止切换。
2. 发布负责人：核实两套项目用途、当前 service/guest 镜像、有效配置和缺失 controller 源路径；确认只操作主验收项目。
3. 系统负责人：提供/使用现有考官密钥完成真实 SSH 登录；不要复用 root 身份冒充考官。
4. 发布负责人：批准新数据卷与运行路径方案；克隆数据中的 Docker sandbox 绝对路径需同步迁移验证，不能只改 Compose 卷名。
5. 发布负责人：审批本地镜像传输及服务切换后，服务器加载并重新核验 Image ID、OCI、平台；registry digest 当前不存在。
6. 验收负责人：另行授权付费 E2E 和重启恢复验证；保留两个永久限制。

部署步骤和考官验收计划见 `14_P2C_DEPLOYMENT_RUNBOOK.md`，均为未执行计划。本轮报告达到可内部 Gate Review 状态；服务器正式交付条件未满足。

## 8. 最终自检

Secret Scan 覆盖最终 main 全部受跟踪文件和本轮新报告/日志；仅三个已人工核验的占位或测试凭据匹配，没有发现已知真实凭据或私钥。见 `secret-scan.json`；该扫描不证明所有类型秘密绝对不存在。Git 历史证据文件逐一保留哈希，干净源码仍无未提交变化；见 `final-validation.json`。V1 annotated tag 对象已再次读取，peeled commit 仍为 0733933113faee3121b2c5d692ef4ee1400d4d0d。

报告达到可内部评审标准；备份、恢复与考官实际 SSH 仍需补齐。没有提交或推送本轮材料，没有服务器写入部署操作。
