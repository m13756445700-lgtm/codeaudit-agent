> 2026-09-24更新：本页保留此前阶段记录。当前HR交付、公钥登录、原题触发器等状态统一以[原题核对表](EXAM-COMPLIANCE.md)和README为准；“待发布/可选SSH/私有仓库优先”等旧建议已撤销。

# CodeAudit V1.0交付资源总表

版本1.0；日期2026-09-23；交付对象：面试评审人员。

## 结论与范围

技术环境与限定功能已经验证；GitHub发布和评审授权尚未完成。不能以技术Phase通过代替全部交付物完成。只交付BRD范围内功能及TC-05、TC-10已确认勘误。

## 十五项交付物

| 交付物 | 位置/状态 | 交付标准 |
|---|---|---|
| GitHub Repository | 已发布并设为Public，见README | 考官可访问，固定Commit可克隆 |
| README | 根目录README.md | 15个必需章节齐全 |
| BRD/PRD | docs/BRD-PRD.md | 原文保留，勘误单列 |
| Architecture | docs/ARCHITECTURE.md | 模型与Gate边界明确 |
| agent-compose.yml | 根目录模板、deploy/server/恢复定义 | 私有配置另行保管 |
| OctoBus Service | octobus/code-audit-service/ | 五方法真实验证 |
| Capset | code-audit-agent | 精选证据与资源映射，不交付Token |
| Semgrep规则 | rules/semgrep/ | 四类固定规则 |
| 知识库 | knowledge/java-spring/ | 有版本和知识开关案例 |
| Finding Schema | schemas/finding.schema.json | 三状态及证据字段 |
| Demo Repository | fixtures/工程；独立Demo Git包 | GitHub地址待发布，历史Commit可离线恢复 |
| 十二测试案例 | scripts/run_acceptance_matrix.py、tests/ | 服务器12/12通过 |
| Acceptance Matrix | docs/ACCEPTANCE-MATRIX.md、REQUIREMENTS-DELIVERY-MATRIX.md | 案例与作业要求分别覆盖 |
| Troubleshooting | docs/TROUBLESHOOTING.md | 故障、处理、验证及边界 |
| SSH信息 | README与专用评审账号 | 公钥已配置；考官实际登录待确认 |

## 三类交付资料

1. GitHub：源码、空配置、需求、测试、精选去密证据、Demo固定提交bundle。
2. 单独交接：服务器地址、评审用户名、有效期、可执行范围，由双方通过受控渠道确认。
3. 所有者保管：root私钥、云账号、模型Key、Capset Token、完整原始会话和私有配置，不放仓库或Release附件。

## 服务器事实

Ubuntu 22.04.5 LTS，x86_64，4核、约8GB、40GB系统盘；2026-09-23复核空闲约25GB。新部署三个服务运行，原有服务保留。OctoBus仅主机回环端口19000，模型守护进程在容器网络，Demo无外部网络。整机恢复见PHASE10-SERVER-ACCEPTANCE.md。

目前不需要另买域名、新服务器、Docker Hub付费账号或更换模型平台。GitHub账户尚需注册；现有DeepSeek和云主机继续使用，但额度、到期和费用需所有者自行核对。

## 发布前最后四项

- 所有者注册GitHub并在本机登录，发布两个私有仓库（主工程与Demo）；若考官允许单仓库，可仅发布主工程并明确Demo路径及bundle。
- 登记仓库URL、提交SHA、验收时间；发布前扫描通过后再提交。
- 获取考官GitHub用户名；若需SSH，另获取其公钥和评审期限。公钥可交接，私钥不交接。
- 明确Instance名称映射：BRD示例java-audit-instance，当前code-audit-local。功能通过不等于名称完全一致，待考官确认映射或另行按要求变更复验。

## 责任与完成标准

所有者负责账号注册、登录、授权和费用；助手负责打包、核验、操作指导和必要配置；考官确认访问及验收结果。仓库可访问、固定版本可复现、SSH授权符合评审约定、命名差异确认后，方可标记正式交付完成。

自检：达到可内部评审、可交付准备状态；尚未达到“GitHub发布和考官授权已完成”。下一步按GITHUB-HANDOFF.md执行。
