def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "agent_id": "server-agent-01",
        "version": "0.1.0",
    }
