# P2-B Checkpoint A：GitHub 候选分支与真实 CI 验收

日期：2026-10-08；范围：证据提交、候选分支推送、PR 创建、真实 GitHub Actions 与 PR diff 核对。

## 结论

**CHECKPOINT_A_GATE=PASS。** 具备进入 Checkpoint B Gate Review 的条件；本轮未授权或执行 main 合并、最终 Release Tag、服务器部署或 P2-C。

## 提交、PR 与镜像来源

| 字段 | 已确认值 |
|---|---|
| P2_A_SOURCE_SHA | d26c64e0f1d53060e80da39a9ebc37413727ce38 |
| P2_A_EVIDENCE_SHA | f0a15796620fb262eb152f89c00f7f0063499a91 |
| PUSHED_BRANCH | codex/p0-evidence-recovery |
| REMOTE_HEAD_SHA | f0a15796620fb262eb152f89c00f7f0063499a91 |
| PR_NUMBER | 1 |
| PR_URL | https://github.com/m13756445700-lgtm/codeaudit-agent/pull/1 |
| PR_HEAD_SHA | f0a15796620fb262eb152f89c00f7f0063499a91 |
| 当前 main / PR base | 0733933113faee3121b2c5d692ef4ee1400d4d0d |
| P2-A 本地镜像 OCI revision | d26c64e0f1d53060e80da39a9ebc37413727ce38 |
| P2-A 本地 Image ID | sha256:663290089e669447e8240f3108353e33de78f1869b3d549d538ae63b94f85a9c |

f0a1579 仅新增 P2-A 报告、日志和清单，共 36 文件；未更改产品源码、依赖、Dockerfile、Compose、CI 或测试。通过明确文件列表添加，未使用 git add -A；提交前已重新扫描。此前本地 252 项测试和构建结果引用 d26c64e，不能说旧镜像包含 f0a1579。

fetch 后确认 main 未改变、工作区 clean、main 为分支祖先，历史证据保留。普通 push 成功，无 force 或历史改写。报告 10 是上一阶段快照；其中当时尚未提交的 P2-A 产物现已通过 f0a1579 提交。当前报告 11 和 p2-github 结果是本次验证后的待评审产物，尚未加入有效 PR Head，以保持 CI 与已验证 Head 一致。

## 真实 GitHub Actions

Workflow：**Core verification**。两次触发均为 completed / success，Job core 和全部步骤 completed / success。

| 触发 | Run ID | URL | API Head SHA | Conclusion |
|---|---|---|---|---|
| push | 37738361710 | https://github.com/m13756445700-lgtm/codeaudit-agent/actions/runs/37738361710 | f0a15796620fb262eb152f89c00f7f0063499a91 | success |
| pull_request | 37738498456 | https://github.com/m13756445700-lgtm/codeaudit-agent/actions/runs/37738498456 | f0a15796620fb262eb152f89c00f7f0063499a91 | success |

| 字段 / 必查步骤 | 实际结果 |
|---|---|
| GITHUB_ACTIONS_RUN_ID | 37738361710（主记录）；PR 记录见上表 |
| GITHUB_ACTIONS_URL | 上表 push URL |
| GITHUB_ACTIONS_STATUS | PASS |
| PYTEST_STATUS | PASS；两次均 252 passed / 0 failed / 0 skipped |
| pytest 时长 | push 10.40s；PR 13.46s |
| Semgrep dependency | 安装日志确认 semgrep 1.99.0 |
| SCHEMA_STATUS | PASS，All persisted and V2 tool schemas valid |
| DOCKER_BUILD_STATUS | PASS；实际 Docker build 步骤成功 |
| Docker smoke | PASS；两份日志均 DOCKER_SMOKE=PASS |
| SECRET_SCAN_STATUS | PASS；占位符与模拟测试凭据已复核，无实际凭据匹配 |
| HISTORICAL_EVIDENCE_PRESERVED | YES |

push 工作流在 f0a1579 执行。PR 工作流按 GitHub 默认行为检出临时合并提交 53acce6c8752edeb8b02edbccd7be77030b0f58f；其 Git tree 与 f0a1579 完全一致（992a882b8c14dd4b0d0bfa3f029045938ec49d82）。该提交不表示 main 已合并。CI 的 build 参数分别指向实际检出的 SHA，不混用本地 d26c64e 镜像标识，也不将 hosted build 日志冒充镜像 registry 发布。

原始日志、Run/Job/Step 状态、执行时间和远端 Head 信息位于 evaluation/final-remediation/p2-github/。一次日志下载 TLS handshake timeout 已保留；重试成功取得两份完整原始日志，不属于 workflow 失败。

## PR diff 完整性核对

- 全部 11 个本地预期提交均在 PR，317 个远端变更文件与本地 diff 清单完全匹配。
- 无删除文件、无异常二进制、无缓存、私钥、数据库、归档或运行密钥文件；历史失败路径未删除。
- GitHub 完整 diff API 因超过 300 文件上限返回 HTTP406。已保留错误，改用分页文件 API 与完整本地 diff 对照；未删除历史证据规避限制。
- 最大变更文件为历史知识消融 result.json（250551 bytes）；其他大文件主要为已有真实模型请求或审计计划。历史 raw trace 保留，新的重复 dump 按 release policy 隔离。
- 活跃产品、脚本、测试、CI、Docker/Compose 中未发现 /Users/ 或 /home/ 本地路径依赖；历史诊断日志里的绝对路径属于溯源信息。
- PR 正文提供 Examiner Guide、Evidence/History Index、Release Policy、P1/P2-A Gate 和 Manifest 入口，并明确服务器尚未部署本候选版本。

PR diff 检查记录见 pr-review.json；未将重复的完整 patch/model dump 再次加入验收目录。完整 local diff hash 已记录，GitHub 文件清单和提交集合核对可独立复现。

## 永久限制与下一步

P0_REAL_POST_REJECTION=INCONCLUSIVE。
REAL_MODEL_POST_REJECTION_RECOVERY=INCONCLUSIVE。
UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED。

真实模型主动补证据与 deterministic recovery 不等于真实模型拒绝后恢复；知识消融包含历史未完成/部分完成结果。没有升级既有限制，也没有新增模型实验。

下一步：等待 Checkpoint B Gate Review 和 main 合并的明确授权。合并若改变最终 main SHA，必须按最终 main 重新构建、核验和执行后续部署暂停点。本轮到此停止。
