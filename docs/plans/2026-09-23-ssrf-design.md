# SSRF 首批实现与验收边界

依据：BRD 14.2、TC-07/08。保留原需求文件。

## 方案

采用已存在的AST分析、知识规则、独立Gate、受控服务结构。Semgrep只提供候选，不作裁决；不增加工具权限。

- TC-07：明确Spring请求参数，进入无自定义配置的默认RestTemplate完整URL，六类证据齐全后VERIFIED。
- TC-08：serviceId经不可变Map.of映射为固定http/https URL；用户不能拼接或替换scheme/host，REJECTED。
- 字符串前缀检查、未知过滤、动态构造或变更客户端、映射与用户字符串拼接均NEEDS_REVIEW。
- 扫描类别从源码AST识别；不能由模型指定类别或裁决绕过Gate。

固定映射结论只证明本条用户输入路径不能选择完整URL，不证明远端DNS、重定向或出口策略安全。V1.0不开展完整DNS重绑定试验。示例使用example.invalid域名，分析与验收不执行样例HTTP请求。

## 验收顺序

1. 原始URL正例、固定映射负例、前缀检查待复核。
2. 类型冒用、可变映射、未知保护、客户端泄漏/修改、类别及证据篡改测试。
3. 真实Semgrep与受控RunValidation、全量回归。
4. 新镜像真实MCP调用；保留SQL、Command回归。

不承诺本批覆盖WebClient、任意HTTP客户端、注入型可变RestTemplate、SSRF跨方法调用。未支持情况不提升为VERIFIED。
