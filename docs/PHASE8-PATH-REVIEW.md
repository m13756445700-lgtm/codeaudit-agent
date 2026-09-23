# Path Traversal 实施进度与待确认事项

日期：2026-09-23。原BRD未修改。

## 已实施

- Files.readString候选扫描与源码AST类别识别。
- Spring请求参数→路径字符串拼接→Paths.get→Files.readString的独立证据分析。
- Gate按固定提交重新读取并重分析，六类证据及类别匹配后才能VERIFIED。
- 断链、未知过滤、删除../、重赋值、类型冒用、可变目录等情况不作VERIFIED。

## TC-10待确认的验收冲突

原BRD要求base.toRealPath、target.normalize、target.startsWith(base)即可REJECTED。Java 17隔离探测显示，该词法检查仍允许目录内符号链接指向目录外。

实测文件：`runs/phase8-path/java17-probe.txt`，源码：`scripts/probes/PathBoundaryProbe.java`。

```text
normalize_boundary_pass=true
realpath_boundary_pass=false
outside_marker_read=true
```

容器关闭网络、根文件系统只读，全部文件在临时目录，不访问真实业务文件。Java官方文档：https://docs.oracle.com/javase/tutorial/essential/io/pathOps.html 。

已提交用户确认的建议：保留原BRD，以勘误补充目标toRealPath之后做边界校验的负例；原normalize样例缺少符号链接约束证据时待复核。即便目标做了真实路径检查，文件系统在检查与读取之间不能由攻击者并发修改仍是部署前提。

**尚未收到勘误确认，安全负例未验收，当前UNKNOWN表示实现/证据不足，不表示已修改原验收要求。**

## 剩余事项

安全边界验收口径确认、对应负例实现与测试、新版OctoBus及模型联调、四类漏洞统一验收。当前运行中OctoBus仍是phase8-ssrf镜像，不能把新增本地代码当作已部署能力。

## 本轮测试

全量109 passed in 140.20s。日志：`runs/phase8-path/regression.txt`。新增14项路径测试覆盖危险正例、未实现的边界保护保留UNKNOWN、未知过滤、删除../、断链、类型冒用、证据篡改、知识禁用及真实Semgrep。测试通过不代表TC-10已满足。

## 后续确认与更新

用户已明确确认TC-10勘误，正式口径见PHASE8-PATH-ERRATUM.md。真实路径安全负例已实现，全量121项通过；四类漏洞真实MCP回归通过。上方“待确认”保留为历史记录，不代表最新状态。当前镜像已更新为phase8-path。
