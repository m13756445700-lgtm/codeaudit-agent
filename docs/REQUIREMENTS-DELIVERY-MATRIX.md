> 2026-09-24更新：本页保留此前阶段记录。当前HR交付、公钥登录、原题触发器等状态统一以[原题核对表](EXAM-COMPLIANCE.md)和README为准；“待发布/可选SSH/私有仓库优先”等旧建议已撤销。

# 作业要求交付矩阵

2026-09-23；依据BRD第24节。技术通过不等于GitHub发布、评审授权已完成。

| ID | 要求 | 状态 | 资源与证据 |
|---|---|---|---|
| R01 | GitHub仓库 | 待发布 | URL待填写 |
| R02 | Agent源码 | 已准备 | agent/ |
| R03 | 部署配置 | 已准备 | agent-compose.yml、deploy/server/；私有配置另存 |
| R04 | README | 已补齐 | 15个必需章节 |
| R05 | 无明文密钥 | 发布包扫描 | evidence/review/PUBLICATION-CHECK.json；非所有未知密钥的保证 |
| R06 | 云服务器 | 已验证 | Ubuntu22.04.5、4C/约8G/40G；SSH单独交接 |
| R07 | Docker | 已验证 | 容器与整机恢复记录 |
| R08 | agent-compose | 已验证 | codeaudit-server-agent-compose |
| R09 | Project | 已验证 | codeaudit-server |
| R10 | Agent执行 | 已验证 | 重启前后真实模型Run |
| R11 | 运行日志 | 已保存 | 精选证据公开；原始会话受控 |
| R12 | OctoBus | 已验证 | codeaudit-server-octobus |
| R13 | Service | 已验证 | code-audit-service |
| R14 | Instance | 名称差异待确认 | 实际code-audit-local，BRD示例java-audit-instance；五方法已通过 |
| R15 | Capset | 已验证 | code-audit-agent；不公开Token |
| R16 | 实际调用 | 已验证 | 每次模型会话8次MCP调用；摘录和原始哈希 |
| R17 | 非公网暴露 | 已验证 | 主机回环19000、容器内部网络 |
| R18 | 重启恢复 | 已验证 | 启动标识变化、三个服务自动恢复 |
| R19 | 业务闭环 | 已验证 | Repo到Finding、受控Demo |
| R20 | LLM边界 | 已实现 | ARCHITECTURE.md及workflow/validation.py |
| R21 | 强决策 | 已实现 | validator/gate.py及负向测试 |
| R22 | 知识参与 | 已验证 | TC-12、rules_applied、decision_trace |
| R23 | 非显然知识 | 已实现 | false-positives.yaml等 |
| R24 | 通用失败模式 | 已准备 | field-notes.yaml，不冒充客户经历 |
| R25 | 工程复盘 | 已准备 | TROUBLESHOOTING.md |
| R26 | 证据链 | 已验证 | cases/完整六类证据 |
| R27 | 固定Commit复现 | 已准备 | matrix.json、Git bundle；发布SHA待填写 |

正式交付前：补仓库URL、发布Commit、考官访问确认和Instance名称映射确认。
