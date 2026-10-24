
import os
import tempfile
from pathlib import Path

from database import init_db, create_task, get_task, count_tasks


with tempfile.TemporaryDirectory() as temp_dir:
    os.environ["TASK_DB_PATH"] = str(
        Path(temp_dir) / "tasks.db"
    )

    init_db()

    record = {
        "task_id": "test-001",
        "task_type": "text_length",
        "status": "succeeded",
        "result": {"length": 15},
        "created_at": "2026-10-25T12:00:00",
    }

    create_task(record)

    print("任务数量：", count_tasks())
    print("查询结果：", get_task("test-001"))
    print("不存在的任务：", get_task("not-exist"))

    # 再次初始化不能删除已有记录
    init_db()

    assert get_task("test-001") == record
    assert count_tasks() == 1
    assert get_task("not-exist") is None

    print("数据库基础功能测试全部通过！")
