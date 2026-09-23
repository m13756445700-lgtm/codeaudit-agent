# CodeAudit Agent V1.0

**交付状态（2026-09-23）：技术验收通过；GitHub首次发布、考官访问确认待完成。**

入口：[资源清单](docs/DELIVERY.md) · [27项要求映射](docs/REQUIREMENTS-DELIVERY-MATRIX.md) · [演示流程](docs/EXAMINER-DEMO.md) · [GitHub上传与协作](docs/GITHUB-HANDOFF.md)。

## 1. Project Overview

输入受控Git仓库和固定Commit，分析Java Spring Boot + MyBatis代码并输出Finding JSON及Markdown。需求基线：[BRD/PRD](docs/BRD-PRD.md)，原文哈希见docs/BASELINE.sha256。

## 2. Why this project

区分扫描候选、证据充分的漏洞、误报和待复核结果。成功标准是判断可验证、证据可复现，不以发现数量评估。

## 3. Architecture

Codex/DeepSeek规划 → OctoBus五个受控方法 → Semgrep候选 → 专项分析与知识规则 → 独立Evidence Gate → JSON/Markdown → 真实会话一致性验证。模块职责见[架构说明](docs/ARCHITECTURE.md)。

## 4. Supported vulnerabilities

支持SQL Injection、Command Injection、SSRF、Path Traversal的限定静态场景。未知语法、动态分派、未知保护保持NEEDS_REVIEW。TC-05和TC-10采用用户确认勘误，见docs/PHASE8-COMMAND-ERRATUM.md、PHASE8-PATH-ERRATUM.md。

## 5. LLM vs Deterministic Boundary

模型仅规划、调用和解释。VERIFIED必须满足Source、Dataflow、Sink、Protection、Reachability、Evidence Integrity六类证据。Gate独立重新读取和验证；Schema不能代替Gate。模型会话结果必须与实际工具及可信记录一致。

## 6. Installation

推荐Linux、Python 3.9+、Git；容器已在Python 3.11验证。Java Demo另需Java17和Maven；真实模型链路另需Docker、OctoBus、Agent Compose及模型凭据。

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m pytest -q
```

核心回归历史结果121项通过。本次交付整理未改核心分析代码，未重复运行该全套测试。服务器另有12项案例与真实调用证据。

## 7. Configuration

`.env.example`仅提供空模板。根目录agent-compose.yml为通用模板，不是服务器实际私有配置。真实凭据不进入Git。

- 应用agent/，规则rules/semgrep/，知识knowledge/java-spring/。
- 服务octobus/code-audit-service/，模型受限运行镜像deploy/guest/。
- 服务镜像deploy/local/Dockerfile；服务器恢复定义deploy/server/compose.yml。
- 当前服务器前提与运行信息见[服务器验收](docs/PHASE10-SERVER-ACCEPTANCE.md)。

## 8. Run

确定性12项验收无需模型，输出目录必须不存在：

```bash
PYTHONPATH=. python scripts/run_acceptance_matrix.py --output runs/acceptance-new
```

此命令生成固定提交、Semgrep扫描、Finding及matrix.json，不代替模型链路验收。单仓库审计：

```bash
python -m agent.cli audit --repository /approved/repo \
  --commit FULL_COMMIT_SHA --rules rules/semgrep --output runs/audit-new
```

替换为实际受控路径及完整Commit。真实服务器调用见[演示流程](docs/EXAMINER-DEMO.md)。

## 9. Demo

fixtures/spring-security-lab为隔离演示工程。独立Demo GitHub仓库待发布；评审包提供历史提交的Git bundle，支持离线克隆。

```bash
cd fixtures/spring-security-lab
mvn -B package
java -jar target/spring-security-lab-1.0.0.jar
```

仅在隔离环境运行。默认回环监听；服务器容器非root、无外部网络、根文件系统只读。已实际构建运行并验证三个HTTP检查，不代表每个静态样例均已运行时利用。

## 10. Finding Format

schemas/finding.schema.json规定VERIFIED、NEEDS_REVIEW、REJECTED三种状态，无主观可信度分数。评审包中的evidence/review/cases/保留完整Finding；evidence/review/report/包含由真实Finding生成的JSON/Markdown。

## 11. Knowledge Base

knowledge/java-spring/记录通用保护与误报规则。结果记录rules_applied、knowledge_version和decision_trace。TC-12对照验证知识开关产生的结果变化；field-notes不冒充个人客户经历。

## 12. Test Cases

tests/functional/为测试入口，12案例见docs/ACCEPTANCE-MATRIX.md。精选发布证据在evidence/review/；原始会话和私有配置由所有者保管。runs/不提交Git。

## 13. Security Design

限制仓库根目录和Commit；拒绝路径越界；固定扫描参数；不执行目标仓库脚本。Agent仅获得五个受控方法。模型密钥、Capset Token、服务器私钥、私有配置不得公开。GitHub和SSH权限分开管理，不向考官共享root私钥。

## 14. Troubleshooting

见[故障复盘](docs/TROUBLESHOOTING.md)。退出0不等于真实工具执行完成，扫描失败不得写“无漏洞”。必须核对实际调用、候选覆盖、可信结果一致性。

## 15. Known Limitations

- 非通用Java全程序分析器，复杂动态调用、未知过滤保持待复核。
- Path真实路径边界依赖可信目录及无并发文件系统篡改，不宣称消除TOCTOU。
- SSRF映射不替代DNS、重定向与出口网络检查。
- 工具限制不等于容器逃逸安全证明。
- BRD示例Instance为java-audit-instance，实际验收ID为code-audit-local；五方法功能已验证，名称差异需在评审中确认。

下一步：发布私有仓库、记录发布Commit，完成考官访问确认。
