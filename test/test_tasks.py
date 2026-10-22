from fastapi.testclient import TestClient
from server_agent import app
from task_agent import tasks

client = TestClient(app)

def test_task_not_found():
    response = client.get("/tasks/not-exist")
    assert response.status_code == 404

def test_unique_task_id():
    payload={
		"task_type":"text_length",
		"text":"hello"
}
    response1 = client.post("/tasks",
	json=payload)
    response2 = client.post("/tasks",
	json=payload)

    assert response1.status_code == 201
    assert response2.status_code == 201

    id1 = response1.json()["task_id"]
    id2 = response2.json()["task_id"]

    assert id1 != id2
    assert len(tasks) == 2

def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "task_type": "text_length",
            "text": "hello"
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert data["result"]["character_count"] == 5
    assert data["status"] == "succeeded"
    assert "task_id" in data

    task_id =  data["task_id"]

    get_resp = client.get(f"/tasks/{task_id}")
    get_data = get_resp.json()

    assert get_resp.status_code == 200
    assert get_data == data

def test_task_limit():
    # 模拟字典中已有 1000 条任务
    for i in range(1000):
        tasks[str(i)] = {"status": "succeeded"}

    # 再提交一条任务
    response = client.post(
        "/tasks",
        json={
            "task_type": "text_length",
            "text": "hello"
        }
    )

    assert response.status_code == 503
    assert len(tasks) == 1000
