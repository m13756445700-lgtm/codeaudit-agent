# P1 FINAL GATE REPORT

## 结论

**P1_FINAL_GATE=PASS；READY_FOR_P2=YES（仅具备后续阶段条件，本轮未执行 P2）。**

工程门禁通过不等于保证考试通过。GitHub Actions 尚未运行，最终 GitHub fresh clone、考官服务器部署与验收属于后续阶段。当前仅在隔离分支创建本地 RC，等待 Gate Review。

## 可追溯提交与镜像

- 请求起点：66e04e5884ae6bba772876ce59347af21807ce55。
- 已存在工程续提交：764e1cb48ac9289cc1abdefd501d84e17c97ca2e。
- CURRENT_SHA / BUILD_SHA：90586134ec701b4ec605c3536675f4e647b37965。
- RC_SHA：包含本报告的 `chore(release): prepare examiner release candidate` 提交；精确值见交付时 git rev-parse HEAD。报告不预写自身提交哈希。
- RC 相对 BUILD_SHA 仅增加/整理文档与验收证据，产品代码、测试、Dockerfile、CI 和 smoke 脚本保持相同。镜像 OCI revision 如实引用实际构建提交。
- IMAGE_ID：sha256:ec3348b7df103c921b390c5141eb8565cd1cb8b763d34cdd5376913598a4f846。
- IMAGE_DIGEST：NOT_AVAILABLE_PRE_PUSH。Docker Desktop 提供本地 RepoDigest（见 verified/image.json），尚未发布或验证远端 registry digest。
- 目标：linux/amd64；本地：macOS arm64，使用 Docker Desktop 架构模拟。

## 门禁结果

| 检查项 | 已确认结果 | 证据 |
|---|---|---|
| FULL_PYTEST | passed=252, failed=0, skipped=0 | verified/ci-local.log，20.84s |
| SEMGREP_VERSION | 1.99.0，宿主与镜像均核对 | requirements-dev.txt、Dockerfile、ci-local.log |
| SCHEMA_VALIDATION | PASS | All persisted and V2 tool schemas valid |
| DOCKER_DIAGNOSIS | B daemon unavailable，已恢复 | continuation/diagnostic-*.json；08_DOCKER_CI_DIAGNOSIS.md |
| DOCKER_BUILD | PASS，no-cache build + smoke | docker-build.log、docker-smoke.log |
| DOCKER_SMOKE | PASS | 导入、入口、两服务 health、OctoBus status、持续 Running |
| CI_CONFIG | PASS | verified/ci-config.json |
| CI_LOCAL_EQUIVALENT | PASS | verified/python-ci-result.json；完整 ci-local.log |
| GITHUB_ACTIONS | NOT_RUN | 分支未 push，未声称 hosted PASS |
| CLEAN_ENVIRONMENT | PASS | 全新本地 clone + 新 venv；初始 status 空 |
| SECRET_SCAN | PASS | verified/secret-scan.json；范围和误报说明见该文件 |
| EVIDENCE_INDEX / RELEASE_TREE_POLICY | 完成 | docs/EVIDENCE_INDEX.md；docs/RELEASE_TREE_POLICY.md |
| HISTORICAL_EVIDENCE_PRESERVED | YES | 历史证据与请求起点对比无修改 |

证据路径前缀为 evaluation/final-remediation/p1-5/。根路径日志保留原失败并追加新重试，当前成功结果见 verified/result.json；早期 FAIL 仍描述其当时的检查。

## 永久保留的证据边界

P0_STATUS=PASS_WITH_LIMITATION。
REAL_MODEL_POST_REJECTION_RECOVERY=INCONCLUSIVE。
P0_REAL_POST_REJECTION=INCONCLUSIVE。
UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED。

本轮未重跑知识消融或真实模型实验，未修改语义、Critic、知识处理或恢复逻辑。工程门禁不升级以上结论。知识消融的完成状态包含历史未完成/部分完成单元，不等于所有单元成功。

## Release hygiene

Raw trace 通过 EVIDENCE_INDEX 和 HISTORY_INDEX 索引，历史已提交记录保留；未来 dump、cache、runtime output、私有配置与临时 clone/venv 由 ignore 规则隔离。完整验收日志是本轮明确保留的例外，不无限保存重复模型输出。

新临时 scan-review.json 重复文件未进入提交；正式扫描结果和复核说明已保留。无历史 evidence 删除、Git history rewrite、main push 或服务器部署。

仓库 tracked 体积、Top 20 与 Git object 统计见 verified/repository-size.json。现有 worktree Git metadata 的 64 bytes garbage warning 如实记录，不执行清理或 prune。

## 下一步与验收边界

BLOCKERS=NONE（P1.5 范围）。READY_FOR_P2=YES，等待用户 Gate Review。后续仍需真实 GitHub Actions 和 P2 验收；本轮到此停止，不执行部署或最终发布。

## 候选树体积与最大文件（提交前快照）

Tracked files: 603；tracked bytes: 5924872。

```text
count: 1274
size: 6.61 MiB
in-pack: 218
packs: 1
size-pack: 180.85 KiB
prune-packable: 65
garbage: 1
size-garbage: 64 bytes
```

| 文件 | bytes | 分类 |
|---|---:|---|
| evaluation/final-remediation/p1-heldout/result.json | 250551 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/final-remediation/p0-real-recovery/run-03/request-11.json | 96777 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/final-remediation/p0-real-recovery/run-03/request-10.json | 95429 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/final-remediation/p0-real-recovery/run-03/request-09.json | 92445 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/final-remediation/p0-real-recovery/run-02/request-09.json | 87611 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/final-remediation/p0-real-recovery/run-02/request-08.json | 86234 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/final-remediation/p0-real-recovery/run-02/request-07.json | 83130 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/final-remediation/p0-real-recovery/run-03/request-08.json | 82981 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-15/plan.json | 80053 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-19/plan.json | 74834 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-18/plan.json | 74598 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-17/plan.json | 74455 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-16/plan.json | 74329 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-14/plan.json | 74207 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/final-remediation/p0-real-recovery/run-02/request-06.json | 73250 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-08/plan.json | 73203 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-09/plan.json | 73202 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-07/plan.json | 73011 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-13/plan.json | 72777 | 历史 JSON trace / result 或必需验收日志 |
| evaluation/evidence-remediation-12/plan.json | 72724 | 历史 JSON trace / result 或必需验收日志 |

原始完整构建/CI 日志保留 apt 输出的回车及尾随空格，因此仅这些原始日志触发 git diff --check 的空白提示；代码与文档格式检查通过。未为美化日志改写历史输出。
