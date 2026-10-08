# P2-A 发布预检与完整候选源码验收

版本：P2-A Gate Review；日期：2026-10-08；范围：隔离分支、全新本地副本、本地镜像。

## 结论与冻结基线

**P2-A_GATE=PASS。** 本轮停在 CHECKPOINT A，不代表最终发布验收 PASS。GitHub Actions、PR 合并、GitHub fresh clone、服务器部署、考官权限和新的真实模型 E2E 均未执行。

| 项目 | 已确认事实 |
|---|---|
| 仓库 | https://github.com/m13756445700-lgtm/codeaudit-agent |
| 分支 | codex/p0-evidence-recovery |
| BASELINE_SHA / 当前 main | 0733933113faee3121b2c5d692ef4ee1400d4d0d |
| RC_SHA / 本轮 RELEASE_SHA / 全新副本 SHA | d26c64e0f1d53060e80da39a9ebc37413727ce38 |
| Git tree SHA | be9f767eabc8e75e30d37530539d6e443486c8d0 |
| IMAGE_OCI_REVISION | d26c64e0f1d53060e80da39a9ebc37413727ce38 |
| IMAGE_ID | sha256:663290089e669447e8240f3108353e33de78f1869b3d549d538ae63b94f85a9c |
| REGISTRY_DIGEST | NOT_AVAILABLE_PRE_PUSH |
| 平台 | linux/amd64；macOS arm64 本地架构模拟 |

首次冻结前工作区干净、远端仓库正确。main 仍与基线一致，且是候选分支祖先，当前关系具备快进条件，未发现合并冲突。后续一次远端读取超时已保留；重试退出 0 并确认 main 未变化。

镜像从完整 d26c64e 构建，其 OCI 标识不再引用 P1.5 的 9058613。Docker Desktop 本地 RepoDigest 不作为已发布 Registry Digest。本轮未传输镜像，传输校验值与服务器实际镜像对比留待部署阶段。

本轮新报告和证据是冻结源码之外的待评审产物，尚未提交或推送，候选源码 SHA 未改变。若后续将报告纳入新提交，或 PR 合并改变 SHA，必须从实际最终 main SHA 重新构建与核验。

## 全新环境验收结果

| 验收项 | 新执行结果 | 原始证据 |
|---|---|---|
| Clone / venv | PASS；初始及结束 tracked 状态 clean | clone.log、checkout.log、venv.log、clean-source.json |
| 依赖安装 | PASS；直接依赖固定版本 | dependencies.log、dependency-resolutions.log |
| Semgrep | 宿主和镜像均 1.99.0 | semgrep.log、container-semgrep.log |
| FULL_PYTEST | 252 passed / 0 failed / 0 skipped，20.32s | pytest.log |
| Schema | PASS | schema.log |
| Docker no-cache build | PASS | docker-build.log |
| Docker smoke | PASS：导入、入口、两服务 health、OctoBus status、持续运行 | docker-smoke.log |
| Compose config | PASS，合成配置的语法与结构 | compose-config.log |
| Agent project YAML | PASS，secret 标记与 scheduler 结构 | agent-compose-config.log |
| Secret scan | PASS；占位符及两个模拟测试值已复核 | secret-scan.json、secret-scan.log |
| Release manifest | PASS：SHA、tree、文件哈希、实际镜像、OCI、平台、命令与执行结果 | release-manifest.json、manifest-validation.json |
| GitHub Actions | NOT_RUN | 本轮未 push |
| 历史 evidence | PRESERVED | preflight.json |

证据前缀：evaluation/final-remediation/p2-release/。steps.json 保存真实命令、源码 SHA、时间、退出码和原始日志路径。构建及 Compose 文件 SHA256 在 release-manifest.json；所有结果来自本轮执行，不覆盖旧 P0/P1 记录。

Compose 仅使用临时 CONFIG_ONLY 配置，无生产凭据；临时 .env 和 .runtime.env 权限 0600，被 Git 和 Docker context 排除。配置解析不证明实际项目注册、MCP 发现或服务器可用。

直接依赖已固定，传递依赖仍在安装时解析；实际宿主/容器 pip freeze 已归档，不宣称全部传递依赖完全锁定或字节级可重复构建。

## 后续发布与部署约束

| 事项 | 依据与影响 | 处理要求 |
|---|---|---|
| 默认启动脚本重建 | control.py 的普通 compose build 未传 BUILD_SHA | 正式部署使用最终 main 对应的已验证不可变镜像，不能用未标识的默认重建替代 |
| Compose 可变标签 | 当前引用 codeaudit-final:2.0 | P2-B 必须固定到已验证 Image ID 或真实 registry digest，保存最终配置 |
| 控制器 Docker socket | agent-compose 具备宿主机管理能力，SECURITY 已披露可信操作员边界 | 考官账号不得因此获得额外 socket、宿主机管理或 secret 权限；后续实测 |
| 本地平台 | amd64 容器在 arm64 主机模拟运行 | 仍需 Ubuntu hosted CI 与服务器运行验收 |
| 后续 SHA 变化 | 新提交、merge、squash 可能改变 SHA | 按最终 main 重建、核验、部署，不复用过期标识 |

未修改产品代码、未降低安全 Gate。以上约束不能据本轮测试推断已在服务器落实。

## 永久证据边界

P0_STATUS=PASS_WITH_LIMITATION。
P0_REAL_POST_REJECTION=INCONCLUSIVE。
REAL_MODEL_POST_REJECTION_RECOVERY=INCONCLUSIVE。
UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED。

本轮无真实模型调用或知识消融重跑。Smoke 和自动化测试不是模型 E2E，也不证明 SECURITY_FINDINGS_CORRECT、完整漏洞覆盖或考官评分通过。

## 下一暂停点

CHECKPOINT A：等待 Gate Review 和首次远程 push 的明确确认。拟推送仓库及分支如上，冻结 SHA 为 d26c64e0f1d53060e80da39a9ebc37413727ce38；main 未变化，未发现实际凭据。

最终发布报告及考官真实验收报告应在后续阶段完成后形成，当前不预写完成事实。未推送、未合并、未部署服务器。
