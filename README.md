# Multi-Agent System

基于 Python、FastAPI 和 Uvicorn 的多 Agent 协作系统（逐步开发中）。

## 当前阶段：W01 — 服务端健康检查

**目标：** 在 Ubuntu 服务器上构建可启动、可停止、可通过 SSH 隧道访问、可在新虚拟环境中复现的服务端骨架。

> 当前状态：以下验收项尚未提供实测结果；完成测试后勾选，不要将预期行为视为已验证结果。

### 技术栈

- Ubuntu（服务器）
- Python 3（以 `python3 --version` 实测为准）
- FastAPI（HTTP API）
- Uvicorn（ASGI 服务器）
- Python `venv`（依赖隔离）
- SSH 本地端口转发（Windows ↔ Ubuntu）

### 项目结构

```text
multi-agent-system/
├── server_agent.py       # FastAPI 应用及 /health 接口
├── run_server.sh         # 使用 .venv 启动服务
├── requirements.txt      # 当前 Python 环境导出的依赖版本
├── .gitignore            # 忽略本地环境和缓存
└── README.md             # 项目说明和验收记录
```

`.venv/` 和 `.venv-check/` 在本地生成，不应提交到 Git。

## 环境配置

以下命令在 **Ubuntu 服务器的项目目录** 执行：

```bash
cd ~/multi-agent-system
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

首次创建项目、尚无 `requirements.txt` 时：

```bash
.venv/bin/python -m pip install fastapi uvicorn
.venv/bin/python -m pip check
.venv/bin/python -m pip freeze > requirements.txt
```

> 若实际项目目录是 `~/app`，请将本说明中的 `~/multi-agent-system` 改为 `~/app`，无需为了文档移动现有项目。

## 启动服务

```bash
cd ~/multi-agent-system
bash run_server.sh
```

预期监听地址：`127.0.0.1:8000`。服务只监听服务器本机，不需要在云安全组开放 8000 端口。

在**另一 SSH 终端**测试：

```bash
curl --max-time 5 -i http://127.0.0.1:8000/health
ss -ltnp 'sport = :8000'
```

预期返回 HTTP `200`，正文类似：

```json
{"status":"ok","agent_id":"server-agent-01","version":"0.1.0"}
```

### Windows 本地访问（SSH 隧道）

在 Windows 终端执行以下单行命令；将连接目标替换为可正常登录的 SSH 目标，必要时保留原有 `-i` 私钥路径或 `-p` SSH 端口参数：

```powershell
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:18000:127.0.0.1:8000 root@<服务器公网IP>
```

隧道建立后，在 Windows **另一个终端**执行：

```powershell
curl.exe -i http://127.0.0.1:18000/health
```

或在浏览器打开 `http://127.0.0.1:18000/health`。

## 停止与环境复现

在运行服务的终端按 `Ctrl+C`。重新运行服务器本地 `curl`，预期连接失败（前提是没有其他服务占用 8000 端口）。

创建干净测试环境，并安装记录的依赖：

```bash
cd ~/multi-agent-system
python3 -m venv .venv-check
.venv-check/bin/python -m pip install -r requirements.txt
.venv-check/bin/python -m pip check
.venv-check/bin/python -m uvicorn server_agent:app --host 127.0.0.1 --port 8000
```

重新检查服务器的 `/health`，并通过 Windows SSH 隧道复测。验证结束后，按 `Ctrl+C` 停止测试服务；确认 `.venv-check` 不含需要保留的数据，再删除：

```bash
rm -r .venv-check
```

## W01 验收清单

- [ ] `python3 --version` 已记录：`待填写`
- [ ] `.venv` 建立完成，`pip check` 无冲突
- [ ] `/health` 返回 HTTP 200，包含 `status`、`agent_id`、`version`
- [ ] `ss` 确认仅监听 `127.0.0.1:8000`
- [ ] Windows 经 SSH 隧道收到相同 JSON
- [ ] `Ctrl+C` 停止后访问失败，重新启动后恢复
- [ ] `.venv-check` 依据 `requirements.txt` 成功安装并运行

**验收日期：** 待填写  
**测试环境：** Ubuntu 版本待填写；Python 版本待填写  
**遇到的问题及解决办法：** 待填写

## 已完成与下一步

- 已确认：Ubuntu 云服务器基础部署和 SSH 登录可用。
- W01 待核验：健康检查、隧道访问、停止/恢复及新环境复现。
- W02 候选：实现单 Agent 的固定任务提交与执行接口，增加请求校验、状态与错误处理。

## 注意事项

- 当前服务只是 HTTP 服务骨架，**不具备**模型推理、任务调度或多 Agent 协作能力。
- `requirements.txt` 固定的是导出的包版本，不等同于跨所有系统完全可复现的锁文件。
- 请勿向 Git 提交 `.venv/`、密钥、密码或其他敏感配置。
