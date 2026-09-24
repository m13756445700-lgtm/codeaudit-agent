# 当前提交与考官访问

2026-09-24更新：HR明确要求Public。此前私有仓库教程已撤换，以本页和README为准。

仓库：https://github.com/m13756445700-lgtm/codeaudit-agent 。Public状态必须以退出登录也能浏览为验收依据，不能仅看本人登录成功。

GitHub提供源码和去密证据，不承载服务器公钥认证。HR提供的SSH公钥应位于服务器评审账号的~/.ssh/authorized_keys，README必须给出地址、用户名、端口。私钥、模型Key、Capset Token及私有运行配置禁止入库。

提交前检查：公开可读；公钥已配置；README连接信息完整；项目/触发器/能力方法可查；一次真实自动运行有记录；服务自动恢复；原题核对表中未完成项明确。随后发送仓库地址、固定Commit和服务器登录信息给HR。无需索取考官GitHub账号才能读取Public仓库。

参见EXAM-COMPLIANCE.md和DEFENSE-30MIN.md。
