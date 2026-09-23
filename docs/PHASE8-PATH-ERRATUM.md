# TC-10 路径边界验收勘误

日期：2026-09-23。用户已明确确认；原BRD保留。

## 裁决口径

- TC-09用户文件名直接拼接路径并读取：证据齐全后VERIFIED。
- 原TC-10目标仅normalize后startsWith(base)：缺少符号链接约束证明，NEEDS_REVIEW。
- 修正TC-10：base与target均toRealPath，目标不在base下立即抛出SecurityException，最终读取同一个target：REJECTED。

## 实施前提与限制

此处REJECTED针对用户文件名引起的路径越界，不表示整个文件系统安全。配置的基目录必须是可信的预期目录；攻击者不能在校验和读取之间修改目录、文件或符号链接。该并发竞态需要只读挂载、目录所有权等部署约束，本工具不宣称已经验证这些运行条件。

无法证明guard终止执行、检查与读取目标一致、类型唯一、真实路径解析及固定目录时，不作安全结论。单纯删除../、字符串startsWith、NOFOLLOW_LINKS及未知过滤器保留NEEDS_REVIEW。

## 语义验证

Java17容器探测：normalize_boundary_pass=true、realpath_boundary_pass=false、outside_marker_read=true。容器无网络、根只读，标记文件仅在临时目录。源码scripts/probes/PathBoundaryProbe.java，输出runs/phase8-path/java17-probe.txt。
