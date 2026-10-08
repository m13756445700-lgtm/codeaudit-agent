# 最终作业提交状态（2026-10-08）

当前应用发布源码：`567a9aeed8429866c8e8cd551ddb596627bdd7ae`。服务器已部署同一 OCI revision，镜像为 `sha256:f140f0a72acc35b48bdc5c144a0f87b25cd77d3d14f51221f2d948007f33ec3c`。GitHub main之后的说明文档/证据提交与Merge Commit独立于应用发布SHA，不能称为镜像已包含这些新提交。

## 当前已验证结果

| 轮次 / 日期 | 版本和范围 | 实际结果 / 证据 |
|---|---|---|
| P2-C，2026-10-08 | 干净 checkout 应用发布SHA | 252 passed / 20.63s；[pytest原始日志](../evaluation/final-remediation/p2-server-preflight/local-build/pytest.log) |
| P2-B / 最终main，2026-10-08 | 合并前候选及最终main CI分别记录 | Python tests、Schema、Docker构建、Smoke成功；[main run37741956460](https://github.com/m13756445700-lgtm/codeaudit-agent/actions/runs/37741956460) |
| P2-D，2026-10-08 | 从发布SHA服务器全新no-cache构建 | 固定Image ID、linux/amd64、OCI revision核验、服务器Smoke与四常驻服务healthy；[部署结果](../evaluation/final-remediation/p2-deployment/result.json) |
| P2-D真实模型，2026-10-08 | 实际V2，内置3文件cross-file-flow | deepseek-flash，Run28250be863ed，COMPLETE/succeeded；7次模型响应、53,474 total tokens、4次MCP调用，H1 conditional_code Gate通过 |
| P2-D读回 / 重启，2026-10-08 | 新项目四常驻容器；完成任务，无在途任务 | 报告/trace可读；重启后6个持久化产物哈希一致、完成任务记录和注册恢复，无需bootstrap |

新文档提交和最终文档合并后的CI按各自实际Head重新验证；不能以应用发布SHA的旧CI替代新Head检查。最终提交操作结果以GitHub已合并PR和对应main Actions为准。

## 提交验收与交付后验收分开

本次GitHub提交检查包含：必要文档一致、真实证据保留、凭据检查、PR仅文档/证据、最新CI通过、正常Merge Commit及已合并分支收敛。

`POST_SUBMISSION_ACCEPTANCE=NOT_RUN`：考官真实SSH登录及远程逐项操作等待原授权私钥持有人验证。其为交付后验收，按用户本轮发布策略不阻断GitHub作业提交。本地考官身份下CLI、真实任务与报告读取已通过；二者不混同。P2-D阶段报告的CONDITIONAL是当时服务器/考官交付Gate，不等于本轮GitHub提交失败。

运行中任务中断续跑：NOT_RUN_NO_INFLIGHT_TASK。宿主机重启：NOT_RUN。已验证的是完成任务持久化与应用级容器重启；配置unless-stopped不能替代宿主机重启实测。旧环境备份要求已由用户取消，数据/镜像/旧容器保留不等于已做一致性备份。

## 必须保留的限制

- `P0_REAL_POST_REJECTION=INCONCLUSIVE`：新的单条成功审计不消除历史真实post-rejection恢复限制。
- `UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED`：18次真实知识消融未建立独特收益，不能泛化为已证明知识优于模型常识。
- COMPLETE是有界工作流完成，不是全仓安全、全覆盖或无误判的证明。当前H1是受控源码的条件化判断，部署暴露面未知。
- 较大仓库可靠性、任意项目准确率和独立泛化未全面建立。历史INCOMPLETE、PARTIAL、失败及模型误判证据原样保留。

## 历史轮次（非当前验收）

2026-10-07提交候选曾记录211项Linux回归/18.38s，这是此前实现的历史轮次，不是本次252项的另一种口径；其旧服务器SHA91c9e7a及“未部署新增修复”描述已被2026-10-08 P2-D实际部署取代。[原版状态文档](https://github.com/m13756445700-lgtm/codeaudit-agent/blob/262732f3911c04a3829340a6b463a524c4f9dd32/docs/SUBMISSION_STATUS.md)和[状态历史](SUBMISSION_STATUS_HISTORY.md)可追溯。

第11轮历史44/44、20个开发样例TP10/TN10/FP0/FN0及知识对照仅适用于当时实现/固定已知样例；第19轮九模块INCOMPLETE与未执行余例继续保留。不得把历史样本表现重标为本次最终应用完整重测或独立盲测。

操作入口：[提交入口](SUBMISSION.md) / [考官指南](EXAMINER_GUIDE.md)。证据入口：[历史索引](EVIDENCE_INDEX.md) / [P2-D真实结果](../evaluation/final-remediation/p2-deployment/result.json)。本轮仅修正文档和收敛GitHub交付，不新增功能或付费实验。
