# 方案一：CodeAudit Agent 完整 BRD + PRD V1.0

> 面试作业方向：安全技术 —— 代码安全审计  
> Agent 技术栈：Codex + agent-compose + OctoBus  
> 目标语言/框架：Java + Spring Boot + MyBatis  
> 服务器基线：4C / 8G / 40G  
> 文档用途：作为 Codex 的需求输入、实施蓝图、验收依据与面试演示基线  
> 版本：V1.0

---

## 0. 文档目标

本文档用于指导实现一个具备真实安全分析闭环的代码安全审计 Agent，而不是简单的“LLM + 代码扫描器”组合。

整个系统应完整覆盖：

1. 产品背景与业务价值；
2. 用户角色与典型场景；
3. Agent 业务流程与状态机；
4. LLM 与确定性程序的职责边界；
5. OctoBus 能力设计；
6. Evidence Gate 强校验机制；
7. 安全知识库 Schema；
8. Finding Schema；
9. 异常流程；
10. 测试与实验案例；
11. 需求验收矩阵；
12. 最终交付清单；
13. 面试演示路径。

本项目采用“方案先行、实施后置”的方式，先冻结产品目标、分析逻辑、能力边界、验收口径，再进入实际 Agent 编码和环境部署，避免出现无目标堆功能、仅做表层扫描、无法形成验证闭环的问题。

---

# 1. 产品定义

## 1.1 产品名称

**CodeAudit Agent**

副标题：

**基于 Source-to-Sink 证据链的 Java 代码安全审计智能体**

---

## 1.2 产品定位

CodeAudit Agent 面向 Java Spring Boot + MyBatis 项目，通过 LLM 推理、静态分析、代码取证、规则知识库与确定性验证程序协同工作，自动完成：

- 代码仓库资产识别；
- Web 输入入口识别；
- 危险函数候选发现；
- Source-to-Sink 数据流追踪；
- 安全措施判断；
- 误报排除；
- 证据完整性校验；
- 漏洞状态裁决；
- 审计报告生成。

本项目不追求一次性覆盖所有语言和全部漏洞类型，而是围绕有限技术栈建立可验证、可解释、可复现的最佳实践。

---

## 1.3 V1.0 支持范围

技术栈：

- Java 17+；
- Spring Boot；
- Spring MVC；
- MyBatis；
- Maven / Gradle 项目均可识别；
- Git 代码仓库；
- Codex 作为 Agent 的核心 LLM。

V1.0 首期支持 4 类风险：

1. SQL Injection；
2. Command Injection；
3. SSRF；
4. Path Traversal。

---

## 1.4 非目标

V1.0 不承诺：

- 支持所有 Java Web 框架；
- 支持所有数据库访问组件；
- 做全语言 SAST；
- 替代成熟商业 SAST 产品；
- 自动生成 CVSS 分数；
- 依赖 LLM 单独决定漏洞是否成立；
- 执行不受控的任意 Shell 命令；
- 自动利用生产系统漏洞。

---

# 2. BRD：业务背景

## 2.1 业务痛点

传统代码审计常见问题：

### 问题一：候选结果多，真实漏洞少

传统规则扫描器可以快速找到大量危险 API 或危险语法，但候选点通常不能直接代表真实漏洞。

例如：

```java
@Select("SELECT * FROM user WHERE id = #{id}")
User getUser(String id);
```

虽存在外部输入，但参数化查询本身不构成 SQL 注入。

---

### 问题二：缺少完整上下文

单点规则难以回答：

- 参数是否真的来自用户输入？
- 数据是否经过中间函数转换？
- 是否存在 Allowlist？
- 是否仅存在于测试代码？
- 是否真正到达危险函数？
- 是否存在不可达分支？

---

### 问题三：LLM 容易过度推断

如果直接把源码交给 LLM 并要求判断漏洞，会产生：

- 漏报；
- 误报；
- 幻觉；
- 行号引用错误；
- 缺少可复现证据；
- 对安全控制有效性判断不一致。

因此最终漏洞状态必须由确定性逻辑参与裁决。

---

## 2.2 产品价值

CodeAudit Agent 的核心价值不是“扫描更多”，而是将候选安全问题进一步转换为：

> **有代码来源、有完整数据流、有安全控制判断、有证据完整性校验、有明确状态的可验证安全结论。**

---

# 3. 用户与用户故事

## 3.1 目标用户

- 应用安全工程师；
- 代码审计工程师；
- 安全顾问；
- 研发安全负责人；
- DevSecOps 工程师；
- PoC/交付工程师。

---

## 3.2 核心用户故事

### US-01：代码仓库审计

作为安全工程师，我希望输入 Git 仓库和 Commit，Agent 自动完成安全分析，输出经过证据验证的漏洞结果。

### US-02：误报排除

作为代码审计人员，我希望 Agent 不只识别危险 API，还能分析安全控制逻辑，避免将安全代码误报为漏洞。

### US-03：证据复核

作为面试考官或安全审核人员，我希望每个 Finding 都能看到具体文件、行号、Source、Propagation、Sink、Protection 和 Commit 信息。

### US-04：结果复现

作为安全人员，我希望对同一 Commit 重复执行时，可以复现主要证据路径和最终状态。

### US-05：知识驱动判断

作为安全专家，我希望可以通过知识库持续沉淀特定框架、误报条件和安全判断规则，并让这些知识真正参与 Agent 运行态决策。

---

# 4. 核心产品原则

## 4.1 原则一：LLM 不拥有最终漏洞裁决权

LLM 可以：

- 理解需求；
- 制定分析计划；
- 解释代码；
- 判断需要继续查看哪些上下文；
- 对复杂业务逻辑提出安全判断建议。

但最终漏洞状态必须经过 Evidence Gate。

---

## 4.2 原则二：所有 VERIFIED Finding 必须存在证据链

每个 VERIFIED Finding 至少包含：

```text
Source
  ↓
Propagation
  ↓
Sink
  ↓
Protection Evaluation
  ↓
Reachability
  ↓
Evidence Integrity
```

---

## 4.3 原则三：代码引用必须绑定固定 Commit

所有审计证据必须绑定：

- Repository；
- Branch；
- Commit SHA；
- 文件路径；
- 行号；
- 文件 Hash；
- Rule Version；
- Knowledge Version；
- Agent Version。

---

## 4.4 原则四：知识必须参与判断

知识库不能只作为 Prompt 附件。

每个 Finding 必须记录：

```text
rules_applied
knowledge_version
decision_trace
```

以证明知识实际改变或参与了 Agent 的分析结果。

---

# 5. 系统总体架构

```text
┌──────────────────────────┐
│        用户 / 考官       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      CodeAudit Agent     │
│          Codex           │
│                          │
│ Planner                  │
│ Context Analyzer         │
│ Security Reasoner        │
│ Reporter                 │
└────────────┬─────────────┘
             │
             │ MCP / RPC
             ▼
┌──────────────────────────┐
│        OctoBus           │
│                          │
│ Capset: code-audit-agent │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   code-audit-service     │
│                          │
│ Repository Inventory     │
│ Semgrep Scan             │
│ Code Slice               │
│ Evidence Hash            │
│ Validation               │
└───────┬────────┬─────────┘
        │        │
        ▼        ▼
   Static Scan   Git Repo
        │
        ▼
   Evidence Gate
        │
        ▼
┌──────────────────────────┐
│    Finding JSON / MD     │
└──────────────────────────┘
```

---

# 6. LLM 与确定性程序职责边界

| 能力 | Codex/LLM | 确定性程序 |
|---|---:|---:|
| 理解用户审计目标 | ✅ | |
| 制定分析计划 | ✅ | |
| 判断下一步查看哪些文件 | ✅ | |
| 复杂业务语义理解 | ✅ | |
| 解释代码 | ✅ | |
| 输出最终自然语言报告 | ✅ | |
| Git 仓库枚举 | | ✅ |
| Commit 获取 | | ✅ |
| 文件 Hash | | ✅ |
| 静态规则扫描 | | ✅ |
| 候选 Sink 检测 | | ✅ |
| Schema 校验 | | ✅ |
| Evidence 存在性校验 | | ✅ |
| 最终状态规则执行 | | ✅ |
| Finding ID 生成 | | ✅ |
| 证据完整性校验 | | ✅ |

核心原则：

> **LLM 可以提出判断，但不能单独批准 VERIFIED。**

---

# 7. PRD：核心功能需求

## FR-01 Repository Preflight

### 输入

```yaml
repository: <repo path or git url>
branch: main
commit: optional
scope:
  - SQL_INJECTION
  - COMMAND_INJECTION
  - SSRF
  - PATH_TRAVERSAL
```

### 输出

```json
{
  "repository": "...",
  "branch": "main",
  "commit": "81a5...",
  "language": ["Java"],
  "framework": ["Spring Boot", "MyBatis"],
  "build_system": "Maven",
  "scan_started_at": "...",
  "agent_version": "1.0.0",
  "rule_version": "1.0.0",
  "knowledge_version": "1.0.0"
}
```

### 验收

必须能够：

- 正确读取 Commit；
- 识别 Java；
- 识别 Spring Boot；
- 识别 MyBatis；
- 输出结构化 Manifest。

---

## FR-02 Entry Point Discovery

识别常见用户输入源：

```java
@RequestParam
@PathVariable
@RequestBody
@RequestHeader
@CookieValue
HttpServletRequest.getParameter
MultipartFile
```

输出：

```json
{
  "source_type": "HTTP_REQUEST_PARAM",
  "file": "...",
  "line": 42,
  "symbol": "order",
  "method": "listUsers"
}
```

---

## FR-03 Candidate Scan

通过 Semgrep 或自定义静态规则识别危险候选点。

### SQL Injection Sink

重点：

```text
MyBatis ${}
Statement.execute
Statement.executeQuery
JdbcTemplate 拼接 SQL
```

### Command Injection Sink

重点：

```text
Runtime.exec
ProcessBuilder
/bin/sh -c
cmd.exe /c
```

### SSRF Sink

重点：

```text
RestTemplate
WebClient
HttpClient
URLConnection
OkHttp
```

### Path Traversal Sink

重点：

```text
File
FileInputStream
Files.read*
Paths.get
ResourceLoader
```

---

## FR-04 Dataflow Analysis

Agent 对候选点进行上下文分析。

必须追踪：

```text
Source
→ Controller
→ Service
→ DAO / Client / File API
→ Sink
```

允许第一版采用混合方式：

- 静态规则定位；
- LLM 阅读上下文；
- 程序化证据记录；
- 有限深度的跨函数追踪。

---

## FR-05 Protection Evaluation

识别安全控制：

- Parameterized Query；
- Allowlist；
- Enum Mapping；
- Canonical Path；
- Base Directory Check；
- Host Allowlist；
- Scheme Restriction；
- IP Range Restriction；
- Shell Avoidance；
- Fixed Command Mapping。

安全控制不能仅凭函数名判断，应结合数据是否真正经过该控制。

---

## FR-06 Reachability

至少区分：

```text
PRODUCTION_REACHABLE
TEST_ONLY
DEAD_CODE
UNKNOWN
```

生产代码中的真实调用链优先。

测试目录、example 目录、废弃代码不应直接输出 VERIFIED。

---

## FR-07 Evidence Integrity

每个 Finding 至少保存：

```text
repository
commit
file
line
snippet_hash
rule_id
knowledge_version
```

可选增强：

```text
file_sha256
evidence_sha256
```

---

## FR-08 Finding Verdict

最终状态仅允许：

```text
VERIFIED
NEEDS_REVIEW
REJECTED
```

禁止输出基于主观权重的 0-100 漏洞可信度。

---

## FR-09 Report Generation

输出两份结果：

### 机器结果

```text
findings.json
```

### 人类结果

```text
report.md
```

---

# 8. Agent 状态机

```text
INIT
 │
 ▼
PREFLIGHT
 │
 ├── fail → STOP_ERROR
 │
 ▼
DISCOVER_SOURCES
 │
 ▼
SCAN_CANDIDATES
 │
 ├── no candidate → REPORT_CLEAN
 │
 ▼
ANALYZE_CANDIDATE
 │
 ▼
TRACE_DATAFLOW
 │
 ├── insufficient evidence → NEEDS_REVIEW
 │
 ▼
EVALUATE_PROTECTION
 │
 ▼
CHECK_REACHABILITY
 │
 ▼
VALIDATE_EVIDENCE
 │
 ▼
EVIDENCE_GATE
 │
 ├── verified → VERIFIED
 │
 ├── uncertain → NEEDS_REVIEW
 │
 └── disproved → REJECTED
 │
 ▼
GENERATE_REPORT
 │
 ▼
DONE
```

---

# 9. Evidence Gate 设计

## 9.1 VERIFIED 条件

```text
source_verified = true
sink_verified = true
dataflow_verified = true
reachable = true
protection_status = ABSENT | INEFFECTIVE
evidence_integrity = PASS
```

则：

```text
VERIFIED
```

---

## 9.2 NEEDS_REVIEW 条件

例如：

```text
source_verified = true
sink_verified = true
dataflow_verified = partial
```

或：

```text
protection_status = UNKNOWN
```

则：

```text
NEEDS_REVIEW
```

---

## 9.3 REJECTED 条件

包括：

- Source 实际不可控；
- Sink 并非危险调用；
- 数据流未连接；
- 有效参数化；
- 有效 Allowlist；
- Path 经过 canonical 校验；
- SSRF Host 由有限映射决定；
- 仅 test/example 可达；
- 代码不可达。

---

## 9.4 伪代码

```python
def evidence_gate(finding):
    if not finding.source_verified:
        return "REJECTED"

    if not finding.sink_verified:
        return "REJECTED"

    if finding.reachability in ["TEST_ONLY", "DEAD_CODE"]:
        return "REJECTED"

    if not finding.dataflow_verified:
        return "NEEDS_REVIEW"

    if finding.protection_status == "VALID":
        return "REJECTED"

    if finding.protection_status == "UNKNOWN":
        return "NEEDS_REVIEW"

    if not finding.evidence_integrity_pass:
        return "NEEDS_REVIEW"

    return "VERIFIED"
```

---

# 10. OctoBus 能力定义

## 10.1 Service

```text
code-audit-service
```

## 10.2 Instance

```text
java-audit-instance
```

## 10.3 Capset

```text
code-audit-agent
```

## 10.4 Methods

### InventoryRepository

作用：

- 识别仓库；
- Commit；
- 语言；
- 框架；
- 构建工具。

### ScanCandidates

作用：

- 调用 Semgrep；
- 扫描危险语法；
- 返回候选点。

### ReadCodeSlice

作用：

- 根据文件和行号读取限定上下文；
- 避免 Agent 获得无边界文件操作能力。

### HashEvidence

作用：

- 计算证据 Hash；
- 绑定 Commit 与证据。

### RunValidation

作用：

- 校验 Finding Schema；
- 执行 Evidence Gate；
- 输出最终状态。

---

# 11. OctoBus 最小权限原则

Agent 不直接获得：

- 任意 Shell；
- 任意文件写权限；
- 任意 Docker 管理权限；
- 任意公网访问权限。

仅暴露完成代码审计必要的能力。

推荐：

```text
code-audit-agent capset
  ├── InventoryRepository
  ├── ScanCandidates
  ├── ReadCodeSlice
  ├── HashEvidence
  └── RunValidation
```

---

# 12. 安全知识库设计

目录：

```text
knowledge/
└── java-spring/
    ├── sources.yaml
    ├── sinks.yaml
    ├── sanitizers.yaml
    ├── false-positives.yaml
    ├── framework-notes.yaml
    └── field-notes.yaml
```

---

# 13. Knowledge Schema

示例：

```yaml
rule_id: KB-MYBATIS-SQL-001

category: SQL_INJECTION

framework:
  - Spring Boot
  - MyBatis

description: >
  用户可控数据进入 MyBatis ${} 原始文本替换时，
  若不存在有限集合映射或其他等价控制，则可能构成 SQL 注入。

sources:
  - RequestParam
  - PathVariable
  - RequestBody
  - HttpServletRequest.getParameter

sinks:
  - type: MYBATIS_RAW_SUBSTITUTION
    pattern: '${...}'

safe_patterns:
  - type: PARAMETER_BINDING
    pattern: '#{...}'

false_positive_conditions:
  - CONSTANT_VALUE
  - FINITE_ALLOWLIST_MAPPING
  - ENUM_MAPPING
  - TEST_ONLY
  - UNREACHABLE

required_evidence:
  - source
  - sink
  - dataflow
  - protection
  - reachability

decision:
  unsafe_if:
    - USER_CONTROLLED_SOURCE
    - RAW_SUBSTITUTION
    - NO_VALID_PROTECTION
```

---

# 14. 通用行业经验规则

> 注意：以下内容定义为“通用行业审计知识与最佳实践”，不宣称来自用户个人真实项目经历。后续如果有真实案例，可以追加到 field-notes。

## 14.1 SQL Injection

### 通用规则一

MyBatis `${}` 是文本替换，但并非出现 `${}` 就一定构成注入。

必须继续验证：

- 参数是否用户可控；
- 是否经过有限集合映射；
- 是否来自固定 Enum；
- 是否能够影响 SQL 结构；
- 是否生产路径可达。

---

## 14.2 SSRF

### 通用规则二

仅校验 URL 字符串前缀并不能天然视为有效 SSRF 防护。

需进一步判断：

- Scheme 是否受限；
- Host 是否受限；
- DNS 解析后 IP 是否可能落入私网；
- 是否可通过重定向绕过；
- 是否允许用户控制完整 URL。

V1.0 不要求完成全部 DNS 重绑定测试，但必须能够识别“字符串前缀校验”和“明确 Host Allowlist”的安全强度不同。

---

## 14.3 Path Traversal

### 通用规则三

仅删除 `"../"` 字符串不应被视为强安全控制。

更可靠的判断应包括：

```text
normalize/canonicalize
+
最终路径仍必须位于允许的 base directory
```

---

## 14.4 Command Injection

### 通用规则四

以下两种方式应区别判断：

危险：

```java
Runtime.getRuntime().exec("sh -c " + userInput);
```

更安全：

```java
new ProcessBuilder("/usr/bin/tool", fixedArg, mappedArg)
```

前提是：

- 不进入 shell；
- 参数经过有限映射；
- 用户无法控制可执行文件路径。

---

# 15. Finding Schema

建议保存为：

```text
schemas/finding.schema.json
```

核心结构：

```json
{
  "finding_id": "SQLI-001",
  "category": "SQL_INJECTION",
  "status": "VERIFIED",

  "repository": {
    "name": "demo-java-security",
    "commit": "81a5xxxx"
  },

  "source": {
    "type": "HTTP_REQUEST_PARAM",
    "file": "src/main/java/.../UserController.java",
    "line": 42,
    "symbol": "order"
  },

  "dataflow": [
    {
      "file": "src/main/java/.../UserController.java",
      "line": 42,
      "symbol": "order"
    },
    {
      "file": "src/main/java/.../UserService.java",
      "line": 61,
      "symbol": "order"
    },
    {
      "file": "src/main/resources/mapper/UserMapper.xml",
      "line": 18,
      "symbol": "order"
    }
  ],

  "sink": {
    "type": "MYBATIS_RAW_SUBSTITUTION",
    "file": "src/main/resources/mapper/UserMapper.xml",
    "line": 18
  },

  "protection": {
    "status": "ABSENT",
    "evidence": []
  },

  "reachability": "PRODUCTION_REACHABLE",

  "rules_applied": [
    "KB-MYBATIS-SQL-001"
  ],

  "decision_trace": [
    "HTTP input confirmed",
    "Data reaches MyBatis mapper",
    "Raw substitution detected",
    "No allowlist mapping found"
  ],

  "evidence_integrity": {
    "commit": "81a5xxxx",
    "file_sha256": "...",
    "status": "PASS"
  },

  "recommendation": "Use parameterized query or finite allowlist mapping."
}
```

---

# 16. 12 个核心实验案例

| ID | 类别 | 场景 | 关键证据 | 预期 |
|---|---|---|---|---|
| TC-01 | SQLi | Request 参数进入 MyBatis `${}` | Controller→Service→Mapper→`${}` | VERIFIED |
| TC-02 | SQLi | Request 参数进入 `#{}` | Parameter Binding | REJECTED |
| TC-03 | SQLi | `${order}` 前存在有限 Allowlist | Enum/Mapping | REJECTED |
| TC-04 | SQLi | `${order}` 无任何约束 | 完整 Source→Sink | VERIFIED |
| TC-05 | CMD | 用户参数进入 `sh -c` | Input→Command String→Shell | VERIFIED |
| TC-06 | CMD | 固定命令 + 有限参数映射 | No Shell + Allowlist | REJECTED |
| TC-07 | SSRF | 用户控制完整 URL | Request→HTTP Client | VERIFIED |
| TC-08 | SSRF | Scheme/Host 均为有限 Allowlist | Effective Protection | REJECTED |
| TC-09 | Path | 文件名直接拼接目录 | Input→Path→File Read | VERIFIED |
| TC-10 | Path | normalize + baseDir 校验 | Canonical Boundary | REJECTED |
| TC-11 | Reachability | 漏洞仅存在 test/example | Test Only | REJECTED |
| TC-12 | Knowledge | 开关知识规则前后结果变化 | Knowledge Trace | PASS |

---

# 17. 测试用例详细定义

## TC-01 SQL Injection：MyBatis Raw Substitution

### 输入

```java
@GetMapping("/users")
public List<User> list(@RequestParam String order) {
    return service.list(order);
}
```

```xml
<select id="list">
  SELECT * FROM users ORDER BY ${order}
</select>
```

### 预期

```text
Source = order
Sink = ${order}
Protection = ABSENT
Reachability = PRODUCTION_REACHABLE
Status = VERIFIED
```

---

## TC-02 SQL Injection：安全参数绑定

```xml
SELECT * FROM users WHERE username = #{username}
```

预期：

```text
Status = REJECTED
Reason = Parameterized binding
```

---

## TC-03 SQL Injection：有限 Allowlist

```java
String field;

switch(order) {
    case "name":
        field = "username";
        break;
    case "time":
        field = "create_time";
        break;
    default:
        field = "id";
}
```

```xml
ORDER BY ${field}
```

预期：

```text
Status = REJECTED
Reason = User input cannot directly reach SQL structure;
         only finite static identifiers reach sink.
```

---

## TC-04 SQL Injection：无约束排序字段

```java
return mapper.list(order);
```

```xml
ORDER BY ${order}
```

预期：

```text
Status = VERIFIED
```

---

## TC-05 Command Injection

```java
String cmd = "sh -c ping " + host;
Runtime.getRuntime().exec(cmd);
```

预期：

```text
Status = VERIFIED
```

---

## TC-06 Command：安全参数映射

```java
String mapped = HOST_MAP.get(input);
new ProcessBuilder("/usr/bin/ping", "-c", "1", mapped).start();
```

前提：

```text
HOST_MAP 为固定映射
无法控制 executable
不经过 shell
```

预期：

```text
Status = REJECTED
```

---

## TC-07 SSRF

```java
@GetMapping("/fetch")
public String fetch(@RequestParam String url) {
    return restTemplate.getForObject(url, String.class);
}
```

预期：

```text
Status = VERIFIED
```

---

## TC-08 SSRF：Host Allowlist

```text
用户仅提交 serviceId
serviceId → 固定 URL 映射
```

预期：

```text
Status = REJECTED
```

---

## TC-09 Path Traversal

```java
String path = BASE_DIR + "/" + filename;
return Files.readString(Paths.get(path));
```

预期：

```text
Status = VERIFIED
```

---

## TC-10 Path Traversal：Canonical Boundary

```java
Path base = Paths.get(BASE).toRealPath();
Path target = base.resolve(filename).normalize();

if (!target.startsWith(base)) {
    throw new SecurityException();
}
```

预期：

```text
Status = REJECTED
```

---

## TC-11 Test-only

代码位于：

```text
src/test/java/
examples/
demo/
```

且无法从生产 Controller 调用。

预期：

```text
Reachability = TEST_ONLY
Status = REJECTED
```

---

## TC-12 Knowledge Runtime Proof

第一次：

```text
禁用 KB-MYBATIS-SQL-FP-ALLOWLIST
```

第二次：

```text
启用 KB-MYBATIS-SQL-FP-ALLOWLIST
```

预期：

```text
TC-03 的状态/决策 Trace 发生预期变化。
```

用于证明知识库实际参与 Agent 运行时分析，而不是静态文档。

---

# 18. 工程验收案例

| ID | 验证项 | 操作 | 通过标准 |
|---|---|---|---|
| ENV-01 | 自动恢复 | 重启服务器 | agent-compose 与 OctoBus 自动恢复 |
| ENV-02 | Agent 可运行 | 重启后运行一次 | 完整审计成功 |
| ENV-03 | OctoBus 调用 | 执行 ScanCandidates | Access Log 有记录 |
| ENV-04 | Secret 安全 | 扫描 Git 仓库 | 无 API Key/Token/密码 |
| ENV-05 | Replay | 同 Commit 重跑 | 关键 Finding 可复现 |

---

# 19. 异常流程

## EX-01 无法识别项目类型

处理：

```text
状态：STOPPED
原因：UNSUPPORTED_PROJECT
```

不得假装继续分析。

---

## EX-02 Semgrep 执行失败

处理：

- 重试一次；
- 保存 stderr；
- 标记工具失败；
- 不允许将未扫描状态描述为“无漏洞”。

---

## EX-03 文件不存在

处理：

```text
Evidence Integrity = FAIL
Finding Status = NEEDS_REVIEW
```

---

## EX-04 行号漂移

如果文件 Hash 与分析时不同：

```text
STALE_EVIDENCE
```

不得继续输出 VERIFIED。

---

## EX-05 数据流不完整

处理：

```text
NEEDS_REVIEW
```

不得让 LLM 猜测中间调用链。

---

## EX-06 安全控制无法明确判断

例如复杂自研过滤函数。

处理：

```text
Protection Status = UNKNOWN
Finding Status = NEEDS_REVIEW
```

---

## EX-07 LLM 输出不符合 Schema

处理：

- 自动重试结构化输出；
- 最多重试 N 次；
- 最终仍失败则标记执行失败；
- 不生成伪造 Finding。

---

# 20. 非功能需求

## NFR-01 稳定性

4C / 8G / 40G 环境下能够稳定执行 Demo 项目。

---

## NFR-02 可维护性

代码模块至少拆分：

```text
planner
scanner
evidence
knowledge
validator
reporter
```

---

## NFR-03 可审计性

Agent 每个重要阶段生成日志。

最低包括：

```text
run_id
timestamp
method
candidate_id
rule_id
finding_id
status
```

---

## NFR-04 安全性

禁止：

- Git 提交真实 LLM Key；
- 硬编码 SSH 密码；
- 暴露 OctoBus 管理接口到公网；
- Agent 获取无边界 root Shell。

---

## NFR-05 可复现

相同：

```text
Commit
Rule Version
Knowledge Version
Agent Version
```

应能够复现主要 Finding。

---

# 21. 部署基线

服务器：

```text
4 vCPU
8 GB RAM
40 GB Disk
Ubuntu 22.04 / 24.04
```

建议部署：

```text
Docker
agent-compose
OctoBus
code-audit-service
Semgrep
Codex credentials via environment/secret
```

---

# 22. 安全网络要求

推荐：

```text
Internet
   │
   │ SSH
   ▼
Ubuntu Server
   │
   ├── agent-compose daemon
   ├── OctoBus
   ├── CodeAudit Agent
   └── code-audit-service
```

外部开放：

```text
22/tcp
```

并建议限制源 IP。

不直接公网开放：

```text
OctoBus
agent-compose control API
internal service
```

---

# 23. Repository 目录标准

```text
codeaudit-agent/
│
├── README.md
├── agent-compose.yml
├── .env.example
├── .gitignore
│
├── agent/
│   ├── prompts/
│   ├── planner/
│   ├── workflow/
│   ├── evidence/
│   └── reporter/
│
├── octobus/
│   └── code-audit-service/
│       ├── proto/
│       ├── src/
│       └── config/
│
├── knowledge/
│   └── java-spring/
│       ├── sources.yaml
│       ├── sinks.yaml
│       ├── sanitizers.yaml
│       ├── false-positives.yaml
│       ├── framework-notes.yaml
│       └── field-notes.yaml
│
├── rules/
│   └── semgrep/
│
├── schemas/
│   └── finding.schema.json
│
├── fixtures/
│   └── spring-security-lab/
│
├── tests/
│   ├── functional/
│   ├── false-positive/
│   ├── knowledge/
│   └── recovery/
│
├── scripts/
│   ├── install.sh
│   ├── smoke-test.sh
│   └── acceptance-test.sh
│
└── docs/
    ├── BRD-PRD.md
    ├── ARCHITECTURE.md
    ├── ACCEPTANCE-MATRIX.md
    ├── TEST-CASES.md
    └── TROUBLESHOOTING.md
```

---

# 24. 需求验收矩阵

| Req ID | 作业要求 | 实现 | 验收证据 |
|---|---|---|---|
| R01 | GitHub 仓库 | 独立 Repo | GitHub URL |
| R02 | Agent 源码 | agent/ | Code Review |
| R03 | 部署配置 | agent-compose.yml | Repo |
| R04 | README | 安装/运行/架构 | README.md |
| R05 | 无明文密钥 | Secret/Env | Secret Scan |
| R06 | 公有云服务器 | 4C8G40G Ubuntu | SSH |
| R07 | Docker | Docker Engine | docker info |
| R08 | agent-compose | daemon 正常 | status |
| R09 | Project | agent-compose 项目 | project status |
| R10 | Agent 可执行 | run command | run log |
| R11 | 日志 | 完整运行日志 | logs |
| R12 | OctoBus | daemon 正常 | status |
| R13 | Service | code-audit-service | service list |
| R14 | Instance | java-audit-instance | instance list |
| R15 | Capset | code-audit-agent | capset config |
| R16 | 实际能力调用 | ScanCandidates | access log |
| R17 | OctoBus 不公网暴露 | 内网监听/ACL | netstat/ss |
| R18 | 重启恢复 | restart policy | reboot test |
| R19 | 业务闭环 | Repo→Finding | Demo |
| R20 | LLM 边界 | Planner≠Final Judge | Code/Architecture |
| R21 | 强决策 | Evidence Gate | Unit Test |
| R22 | 知识参与 | rules_applied | Finding JSON |
| R23 | 非显然知识 | FP/Protection Rules | knowledge/ |
| R24 | 通用失败模式 | field-notes | Docs |
| R25 | 工程问题复盘 | Troubleshooting | Interview |
| R26 | 证据链 | File/Line/Flow/Hash | Finding |
| R27 | 可复现 | 固定 Commit | Replay |

---

# 25. 最终交付物

必须完成：

```text
1. GitHub Repository
2. README.md
3. BRD/PRD
4. Architecture
5. agent-compose.yml
6. OctoBus Service
7. Capset
8. Semgrep Rules
9. Knowledge Base
10. Finding Schema
11. Demo Repository
12. 12 个测试案例
13. Acceptance Matrix
14. Troubleshooting
15. 服务器 SSH 信息
```

---

# 26. README 必须包含的章节

```text
1. Project Overview
2. Why this project
3. Architecture
4. Supported vulnerabilities
5. LLM vs Deterministic Boundary
6. Installation
7. Configuration
8. Run
9. Demo
10. Finding Format
11. Knowledge Base
12. Test Cases
13. Security Design
14. Troubleshooting
15. Known Limitations
```

---

# 27. 面试演示脚本

建议现场控制在 8～12 分钟。

## Step 1：展示架构

说明：

```text
Codex 负责分析规划
OctoBus 负责受控能力暴露
Semgrep 负责候选扫描
Evidence Gate 负责最终确定性裁决
```

---

## Step 2：展示 Agent 环境

```bash
agent-compose ps
```

确认 Project 正常。

---

## Step 3：展示 OctoBus

展示：

```text
service
instance
capset
```

---

## Step 4：运行一次审计

目标项目：

```text
spring-security-lab
```

运行：

```text
audit repository
```

---

## Step 5：演示真实漏洞

推荐：

```text
TC-01
```

展示：

```text
Source
Propagation
Sink
Rules Applied
Status = VERIFIED
```

---

## Step 6：演示误报排除

推荐：

```text
TC-03
```

强调：

```text
同样存在 ${}
但因为前面存在有限 Allowlist
最终 REJECTED
```

这个 Demo 比单纯展示漏洞更能证明 Agent 的安全专业能力。

---

## Step 7：证明知识参与

展示：

```text
rules_applied
decision_trace
```

必要时演示 TC-12。

---

## Step 8：证明 OctoBus 被真正调用

展示 access log。

---

## Step 9：证明可复现

展示：

```text
Commit SHA
Finding JSON
Evidence Hash
```

---

# 28. Codex 开发执行顺序

Codex 实施时禁止直接“一次性完成全部功能”。

按以下顺序开发。

## Phase 1：Skeleton

完成：

```text
repo structure
finding schema
basic CLI
configuration
logging
```

验收后再继续。

---

## Phase 2：Static Scan

完成：

```text
Semgrep
candidate output
SQL Injection TC-01/02
```

---

## Phase 3：Evidence Pipeline

完成：

```text
source
sink
dataflow
protection
reachability
```

---

## Phase 4：Evidence Gate

实现：

```text
VERIFIED
NEEDS_REVIEW
REJECTED
```

---

## Phase 5：Knowledge

实现：

```text
knowledge loader
rules_applied
decision_trace
```

---

## Phase 6：OctoBus

将：

```text
InventoryRepository
ScanCandidates
ReadCodeSlice
HashEvidence
RunValidation
```

封装进入 OctoBus。

---

## Phase 7：Agent Compose

完成 Codex Agent 与 OctoBus 能力联动。

---

## Phase 8：全部漏洞类型

依次：

```text
SQL Injection
Command Injection
SSRF
Path Traversal
```

---

## Phase 9：Tests

完成 12 个 Case。

---

## Phase 10：Deployment

部署至：

```text
4C / 8G / 40G
```

完成重启恢复和 SSH 验收。

---

# 29. Codex 开发约束

Codex 必须遵守：

1. 不允许伪造测试通过结果；
2. 不允许跳过失败测试；
3. 不允许硬编码 Secret；
4. 不允许让 LLM 文本直接覆盖最终 Finding 状态；
5. 所有 VERIFIED 必须通过 Evidence Gate；
6. 所有 Finding 必须符合 JSON Schema；
7. 关键模块必须有单元测试；
8. 每个阶段完成后先运行测试；
9. 不做与 V1.0 无关的过度架构；
10. 优先实现可演示、可复现、可验证闭环。

---

# 30. V1.0 Definition of Done

只有全部满足以下条件，才视为项目完成：

```text
[ ] Java Spring Boot + MyBatis Demo Repo 可运行
[ ] Codex Agent 可以启动
[ ] agent-compose 正常
[ ] OctoBus 正常
[ ] code-audit-service 注册成功
[ ] Capset 注册成功
[ ] Agent 确实调用 OctoBus
[ ] Semgrep 可以返回候选点
[ ] Evidence Pipeline 工作正常
[ ] Evidence Gate 工作正常
[ ] SQLi 4 个案例通过
[ ] Command 2 个案例通过
[ ] SSRF 2 个案例通过
[ ] Path Traversal 2 个案例通过
[ ] Reachability 案例通过
[ ] Knowledge Runtime 案例通过
[ ] Finding Schema 校验通过
[ ] Report Markdown 可生成
[ ] 无明文 Secret
[ ] Server reboot 后服务可恢复
[ ] README 完整
[ ] Acceptance Matrix 完整
```

---

# 31. 成功标准

项目成功不以“扫描出多少漏洞”为核心。

最终成功标准是：

> **在限定 Java Spring Boot + MyBatis 场景下，Agent 能够基于真实代码证据，区分“危险候选”“真实漏洞”和“误报”，并通过 OctoBus 受控调用、安全知识、Evidence Gate 和可复现证据链完成完整审计闭环。**

---

# 32. 下一阶段建议

完成本文档确认后，进入工程设计 V1.1，依次产出：

1. `ARCHITECTURE.md`
2. `finding.schema.json`
3. Knowledge YAML 完整模板
4. Semgrep Rules V1
5. Demo Spring Boot 项目代码设计
6. OctoBus RPC/Method 定义
7. Agent Prompt / System Prompt
8. Codex 实施任务拆解
9. Acceptance Test Script
10. 面试答辩 FAQ

其中优先级最高的是：

```text
Finding Schema
→ Knowledge Schema
→ Test Fixtures
→ Evidence Gate
→ OctoBus Method
→ Agent Prompt
```

不要反过来先写 Prompt。

---

# 33. 给 Codex 的总任务指令

可以直接将以下内容与本文档一起提供给 Codex：

> 你需要实现 CodeAudit Agent V1.0。严格以本 BRD+PRD 为最高需求基线。不得自行扩大产品范围，不得以 LLM 文本判断替代 Evidence Gate，不得伪造工具执行结果。优先保证 SQL Injection 端到端闭环，再逐步支持 Command Injection、SSRF 和 Path Traversal。每个 VERIFIED Finding 必须存在 Source、Dataflow、Sink、Protection、Reachability 和 Evidence Integrity 六类证据。所有中间能力通过清晰模块封装，并最终将必要的受控能力暴露为 OctoBus Service/Instance/Capset。每完成一个 Phase，先运行测试并报告通过/失败情况，再进入下一阶段。
