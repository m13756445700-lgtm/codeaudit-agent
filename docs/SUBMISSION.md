# 考官提交入口

GitHub（公开、V2 main）：https://github.com/m13756445700-lgtm/codeaudit-agent

服务器：8.130.121.3；用户codeaudit-reviewer；端口22。考官公钥已配置，请使用对应私钥：

```bash
ssh -p 22 -i /path/to/examiner_private_key codeaudit-reviewer@8.130.121.3
sudo codeaudit-review status
sudo codeaudit-review projects
sudo codeaudit-review triggers
sudo codeaudit-review methods
sudo codeaudit-review runs
sudo codeaudit-review report
```

演示调用 `sudo codeaudit-review trigger` 会使用配置的模型额度。请先查看已有report/trace。服务器保留此前已验证V2部署；当前提交源码的新增修复需从GitHub按README构建复现，两者版本差异见[交付状态](SUBMISSION_STATUS.md)。本次没有宣称已完成最新源码服务器部署验收。

建议阅读顺序：README（架构、部署、入口）→[交付状态](SUBMISSION_STATUS.md)（当前证据与边界）→[第11轮基准与消融](EVIDENCE_REMEDIATION_11_RESULT.md)→[最新反证机制](plans/2026-10-07-fresh-context-critique.md)。失败样例和新轮次结果均在evaluation目录，不删除、不改写模型原始判断。

提交说明可直接使用：

> 已提交CodeAudit Agent V2最新版源码、部署说明、考官SSH入口及测试/评估材料。当前源码211项Linux测试通过，具备Git/ZIP/本地仓库输入、AI动态调查、真实OctoBus调用及证据报告。已知开发基准与AI对照结果附于仓库。较大仓库审计稳定性和独特知识收益仍有明确限制，已在交付状态中披露，供现场讨论与复核。
