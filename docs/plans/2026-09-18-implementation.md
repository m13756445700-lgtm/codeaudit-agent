# CodeAudit V1.0 Implementation Plan

Goal: 按冻结 BRD 实现 Java Spring Boot + MyBatis 证据审计。
Architecture: 受控仓库读取和扫描形成证据，确定性 Gate 独占最终状态；LLM 仅规划、上下文解释和报告。OctoBus 暴露五个方法。
Tech Stack: Python 确定性核心、JSON Schema、Semgrep、Java 17 测试仓库、OctoBus Node SDK、agent-compose Codex。

## 执行与验收顺序
1. Skeleton：目录、Schema、CLI、配置、结构日志；测试配置边界与 Schema。
2. Static Scan：真实 Semgrep 执行，TC01/02 候选；工具失败重试一次并明确失败。
3. Evidence Pipeline：固定 Git commit 取证；有限跨函数分析；不支持语法降级 UNKNOWN。
4. Evidence Gate：六类证据逐项校验；篡改、缺失、断链、不可达测试。
5. Knowledge：版本化规则与开关，TC12 对照实验。
6. OctoBus：五方法与受限目录、参数、资源配额；本地契约与实际服务测试分开记录。
7. Agent Compose：Codex 受控能力调用；LLM 输出 Schema 重试；真实日志验收。
8. 其余漏洞类型：Command、SSRF、Path，分别正反例。
9. 全量验收：12 Case、重放、负向与密钥扫描。
10. Deployment：云端部署、重启恢复、SSH；无服务器访问时标待现场验证。

## 强制边界
每阶段先测试并报告，再继续。文档伪代码对 UNKNOWN reachability 检查不足，以第9.1条为准：UNKNOWN 不能 VERIFIED。缺证与已证伪分开。有效防护需控制实际流向 Sink 的值。绝不接受 LLM 自报 integrity PASS。
BRD 明确 Codex，既有 OpenCode 冒烟不能冒充 Phase7 完成。
