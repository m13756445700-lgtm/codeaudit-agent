# 运行时证据复核（2026-10-06）

官方公告说明旧版Werkzeug在Windows特定Python环境下可能返回不安全路径。但固定标签的CPython源码与路径形状对照表明，先前报告的版本及影响表述过宽。本轮没有付费模型调用，不改变历史判定或发布。

| 固定标签 | //server/share | //server/share/file |
|---|---|---|
| CPython3.10.0 | isabs=False | isabs=True |
| CPython3.11.0 | isabs=False | isabs=True |
| CPython3.11.1 | isabs=False | isabs=True |
| CPython3.11.2 | isabs=True | isabs=True |
| CPython3.11.9 | isabs=True | isabs=True |

方法：从官方固定标签下载ntpath.py并记录SHA256，人工检查isabs、splitdrive和_get_bothseps，仅提取这三个字符串函数，在本机Python执行输入对照。没有执行完整外部模块、目标仓库或任何文件系统攻击。这不是在Windows运行这些Python版本，不能替代部署或利用验证。原始源码私有保留，公开的来源URL、哈希及结果在[evaluation记录](../evaluation/runtime-evidence-20261006.json)。

公告的“Python>=3.11不受影响”摘要与3.11.0标签实现存在差异，尚未定位实际变更的补丁版本，不能猜测。已将差异写入知识卡。此前模型以带文件后缀的UNC路径泛化绕过，以及把反斜杠路径也归入绕过的表述，均不能由这些证据支持。Werkzeug还会检查反斜杠；调用者的isfile/open也需要单独证明，不能从不安全路径字符串直接推出任意文件读取。

调用者“没有独立缺陷”与“没有继承风险”不是同一结论。下一步应在报告中清楚表达依赖风险，并校正验收标准的证据层级：区分路径原语缺陷与完整文件暴露，不为匹配标签强迫模型升级CONFIRMED。历史冻结标签及失败结果保持原样，新协议应说明变更理由。

本轮知识卡更新后，28项相关工具与冻结协议测试通过（0.28s）。既有198项全量测试对应此前代码；本轮未重复全量Linux或真实模型验收。next_task：确定补丁版本边界及具体路径在调用链上的影响，补可重复且隔离的语义证据，再设计新版验收与继承风险表达。整体仍未通过，不推送或部署。

## Patch boundary follow-up

The previous unknown transition is now established for the 3.11 branch: adjacent official tags 3.11.1 and 3.11.2 differ on bare UNC paths. This does not establish other release branches or Windows filesystem exposure. Historical evidence remains unchanged.

[Replay script](../scripts/replay_runtime_evidence.py) and [new evidence](../evaluation/runtime-patch-boundary-20261006.json) pin the official URLs and SHA256. Save those raw sources as ntpath-3.11.1.py.txt and ntpath-3.11.2.py.txt, then run `python -m scripts.replay_runtime_evidence SOURCE_DIRECTORY`. The script checks hashes before compiling only the three reviewed string helpers. It neither downloads nor imports the target repository.

Tampered-source rejection test: 1 PASS. Adjacent-tag replay completed with expected False/True bare-UNC behavior. No live model test, publication, or filesystem exploit claim. Next: establish caller impact and freeze an explicit distinction between a path-primitive contract defect and proven file exposure.

## Call-chain follow-up and frozen regression06

The public helper accepts variadic components. Distinguish one UNC filename from a bare UNC share plus a separate relative filename. The local string-only [trace](../evaluation/path-component-trace-20261006.json) preserves this distinction; it does not run target code or prove filesystem access. Actual single-component callers additionally use isfile or resource-reader checks. Pinned runtime facts are now included in the retrieved knowledge card, so the model can cite the knowledge hash while independently reading target guards. [Protocol and offline verification](plans/2026-10-06-runtime06.md).

## Pinned POSIX string semantics (follow-up 2026-10-07)

Added [exact tagged normalization/join replay](../evaluation/posix-runtime-evidence-20261006.json), selected from CPython3.11.1 after SHA verification. Run `python -m scripts.replay_runtime_evidence SOURCE_DIRECTORY --posix`. It selects the reviewed Python fallback, not native acceleration; no target code or filesystem access is executed. This closes the missing dependency-string-semantics evidence, not deployment or file exposure.
