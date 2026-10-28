import pytest

from database import count_tasks, get_task


@pytest.mark.parametrize(
    "task_type, text, expected",
    [
        ("text_length", "hello world", {"character_count": 11}),
        ("word_count", "hello world", {"word_count": 2}),
        ("word_count", "hello   world", {"word_count": 2}),
        ("word_count", "hello\tworld\nPython", {"word_count": 3}),
        ("word_count", "  hello world  ", {"word_count": 2}),
        ("word_count", "   ", {"word_count": 0}),
        ("word_count", "你好世界", {"word_count": 1}),
    ],
)
def test_create_store_and_query_task(client, task_type, text, expected):
    response = client.post(
        "/tasks",
        json={"task_type": task_type, "text": text},
    )

    # 验证 API 执行结果。
    assert response.status_code == 201
    data = response.json()
    assert set(data) == {"task_id", "task_type", "status", "result"}
    assert data["task_type"] == task_type
    assert data["status"] == "succeeded"
    assert data["result"] == expected

    # 验证任务确实写入 SQLite。
    assert count_tasks() == 1
    stored = get_task(data["task_id"])
    assert stored is not None
    assert stored["task_type"] == task_type
    assert stored["status"] == "succeeded"
    assert stored["result"] == expected

    # 验证通过 UUID 查询得到相同结果。
    query_response = client.get(f"/tasks/{data['task_id']}")
    assert query_response.status_code == 200
    assert query_response.json() == data