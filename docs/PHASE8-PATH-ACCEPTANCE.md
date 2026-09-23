# Path Traversal 首批验收记录

日期：2026-09-23。TC-10采用用户明确确认的勘误，原BRD保留。

## 实现与本地验证

- TC-09未保护文件路径：VERIFIED。
- 原normalize边界样例：NEEDS_REVIEW。
- base和target均toRealPath、越界抛异常、读取同一target：REJECTED。
- 全量121 passed in 56.66s。证据：runs/phase8-path/final-regression.txt。
- 首轮专项扫描出现外部终止（-9）；后续全量回归通过，根因未确定，未更改失败判定。

## 真实服务验收

镜像codeaudit-octobus:phase8-path已部署。本次脚本先验证SQL，再验证Command及静态跨文件调用、SSRF，最后验证Path三候选；全部通过。日志：runs/phase8-path/mcp-verification.log；路径证据：runs/phase8-path/mcp-result.json。

原phase8-ssrf容器停止并保留为回退版本，不并发使用数据卷。五个受控方法及原Service/Instance/Capset沿用。

## 边界

仅支持明确类型、单方法直线数据流以及严格的真实路径检查结构；不支持的路径变换、保护、分支保持NEEDS_REVIEW。负例不构成对文件系统竞态安全的认证：可信基目录和阻止攻击者并发修改文件系统是部署前提。见PHASE8-PATH-ERRATUM.md。

模型及十二案例统一验收结果在完成后补充，不以本地单元测试替代。

## 模型验收：通过

Run a2a274853ac075aaeb405a0bebb051f2c850fbbe0392d39c32c86d08ee2daca6，17次真实工具调用，5个候选全部覆盖，最终JSON与服务端可信证据一致。证据：runs/phase8-path/agent/summary.json。Phase8限定场景验收通过，完整十二案例在Phase9另行汇总。
