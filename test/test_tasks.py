from datetime import datetime, timezone
from uuid import UUID

from database import count_tasks, create_task, get_task


def test_task_not_found(client):
    response = client.get("/tasks/not-exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_unique_task_id(client):
    payload = {"task_type": "text_length", "text": "hello"}
    response1 = client.post("/tasks", json=payload)
    response2 = client.post("/tasks", json=payload)
    assert response1.status_code == 201
    assert response2.status_code == 201
    id1 = response1.json()["task_id"]
    id2 = response2.json()["task_id"]
    assert UUID(id1).version == UUID(id2).version == 4
    assert id1 != id2
    assert count_tasks() == 2


def test_create_task(client):
    response = client.post(
        "/tasks", json={"task_type": "text_length", "text": "hello"}
    )
    assert response.status_code == 201
    data = response.json()
    assert set(data) == {"task_id", "task_type", "status", "result"}
    assert data["task_type"] == "text_length"
    assert data["result"] == {"character_count": 5}
    assert data["status"] == "succeeded"
    stored = get_task(data["task_id"])
    assert stored is not None
    assert stored["result"] == data["result"]
    assert datetime.fromisoformat(stored["created_at"]).tzinfo == timezone.utc
    get_response = client.get(f"/tasks/{data['task_id']}")
    assert get_response.status_code == 200
    assert get_response.json() == data


def test_task_limit(client):
    # 数据库存量达到 999 时仍允许创建第 1000 条任务。
    for i in range(999):
        create_task({
            "task_id": str(i),
            "task_type": "text_length",
            "status": "succeeded",
            "result": {"character_count": 5},
            "created_at": "2026-10-25T00:00:00+00:00",
        })
    payload = {"task_type": "text_length", "text": "hello"}
    assert client.post("/tasks", json=payload).status_code == 201
    assert count_tasks() == 1000
    response = client.post("/tasks", json=payload)
    assert response.status_code == 503
    assert response.json() == {"detail": "Task storage is full"}
    assert count_tasks() == 1000
    assert client.get("/tasks/0").status_code == 200
