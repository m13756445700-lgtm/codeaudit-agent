# 评估输入

本目录保留开发者编写的可复现样例，不包含模型调用原始记录或特定机器的部署数据。

| 内容 | 作用 | 使用入口 |
|---|---|---|
| `business-cases/` 与 `business-ground-truth.json` | 多租户读写、批量与缓存访问的授权对照 | `scripts/consolidated_acceptance.py` |
| `p1-heldout/` | 命令注入、授权、路径、反序列化、SSRF 与模板样例 | `scripts/p1_knowledge_eval.py` |
| `../benchmark/` | 固定 20 个安全分析样例与标注 | `make benchmark` |

标注包含适用前提，不能脱离前提判断正负例。开发者自建样例不是独立盲测，也不能代表任意仓库上的准确率。运行模型对照需要自行配置服务及配额；先阅读对应脚本的参数和预算约束，再运行并保留本次结果进行人工复核。
