import pytest
from fastapi.testclient import TestClient

from database import init_db
from server_agent import app


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setenv("TASK_DB_PATH", str(tmp_path / "tasks.db"))
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
