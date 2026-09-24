# 2026-09-24交付对齐证据

- access-and-runtime.json：公钥配置、受控查询、权限反向检查与恢复策略。
- scheduler-summary.json：真实cron运行ID、时间与状态。
- first-run-validation.json：首次自动运行最终结果一致，但严格会话校验失败，未删除失败记录。
- scheduler-validation.json：第二次自动运行严格会话校验PASS、8次MCP、VERIFIED/REJECTED。

仅公布核验摘要，不含原始会话、模型密钥、工具参数或完整响应。原始记录由所有者在服务器受限目录保管；摘要哈希不能替代原始记录独立复验。考官可通过README只读入口查询服务器当前状态；本人私钥登录与来源IP仍待确认。
