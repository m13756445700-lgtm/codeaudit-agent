# Phase 7：Codex 与 OctoBus 联动验收

状态：2026-09-22 本地Phase7验收通过，详见 PHASE7-LOCAL-ACCEPTANCE.md。以下保留服务器部署操作参考，服务器仍需独立复验。

## 本轮新增
- agent-compose.yml：独立 codeaudit-agent 项目，provider=codex，引用已验收的 code-audit-agent capset。
- deploy/guest：基于既有固定摘要 guest 镜像生成受限镜像。补丁仅匹配已核对的 runner 结构；不匹配即构建失败。
- agent/prompts/auditor.md：五方法调用流程，固定Commit，禁止修改Gate结论。
- agent/workflow/validation.py：比较模型结果与服务保存的 validation-result.json；结构化输出最多2次尝试。现已通过 scripts/run_phase7_verification.py 接入本地实际运行及有限重试，逐项核对本次会话证据。

## 服务器准备
将完整 codeaudit-agent 项目同步到 /opt/agent-poc/data/agent-compose/work/codeaudit-agent。不要复制本机虚拟环境、node_modules或真实密钥。
在该目录建立权限0600的 .env，填写 CODEAUDIT_CODEX_MODEL 和 CODEAUDIT_OCTOBUS_TOKEN。使用现有capset令牌；不打印令牌。
本轮服务增加 validation-result.json 留存：同步 agent/service.py 后需按既有Phase6部署方式更新实例代码，再做结果一致性验收。
模型需支持当前Codex运行链路，不能根据历史OpenCode成功推断Codex已经可用。

## 执行（服务器 /opt/agent-poc/deploy）
```bash
cd /opt/agent-poc/deploy
ac() {
  docker compose --env-file agent-compose.env -f agent-compose.compose.yml exec -T agent-compose agent-compose --host http://127.0.0.1:7410 -f /data/work/codeaudit-agent/agent-compose.yml "$@"
}
ac config --quiet
ac build
ac up
```
三个步骤分别确认成功。构建失败不得跳过补丁改用原始宽权限镜像。

启动审计时提供真实已登记仓库标识和固定commit：
```bash
ac run auditor --detach --prompt '审计 repository=<仓库标识> commit=<完整Commit SHA>。仅使用OctoBus五个受控方法，逐候选执行RunValidation，并按系统约定返回结构化结果。'
```
记录输出中的Run ID，按该ID查询，不混入历史运行日志：
```bash
ac inspect run <Run-ID>
ac logs --run <Run-ID> --tail 100
```

## 验收必须同时满足
1. Codex真实运行成功；不能仅看exit code。
2. OctoBus审计包含InventoryRepository、ScanCandidates及RunValidation成功调用，时间与本次运行匹配。
3. 所有候选已验证或明确列为失败/待复核；无遗漏宣称干净。
4. 模型输出与该次服务保存的裁决一致；变更状态必须被校验器拒绝。
5. 实测Shell、文件写入、任意公网访问不可用。当前补丁仅是配置措施，不等同于网络防火墙；如实测仍可越权则Phase7失败，应增加隔离策略后重测。
6. 保存运行日志、access log、裁决JSON及权限负向测试结果。

## 兼容性边界
已核对本地agent-compose v2607.10.0源代码。镜像内编译产物仍须通过实际build验证。
Codex功能开关参考：https://developers.openai.com/codex/config-reference 。服务器版本支持情况须实测。

下一步：取得上述真实证据后，再进入Command Injection、SSRF、Path Traversal；禁止把本地配置测试当成端到端验收。
