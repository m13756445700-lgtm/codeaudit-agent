# 部署与恢复

使用 Docker Engine/Desktop、Compose v2（支持 volume.subpath）、Python 3.9+ 和 Git。Ubuntu 需管理员为当前用户授予 Docker 权限；Docker socket 等同主机管理权限。建议 4 CPU / 8 GiB / 15 GiB 可用 Docker 空间。首轮访问 GHCR、Debian、PyPI、npm 及模型 HTTPS API；不开启目标代码执行。

```bash
cp .env.example .env
# 用编辑器设置实际模型配置。API endpoint 不含 /chat/completions。
chmod 600 .env
./scripts/start.sh
./scripts/healthcheck.sh
make docker-test
./scripts/demo.sh c
make ablation-test
```

启动脚本生成 0600 的 `.runtime.env`：强随机 token、Docker volume 的真实 mountpoint、沙箱所需 MCP/daemon URL。Linux 使用默认 Docker bridge gateway 的私有监听地址；Docker Desktop 使用 host.docker.internal 和宿主回环监听。无需填写个人路径或使用历史容器。当前方案针对标准 rootful Docker；rootless/远程 Docker context 未验证。

首次启动先构建单一镜像，再创建 workspace 子目录，启动 repo-tools/static-analysis、OctoBus、agent-compose daemon，最后注册服务和鉴权。已有 token 保留，不静默旋转。`.runtime.env` 与对应 volumes 一起保留；换主机需在新项目重新生成，不能复制旧机器的 mountpoint。勿公开 `docker compose config` 的完整输出，它可能含私密环境变量。

| 组件 | 网络/数据 | 资源上限 |
|---|---|---|
| agent-compose | Docker socket、专用 agent-data；私有 host 端口默认17420 | 1 CPU / 1 GiB |
| OctoBus | 私有 host 端口默认19013、独立状态卷 | 0.5 CPU / 512 MiB |
| repo-tools | internal能力网、只读快照卷、无宿主端口 | 0.5 CPU / 512 MiB |
| static-analysis | internal能力网、证据卷可写、无宿主端口 | 2 CPU / 2 GiB |
| codeaudit-agent | 按需容器作业、共享快照路径 | 1 CPU / 1 GiB |

agent-compose 另行创建审计沙箱；其生命周期由 daemon 管理，不能把 Docker Compose 作业的资源限制冒称沙箱限制。源码读取/模型上下文/工具调用有应用预算；本版本不面向不可信多租户。

可以设置 `.env` 的 COMPOSE_PROJECT_NAME、两个端口，在同一 Docker 主机隔离验收。所有本项目 volume/network 自动加项目名前缀。没有外部数据卷依赖；既有项目不受影响。

常规操作：

```bash
./scripts/healthcheck.sh
# 看具体服务日志；勿把含私有代码的日志公开
docker compose --env-file .env --env-file .runtime.env logs --tail 80 octobus
# 重启后重新检查并运行真实集成测试
docker compose --env-file .env --env-file .runtime.env restart octobus repo-tools static-analysis
./scripts/healthcheck.sh
make integration-test
# 停止沙箱和本项目服务，保留证据卷
./scripts/stop.sh
```

`start.sh` 可重复运行；注册时刷新 capability 配置。服务 unhealthy 则启动失败；healthcheck 还做真实 MCP initialize/tools/list，不能仅靠容器 running 判断业务正常。MCP 初始化失败时检查 OctoBus 注册和 npm 下载；模型错误检查 endpoint/key/model，不能改成 mock 通过。预算耗尽输出 INCOMPLETE，保留结果再调查。

升级前保留 Git commit、镜像标签和数据卷备份。不要使用 `down -v` 除非明确要删除所有本项目证据。私有 Git 凭据只通过操作员显式只读挂载与受控环境注入；SSH 必须保持 known_hosts 验证，不关闭主机身份校验。
