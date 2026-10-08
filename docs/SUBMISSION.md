# 考官提交入口（2026-10-08）

公开作业仓库：[CodeAudit Agent V2](https://github.com/m13756445700-lgtm/codeaudit-agent)，提交入口为 `main`。最终应用发布源码为 `567a9aeed8429866c8e8cd551ddb596627bdd7ae`；服务器已部署该版本，OCI revision 与其一致。后续仅文档/证据的提交或 Merge Commit 会改变 main Head，不改变该应用发布身份。

## 服务器与实际操作

服务器 `8.130.121.3`，SSH22，用户 `codeaudit-reviewer`。使用已有授权公钥对应的私钥；先可信核对主机key，不上传私钥或关闭校验：

```bash
ssh -p 22 -i /path/to/existing-authorized-reviewer-private-key -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes codeaudit-reviewer@8.130.121.3
sudo codeaudit-review status
sudo codeaudit-review projects
sudo codeaudit-review triggers
sudo codeaudit-review methods
sudo codeaudit-review runs
sudo codeaudit-review report f9766bf65b304b29b9c02f9aa4b80234
sudo codeaudit-review trace f9766bf65b304b29b9c02f9aa4b80234
```

真实模型审计已完成：Scheduler Run `28250be863ed`，报告 Audit ID `f9766bf65b304b29b9c02f9aa4b80234`。report/trace用 Audit ID，不用短 Run ID。上述读取不触发新审计；`sudo codeaudit-review trigger` 会执行受控样例并使用真实模型额度。完整参数、认证条件和验收步骤见[考官指南](EXAMINER_GUIDE.md)。

**考官真实 SSH 登录是交付后待验收项（POST_SUBMISSION_ACCEPTANCE=NOT_RUN），不阻断本次 GitHub 作业提交。** 维护人员没有考官私钥；已验证本地考官身份下受限 CLI、审计触发与报告读取，未冒充远程登录成功。

## 最短阅读路径

1. [交付状态](SUBMISSION_STATUS.md)：当前版本、测试轮次与边界。
2. [考官指南](EXAMINER_GUIDE.md)：SSH、查询、审计触发和报告命令。
3. [服务器部署记录](final-remediation/17_P2D_SERVER_DEPLOYMENT.md)与[发布清单](../RELEASE_MANIFEST.md)：不可变镜像身份及实际验收；[历史证据索引](EVIDENCE_INDEX.md)保留失败和受限实验。

README可一次点击到本入口或考官指南。历史阶段报告中的“未部署”、旧SHA及旧测试数量只适用于其记录日期，不代表当前交付状态。

## 提交说明

> 已提交 CodeAudit Agent V2 应用源码、部署说明、考官入口及真实验收证据。最终应用发布 SHA 为 567a9aeed8429866c8e8cd551ddb596627bdd7ae，服务器已运行相同 OCI revision；2026-10-08 该源码干净环境252项测试、Schema、Docker构建及Smoke通过。服务器真实模型审计、MCP与Agent编排、报告读取及完成任务的容器重启恢复通过。考官远程SSH登录留作交付后验收；运行中任务续跑和宿主机重启未验证。P0真实post-rejection恢复仍INCONCLUSIVE，独特知识收益仍NOT_ESTABLISHED，不据此宣称任意仓库准确率或保证通过考核。
