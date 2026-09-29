# 30 分钟现场核查

## 0–5 分钟：设计

展示 README 架构图。以公开 Git URL 输入，解释安全快照、模型自主计划与假设、OctoBus 工具证据、模型判断、只降级不创造漏洞的 Evidence Gate。用实际 trace 说明读取和知识检索的选择来自模型，不来自固定流水线。

## 5–15 分钟：运行与架构

按 README SSH 登录。运行 `sudo codeaudit-review projects`、`triggers`、`methods`、`runs`、`report`，核对 V2 方法与审计 UUID。启动 `trigger`，检查 MCP transport、逐项攻击面结算、已读行数和未读文件。说明 daemon 管理沙箱，OctoBus 路由能力，Engine 调用实际配置模型；provider 名称并非审计模型的证据。

## 15–25 分钟：知识与安全判断

打开 `knowledge/v2/command_injection.md` 的 CA-K01，对比 Runtime.exec 字符串、显式 shell 和 argv 三种边界。沿 app → service → worker 查看实际行号与反证，再查看 `knowledge_application`。打开 CA-K02，解释为什么 debug 设置不能自动证明生产 RCE。展示知识开关对照的实际成功和失败；如果知识没有改善结果，明确承认。固定小样本通过不代表完整任意仓库审计。

## 25–30 分钟：实际问题

从 `docs/REMEDIATION.md` 选取两项：静态基线预检不兼容快照、运行器覆盖模型环境、完成条件过宽、scheduler PATH 启动失败。说明触发条件、定位证据、修复与回归。最后明确尚未支持的动态语言分派、外部依赖语义、部署事实和超预算范围。
