import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def get_db_path():
    """获取数据库路径，允许测试环境覆盖。"""
    return Path(
        os.environ.get("TASK_DB_PATH", BASE_DIR / "data" / "tasks.db")
    )

def init_db():
    """初始化数据库和任务表。"""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

def create_task(record):
    """向数据库插入一条任务记录。"""
    db_path = get_db_path()

    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    task_id, task_type, status,
                    result_json, created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record["task_id"],
                    record["task_type"],
                    record["status"],
                    json.dumps(
                        record["result"],
                        ensure_ascii=False
                    ),
                    record["created_at"],
                ),
            )

def get_task(task_id):
    """根据 task_id 查询任务，不存在时返回 None。"""
    db_path = get_db_path()

    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            "SELECT * FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "task_id": row["task_id"],
        "task_type": row["task_type"],
        "status": row["status"],
        "result": json.loads(row["result_json"]),
        "created_at": row["created_at"],
    }

def count_tasks():
    """返回数据库中任务记录的总数量。"""
    db_path = get_db_path()

    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()

    return row[0]