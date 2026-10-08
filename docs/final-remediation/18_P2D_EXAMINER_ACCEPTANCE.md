# P2-D 考官访问与验收记录

版本：1.0｜日期：2026-10-08｜对象：codeaudit-reviewer@8.130.121.3。

## 1. 结论

**EXAMINER_SSH_LOGIN=NOT_RUN**。用户没有考官私钥；未生成替代密钥、未复用 root 密钥、未修改 SSH/authorized_keys/sudoers。**EXAMINER_CLI_ACCESS=PASS_VIA_RUNUSER_NOT_SSH**：以下命令是在服务器上切换到已有考官用户后，通过原受限 sudo wrapper 执行，不能替代真实远程认证。

| 项目 | 实际执行结果 | 适用范围 |
|---|---|---|
| status / projects / triggers / methods / runs | 各退出0，重启前后均通过 | 本地考官身份+现有sudo策略 |
| trigger | 退出0；调度 Run `28250be863ed` succeeded | 一条真实模型受控任务，非Mock |
| report / trace | Audit `f9766bf65b304b29b9c02f9aa4b80234`，各退出0 | 已生成的实际报告及trace |
| 重启后report | 退出0；输出校验和不变 | 新四容器重启、完成任务持久化 |
| .env / .runtime.env 读取 | 各退出1 | 预期拒绝 |
| Docker socket写权限 | 退出1 | 预期拒绝 |
| root shell sudo策略查询 | 退出1 | 不在授权命令列表，未执行root shell |
| 实际SSH登录 | NOT_RUN | 待现有私钥持有人完成 |

wrapper SHA256=`444cd41fb50941fefe0712017685d67026da05f50cb34fed8f0788a478a8f78a`，与修改运行目录alias前一致；普通bash shell仍存在，无Docker/root组权限扩展。此前账号密码锁定的配置检查不构成公钥登录成功证明，考官来源IP/PAM链尚需实测。权限测试仅覆盖列出的边界，不能宣称所有恶意输入、环境变量或普通文件读取面均通过审计。

## 2. 实际入口与受控结果

wrapper实际usage：`status|projects|triggers|runs|methods|trigger|audit HTTPS_URL|report [AUDIT_ID]|trace AUDIT_ID`。没有新增restart/shell子命令，指南未编造参数。

新project=`codeaudit-final`，Agent=`auditor`，scheduler=`daily-v2-audit`。Report使用32位 Audit ID，不能使用短Scheduler Run ID。模型deepseek-flash：7次真实响应、53,474 total tokens；14Agent动作中仅4次为OctoBus MCP调用。H1 gate通过，conditional_code command_injection CONFIRMED；部署可利用性未知。

报告文件SHA256=`4cb6b870703422192fe97cac4428f394b6569b048d08aec5fde97b9225121e78`；读取stdout含汇总，其SHA256=`ea114e12160c3a4096ed364e5570dfe17d3027e0158d3d968d6253537f6d1712`，二者口径不同。新四容器重启后报告、trace等6文件SHA一致，project/scheduler/MCP无需bootstrap恢复；正在执行任务续跑NOT_RUN。

## 3. 人工真实登录验收

具体登录与命令见 [EXAMINER_GUIDE](../EXAMINER_GUIDE.md)。需要现有授权私钥持有人、独立客户端、可信主机key核对及可达的SSH22；不要把私钥发送到聊天。登录成功后逐项保存五个查询、已有报告和trace的脱敏执行结果；一次成功不能自动标记所有操作通过。

审计触发入口已通过本地考官身份实测；考官如需独立触发，使用指南的现有命令并确认真实模型用量。不需更改账号权限。若现有密钥不可用或登录失败，先保留错误并提出具体认证整改，等待单独授权，不能自行解锁或换key。

## 4. 剩余条件与交付等级

已完成：部署版本身份、实际工具/模型审计、报告读取、容器重启恢复、现有考官CLI和已列权限边界。待完成：考官真实SSH和远程逐项操作确认。`P2D_GATE=CONDITIONAL`。

`P0_REAL_POST_REJECTION=INCONCLUSIVE`，`UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED`。证据：`evaluation/final-remediation/p2-deployment/result.json`、`runtime-verification.json`、`e2e-result.json`、`evidence-result.json`、`restart-result.json`。未把历史受限实验改为PASS。

自检结论：可内部评审与考官操作参考；真实登录验收未完成，下一步由原授权密钥持有人执行人工步骤，然后等待最终Gate Review。
