# P1.5 Docker / CI 诊断

## 结论与范围

本轮原始阻塞分类为 **B：daemon unavailable**。Docker Desktop 留存的后台进程无法响应；上下文为 desktop-linux，socket 属于当前用户，恢复前磁盘仍有约 60 GiB 可用，未发现当前磁盘耗尽或上下文错误的证据。恢复后 Docker Client/Server 29.8.0 正常响应，info、context、compose、system df 均退出 0。

本轮从隔离分支已有工程提交 `764e1cb48ac9289cc1abdefd501d84e17c97ca2e` 继续；其父提交为用户指定的 `66e04e5884ae6bba772876ce59347af21807ce55`。保留已有工程改动与历史，不回退或改写提交。

## 恢复动作与证据

先记录版本、上下文、存储占用与 socket 状态，再尝试 Docker Desktop 支持的 restart；restart 未能终止失去响应的进程。随后仅终止本地已确认的 Docker Desktop 进程并重新启动应用；残留 backend 在 TERM 无效后被终止。未执行 factory reset、prune、镜像/卷删除，未连接考官服务器。

详细命令、退出码和输出位于 `evaluation/final-remediation/p1-5/continuation/`：diagnostic-before.json、restart.json、recovery-term.json、recovery-relaunch.json、recovered-version.json、diagnostic-after.json。原 p1-5 失败记录继续保留，其结果仅描述当时环境，不代表恢复后的检查。

## CI 验证方法

检查 `.github/workflows/ci.yml`：Python 3.11、依赖安装、完整 pytest、Schema 校验、linux/amd64 镜像构建与容器 smoke 均为必过步骤；Semgrep 在 requirements-dev.txt 和 Dockerfile 中固定为 1.99.0。未发现核心步骤 continue-on-error、allow-failure 或 `|| true`，普通 CI 不调用付费模型。

新建当前提交的本地干净 clone，确认初始 git status 为空，再创建全新 Python 3.11.17 venv 并按 CI 命令安装依赖、运行测试与 Schema 校验。Docker 采用额外严格的 `--no-cache --platform linux/amd64` 构建，并动态传入 BUILD_SHA。完整日志位于 p1-5/continuation；p1-5 根路径日志汇总此前失败和本次重试。

本地主机为 macOS arm64，目标镜像为 Linux amd64，运行依赖 Docker Desktop 的架构模拟。该检查属于本地 CI 等价验证；Ubuntu hosted runner 的实际执行状态仍为 **GITHUB_ACTIONS=NOT_RUN**，需后续候选分支 push 后确认。它也不替代 P2 从 GitHub 拉取的最终验收。

## 证据边界

第一次无缓存 build 成功，但 smoke 中内部服务因缺失 CODEAUDIT_WORKSPACES 配置退出。与 docker-compose.yml 对照后确认是 smoke 启动配置遗漏；工程提交 `9058613` 补齐测试配置并在清理前采集容器日志。原失败日志保留于 continuation/docker-smoke.log。最终完整验证从 `9058613` 的新的干净 clone 和全新 venv 重跑，证据位于 p1-5/verified/。

产品语义、Critic、知识处理及恢复逻辑未在本轮修改，不重复真实模型或知识消融实验。永久保留 REAL_MODEL_POST_REJECTION_RECOVERY=INCONCLUSIVE 与 UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED。最终工程门禁见 09_P1_FINAL_GATE.md；通过工程门禁不等于保证考官评分通过。
