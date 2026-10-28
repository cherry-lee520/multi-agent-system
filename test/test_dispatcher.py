from unittest.mock import Mock

import pytest

from agents.length_agent import LengthAgent
from agents.word_count_agent import WordCountAgent
from dispatcher import AGENTS, dispatch_task


@pytest.mark.parametrize(
    "task_type, agent_class, expected",
    [
        ("text_length", LengthAgent, {"character_count": 11}),
        ("word_count", WordCountAgent, {"word_count": 2}),
    ],
)
def test_dispatch_to_correct_agent(
    monkeypatch, task_type, agent_class, expected
):
    # 确认任务类型注册了正确的 Agent。
    assert isinstance(AGENTS[task_type], agent_class)

    # 记录调用，同时保留真实的执行逻辑。
    spies = {}
    for name, agent in AGENTS.items():
        spy = Mock(wraps=agent.execute)
        monkeypatch.setattr(agent, "execute", spy)
        spies[name] = spy

    result = dispatch_task(task_type, "hello world")

    assert result == expected
    spies[task_type].assert_called_once_with("hello world")

    # 其他 Agent 不应被调用。
    for name, spy in spies.items():
        if name != task_type:
            spy.assert_not_called()


def test_dispatch_unsupported_task():
    with pytest.raises(
        ValueError,
        match="Unsupported task type: unknown",
    ):
        dispatch_task("unknown", "hello world")