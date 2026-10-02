# 提交前状态（2026-10-02）

**暂不建议作为最终达标作品提交。** 部署与入口问题已修复，通用大仓库审计和独特知识收益仍未闭环。题目没有给出“120分”的量化标准，不能承诺该分数。

## Latest live acceptance: FAILED (2026-10-02)

Recharge verified. Six frozen real MCP runs finished: 3 COMPLETE, 3 PARTIAL, no HTTP errors. Both vulnerable full-scope runs missed the target. Focused vulnerable run recognized the flaw but reported INSUFFICIENT_EVIDENCE; focused fixed run rejected the target with implementation evidence. Safety conclusions outside formal decisions and weak self-review evidence remain open. See [full review](EVIDENCE_REMEDIATION_02_RESULT.md). No push/deployment. Earlier provider-blocked entries below are historical.

## Latest runner update (2026-10-02)

Per-job focus and persistent provider-failure stop are implemented in668f100. 184 offline Linux tests pass. The new [freeze02 plan](../evaluation/evidence-remediation-02/plan.json) and both311-file snapshots were verified on server. Prior freeze01 is historical and retained. Zero of six live audits executed; provider restoration is required. No publication or deployment.

## 最新集中验收：不通过（尚未发布）

候选9214a05完成99/100次真实尝试：92COMPLETE、2PARTIAL、5INCOMPLETE；job98再次HTTP402后停止。40次Benchmark和48次业务案例目标判断通过，但真实仓库漏洞版6次均漏掉已知目标，其中有错误防护解释。验收条件不满足，未推送、未部署。详见[集中验收结果](CONSOLIDATED_ACCEPTANCE_RESULT.md)。

## 最新离线整改（尚未发布）

已补防护主张的实现引用、平台前提证据契约和 REJECTED 反证要求，已加入 job91 原始失败判定回放与每段12次能力调用的调查检查点，并补齐绑定判定版本的结束前反证自复核。44项定向测试、178项隔离断网Linux全量测试通过；真实模型纠错效果未验证，模型自复核不等于独立评审。见[整改计划与测试记录](plans/2026-10-02-evidence-remediation.md)。

## 最新模型服务检查

2026-10-02单次连通性探针返回HTTP402，立即停止；新一轮6次审计均未执行。已冻结已知案例协议，并在断网容器核对实现指纹和两个版本各311个源文件。协议见[evidence-remediation-01](../evaluation/evidence-remediation-01/plan.json)。现有执行器尚需支持逐任务focus，修改后须生成新的实现指纹与计划，当前冻结记录不得覆写。

## 本地集中开发候选（历史阶段记录）

按操作者要求，本批先开发后集中离线测试，不调用付费模型、不推送或部署中间版本。已补调查笔记与逐项审查账本、src布局导航、8个跨租户成对回归案例、业务知识判断卡、默认零调用的冻结验收计划，以及遇模型HTTP错误停止整批的执行器和人工裁决汇总。具体步骤见[集中验收流程](CONSOLIDATED_ACCEPTANCE.md)。

真实模型有效性、全仓稳定性、独立案例和知识独特收益仍待集中验收；新增自编案例不能替代独立证据。线上与GitHub仍为91c9e7a。

## 已完成

| 要求 | 实际验证 |
|---|---|
| 公开 GitHub、唯一 V2 main | main 已更新；V1 archive 分支按旧 SHA lease 删除，历史 bundle 仅保留本机 |
| 服务器只运行 V2 | V1/重复 V2 容器、旧数据卷、旧部署目录和旧镜像已清理；保留唯一 V2 栈 |
| 考官 SSH 提交信息 | README 有地址、账户、22端口和登录示例；公钥已安装，未持有考官私钥，不冒称替考官完成了私钥登录 |
| 考官访问 V2 | 以 reviewer 权限验证 projects/triggers/methods/runs/report；可读源码，不可读 `.env`；sudo 仅限受控包装器 |
| 自动触发 | 每日北京时间09:00任务真实成功，run `5cb3b6c863fd` |
| 整机重启恢复 | boot ID 变化，四服务自动健康；重启后自动验收 run `229e4eb95ba8` 成功、MCP真实调用 |
| 完成契约 | 攻击面逐项结算；延期 PARTIAL、执行失败 INCOMPLETE；引用必须来自实际读取 |
| 模型实质参与 | 自主计划、假设与安全判断；确定性工具提供证据，Gate不创造安全结论 |
| 工程回归 | 部署源码145项Linux测试通过；GitHub源码 `0cd8d15` fresh-clone测试145项通过（17.75秒）；状态反馈846c881的GitHub独立checkout通过148项（17.48秒）；82d37bb边界修复GitHub独立checkout150项通过（18.13秒） |
| 公开文档 | 部署、SSH、设计、知识来源、实际排错、30分钟演示和失败评估记录齐备 |

## 尚未通过与下一步

1. **模型再次HTTP402，真实评估等待供应商恢复。** 第九轮发生新的402，已停止新增模型调用并保留失败数据。此前恢复记录如下： 第四轮评估期间返回 HTTP 402；操作者充值后真实V2触发 run `c567740b179d` 已成功。失败记录保留。并行实验还暴露能力忙碌错误被误报为响应无效，已实现明确错误及有界重试，后续验收串行运行。
2. **真实规模自主审计未达标。** Werkzeug 311文件的前三轮共24次均耗尽上下文或迭代预算。第四轮一个全库运行仍超限，其余三个被HTTP402中断。所有失败数据保留在 `evaluation/`，未发现目标不能包装成通过。第五轮充值后仍有漏报和超限。第六轮加入字面证据记忆及已知案例实践卡后，漏洞版本定向审查为LIKELY/PARTIAL，修复版本定向审查COMPLETE；两次全库运行仍超限。这是训练后回归，不能算独立泛化验证。EOF反馈已修复并部署。第七轮漏洞版定向COMPLETE/CONFIRMED，修复版定向PARTIAL，两次全库仍INCOMPLETE。全库追踪显示收尾过晚、未先登记假设即提交判断等问题。第八轮加入每轮状态反馈与提前收尾后，两次定向均COMPLETE并正确区分目标，go-shell三次COMPLETE/CONFIRMED；两次全库仍INCOMPLETE，不能算整体闭环。首次读取EOF及序列化上下文大小修复已部署，但第九轮再次HTTP402：首例27次调用后中断，其余三例0次调用；Go三次也INCOMPLETE，不能评价修复效果。
3. **知识的独特收益未证明。** 18次对照中项目知识避免了关闭知识时的两次误报，但通用文本也有效；项目知识组还有一次PARTIAL。需要更具业务针对性的真实案例、独立评判和足够重复。现有实践卡仅声明项目实验来源，不虚构客户经验。
4. **最终Benchmark未通过。** 首轮20例TP10/FP0/FN0，但两例PARTIAL；最新尝试受HTTP402影响失败。充值后已在0cd8d15完整串行重跑20例：TP10/FP0/FN0，19例COMPLETE，go-shell因将不存在功能标为deferred而PARTIAL，整体仍未通过。详见 `evaluation/benchmark-post-recharge-results.json`。不能把开发夹具结果宣称为独立准确率。
5. **支持边界仍存在。** Python AST导航仅提供语法候选；动态分派、其他语言语义和未提供的部署/权限策略不能保证。跨租户权限等真实业务标注评估尚未补齐。`--focus` 是明确限定范围的辅助调查，不等于全库成功。

完整过程见 [整改记录](REMEDIATION.md)，协议及结果见 [evaluation](../evaluation/)；下次工作从上述未通过项继续，已验证部署和历史成功记录不重新包装为新结果。
