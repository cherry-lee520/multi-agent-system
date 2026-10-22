from fastapi.testclient import TestClient
from server_agent import app

client = TestClient(app)

def test_invalid_task():
    response = client.post("/tasks",json={"task_type":"Unknow",
		"text":"hello"})

    assert response.status_code == 422
