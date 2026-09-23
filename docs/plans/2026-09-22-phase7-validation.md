# Phase7验收实现约束

需求已明确，不扩大产品范围。沿用五个OctoBus受控方法，修复参数契约和专用授权。保留只读、关闭Shell/网页工具。

最终结果采用宿主侧确定性校验：读取真实Codex事件，匹配本次repository/commit与候选集合；逐候选确认ReadCodeSlice/HashEvidence/RunValidation，验证run_id属于本会话且最终finding等于服务端保存结果。禁止仅解析模型自述中的工具调用标记。最多两次实际运行，失败保留证据。

验收：真实8次MCP调用、两个候选正负裁决、完整JSON一致；模型改写/遗漏/重放/错误范围/缺失读取/工具错误等均被拒绝。权限边界按PHASE7-LOCAL-ACCEPTANCE.md披露。
