# SSRF 首批验收记录

日期：2026-09-23。依据：BRD 14.2、TC-07/08；原需求文件未修改。

## 本批交付

- 新增RestTemplate候选扫描、独立AST分析及SSRF知识规则。
- 请求参数直接进入完整URL，且无已识别保护时，六类证据齐全后VERIFIED。
- serviceId只能选择不可变固定URL映射时REJECTED。
- 字符串前缀检查、未知过滤、可变映射、自定义或修改客户端、类型冒用等情况NEEDS_REVIEW。
- 沿用现有五个OctoBus受控方法，Gate重新读取固定提交并独立分析；不接受模型自定裁决。

## 已完成验证

| 验证 | 结果 | 本地证据 |
|---|---|---|
| 全量回归 | 95 passed in 28.29s | runs/phase8-ssrf/regression.txt |
| 真实扫描诊断 | 0 errors，3个SSRF候选 | runs/phase8-ssrf/scanner-diagnostic.json |
| SQL、Command及跨文件调用MCP回归 | 通过 | runs/phase8-ssrf/mcp-verification.log |
| SSRF真实MCP | 三样例裁决一致，五方法可用 | runs/phase8-ssrf/mcp-result.json |

当前镜像：codeaudit-octobus:phase8-ssrf。此前容器停止并保留，沿用受控Service/Instance/Capset，不增加权限。

## 失败记录

首次专项测试22项通过、扫描测试失败；两个扫描子进程退出码均为-9。同期进行了镜像构建，尚不能据此确定资源不足为根因。之后将构建与测试分开，真实扫描及全量回归通过，未降低失败判定标准。

## 范围与限制

本批支持明确导入的Spring注解、单方法直线数据流、未修改的默认RestTemplate，以及Map.of固定URL映射。注入型或自定义HTTP客户端、WebClient、跨方法SSRF等尚未支持，不会提升为VERIFIED。

固定映射结论仅证明该输入路径不能选择任意scheme/host；不证明外部DNS、重定向目标或网络出口策略安全。完整DNS重绑定测试不在本批范围。所有样例地址使用example.invalid；分析和验收没有执行样例中的外部HTTP请求。

Phase8整体仍未完成，下一批为Path Traversal。

## 真实模型验收：通过

Codex/DeepSeek Run `73f5d510128b93a2a9c5a2e144e115b4e42203100ff14a1a7e1e7105560b7567`，共17次真实受控调用，5个候选全部覆盖；最终JSON与本次服务端证据记录完全一致，2 VERIFIED、2 REJECTED、1 NEEDS_REVIEW。证据：`runs/phase8-ssrf/agent/summary.json`及同目录原始会话。
