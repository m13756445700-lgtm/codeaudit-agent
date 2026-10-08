# CodeAudit Agent V2 最终应用发布清单

更新：2026-10-08。当前事实以本节和[P2-D实际部署记录](docs/final-remediation/17_P2D_SERVER_DEPLOYMENT.md)为准；下方9月记录保留为历史轮次，不能替代当前验收。

| 身份 / 验收 | 当前值 |
|---|---|
| DEPLOYED_APPLICATION_SOURCE_SHA | `567a9aeed8429866c8e8cd551ddb596627bdd7ae` |
| DEPLOYED_IMAGE_OCI_REVISION | `567a9aeed8429866c8e8cd551ddb596627bdd7ae` |
| SERVER_IMAGE_ID | `sha256:f140f0a72acc35b48bdc5c144a0f87b25cd77d3d14f51221f2d948007f33ec3c` |
| 平台 | linux/amd64 |
| 实际运行Compose SHA256 | `b50a17df6cc1e3a95071b9fd0729a87fea952eee22b1ab1014f606d9eecd2cdc` |
| GITHUB_MAIN_HEAD_SHA | GitHub当前main Head；文档合并后为新Merge Commit，与上述应用SHA分开记录 |
| 源码回归 | 2026-10-08 P2-C，冻结应用SHA，252 passed / 20.63s；原始日志不改写 |
| Schema / Docker / Smoke | 该源码本地及GitHub验收通过；服务器全新no-cache构建和Smoke通过 |
| 服务器部署 | 已完成；四常驻服务healthy，OctoBus / agent-compose / MCP实际可用 |
| 真实模型E2E | deepseek-flash；Run28250be863ed / Audit f9766bf65b304b29b9c02f9aa4b80234；7响应、53,474 total tokens、4 MCP调用；COMPLETE/succeeded |
| 报告 / 重启恢复 | 报告生成/读取通过；完成任务的四容器重启恢复通过，6个产物哈希不变 |
| 考官真实SSH | POST_SUBMISSION_ACCEPTANCE=NOT_RUN；交付后验收，不阻断GitHub作业提交 |
| 在途任务续跑 / 宿主机重启 | 两者未验证，不得用完成任务恢复代替 |
| P0_REAL_POST_REJECTION | INCONCLUSIVE |
| UNIQUE_KNOWLEDGE_BENEFIT | NOT_ESTABLISHED |
| V1保护 | annotated tag v1-pre-v2-release → 0733933113faee3121b2c5d692ef4ee1400d4d0d |

证据：[252项日志](evaluation/final-remediation/p2-server-preflight/local-build/pytest.log)、[应用main CI](https://github.com/m13756445700-lgtm/codeaudit-agent/actions/runs/37741956460)、[P2-D结构化结果](evaluation/final-remediation/p2-deployment/result.json)、[考官指南](docs/EXAMINER_GUIDE.md)。

文档提交/合并不重建或替换服务器镜像。旧镜像、容器和数据卷保留，原始成功与失败日志保留；无需旧数据备份是用户本轮批准的发布策略，不是已完成备份。历史日志中的本地绝对路径是溯源信息，不是当前部署依赖；当前考官入口仅使用服务器路径和明确占位私钥路径。

本次仅文档/验收证据发布，禁止把新的GitHub main文档Merge SHA等同于旧镜像OCI revision。最终提交检查结果由PR #2合并及新main CI实际状态确认，不用历史CI冒充。

---

以下为2026-09-29/30历史发布轮次描述，原测试数、SHA与运行记录按当时范围保留。关于“整机重启”“仅main”“当前栈”的说法只适用于其历史日期；**本次最终应用的宿主机重启未验证**，分支列表以本轮最终远端核验为准。不得据此扩大当前验收声明。

# 历史发布记录（2026-09-29 / 2026-09-30）

## 历史整改状态（2026-09-30）

以下2026-09-29记录属于历史发布基线，不能替代当前整改验收。当前源码已增加攻击面结算、知识应用记录、Python AST导航、上下文压缩、读取范围反馈及可配置预算。各阶段测试结果和当前状态见下文。

服务器已只保留当前 V2 栈，考官入口已切换；每日自动任务及整机重启后自动恢复均实测成功。GitHub 仅保留公开 main。SSH 与考官命令见 README。

首轮20例复测TP10/FP0/FN0，但有两例PARTIAL；其后一次受HTTP402影响失败。充值后0cd8d15完整串行重跑TP10/FP0/FN0，19COMPLETE/1PARTIAL，整体完成性检查仍失败。真实311文件仓库前三轮均未完成；第四轮一例超限，三例被HTTP402中断。截至代码0cd8d15，GitHub fresh clone145项通过；EOF反馈修复源码在Linux146项通过（17.52秒）。第六轮定向回归有改善但全库仍未完成，见round6结果。不得据此宣传普遍准确率或已达到某个分数。详见 [提交状态](docs/SUBMISSION_STATUS.md)、[整改记录](docs/REMEDIATION.md) 和 `evaluation/` 中的预注册协议、成功与失败数据。

最新整改：846c881的定向两例及go-shell三次全部COMPLETE，全仓两例仍INCOMPLETE；82d37bb修复首次EOF反馈和JSON序列化预算，GitHub独立checkout150项通过。第九轮模型再次HTTP402，效果验收未完成，详见round8/round9记录。

正式白名单：`README.md`、本清单、`.gitignore`、`.dockerignore`、`.env.example`、`pyproject.toml`、`requirements-dev.txt`、`Makefile`、`Dockerfile`、`docker-compose.yml`、`agent-compose.yml`，以及以下目录。

| 目录 | 发布用途 |
|---|---|
| agent/ | V2 Engine、工具和有效静态消融依赖；无旧service/workflow |
| knowledge/、rules/、schemas/ | 判断知识、候选规则、静态结果schema |
| benchmark/、fixtures/ | 20个小型合成真值案例及分析器回归夹具；不是独立盲测集 |
| octobus/repo-tools/ | 固定SDK版本与锁文件、真实MCP能力桥 |
| scripts/ | 单入口部署、健康、Demo、真实模型/私有Git验收 |
| tests/ | V2及保留的确定性回归；测试容器将源码COPY进镜像 |
| docs/ | ARCHITECTURE、DEPLOYMENT、DEMO、SECURITY四份指南 |
| evaluation/ | 扩大评估、知识对照协议及公开汇总结果 |

原始开发证据、Master Plan、历史文档、日志、缓存、私密配置和发布过程报告保存在原工作区或忽略的 `.internal/`，不进入考官源码树。没有新增未经权利人授权的 LICENSE。

## 发布验证记录（2026-09-29）

- 清理后 Linux 回归：135 passed / 10.37s。原153项中移除18项退役V1服务契约测试；语义分析/防篡改/快照/SSH与HTTP输入/工具/Gate/模型契约仍保留。
- 全新项目名、独立daemon和volumes启动；真实MCP initialize/tools/list通过。
- 四组真实agent-compose Demo：A CONFIRMED1；B SQL假设REJECTED、另一个权限假设INSUFFICIENT；C CONFIRMED1/读取3of3；D COMPLETE/读取10of18/REJECTED2。D没有完整真值，不计算准确率。
- 新AI消融：replay=false，跨文件无候选而AI确认；安全映射静态NEEDS_REVIEW、AI拒绝；全部验收检查通过。
- 实际SSH私有Git夹具：通过；临时密钥、严格固定host key、不调用第三方账户。
- 核心/知识/规则/基准/OctoBus的64个文件与本轮原始构建字节一致。历史REV20例结果继续明确标为历史，不重新包装成发布期新模型测试。
- 已审查配置/测试中的secret/token等关键词；候选文件中真实配置凭据匹配0，私钥块0。该扫描不声称能识别一切未知敏感数据。

首次agent-compose image插值失败已修正；Docker Desktop云同步目录挂载I/O失败记录已保留，回归改用COPY源码的Linux测试镜像，发布工作区迁入独立本地目录。GitHub覆盖前：独立本地Git clone完整启动、135项回归通过（10.67s），真实沙箱C完成并确认跨文件问题；Ubuntu x86_64从标准Dockerfile重新构建、创建全新daemon/volumes，135项回归通过（17.79s），真实沙箱C完成。覆盖后的GitHub fresh clone记录保存在操作员最终发布报告。
