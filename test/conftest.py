import pytest
from task_agent import tasks

@pytest.fixture(autouse = True)
def clear_task():
	tasks.clear()
	yield
	tasks.clear()
