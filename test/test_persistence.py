import json
import subprocess
import sys
import pytest
from pathlib import Path

from fastapi.testclient import TestClient

from database import count_tasks, get_task, init_db
from server_agent import app


def test_initialization_keeps_existing_tasks(client):
    created = client.post(
        "/tasks", json={"task_type": "text_length", "text": "hello"}
    ).json()
    init_db()
    init_db()
    assert count_tasks() == 1
    stored = get_task(created["task_id"])
    assert stored is not None
    assert stored["result"] == created["result"]
    assert get_task("not-exist") is None


def test_lifespan_initializes_database(tmp_path, monkeypatch):
    db_path = tmp_path / "fresh" / "tasks.db"
    monkeypatch.setenv("TASK_DB_PATH", str(db_path))
    assert not db_path.exists()
    with TestClient(app) as client:
        assert db_path.exists()
        assert count_tasks() == 0
        assert client.post(
            "/tasks", json={"task_type": "text_length", "text": "hello"}
        ).status_code == 201
    with TestClient(app) as client:
        assert count_tasks() == 1


def run_in_new_process(code, *args):
    completed = subprocess.run(
        [sys.executable, "-c", code, *args],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return json.loads(completed.stdout)


@pytest.mark.parametrize(
    "task_type, expected",
    [
        ("text_length", {"character_count": 11}),
        ("word_count", {"word_count": 2}),
    ],
)
def test_task_survives_process_restart(
    tmp_path, monkeypatch, task_type, expected
):
    db_path = tmp_path / "restart" / "tasks.db"
    monkeypatch.setenv("TASK_DB_PATH", str(db_path))

    # 第一个进程：创建任务，写入 SQLite，然后退出。
    created = run_in_new_process('''
import json
import sys

from fastapi.testclient import TestClient
from server_agent import app

with TestClient(app) as client:
    response = client.post(
        "/tasks",
        json={"task_type": sys.argv[1], "text": "hello world"},
    )
    assert response.status_code == 201
    print(json.dumps(response.json()))
''', task_type)

    assert created["task_type"] == task_type
    assert created["status"] == "succeeded"
    assert created["result"] == expected

    # 第二个进程：使用同一数据库，按 UUID 查询任务。
    loaded = run_in_new_process('''
import json
import sys

from database import count_tasks
from fastapi.testclient import TestClient
from server_agent import app

with TestClient(app) as client:
    response = client.get("/tasks/" + sys.argv[1])
    assert response.status_code == 200
    assert count_tasks() == 1
    print(json.dumps(response.json()))
''', created["task_id"])

    assert loaded == created