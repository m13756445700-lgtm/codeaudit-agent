# 10分钟评审演示

适用对象：考官与作业所有者。日期2026-09-23。

## 建议顺序

| 时间 | 动作 | 验收要点 |
|---|---|---|
| 0–2分钟 | README及ARCHITECTURE | 模型不裁决、Gate独立复核 |
| 2–4分钟 | 资源清单及服务器验收摘要 | 服务运行、整机重启证据与SSH |
| 4–6分钟 | evidence/review/cases/TC-01、TC-02 | 同一类风险为何分别VERIFIED和REJECTED，检查六类证据 |
| 6–8分钟 | TC-12开关对照、TC-05/10勘误 | 知识真实参与及保守边界 |
| 8–10分钟 | 模型调用摘录、报告和局限 | 真实工具结果、固定Commit、待复核场景 |

## 无服务器也能检查

精选证据位于evidence/review/。查看matrix.json的固定Commit；fixtures/*.bundle可用`git clone <bundle路径> <新目录>`离线克隆。历史证据不冒充本次重新执行。

安装依赖后运行：

```bash
PYTHONPATH=. python scripts/run_acceptance_matrix.py --output runs/exam-new
```

会重新扫描并生成新Commit及证据，旧报告哈希不应被替换。新旧案例预期状态应一致。

## 服务器演示（所有者或已明确授权操作人员）

以下命令不包含凭据，需先通过单独约定的SSH方式登录。

```bash
docker ps --filter name=codeaudit-server --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker exec codeaudit-server-octobus octobus service list
docker exec codeaudit-server-octobus octobus instance list
python3 -m json.tool /opt/codeaudit-agent/evidence/reboot-result.json
python3 -m json.tool /opt/codeaudit-agent/evidence/agent-after-reboot/result.json
```

如需新的真实模型演示（消耗模型额度，先由所有者同意）：

```bash
cd /opt/codeaudit-agent/releases/20260923
CODEAUDIT_DOCKER=/usr/bin/docker \
CODEAUDIT_DAEMON_CONTAINER=codeaudit-server-agent-compose \
CODEAUDIT_OCTOBUS_CONTAINER=codeaudit-server-octobus \
CODEAUDIT_PROJECT_CONFIG=/data/work/codeaudit-server/agent-compose.yml \
PYTHONPATH=. python3 scripts/run_phase7_verification.py \
  --max-attempts 1 --output /opt/codeaudit-agent/evidence/exam-new
```

选尚未使用的输出目录。失败必须显示失败，不用已有结果冒充新运行。只读评审账号默认不能运行Docker；由所有者操作或另配固定验证入口。

## 验收提问

1. Source如何到达Sink？有哪些原始代码引用？
2. 保护存在为何足够/不够？未知过滤为什么待复核？
3. 证据哈希如何绑定提交？修改代码后能否仍通过？
4. 关闭知识规则后为何改变结论？
5. 如何证明模型实际调用而非文本计算？

## 演示结束

确认仓库访问、版本SHA、接受的勘误与命名映射；记录未通过项及后续动作。无需再次演示整机重启，已有真实证据；如考官要求重做，需另约维护窗口。
