# GitHub注册、上传与考官协作指南

版本1.0；核对日期2026-09-23。推荐GitHub Desktop图形界面路线，无需购买GitHub付费套餐；现有模型及云服务器费用另计。

## 一、先明确三个概念

- Git：本机版本记录，本次主工程交付目录已初始化，但尚无所有者首次提交。
- GitHub：在线代码仓库，必须由你注册并登录自己的账号。
- 云服务器：已部署运行环境，GitHub账号不自动获得SSH权限。

## 二、账号准备（由你本人完成）

1. 打开https://github.com/signup，使用你长期可接收邮件的邮箱注册、验证邮件。
2. 设置双重验证，并把恢复码放密码管理器等私有位置，不放项目目录。
3. 从https://desktop.github.com/安装GitHub Desktop，选择登录GitHub.com，在浏览器完成授权。
4. 在Desktop的Git设置中填写提交姓名和邮箱；可使用GitHub设置中提供的真实noreply邮箱，不要凭空编造邮箱。

密码、验证码、恢复码均由你自己输入，不需要发给助手。服务器SSH私钥也不用于GitHub登录。

## 三、主工程首次上传

1. 使用本次交付目录`delivery/codeaudit-agent`，不要选择整个Codex工作空间，也不要上传runs/或私有交接文件夹。
2. Desktop菜单File → Add Local Repository，选择上述目录。
3. 查看Changes：应只有源码、文档、空模板和精选证据。交付扫描报告见evidence/review/PUBLICATION-CHECK.json。
4. 输入提交说明`Prepare CodeAudit V1.0 evaluation delivery`，点击Commit to main。未设置Git身份时先完成上一节第4步。
5. 点击Publish repository，名称`codeaudit-agent`，保留 **Keep this code private**，Organization选择个人账号，点击Publish Repository。
6. 使用View on GitHub检查README、源码和evidence/review/；记录仓库URL和首次提交完整SHA。不能把“点击Publish”当作考官已获权。

## 四、Demo仓库上传

交付目录`delivery/java-spring-security-lab`已保留已验收历史Git提交。按同样方式Add Local Repository，先用你自己的身份提交新增README和.gitignore，再Publish repository，名称`java-spring-security-lab`，保留私有。历史Fixture提交是测试材料的真实来源，不改写成你的开发历史。历史验收仍绑定原Commit，文档提交不冒充当时执行版本。

若考官明确允许一个仓库，主工程已含fixtures/和离线bundle，可不发布第二个；仍须在交付消息里说明Demo位置与固定Commit。

## 五、邀请考官

1. 索取考官GitHub用户名；进入仓库Settings → Collaborators → Add people，选择对应账号并发送邀请。
2. 两个仓库分别邀请；请对方接受后确认网页可读、代码可克隆。
3. **个人私有仓库的Collaborator具有写入能力，不是只读评审权限。** 若考官要求严格只读，可使用组织仓库的Read角色；如不希望增加账号管理工作，可约定只通过Issue提出意见，发布验收Tag并保留备份，但约定不能替代权限隔离。
4. GitHub邀请不包含服务器权限。考官若只看源码和证据，无需提供SSH；如作业要求直接验机，按下一节处理。

## 六、SSH协作

请考官提供其电脑生成的SSH**公钥**，并约定评审时间。由所有者创建专用账号或受控验证入口；不共享root私钥，不默认加入docker组或授予全量sudo（这些权限可等价控制主机）。只读账号不能直接执行Docker验证，需使用审核过的固定验证入口或由所有者屏幕共享运行。具体方式在拿到公钥后配置和验证，当前尚未创建评审账号。

若必须完整交互式管理，优先使用独立评审环境及临时凭据，明确授权范围和到期回收。不要为了网页演示开放OctoBus到公网。

## 七、版本与意见管理

- 首次发布后以真实提交创建`v1.0.0-evaluation` Tag/Release，说明验收日期、通过项、边界及两项勘误。当前Tag尚未创建。
- 考官反馈使用Issue：现象、复现输入、Commit、预期/实际、去密日志。修复开分支和Pull Request，合并前跑相关测试；不要直接覆盖已验收版本。
- 截止评审前冻结版本；涉及云重启、升级或权限调整，先约定时间。
- 结束后按双方约定撤销协作者/SSH权限、停用临时凭据、保留报告与Tag；下载过的副本无法靠撤权删除。

## 八、可直接发送的交付消息（发布后补齐方括号）

老师您好，CodeAudit Agent V1.0已完成限定场景功能及服务器恢复验收，现提交评审：

- 主工程：[仓库URL]，版本：[Tag/Commit]
- Demo：[仓库URL或主工程路径]，固定Commit：[SHA]
- 阅读入口：README → docs/DELIVERY.md → evidence/review/
- 已验证：121项核心回归、服务器12/12案例、四类MCP调用、重启后真实模型调用。
- 范围说明：限定Java场景；TC-05和TC-10勘误及Instance命名映射已单独记录。
- 仓库访问：[邀请已发送/已接受，按实际填写]。如需直接验机，请提供SSH公钥及评审时间，我将配置专用访问方式。

烦请确认可访问，并通过Issue记录评审意见。谢谢。

## 官方参考

- [Desktop上传本地仓库](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-an-existing-project-to-github-using-github-desktop)
- [邀请协作者](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository)
- [个人仓库权限](https://docs.github.com/en/enterprise-cloud%40latest/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository)
- [Desktop登录](https://docs.github.com/en/desktop/installing-and-authenticating-to-github-desktop/authenticating-to-github-in-github-desktop)

下一步：你先完成账号注册与Desktop登录，再提供GitHub用户名；不用提供密码、Token或验证码。
