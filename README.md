# Multi-Agent System

基于 Python 和 FastAPI 开发的 Multi-Agent 协作系统。

项目采用渐进式开发，逐步实现任务接收、任务执行、状态查询、数据持久化以及后续的多 Agent 协作。

目前完成 **W02：单 Agent 固定任务执行与查询**。

## 1. 技术栈

- Python 3
- FastAPI：Web API 框架
- Uvicorn：ASGI 服务器
- Pydantic：数据模型与输入校验
- pytest：自动化测试
- HTTPX：HTTP 测试客户端

## 2. 项目结构

```text
multi-agent-system/
├── server_agent.py       # FastAPI 应用入口
├── task_agent.py         # 任务路由、记录存储与查询
├── task_executor.py      # 文本统计执行器
├── run_server.sh         # 服务启动脚本
├── requirements.txt      # Python 依赖
├── README.md             # 项目说明
└── tests/
    ├── conftest.py       # 测试数据清理
    └── test_tasks.py     # API 自动化测试
```

如使用独立的 `task_models.py`，则该文件负责定义和校验请求模型。

## 3. 已实现功能

### W01：服务端基础功能

- FastAPI 服务部署
- Uvicorn 启动
- `/health` 健康检查
- SSH 隧道访问
- GitHub 仓库管理

### W02：固定任务执行

- POST 提交任务
- Pydantic 请求数据校验
- UUID 生成唯一任务 ID
- `text_length` 文本字符统计
- Python 字典存储任务结果
- GET 根据任务 ID 查询记录
- 1000 条任务容量限制
- HTTP 状态码与异常处理
- pytest 自动化测试

## 4. 安装与启动

克隆仓库后进入项目目录：

```bash
git clone <repository-url>
cd multi-agent-system
```

创建 Python 虚拟环境：

```bash
python3 -m venv .venv
```

安装依赖：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

启动服务器：

```bash
bash run_server.sh
```

服务器默认监听：

```text
127.0.0.1:8000
```

## 5. API 接口

| HTTP 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/health` | 检查服务状态 |
| POST | `/tasks` | 创建并执行任务 |
| GET | `/tasks/{task_id}` | 查询任务结果 |

### 5.1 创建任务

请求：

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"task_type":"text_length","text":"hello world"}'
```

请求体：

```json
{
  "task_type": "text_length",
  "text": "hello world"
}
```

成功响应状态码：`201 Created`

响应示例：

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

字符数使用 Python `len()` 计算，空格、换行均计入字符数。

### 5.2 查询任务

```bash
curl http://127.0.0.1:8000/tasks/<task_id>
```

将 `<task_id>` 替换为创建任务时返回的 UUID。

成功返回 `200 OK`，查询不存在的任务返回 `404 Not Found`。

### 5.3 输入校验

当前仅允许任务类型：

```text
text_length
```

文本长度范围：

```text
1～10000 个字符
```

以下输入返回 `422`：

- 不支持的任务类型
- 缺少必填字段
- 空文本
- 超过 10000 个字符的文本
- 包含额外字段的请求

当任务存储达到 1000 条时，新任务返回 `503 Service Unavailable`。

## 6. 自动化测试

安装测试依赖后运行：

```bash
.venv/bin/python -m pytest -v
```

当前已完成的测试包括：

- POST 创建任务
- GET 查询任务
- 不合法输入返回 422
- 不存在任务返回 404
- 重复提交生成不同 UUID
- 任务存储容量边界检查
- 健康检查接口

测试状态：**已通过**。

具体测试数量和运行结果以最新 pytest 输出为准。

## 7. 当前限制

本阶段采用最简化设计：

- 单进程运行
- 同步执行任务
- 内存字典存储记录
- 服务重启后任务记录丢失
- 不支持多进程共享任务状态
- 不支持异步任务队列
- 不执行 Shell 命令
- 尚未实现真正的多 Agent 协作

## 8. 开发进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| W01 | FastAPI 服务与健康检查 | 完成 |
| W02 | 单 Agent 任务执行与结果查询 | 核心功能与测试完成 |
| W03 | SQLite 任务持久化 | 待开发 |

## 9. 下一阶段计划

W03：SQLite 持久化。

计划实现：

1. 建立任务数据库。
2. 将任务结果写入 SQLite。
3. 支持按 UUID 查询历史任务。
4. 重启服务器后仍能查询已有任务。
5. 增加数据库相关自动化测试。

长期目标：构建具有任务分发、Agent 协作、状态管理和结果汇总能力的 Multi-Agent 系统。
