# Phase 10 服务器最终验收

版本：1.0；日期：2026-09-23；用途：面试作业交付与复核。

## 结论

目标服务器部署、真实工具及模型调用、整机重启恢复、SSH重新登录均已验证通过。此结论适用于BRD及用户确认的TC-05、TC-10勘误、当前限定Java分析场景；不代表任意Java工程或所有漏洞均可自动证明。

## 验收结果

| 项目 | 结果 | 本地证据（相对项目根目录） |
|---|---|---|
| 主机资源 | x86_64、4核、约8GB内存、40GB系统盘；初查可用26GB | runs/phase10-server/evidence/host-before-reboot.json |
| 四类漏洞真实MCP调用 | 重启前后均通过，含五个受控方法、鉴权及越界负例 | evidence/mcp-before-reboot.log、mcp-after-reboot.log |
| BRD案例 | 12/12通过，实际Semgrep与独立Evidence Gate | evidence/acceptance-cases/matrix.json |
| Java Demo | 移植本地实际构建的JAR，服务器Java17容器运行；重启前后3/3接口检查通过 | evidence/demo-before-reboot.json、demo-after-reboot.json |
| 重启前模型 | VERIFIED / REJECTED，严格会话校验通过 | evidence/agent-responses-before-reboot/result.json |
| 整机重启及SSH | 用户授权一次重启；启动标识变化、SSH重新连接、3个服务自动运行 | evidence/reboot-result.json |
| 重启后模型 | VERIFIED / REJECTED，严格会话校验通过 | evidence/agent-after-reboot/result.json |

表内缩写 `evidence/` 均指 `runs/phase10-server/evidence/`。

重启前Run：`eb756a8c982093a0865e4d7a86e5754ff96b11ce8cf475972da02a29c4adecca`。

重启后Run：`cb1b878c2ea7efb28e0829d7fcf52d3c8b7af45ac96d7d7d3ee2e75f6b0e87ba`。

## 部署与访问

- 服务器工作目录：`/opt/codeaudit-agent`；源码：`releases/20260923`；证据：`evidence`。
- 新增独立容器：`codeaudit-server-octobus`、`codeaudit-server-agent-compose`、`codeaudit-server-demo`；原有两个服务保留。
- OctoBus端口仅绑定服务器回环地址`127.0.0.1:19000`；Agent Compose仅容器网络可访问；Demo无外部网络和宿主机端口，非root、根文件系统只读。
- Service：`code-audit-service`；Instance：`code-audit-local`；Capset：`code-audit-agent`。为复用已验证工具前缀，服务器沿用该Instance ID。
- 容器均为`unless-stopped`，Docker开机启动已启用；整机恢复已实际验证。
- 私有凭据保留在服务器受限文件中，不包含于公开文档。模型采用与本地通过配置一致的DeepSeek及Responses接口协议。

## 故障记录与处理

1. 首次服务导入因npm缓存指向root目录而失败；改为服务数据目录缓存后导入成功。
2. 复用旧守护进程时，模型仅输出文本，严格验收拒绝；旧进程使用Chat Completions协议。新建独立守护进程并采用本地已验证配置后会话通过，未修改旧服务模型配置。该结果不证明所有Chat Completions部署均不可用。
3. 新进程首次尚未就绪，随后CLI未登录导致鉴权拒绝；完成真实认证后测试通过。失败日志保留，未计为通过。

## 恢复与回退

恢复定义见 `deploy/server/compose.yml`，服务器副本为 `/opt/codeaudit-agent/compose.yml`，配置语法已校验。当前容器通过Docker直接创建，尚非Compose管理；不得直接执行Compose覆盖。重建前应先备份数据与凭据、停止对应容器、确认名称冲突处理后再使用该定义。

普通主机重启无需重建。若重建Agent Compose容器，需使用服务器现有凭据重新执行CLI认证；不要把凭据写入聊天或公开命令记录。回退可停止新增的三个容器，保留数据卷与证据，原有服务继续使用；不要并发启动两个OctoBus进程共享同一数据卷。

## 能力边界与交付标准

- 四类漏洞按现有规则和固定样例验收；未知过滤、动态分派、证据不足等保持NEEDS_REVIEW。
- TC-10真实路径边界证明依赖可信基目录及检查到读取期间无攻击者文件系统变更；不宣称消除TOCTOU风险。
- SSRF静态映射证明不替代DNS、重定向与出口网络策略验证。
- 模型仅负责调用和解释，VERIFIED仍由六类证据及独立Gate决定。

下一步：以本验收记录、ACCEPTANCE-MATRIX.md和BRD勘误准备作业演示；新增范围须单独定义验收标准。
