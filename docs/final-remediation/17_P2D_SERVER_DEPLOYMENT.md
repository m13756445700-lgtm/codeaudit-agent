# P2-D 最终服务器部署与交付记录

版本：1.0｜日期：2026-10-08｜范围：8.130.121.3 的 CodeAudit 项目。状态：已部署，最终交付 Gate 为 **CONDITIONAL**。

## 1. 结论与版本边界

服务器已运行 GitHub 验收源码 `567a9aeed8429866c8e8cd551ddb596627bdd7ae`。部署健康、真实模型受控审计、MCP 调用、报告生成/读取和新项目四个常驻容器重启恢复均完成实际验证。考官私钥不可用，**没有完成考官真实 SSH 登录验收**；不能写为全部交付通过。

| 发布身份 | 已验证值 |
|---|---|
| GitHub release / deployed source SHA | `567a9aeed8429866c8e8cd551ddb596627bdd7ae` |
| main CI | [37741956460：success](https://github.com/m13756445700-lgtm/codeaudit-agent/actions/runs/37741956460)，Head 与上述 SHA 一致 |
| Server Image ID | `sha256:f140f0a72acc35b48bdc5c144a0f87b25cd77d3d14f51221f2d948007f33ec3c` |
| Server OCI revision | `567a9aeed8429866c8e8cd551ddb596627bdd7ae` |
| 平台 | linux/amd64 |
| 实际运行 Compose SHA256 | `b50a17df6cc1e3a95071b9fd0729a87fea952eee22b1ab1014f606d9eecd2cdc` |
| Agent 配置 SHA256 | `3be63f5ea0a9a1514d106dc5373f67365c19a3d97f65a1265d44642f3e2e6748` |
| 源码目录 | `/opt/codeaudit-releases/main567/source`，HEAD 对应 release、工作树 clean |
| 运行目录 | `/opt/codeaudit-releases/main567/runtime` |
| 考官入口 | `/opt/codeaudit-v2` → 上述运行目录；wrapper 与 sudoers 未修改 |

部署后重新读取 GitHub main，仍为 release SHA；V1 annotated tag `refs/tags/v1-pre-v2-release` 保留，peeled commit 为 `0733933113faee3121b2c5d692ef4ee1400d4d0d`。文档在独立提交中保存，文档提交 SHA 由其 Git commit/PR 提供，**不等于镜像 OCI revision**。不能把文档提交称为已构建产品版本。

## 2. 旧服务停用范围与影响

依据实际镜像入口、Compose labels、配置目录、挂载及网络成员核验，两套项目均为 CodeAudit。停止前检查无未知共享网络成员或正在运行的其他容器使用这些 CodeAudit 数据卷。该检查是当前 Docker 配置和连接快照，不能证明不存在所有外部离线依赖。未停止 SSH、Docker daemon 或其他宿主机服务。

已停止以下七个旧容器以释放原有端口，执行的是 stop，未执行删除或清理：

- `codeaudit-github-agent-compose-1`
- `codeaudit-github-octobus-1`
- `codeaudit-github-repo-tools-1`
- `codeaudit-github-static-analysis-1`
- `codeaudit-submit20-octobus-1`
- `codeaudit-submit20-repo-tools-1`
- `codeaudit-submit20-static-analysis-1`

旧 `/opt/codeaudit-v2` 完整保留在 `/opt/codeaudit-v2-legacy-before-main567`。旧镜像、容器和两个项目的四个数据卷保留，部署后再次检查存在且旧项目容器均未运行。旧两套服务共用旧目录内的环境文件；运行 alias 已切换到新目录，旧容器保留其创建时环境。未来如手动恢复旧 Compose，必须使用保留目录并重新审查环境文件和挂载路径，不能直接在新 alias 下启动旧配置。

用户明确取消旧环境备份要求，本轮未做生产数据备份或恢复演练；保留数据不等于一致性备份或可恢复性承诺。没有删除历史审计证据、数据卷或镜像，也没有格式化磁盘。历史 P2-C/P2-C.1 报告作为阶段快照原样保留，NOT_STARTED/备份阻断属于当时结论。

## 3. 构建与配置

归档传输较慢，两次传输主动中断，未将不完整文件导入 Docker。改为将 Git bundle 传入服务器、checkout 精确 main SHA，并使用最终 Dockerfile全新 no-cache 构建。实际部署使用上表服务器构建镜像，**没有使用此前本地镜像作为部署身份**。服务器 Docker smoke 成功。依赖 freeze 与 Semgrep 1.99.0 已留证；不同构建环境的镜像字节一致性未声称成立。

所有应用服务、workspace-init 及审计 guest 使用同一固定 Image ID；上游 agent-compose 独立固定 digest，其上游 OCI revision 不代表 CodeAudit 应用源码。Compose 去除 build、禁用 pull，并使用 `--no-build --pull never` 启动，避免未知源码重新构建。Agent 配置也引用固定 Image ID。实际 guest `agent-compose-05e5c8c9af73` 的 image 与上述 ID 一致。

新数据卷为 `codeaudit-main567-agent-data`、`codeaudit-main567_octobus-data`，旧数据库没有复用或迁移，因此本轮没有改写旧 Schema。运行时 Compose 是源配置的发布配置：固定镜像身份、独立数据卷/路径、既有内部端口绑定，非产品源码修改。源配置和关键应用文件哈希与冻结 main 一致。

环境只在服务器受限文件中保存，模型凭据沿用服务器已有配置；新 daemon/MCP token 仅用于此新项目，未上传。文件 root0600。监听地址沿用 Docker bridge `172.17.0.1`，daemon17422、MCP19015，没有对公网增加管理端口。四个常驻服务 restart=unless-stopped。

## 4. 实际运行状态

| 服务 | 容器 ID | 重启后健康 | 身份 |
|---|---|---|---|
| codeaudit-main567-agent-compose-1 | `b1c3d72416a3271c78b47c3dd48aeab9acd3ad050c430697afe332c27445e7a1` | healthy | 上游固定 digest |
| codeaudit-main567-octobus-1 | `69f0573959b102877bf889e9439e3a10125aaeee75fbaec972b2ad2e1f5d6d46` | healthy | 最终 main 镜像 |
| codeaudit-main567-repo-tools-1 | `39839cd5243386b748d20a26dd7888ef9c385661b77d3675661c6cbe5cf93d33` | healthy | 最终 main 镜像 |
| codeaudit-main567-static-analysis-1 | `067dbdd7231d633f4f2f7049e8bc5725bf29f2bdb9a1f619a8ab09e241c9b4db` | healthy | 最终 main 镜像 |

OctoBus status 正常；服务/instance/capset 注册完成。Agent-compose project `codeaudit-final`：1 Agent、1 scheduler，`daily-v2-audit` enabled。MCP 查询可见聚合 ExecuteTool；真实审计调用3次源码读取和1次知识检索。独立 post-restart `static.semgrep` 调用成功、返回0候选，不能把0候选当作没有漏洞。日志尾部未见关键异常。

Compose 提示手工预创建的数据卷“not created by Docker Compose”；数据卷名称/路径与发布配置一致，属于配置提示，非丢失或启动失败。workspace-init 与完成的 guest 正常 exited，不按常驻服务健康项统计。

## 5. 唯一一条真实模型受控审计

| 验收字段 | 实测 |
|---|---|
| Scheduler RUN_ID | `28250be863ed` |
| AUDIT_ID / report参数 | `f9766bf65b304b29b9c02f9aa4b80234` |
| MODEL | deepseek-flash，真实 API，非 Mock |
| Workflow / scheduler | COMPLETE / succeeded |
| 模型响应与用量 | 7 次，53,474 total tokens（含一次 fresh-context Critic） |
| Agent 事件 / 真正 MCP 调用 | 14 / 4，不能把全部事件计为 MCP 调用 |
| 受控目标 | 最终 main 自带 cross-file-flow，3文件17行；只读取源码，未执行漏洞载荷 |
| Gate / verdict | H1 gate passed，CONFIRMED command_injection，conditional_code |
| 报告 SHA256 | `4cb6b870703422192fe97cac4428f394b6569b048d08aec5fde97b9225121e78` |

报告：`/var/lib/docker/volumes/codeaudit-main567-agent-data/_data/sandboxes/codeaudit-v2-workspaces/f9766bf65b304b29b9c02f9aa4b80234/report.md`。Trace：`/var/lib/docker/volumes/codeaudit-main567-agent-data/_data/sandboxes/codeaudit-v2-workspaces/f9766bf65b304b29b9c02f9aa4b80234/tool_calls.jsonl`。读回通过考官身份本地 sudo wrapper；报告输出包含汇总信息，因此 stdout 哈希与 report.md 文件哈希不同，分别保留。

COMPLETE 是流程状态，不是安全证明；该结果只证明受控源码样例中的条件化缺陷和当前链路可运行，部署暴露面未知。未重复 P0/P1 付费实验。永久限制继续为 `P0_REAL_POST_REJECTION=INCONCLUSIVE`、`UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED`。

## 6. 重启与数据验证

已仅重启新项目的 agent-compose、octobus、repo-tools、static-analysis；未重启服务器或旧容器。重启前无正在执行的任务。重启后没有重新 bootstrap：项目、scheduler、MCP 注册和完成任务记录可查询；报告、findings、run_summary、trace、知识使用及surface review的6个文件哈希一致，报告可读回。常驻服务均恢复 healthy。

`RESTART_RECOVERY=PASS_COMPLETED_TASK_AND_REGISTRATION`。**正在执行的任务中断续跑未测试**，记录 `INFLIGHT_TASK_RESUME=NOT_RUN_NO_INFLIGHT_TASK`；unless-stopped 配置检查与应用容器重启不等于宿主机重启演练。

## 7. 证据、剩余条件及下一步

结构化结果与真实执行记录位于 `evaluation/final-remediation/p2-deployment/`；manifest提供校验和，秘密文件/私钥未包含。考官操作见 [EXAMINER_GUIDE](../EXAMINER_GUIDE.md) 和 [访问验收记录](18_P2D_EXAMINER_ACCEPTANCE.md)。

剩余条件：现有授权密钥持有人从独立客户端完成真实 SSH 和逐项命令验收，提供脱敏时间、退出码及结果。不增加公钥、不解锁账号、不修改 sudoers。若需要认证变更或宿主机重启，另行评审并单独授权。

最终 Gate：**CONDITIONAL**。本轮部署和允许范围内的验收完成，停止等待最终 Gate Review。

自检结论：可内部评审和考官操作参考；事实、当前结论及尚未执行的登录/续跑验证已区分，未宣称全面通过考核。
