# V2 Final Release Manifest

## 当前整改状态（2026-09-30）

以下 2026-09-29 记录属于历史发布基线，不能替代当前整改验收。当前源码已增加攻击面结算、知识应用记录、Python AST 导航、上下文压缩、读取范围反馈及可配置预算。最新 Linux 全量测试 141 项通过（18.31 秒）。

服务器已只保留当前 V2 栈，考官入口已切换；每日自动任务及整机重启后自动恢复均实测成功。GitHub 仅保留公开 main。SSH 与考官命令见 README。

当前 20 例复测 TP10/FP0/FN0，但有两例 PARTIAL，整体验收检查未通过。真实 311 文件仓库前两轮均未完成，第三轮正在评估。不得据此宣传普遍准确率或已达到某个分数。详见 [整改记录](docs/REMEDIATION.md) 和 `evaluation/` 中的预注册协议、成功与失败数据。

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
