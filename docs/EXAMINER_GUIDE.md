# CodeAudit Agent V2 考官验收指南

版本：1.0｜更新：2026-10-08。服务器已部署源码 `567a9aeed8429866c8e8cd551ddb596627bdd7ae`；对应 OCI revision 相同。固定镜像 ID：`sha256:f140f0a72acc35b48bdc5c144a0f87b25cd77d3d14f51221f2d948007f33ec3c`。文档独立提交不改变运行镜像。部署详情见 [服务器发布记录](final-remediation/17_P2D_SERVER_DEPLOYMENT.md)。

## 1. 登录条件与已知边界

服务器：`8.130.121.3`，SSH22，用户：`codeaudit-reviewer`。使用原已授权私钥，私钥不提供给本聊天或上传 GitHub。当前维护人员没有考官私钥，**真实考官 SSH 登录尚未验证**；运维侧仅以该用户本地执行命令验证。不得使用 root 运维密钥冒充。

由密钥持有人确认公钥指纹 `SHA256:w59gf6u379xQnpdNqYMxtb/MNs4+gvKeG02A1o1B0m4` 并通过可信渠道核对主机 key 后执行（替换本地私钥路径）：

```bash
ssh -i /path/to/existing-authorized-reviewer-private-key -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 codeaudit-reviewer@8.130.121.3
```

首次未知主机 key 应先可信核对，不能关闭校验。认证失败请留存脱敏错误并联系维护人员，不自行更换公钥。账号密码锁定、禁用密码认证；公钥/PAM实际认证链需上述登录验证。

## 2. 只读发现和状态

登录后逐项执行，记录退出码和结果：

```bash
sudo codeaudit-review status
sudo codeaudit-review projects
sudo codeaudit-review triggers
sudo codeaudit-review methods
sudo codeaudit-review runs
```

期望：新 Compose `codeaudit-main567` 四个常驻服务 healthy；project=`codeaudit-final`；Agent=`auditor`；trigger=`daily-v2-audit` enabled；MCP 可见聚合 ExecuteTool；已完成 Run `28250be863ed` 为 succeeded。列表输出和未来 Run 可能增长，以当前实测为准。

## 3. 读取已完成的真实模型审计

```bash
sudo codeaudit-review report f9766bf65b304b29b9c02f9aa4b80234
sudo codeaudit-review trace f9766bf65b304b29b9c02f9aa4b80234
```

Scheduler短 Run ID `28250be863ed` 与32位 Audit ID `f9766bf65b304b29b9c02f9aa4b80234` **不同**；report/trace 使用 Audit ID。上述为已存在报告读取，不发起新模型调用。deepseek-flash 完成受控 cross-file-flow 样例，3源码文件、4次 MCP 调用、H1 Gate通过。报告为条件化命令注入判断，不能推断所有项目安全或真实线上一定可利用。

## 4. 实际审计触发入口

已根据当前 wrapper 的实际 usage 核对以下命令。触发会产生新任务、写报告并调用真实模型计费；只审计有权检查的目标，不并发大量触发。

```bash
sudo codeaudit-review trigger
sudo codeaudit-review runs
```

`trigger` 立即触发当前 `daily-v2-audit`，默认受控目标是部署源码自带 cross-file-flow。等待 runs 完成后，report（不带参数）读取最新报告：

```bash
sudo codeaudit-review report
```

wrapper也支持 `sudo codeaudit-review audit HTTPS_URL`；仅在明确授权审计某HTTPS源码仓库时，将 HTTPS_URL 替换为实际允许地址。未验证任意私有仓库凭据或全部第三方仓库兼容性，不在示例中填写真实账号/token。`trace` 必须使用实际 Audit ID，不能拿调度短ID代替；如最新输出未显示 Audit ID，请由维护人员从 run_summary 关联确认，勿猜测参数。

## 5. 权限、持久化与限制

考官有普通 bash shell；sudo限制为现有 codeaudit-review wrapper，未授予 Docker组或任意root shell。模型环境文件不可读，Docker socket不可写。这是已检查边界，不是所有潜在输入面的完整安全认证。trigger/audit是有写入和计费影响的受控操作，其余上述命令为查询/读取。

新数据卷独立持久化；四个新容器重启后完成任务记录、服务注册和6项报告相关文件校验和保持一致。考官 wrapper 无重启命令，请勿自行停服务；宿主机重启、正在执行任务的续跑未演练。

永久限制：`P0_REAL_POST_REJECTION=INCONCLUSIVE`；`UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED`。历史失败证据继续保留，不能将一次部署审计成功改写为历史实验全部通过。

## 6. 交付验收标准

真实 SSH 成功后，独立确认五个查询命令、报告/trace读取和受控任务触发的实际结果，记录时间、退出码、Run/Audit ID和必要脱敏输出。当前交付 `P2D_GATE=CONDITIONAL`，原因是尚未进行真实考官SSH登录。入口、权限或模型失败时保留真实错误，不用Mock替代。

源码和评审入口：[提交说明](SUBMISSION.md)、[历史证据](EVIDENCE_INDEX.md)、[工程 Gate](final-remediation/09_P1_FINAL_GATE.md)、[本轮考官验收](final-remediation/18_P2D_EXAMINER_ACCEPTANCE.md)。完成上述人工登录验证后进入最终 Gate Review。
