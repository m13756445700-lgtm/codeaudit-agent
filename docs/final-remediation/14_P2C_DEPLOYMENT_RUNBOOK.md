# P2-C 发布操作手册与考官验收计划

版本：1.0｜日期：2026-10-08｜状态：**计划，尚未执行，部署未获授权**。

## 1. 发布目标与责任

将主验收项目 `codeaudit-github` 切换到 main `567a9aeed8429866c8e8cd551ddb596627bdd7ae`，保留现有数据、历史失败和回滚入口。`codeaudit-submit20` 属于另一套运行项目，未经确认不得操作。

| 角色 | 责任 | 放行依据 |
|---|---|---|
| 用户 / Gate Review | 批准备份、维护窗口、切换、付费审计和重启 | 明确授权；本轮均未授权执行 |
| 发布负责人 | 镜像、配置、数据映射、操作日志、回滚 | 校验清单全部通过 |
| 系统负责人 | 安全传输、现有账号与端口核验 | 考官真实 SSH 成功、权限边界符合要求 |
| 验收负责人 | 编排/MCP/模型/报告证据与限制说明 | 一次单独授权的真实任务及可追溯产物 |

不承诺无损回滚：当前数据向后兼容和恢复演练均未验证。

## 2. 冻结身份与停止条件

```text
FINAL_SOURCE_SHA=567a9aeed8429866c8e8cd551ddb596627bdd7ae
FINAL_IMAGE_ID=sha256:1b207430a18eac15161663504911263030cc3ece4b4690153556d954c66163e6
FINAL_IMAGE_OCI_REVISION=567a9aeed8429866c8e8cd551ddb596627bdd7ae
FINAL_IMAGE_REGISTRY_DIGEST=NOT_AVAILABLE_PRE_PUSH
CURRENT_SERVICE_IMAGE_ID=sha256:a56bb11d00d0763b1978e09e5c9a05fc78ebf1cf97739b61c85f885a4ede1b36
CURRENT_AUDITOR_GUEST_IMAGE_ID=sha256:a7ad2a637412283936446e6899d81bb65d6fb5f6603234e5f6909a82997ee48e
CONTROLLER_IMAGE=ghcr.io/chaitin/agent-compose@sha256:3117226250256b03d25815bd1bb584ade5ac225b83f55d527be122b8b75a61e8
V1_ROLLBACK_COMMIT=0733933113faee3121b2c5d692ef4ee1400d4d0d
V1_ROLLBACK_TAG=v1-pre-v2-release
```

当前 service/guest 镜像是现有运行状态的回滚候选，**没有证据证明它们来自 V1 tag commit**。如果要求恢复到严格 V1 源码，必须单独从 V1 commit 构建并验证，不能只更换标签。

以下任一项未通过即停止：GitHub main 漂移；镜像 ID/OCI/平台不一致；完整备份无恢复证明；卷名或 sandbox 绝对路径不明确；存在运行中任务；所需配置/旧镜像缺失；实际考官入口不可用；未获得本次切换授权。

## 3. 发布前准备与数据保护

1. 重新只读核验 main、tag、服务器当前镜像、Compose 项目和服务。记录操作人、时间、旧容器 ID、启动时间、Image ID、有效配置哈希和卷映射。不要依赖旧观测值或 mutable tag。
2. 明确两套项目用途。只允许切换 `codeaudit-github`；禁止 `docker system prune`、全局停止、`down -v`、卷删除或旧镜像删除。
3. 经单独批准，在维护窗口冻结新的任务提交及定时触发，等待运行中任务结束。现有 scheduler enabled，配置加载/agent up 可能恢复或开启调度；须先验证本版本的调度禁用和恢复方式，不能把 bootstrap 当作只读命令。
4. 取得**一致且完整**的 controller SQLite 数据、OctoBus 持久化状态、审计工作空间/报告/日志、有效配置和账号 wrapper 清单。SQLite 含 WAL，采用经验证的在线备份接口或批准的暂停写入快照流程；不要仅复制 data.db。OctoBus 数据备份一致性也需组件级验证。
5. 备份保存 root-only，含敏感配置的归档不得进入 GitHub；记录清单、SHA256、大小、时间、数据库一致性检查结果。恢复到独立测试卷，核对项目、调度、审计数量及代表性报告。创建和恢复命令须依据已批准的备份路径与组件方法补齐；本轮不以未经验证的通用 tar 命令代替方案。
6. 保留旧生产卷不修改，优先从验证后的备份恢复到新的版本化卷。**新卷方案仍须验证**：controller 数据库可能保存旧 sandbox 绝对路径，运行环境中的 CODEAUDIT_SANDBOX_ROOT/DOCKER_HOST_SANDBOX_ROOT 和已登记项目路径必须一致；需要确认该版本支持的迁移方式。未验证迁移前禁止切换。
7. 若最终选择原卷原地升级，必须先证明新旧数据兼容并完成恢复演练，否则不得采用。不能同时让两套 controller 写同一数据库。
8. 估算备份、新数据卷、镜像导入和日志留存的空间；当前约 22.9 GB 剩余不是容量保证。记录维护窗口、负责人和回滚时间目标，具体时间由 Gate Review 确认。

**STOP A：备份与恢复、项目/卷/路径设计未通过，停在准备阶段。**

## 4. 镜像传输计划（尚未执行）

优先直接保存已验证的本地镜像，不在服务器按 mutable tag 重建。以下命令仅为批准后的执行模板，路径需由发布负责人确认；不存在自动执行动作。

本地执行：

```bash
docker image inspect codeaudit-release-candidate:567a9aeed8429866c8e8cd551ddb596627bdd7ae \
  --format '{{.Id}} {{index .Config.Labels "org.opencontainers.image.revision"}} {{.Os}}/{{.Architecture}}'
docker image save --output /approved/private/release-main567.tar \
  codeaudit-release-candidate:567a9aeed8429866c8e8cd551ddb596627bdd7ae
shasum -a 256 /approved/private/release-main567.tar
scp -i /Users/bo/Documents/alipay-lxb.pem -o StrictHostKeyChecking=yes \
  /approved/private/release-main567.tar root@8.130.121.3:/approved/private/release-main567.tar
```

服务器执行（上述路径为占位，先确认存在及 root-only 权限）：

```bash
sha256sum /approved/private/release-main567.tar
docker image load --input /approved/private/release-main567.tar
docker image inspect codeaudit-release-candidate:567a9aeed8429866c8e8cd551ddb596627bdd7ae \
  --format '{{.Id}} {{index .Config.Labels "org.opencontainers.image.revision"}} {{.Os}}/{{.Architecture}}'
```

两端归档哈希必须一致，导入后镜像 ID、OCI revision、linux/amd64 必须逐项符合冻结清单。跨 Docker 存储实现导入结果尚未执行验证，若 Image ID 不一致立即停止调查；不要替它重新打标签来“对齐”。若改用 Registry，需单独授权推送，取得真实不可变 digest 并再次验证，当前没有 Registry digest。

## 5. 配置准备与静态验证

在批准的服务器独立 release 目录中准备最终 main 文件、现有敏感环境文件的受控副本和专用 Compose override，保持 root-owned 与秘密文件 0600。不覆盖 `/opt/codeaudit-v2` 或旧配置。

override 必须包含：

- 明确项目 `codeaudit-github`，准确、已验证的新卷名；旧卷标记为需保留的回滚资产。
- octobus/repo-tools/static-analysis/codeaudit-agent/workspace-init 使用冻结镜像 ID；agent-compose 的 DEFAULT_IMAGE 和 `agent-compose.yml` 中 auditor image 也必须一致。只改三个常驻服务是不完整发布。
- 使用本地 ID 的 agent runtime 兼容性须先在隔离环境验证；如 driver 要求 registry reference，改用真实 digest 并重新审批，不能回退到 mutable `codeaudit-final:2.0`。
- 不改变上游 controller pinned image、能力网络、受限监听、认证、健康检查、restart policy、权限限制或挂载边界；需要改变时单独评审。
- CODEAUDIT_SANDBOX_ROOT 与 DOCKER_HOST_SANDBOX_ROOT 以及恢复数据库内路径经过验证，任务镜像能访问正确的新工作空间。
- 第一轮注册前，使用该版本支持的方式关闭自动调度；禁止通过删历史 scheduler 数据实现。

`release.override.yml` 和 `rollback.override.yml` **本轮未创建**，避免把尚未确定的卷/路径方案做成可误执行配置。下面定义 Shell 函数供后续操作统一使用；须先将两个目录和文件替换成审批通过的真实路径。

```bash
release_dc() {
  docker compose -p codeaudit-github \
    --env-file /approved/releases/main567/.env \
    --env-file /approved/releases/main567/.runtime.env \
    -f /approved/releases/main567/docker-compose.yml \
    -f /approved/releases/main567/release.override.yml "$@"
}
rollback_dc() {
  docker compose -p codeaudit-github \
    --env-file /approved/rollback/current/.env \
    --env-file /approved/rollback/current/.runtime.env \
    -f /approved/rollback/current/docker-compose.yml \
    -f /approved/rollback/current/rollback.override.yml "$@"
}
release_dc config --quiet
rollback_dc config --quiet
```

旧服务启动配置使用旧 service ID；旧 controller 恢复配置使用旧 guest ID 与原卷映射。不要将它们统一替换成一个镜像。配置校验结果只保存经过脱敏的字段，不输出完整环境变量。

**STOP B：取得明确部署授权，确认备份、恢复与配置均通过，再允许切换。**

## 6. 切换计划（尚未执行）

在维护窗口内冻结触发、确认没有运行中的 guest 和其他写入者后：

```bash
rollback_dc stop agent-compose octobus repo-tools static-analysis
release_dc up -d --no-build --pull never workspace-init repo-tools static-analysis octobus agent-compose
release_dc ps
release_dc exec -T octobus octobus status
```

这是未来的停服/切换操作，需要独立授权。`--no-build --pull never` 防止误构建或拉取其他镜像。workspace-init 会写新数据卷，必须使用已批准的新卷，不能意外指向旧卷。若任一组件失败，不继续触发审计。

逐个检查容器实际镜像 ID、健康、监听、restart policy、挂载；核对 controller 本地镜像引用与 auditor 配置。能力服务健康可在各自容器内读取 `/health`；OctoBus 服务/实例/capset 注册只能在正确恢复的新状态上操作。

现有 `scripts/control.py bootstrap` 会写 capset/token、复制配置和执行 agent up；`start` 会构建镜像。**禁止直接执行 start；bootstrap 必须经审查后才使用**，并确保所使用 Compose override、关闭调度配置、新卷和 runtime 映射均生效。采用 `COMPOSE_FILE` 时验证该脚本所有 Docker Compose 子命令均继承它，不假定 reviewer wrapper 继承该变量（wrapper 会清空环境）。

考官 wrapper 固定 `/opt/codeaudit-v2`。release staging 目录运行成功不代表考官入口已切换；需要单独审批原路径配置切换或 wrapper 受控更新，并保留原配置与 wrapper。不可绕过考官入口验证。

## 7. 发布后验收与考官步骤

| 顺序 | 执行方式 | 成功标准 | 当前状态 |
|---|---|---|---|
| 1. 考官 SSH | 使用已授权的考官密钥和 codeaudit-reviewer 登录 | 使用考官本人身份，非 root | NOT_RUN |
| 2. 服务状态 | sudo codeaudit-review status | 主项目各服务健康，实际 Image ID 符合新清单 | 旧服务只读检查 PASS；新版本 NOT_RUN |
| 3. 项目 | sudo codeaudit-review projects | 项目、auditor 与正确配置路径存在 | 旧入口 PASS；新版本 NOT_RUN |
| 4. 触发方式 | sudo codeaudit-review triggers | 手动/定时方式明确，调度开关受控 | 旧入口 PASS；新版本 NOT_RUN |
| 5. 能力 | sudo codeaudit-review methods | capset 有方法且认证正常 | 旧入口 PASS；真实调用 NOT_RUN |
| 6. 单次真实审计 | 经独立付费授权，sudo codeaudit-review audit HTTPS_URL | 一个已批准的公开 GitHub 目标；获得真实 run/audit ID | NOT_RUN |
| 7. 编排 | runs 与 operator 受控日志 | 项目/调度/guest 可关联；guest 使用最终镜像 | NOT_RUN |
| 8. MCP 和模型 | tool_calls、模型请求元数据及 run_summary | 真实工具调用与模型判断均有证据，不输出密钥 | NOT_RUN |
| 9. 报告 | sudo codeaudit-review report AUDIT_ID | report/run_summary/plan/reviews 可读取 | 旧报告只读 PASS；新版本 NOT_RUN |
| 10. 来源追溯 | sudo codeaudit-review trace AUDIT_ID | 工具证据、源码快照版本、知识来源关联 | NOT_RUN |
| 11. 重启恢复 | 独立维护授权后受控重启主项目；整机重启另行审批 | 项目/capset/报告恢复，服务健康，无重复计费任务 | NOT_RUN |
| 12. 权限 | 检查组、sudo 白名单、秘密文件/socket/wrapper | 考官不能读 secrets 或任意管理 Docker | 已做限定只读检查；最终切换后需重验 |

考官 SSH 示例（密钥路径待确认）：

```bash
ssh -i /path/to/approved-reviewer-key -o StrictHostKeyChecking=yes \
  codeaudit-reviewer@8.130.121.3
sudo codeaudit-review status
sudo codeaudit-review projects
sudo codeaudit-review triggers
sudo codeaudit-review methods
sudo codeaudit-review runs
```

真实任务命令须在明确授权后执行，不能把查询 scheduler runs 的历史成功当成新发布验收。每天定时任务也要纳入付费窗口和重复运行风险控制。保持 `P0_REAL_POST_REJECTION=INCONCLUSIVE`、`UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED`。

## 8. 回滚操作与数据边界

触发条件：组件持续不健康、服务不可用、模型/工具链无法完成任务、数据/报告缺失、权限扩大、镜像身份错误。记录实际故障，冻结新增任务，保留失败证据。执行前确认无运行中任务；切回过程中禁止删除新卷，新版任务结果需保留导出。

已通过恢复演练并获回滚授权时：

```bash
release_dc stop agent-compose octobus repo-tools static-analysis
rollback_dc up -d --no-build --pull never workspace-init repo-tools static-analysis octobus agent-compose
rollback_dc ps
rollback_dc exec -T octobus octobus status
```

上述旧配置必须引用原旧卷、当前 service 镜像与旧 guest 镜像。workspace-init 已确认只操作正确旧卷时才允许启动；如不需要初始化，应从已审查方案中去除，避免额外数据写入。恢复 reviewer 入口使用已备份的有效配置/wrapper，并在考官身份重新读取 status/projects/triggers/methods/runs/report。

如旧卷未改变且旧版状态仍有效，可重新连接原卷；若旧卷改变或损坏，只能按已经演练的备份恢复流程恢复到独立卷，验证后切换。**不提供未经演练的直接覆盖生产数据库命令。** 备份点之后的新任务不能自动出现在旧数据库；须保留新版卷/导出供后续合并，数据向后兼容 INCONCLUSIVE，不能称为无损回滚。

## 9. Gate 交付清单

- 完整备份清单与校验和、数据库一致性、独立恢复证据。
- 两项目用途确认、旧 service/guest 镜像清单、有效旧配置、数据卷和 sandbox 路径映射。
- 考官真实 SSH 及最小权限验证。
- 最终镜像传输与服务器导入身份核验。
- 审批通过的 override、数据迁移方案、禁用/恢复调度步骤、维护窗口和回滚负责人。
- 单独授权付费 E2E、重启测试与正式部署。

本轮只完成预检和操作计划，以上执行性项目均需补齐 Gate 后推进。下一步是备份恢复与入口确认评审；不得自动进入上线。
