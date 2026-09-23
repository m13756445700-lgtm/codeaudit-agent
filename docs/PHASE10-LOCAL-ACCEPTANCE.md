# Phase 10 本地部署验证与剩余验收

日期：2026-09-23。

> 后续更新：目标服务器部署、整机重启和SSH验收现已通过，见PHASE10-SERVER-ACCEPTANCE.md。下文“尚未满足”章节保留为本地验证阶段的历史记录。

## 已确认结果

1. Maven 3.9.9 / Java 17实际构建Spring Boot + MyBatis Demo，BUILD SUCCESS。
2. Demo以非root用户在无网络、根文件系统只读的容器内启动；仅容器内回环地址可访问。
3. `/users/raw?order=id` 返回1条测试数据；绑定查询demo返回1条，注入样式字符串作为绑定值返回0条。
4. 本地OctoBus和Agent Compose容器完成重启，原数据卷、服务注册及凭据保留；四类漏洞MCP回归通过。
5. 两个服务已设置unless-stopped重启策略。此设置仍依赖Docker引擎随主机启动，不能替代整机重启验收。
6. 重启后真实Codex/DeepSeek会话通过严格校验：Run `98bf59ccc2f7e87d503d040061d1d12cd17dc45e723cd9880e4ce243ff88bd1e`，SQL正反例分别为VERIFIED、REJECTED。结果与实际工具及可信验证记录一致，证据见 `runs/phase10-local/recovery-agent/result.json` 和对应会话目录。

证据位于 `runs/phase10-local/`：demo-build.log、demo-startup.log、demo-result.json、restart-mcp.log。Demo镜像为codeaudit-demo:verified，审计服务镜像为codeaudit-octobus:phase8-path。

## 尚未满足的最终交付条件

- 指定4C / 8G / 40G服务器的实际资源核验。
- 目标服务器部署与网络、端口、目录权限核验。
- 目标服务器整机重启后的自动恢复。
- SSH登录、重启后服务及模型真实调用验收。

当前缺少目标服务器地址/SSH别名及用户名，已请求用户补充，不收集聊天中的密码或私钥。上述项目保持未完成，不把本地Docker结果当成服务器验收。

## 服务器验收执行顺序

1. 确认目标主机身份、资源、可用磁盘和已运行业务；明确维护窗口。
2. 部署固定版本镜像、受控仓库及服务配置；私有凭据通过主机受限文件注入。
3. 验证服务进程、五个MCP方法和四类案例；保存日志与固定提交。
4. 验证开机启动配置和重启策略，记录回退镜像及配置备份。
5. 在已确认窗口执行整机重启，通过SSH重新登录；重新跑MCP及一次模型会话。
6. 更新验收矩阵和最终状态；失败时保留现场并恢复前一版本，不写通过。

## 回退

本地前版容器保留为停止状态。需要回退时，先停止当前OctoBus，避免并发使用同一数据卷；恢复前版容器及端口后，再跑真实MCP检查。镜像回退不自动回退数据格式，未来有数据迁移时需单独备份和兼容性验证。
