import pytest

from database import count_tasks


@pytest.mark.parametrize("payload", [
    {"task_type": "Unknow", "text": "hello"},
    {"text": "hello"},
    {"task_type": "text_length"},
    {"task_type": "text_length", "text": ""},
    {"task_type": "text_length", "text": "a" * 10001},
    {"task_type": "text_length", "text": "hello", "extra": True},
    {"task_type": "text_length", "text": None},
    {"task_type": "text_length", "text": 123},
])
def test_invalid_task(client, payload):
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
    assert count_tasks() == 0


@pytest.mark.parametrize("text", ["a", "a" * 10000, "你好 世界\n"])
def test_valid_text_boundaries(client, text):
    response = client.post(
        "/tasks", json={"task_type": "text_length", "text": text}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["result"] == {"character_count": len(text)}
    assert client.get(f"/tasks/{data['task_id']}").json() == data
