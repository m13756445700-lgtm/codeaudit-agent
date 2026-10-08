# P2-C.1 考官访问与权限验收

版本：1.0｜日期：2026-10-08｜对象：8.130.121.3 / codeaudit-reviewer。

## 1. 结论与证据范围

**EXAMINER_SSH_LOGIN_VERIFIED=NOT_RUN**。用户本轮明确“没有考官的私钥”；没有生成密钥、没有把root密钥用于考官登录，没有修改账号、公钥、SSHD或sudoers。只使用已授权root身份只读调查，并以runuser模拟考官执行命令。模拟执行成功不代表SSH认证成功。

**EXAMINER_PERMISSION_BOUNDARY=CONDITIONAL**：已检查的组、sudo及文件/socket边界未发现非预期Docker/root权限；账号实际有普通bash shell与TTY，是否符合预期考官政策需确认，不能称为“仅能执行wrapper”。未发现root越权证据，但尚未完成所有输入/环境和普通文件读取面的全面安全测试。

证据：`evaluation/final-remediation/p2-server-preflight/p2c1/inventory.json`、`permission-checks.json`、`followup.json`。

## 2. 账号与认证检查

| 项目 | 已执行结果 | 解释 / 边界 |
|---|---|---|
| 账号 | uid/gid1000；仅自身组；home=/home/codeaudit-reviewer，shell=/bin/bash | 普通交互shell存在；没有docker/sudo组 |
| 密码状态 | passwd -S返回L | **密码锁定**，不能写“账号完全未锁定”；PAM/public-key实际可用性仍需真实登录 |
| 期限 | chage显示Account expires never；/etc/nologin不存在 | 不证明SSH认证成功 |
| SSH认证 | PubkeyAuthentication yes、PasswordAuthentication no、UsePAM yes | 仅配置层检查；未验证PAM完整认证链和密钥持有 |
| SSH配置范围 | sshd -T -C通过；当前运维来源IP上下文 | 考官实际来源IP未知，Match规则应按实际来源重核 |
| SSH文件权限 | home0750；.ssh0700；authorized_keys0600，owner1000 | 存在1条ED25519授权公钥；不输出公钥内容 |
| 公钥指纹 | `SHA256:w59gf6u379xQnpdNqYMxtb/MNs4+gvKeG02A1o1B0m4` | 密钥持有人本地匹配后方可登录测试 |
| 授权公钥限制 | no-agent-forwarding,no-port-forwarding,no-X11-forwarding | 该公钥禁止相应转发；未做主动转发测试 |
| 强制命令 / TTY | ForceCommand none、PermitTTY yes；key无command=限制 | 允许普通shell。全局AllowTcpForwarding yes不代表此受限key可以转发 |
| sudoers | 仅NOPASSWD /usr/local/bin/codeaudit-review | wrapper解释受控子命令；不等于全部子命令只读，audit/trigger会写数据和计费 |
| wrapper | root0755，SHA256=444cd41fb50941fefe0712017685d67026da05f50cb34fed8f0788a478a8f78a | 与已提交脚本一致 |

sshd -T是配置测试、不是握手证明；authorized_keys中的限制分别控制对应功能。依据：[OpenSSH sshd手册](https://man.openbsd.org/sshd)。当前账号密码锁定的语义不能替代实际public-key/PAM认证结果。

## 3. 已执行的权限与只读命令

| 检查 | 退出码 | 判定 |
|---|---:|---|
| reviewer读取.env | 1 | 预期拒绝 |
| reviewer读取.runtime.env | 1 | 预期拒绝 |
| reviewer写Docker socket | 1 | 预期拒绝 |
| reviewer写wrapper | 1 | 预期拒绝 |
| reviewer写/opt/codeaudit-v2/scripts | 1 | 预期拒绝 |
| sudo -n -l /bin/sh | 1 | 任意root shell不在允许列表；没有执行shell |
| status | 0 | 模拟考官执行成功，主项目4服务healthy |
| projects | 0 | codeaudit-final已登记 |
| triggers | 0 | daily-v2-audit enabled；仅查询 |
| methods | 0 | 一个聚合ExecuteTool入口可查询；未实际调用 |
| runs | 0 | 最近10条含两次历史failed，原样保留 |
| report f8ae525c268841399ad807d80ec41cc2 | 0 | 读取已有audit输出，未触发任务；17,653字节，只保存长度/哈希 |

报告选择依据现有run_summary文件；该32位audit ID **不是** scheduler短Run ID。后续由scheduler Run ID->sandbox->run_summary.audit_id定位报告，禁止把两种ID直接混用。报告stdout SHA256见followup.json，完整报告内容不写入新测试日志。

## 4. 无私钥情况下的人工登录验收步骤（尚未执行）

由考官或原密钥持有人在独立客户端进行，不向本聊天发送私钥/密码，不生成替代密钥。本地公钥指纹必须与上表一致；匹配不证明仍有私钥或网络可达。

```bash
ssh-keygen -lf /path/to/existing-reviewer-public-key.pub
ssh -i /path/to/existing-authorized-reviewer-private-key \
  -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes \
  -o BatchMode=yes -o ConnectTimeout=10 \
  codeaudit-reviewer@8.130.121.3 'id'
```

主机key须通过可信渠道核对或复用已确认的known_hosts，不使用StrictHostKeyChecking=no。记录客户端/来源IP、时间、用户名、key指纹、退出码，必要时由管理员只读核验对应SSH认证日志；不要记录密钥内容。

真实SSH成功后，逐项执行并记录结果：

```bash
sudo -n codeaudit-review status
sudo -n codeaudit-review projects
sudo -n codeaudit-review triggers
sudo -n codeaudit-review methods
sudo -n codeaudit-review runs
sudo -n codeaudit-review report f8ae525c268841399ad807d80ec41cc2
```

命令中的现有audit ID应在验证前确认仍存在。若需trace，只读取该已有ID，不触发新任务。报告内容可能含业务证据，记录留存在受限位置并脱敏；不要直接公开完整输出。

检查`id`、`sudo -n -l`及敏感文件/socket不可读写情况；不执行audit、trigger、run、restart或生产写入测试。若普通shell不符合政策，先提出经过评审的受限入口方案；本轮无账号修改授权，不能擅自加入ForceCommand。

## 5. 剩余阻断与下一步

实际SSH登录、考官来源IP下SSHD/PAM接受、普通shell政策确认均未完成。真实登录成功后仍需独立保留五个只读命令和指定历史报告读取结果，不能一项成功就标全通过。

建议由现有密钥持有人完成上面的人工验证并回传脱敏结果；如密钥已不可用，应单独评审认证变更，不能用root密钥冒充考官。权限变更、账号解锁或公钥替换均需另外授权。

P0_REAL_POST_REJECTION=INCONCLUSIVE；UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED。SERVER_DEPLOYMENT=NOT_STARTED。当前材料可供内部评审，未达到考官实际登录验收完成标准。
