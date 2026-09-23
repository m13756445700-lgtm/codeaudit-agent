# Phase 8 Command Injection 验收勘误与实现范围

日期：2026-09-23。原 BRD 保留不改。本补充已获得用户明确同意。

## 验收勘误

TC-05 的 `Runtime.exec("sh -c ping " + host)` 使用单字符串重载。Java 17 按空白拆分参数；shell 的命令文本是 `ping`，后续输入并不自动拼入该命令文本。因此，仅凭该样例不能判为已验证的命令注入。

- 原样例：NEEDS_REVIEW，等待可利用性证据，不据此宣称安全。
- 修正正例：`Runtime.getRuntime().exec(new String[]{"/bin/sh", "-c", cmd})`，其中 cmd 明确来自请求参数拼接。
- 安全负例：固定 `/usr/bin/ping`、固定参数、来自不可变 `Map.of` 的有限映射，不进入 shell，REJECTED。

语义依据：https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Runtime.html

隔离探测源码：`scripts/probes/CommandArgvProbe.java`。Java 17 镜像摘要：`sha256:51d32af96fb8a13ffbc96c719d7b05447a04ca69f314627d64050a64ecd13057`。容器无网络、根文件系统只读，标记文件仅写入临时 /tmp；仅执行 printf。实测输出：

```text
single_string_argv=[sh, -c, printf, ;printf, PROBE>/tmp/codeaudit-probe-marker]
single_string_marker=false
explicit_argv_marker=true
```

这验证了参数传递差异，不等于对所有 Runtime.exec 调用做安全结论。

## 本批实现边界

- Semgrep 发现 Runtime.exec 与 ProcessBuilder 候选。
- 独立 AST 分析支持明确导入 Spring 注解的单个 Controller、单请求参数、同方法直线局部赋值、显式 shell argv。
- 固定不可变映射及固定 ping argv 单独证明为有效保护。
- 分支、重赋值、未知过滤、未知映射、动态可执行文件、其他注解和未支持调用链均不作 VERIFIED。
- Gate 从固定提交重新读取并重新分析六类证据；类别也参与摘要和独立匹配。
- CLI 与 RunValidation 共用入口，保留原有五个受控方法。

## 未完成事项

本批不代表 Phase 8 整体通过。跨方法 Command 追踪、更多安全映射形式、SSRF 和 Path Traversal 尚待完成。当前本地 OctoBus 已更新为 phase8 镜像；SQL 的12项 MCP 回归通过，Command 的3个候选通过真实 MCP 读取、摘要与验证。Codex 验收结果另行记录。

## 本地测试结果

最终全量回归：58 passed in 15.63s。新增21项Command测试，覆盖正例、负例、原样例、未知过滤、断链、重赋值、类别与证据篡改、知识禁用、嵌套类型遮蔽及测试路径。首次扫描失败，后续直接扫描和两轮回归通过，根因未确认。

结果文件：`runs/phase8-command/regression.txt`、`java17-probe.txt`、`mcp-result.json`。

## 实际模型会话：未通过

Run `bac57466885fcfe699de9ef5cd53e797b947e4305e2381f26b50bd4a9b269963` 有越界读取工具失败，严格会话验证拒绝通过。虽随后执行了5个候选的RunValidation并返回JSON，仍不计端到端验收成功。已补充下次单行读取要求，未重跑。原始记录位于 `runs/phase8-command/agent/`。
