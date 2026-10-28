# Multi-Agent System

基于 Python 和 FastAPI 开发的 Multi-Agent 系统，采用渐进式开发，逐步实现任务接收、任务分发、业务执行、结果查询和数据持久化。

目前已完成 **W04：多 Agent 任务路由与分发**，以及 W03 的 SQLite 持久化。系统支持将两种任务分发给独立 Agent，同步执行后保存结果，并在服务重启后按 UUID 查询。

当前 Agent 是规则驱动的执行组件，尚未接入大模型，也不具备自主推理能力。

## 1. 技术栈

- Python 3
- FastAPI：Web API 框架
- Uvicorn：ASGI 服务器
- Pydantic：请求模型与输入校验
- SQLite：任务持久化，使用 Python 标准库 `sqlite3`
- pytest：自动化测试
- HTTPX：支持 FastAPI 测试客户端

## 2. 项目结构

```text
multi-agent-system/
├── server_agent.py          # FastAPI 入口，启动时初始化数据库
├── task_agent.py            # 请求校验、任务创建、保存与查询接口
├── dispatcher.py            # 根据任务类型选择执行 Agent
├── database.py              # SQLite 初始化、写入、查询和数量统计
├── agents/
│   ├── __init__.py
│   ├── length_agent.py      # LengthAgent：字符统计
│   └── word_count_agent.py  # WordCountAgent：按空白分词统计
├── data/
│   └── tasks.db             # 首次启动时自动生成，不提交到 Git
├── script/
│   └── smoke_tasks.py       # 针对运行中服务的 HTTP 冒烟测试
├── test/
│   ├── conftest.py          # TestClient 与临时数据库隔离
│   ├── test_health.py       # 健康检查
│   ├── test_tasks.py        # 任务创建、查询、UUID 和容量限制
│   ├── test_invalid_task.py # 请求校验与文本边界
│   ├── test_multi_agent.py  # 两种任务的执行、保存和查询
│   ├── test_dispatcher.py   # Agent 路由与未知任务类型
│   └── test_persistence.py  # 初始化与跨进程持久化
├── run_server.sh            # Linux / Bash 启动脚本
├── requirements.txt
└── README.md
```

## 3. 任务架构与职责

创建任务的调用流程：

```text
POST /tasks
    ↓
task_agent.py：校验请求、检查容量、生成 UUID
    ↓
dispatcher.py：根据 task_type 选择 Agent
    ├── text_length → LengthAgent.execute(text)
    └── word_count  → WordCountAgent.execute(text)
    ↓
执行结果返回 task_agent.py
    ↓
database.py：写入 SQLite
    ↓
返回 201 与任务记录
```

查询任务时，`GET /tasks/{task_id}` 通过 `database.py` 读取已保存记录，无需重新执行 Agent。

| 模块 | 职责 |
|---|---|
| `server_agent.py` | 创建应用、注册路由、启动时初始化数据库 |
| `task_agent.py` | 定义请求模型，协调分发与存储，返回 HTTP 响应 |
| `dispatcher.py` | 按类型查找 Agent 并返回结果；未知类型抛出 `ValueError` |
| `agents/` | 执行各自的统计逻辑，不处理 HTTP 或数据库 |
| `database.py` | 管理 SQLite 初始化、保存、查询和数量统计 |

Dispatcher 使用 `AGENTS` 映射注册任务类型。以后增加任务时，可以新增 Agent、注册映射，并扩展 API 请求模型允许的任务类型。

## 4. 已实现功能

### W01：服务基础

- FastAPI 服务与 Uvicorn 启动
- `/health` 健康检查与 `/hello` 示例接口

### W02：任务执行与查询

- `POST /tasks` 提交任务，生成 UUID v4
- `GET /tasks/{task_id}` 查询结果
- Pydantic 请求校验与额外字段限制
- 任务总容量限制为 1000 条
- 保留 `201`、`404`、`422`、`503` 等接口行为

### W03：SQLite 持久化

- 服务启动时自动创建数据库目录和任务表
- 保存任务类型、状态、JSON 结果及 UTC 创建时间
- 根据 UUID 查询历史任务，统计已保存任务数量
- 重复初始化保留已有记录
- 服务重启后，使用同一数据库文件即可查询原有任务
- 通过 `TASK_DB_PATH` 环境变量覆盖数据库路径

### W04：多 Agent 分发

- API 统一调用 Dispatcher
- `LengthAgent` 执行 `text_length` 任务
- `WordCountAgent` 执行 `word_count` 任务
- 两种任务共用结果保存与查询流程
- 自动化测试覆盖路由选择、执行结果、空白处理和跨进程持久化

## 5. 安装与启动

克隆仓库并进入项目目录：

```bash
git clone https://github.com/cherry-lee520/multi-agent-system.git
cd multi-agent-system
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn server_agent:app --host 127.0.0.1 --port 8000
```

### Linux / Bash

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
bash run_server.sh
```

默认服务地址为 `http://127.0.0.1:8000`，交互式 API 文档地址为 `http://127.0.0.1:8000/docs`。

开发时可在 Uvicorn 启动命令末尾添加 `--reload`，保存代码后自动重载。

## 6. API 接口

| HTTP 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/health` | 检查服务状态 |
| GET | `/hello` | 返回示例问候信息 |
| POST | `/tasks` | 创建并同步执行任务 |
| GET | `/tasks/{task_id}` | 查询已保存的任务结果 |

### 6.1 字符统计

向 `POST /tasks` 提交：

```json
{
  "task_type": "text_length",
  "text": "hello world"
}
```

成功返回 `201 Created`：

```json
{
  "task_id": "<generated-uuid>",
  "task_type": "text_length",
  "status": "succeeded",
  "result": {
    "character_count": 11
  }
}
```

字符数使用 Python `len(text)` 计算，空格、制表符和换行均计入字符数。

### 6.2 单词统计

向同一个 `POST /tasks` 接口提交：

```json
{
  "task_type": "word_count",
  "text": "hello world"
}
```

成功返回 `201 Created`：

```json
{
  "task_id": "<generated-uuid>",
  "task_type": "word_count",
  "status": "succeeded",
  "result": {
    "word_count": 2
  }
}
```

单词数使用 `len(text.split())` 计算，按空白字符分词，不执行自然语言分词：

| 文本（JSON 字符串表示） | 单词数 |
|---|---|
| `"hello   world"` | 2 |
| `"hello\tworld\nPython"` | 3 |
| `"  hello world  "` | 2 |
| `"   "` | 0 |
| `"你好世界"` | 1 |

任务类型必须写成 `word_count`，包含下划线。

### 6.3 查询任务

将创建任务时返回的 UUID 填入 `GET /tasks/{task_id}`。成功返回 `200 OK`，响应内容与创建任务时的任务记录一致；不存在的任务返回 `404 Not Found`。

两种任务均支持在服务重启后查询，前提是继续使用原来的数据库文件。

`created_at` 仅保存在数据库中，不包含在当前 API 响应里。

### 6.4 输入校验与状态码

请求只允许 `task_type` 和 `text` 两个字段，且均为必填项。`task_type` 只支持 `text_length` 和 `word_count`；`text` 必须为长度 1～10000 的字符串。

| 状态码 | 场景 |
|---|---|
| `201 Created` | 任务执行并保存成功 |
| `200 OK` | 查询任务成功 |
| `404 Not Found` | 查询的任务不存在 |
| `422 Unprocessable Entity` | 未知任务类型、缺少字段、额外字段、文本类型或长度不符合要求 |
| `503 Service Unavailable` | SQLite 中已有至少 1000 条任务记录，拒绝创建新任务 |

空字符串 `""` 不符合长度限制；仅含空白的非空字符串可以提交，`word_count` 的结果为 0。容量限制对两种任务合计计数，达到上限后仍可查询已有记录。

## 7. 数据存储

默认数据库位于项目目录下的 `data/tasks.db`，首次启动自动生成。任务表 `tasks` 包含：

| 字段 | 含义 |
|---|---|
| `task_id` | UUID 字符串，主键 |
| `task_type` | 任务类型 |
| `status` | 当前同步执行成功后保存为 `succeeded` |
| `result_json` | JSON 编码的执行结果 |
| `created_at` | UTC 时间，ISO 8601 格式 |

可在启动服务前通过 `TASK_DB_PATH` 指定数据库路径，重启时需保持相同配置。例如在 PowerShell 中使用项目内的自定义路径：

```powershell
$env:TASK_DB_PATH = Join-Path (Get-Location) "data/custom_tasks.db"
.\.venv\Scripts\python.exe -m uvicorn server_agent:app --host 127.0.0.1 --port 8000
```

默认数据库文件及上述示例中的 `data/*.db` 已通过 `.gitignore` 排除；使用其他目录或文件名时，需自行确认忽略规则。

## 8. 自动化测试

### pytest 回归测试

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Linux / Bash：

```bash
.venv/bin/python -m pytest -q
```

若已激活虚拟环境，可直接使用 `python -m pytest -q`。将 `-q` 换成 `-v` 可查看每个测试用例。

测试覆盖：

- 两种任务的执行结果、SQLite 保存和 UUID 查询
- Dispatcher 调用正确的 Agent，且不调用其他 Agent
- Dispatcher 对未知类型抛出明确异常，API 对未知类型返回 `422`
- 连续空格、制表符、换行及仅含空白的单词统计
- 缺少字段、额外字段、文本类型和长度边界
- UUID 唯一性、任务不存在时的 `404`、容量边界与 `503`
- 数据库首次初始化和重复初始化
- 两种任务分别在一个独立进程中创建、退出后由另一个进程按 UUID 查询
- `/health` 健康检查

`test/conftest.py` 为每个测试设置临时 `TASK_DB_PATH`，隔离正常服务使用的数据库。

当前 W04 开发验收中，全部 pytest 回归测试已通过；具体测试数量与后续运行结果以最新 pytest 输出为准。

### HTTP 冒烟测试

`script/smoke_tasks.py` 使用 Python 标准库 `urllib.request` 请求实际运行的服务，默认地址为 `http://127.0.0.1:8000`。

先启动服务，再在另一个终端运行：

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe script/smoke_tasks.py
```

```bash
# Linux / Bash
.venv/bin/python script/smoke_tasks.py
```

该脚本检查健康接口、`text_length` 创建与查询、不存在的任务和非法任务类型。`word_count` 与跨进程持久化由 pytest 覆盖。

冒烟测试会向当前运行服务的数据库写入一条任务，运行时需有剩余任务容量。

## 9. 当前限制

- 任务同步执行，请求等待执行和保存完成后返回
- 当前使用单个 Uvicorn 进程启动，尚未验证多进程并发下的容量控制
- 保存成功任务的 `succeeded` 状态，尚未实现排队、执行中、失败等状态流转
- 总容量为 1000 条，尚无任务删除或归档接口
- 支持两种规则驱动的任务，尚未接入大模型
- 尚未实现 Agent 间任务传递、协作或结果汇总
- 尚未引入异步任务队列、Redis、Celery 或消息队列

## 10. 开发进度与后续计划

| 阶段 | 核心功能 | 状态 |
|---|---|---|
| W01 | FastAPI 服务与健康检查 | 已完成 |
| W02 | 单 Agent 任务执行与结果查询 | 已完成 |
| W03 | SQLite 任务持久化 | 已完成 |
| W04 | 多 Agent 任务路由与分发 | 实现与回归测试已完成 |
| W05 | 任务状态流转与异步执行 | 规划中 |
| W06 | 接入大模型 API，构建 LLM Agent | 规划中 |
| W07 | Agent 间任务传递与结果汇总 | 规划中 |

下一阶段 W05 将围绕任务状态流转与异步执行展开。长期目标是构建具有任务分发、Agent 协作、状态管理和结果汇总能力的 Multi-Agent 系统。
