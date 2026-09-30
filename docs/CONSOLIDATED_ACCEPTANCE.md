# 集中验收与发布流程

本轮先开发、后统一离线测试；未恢复模型服务前，不运行任何 `--live`、`make benchmark`、`make integration-test` 或服务器演示触发。当前开发内容未推送或部署，线上仍是91c9e7a。已存在的每日09:00服务器任务未在本轮改动；集中验收时应避免与它重叠。

## 1. 离线测试与冻结

完成全部代码与材料后运行 `make docker-test`。没有Docker时可用安装了开发依赖和Semgrep的隔离Python环境执行 `python -m pytest tests -q`；缺少Semgrep的局部测试不能冒充全套。

以下命令仅生成计划，不初始化模型，不联网调用模型：

```sh
python -m scripts.consolidated_acceptance --output .internal/acceptance/frozen-candidate --repeats 2
```

默认包括20个历史开发Benchmark×2次，加8个业务案例×on/off/generic×2次，共88次计划运行。默认真实执行上限为每次1个运行，不会在准备阶段自动执行88次。计划记录实现与知识摘要、逐文件输入摘要、模型名称、预算和真值。任何源文件、知识或计划修改都要求新建验收目录。待部署候选用于真实测试时，应在实际测试环境重新冻结路径和摘要；计划内绝对路径不作跨机移植。

业务案例说明及标注在 `evaluation/business-ground-truth.json`，被审查源码只包含各自 `source/`。标注不能进入模型上下文；业务政策作为独立且对所有实验组一致的上下文提供。此组是项目自编回归，不是独立盲测。

## 2. 独立案例准备

在查看输出前由独立评审者选择真实仓库的固定提交或本地归档、标注目标位置、前置条件、反证与预期状态。用 `--external /path/to/external-cases.json` 加入冻结计划。格式如下；不要把供应商凭据放入配置：

```json
{"cases":[{"id":"external-001","source":"/evaluation/pinned-source","provenance":"repository URL, commit, reviewer and label date","policy":"documented business policy only; no answer hints","target":{"category":"authz","file":"src/service.py","sink":"return record","expected":"CONFIRMED"}}]}
```

没有独立选择和标注时，必须写“尚未独立验收”。Werkzeug已知案例仍可用于回归，但不能改称盲测。全仓默认任务与指定focus任务分开报告，不能相互替代。

## 3. 恢复模型后集中真实验收

操作者明确恢复服务后，使用候选源码及真实OctoBus配置：

```sh
python -m scripts.consolidated_acceptance --output /evaluation/frozen-candidate --live --max-runs 1
```

首个运行证明服务可用后，可显式扩大每批上限。执行串行，模型HTTP错误立即停止整批；失败记录保留，不覆盖重试。后续调用只继续未尝试项目；如需重做失败项目，应新建计划/尝试目录。模型用量保留为供应商返回的token，不伪造货币费用。不同实验组快照必须相同；有基础设施失败的样本不按语义漏报解释。

每例同时保留真实工具轨迹、计划、假设、调查笔记、逐项审查状态、最终判断、引用Gate及模型用量。历史Benchmark另运行相同快照的静态基线；AI差异按匹配漏洞位置与类别判断，不按调用次数证明价值。

## 4. 人工裁决与发布门槛

逐例核对目标及额外发现：可控输入、跨文件流、受保护操作、有效防护、业务政策、部署前提及引用完整性。将错误确认计FP，目标漏检计FN；LIKELY/INSUFFICIENT单独报告，不算CONFIRMED。未完成、延期、API故障与语义正确率分开统计。

知识收益以相同案例/预算下on/off/generic的重复配对差异为依据。只有on优于generic、改进实际影响判断且存在可核对知识应用时，才支持“独特收益”；样本少或置信不足必须保留限制。新增CA-K05是项目编写的分析方法，不是客户经验。

发布前必须同时具备：离线回归通过；完整Benchmark完成性/正确性检查通过；新业务成对案例通过；真实仓库重复有界审查正确且可靠收尾；有效AI消融；知识对照有可解释结果；所有失败和未审范围公开。准备脚本的`release_ready=false`是有意的：它不能替代人工裁决批准发布。

通过后统一提交、推送main、同步服务器并核对源码/镜像摘要，最后验证GitHub fresh clone。不得把开发完成写成模型验收完成，不承诺题目未定义的分数。

生成和汇总人工裁决均可离线执行：

```sh
python -m scripts.acceptance_review --campaign /evaluation/frozen-candidate
# 将review-template.json复制为reviews.json，逐例由评审者填写后：
python -m scripts.acceptance_review --campaign /evaluation/frozen-candidate --reviews /evaluation/frozen-candidate/reviews.json
```

汇总器拒绝不同快照的配对、重复裁决、缺少评审者或依据的裁决，也拒绝把模型HTTP故障写成语义FN。分组展示on/off/generic的重复次数与TP/TN/FP/FN/UNRESOLVED；它不会替评审者生成答案或自动证明知识独特收益。
