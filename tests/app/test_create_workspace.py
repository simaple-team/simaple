from fastapi.testclient import TestClient

from simaple.app.interface.web import app

client = TestClient(app)


def test_read_main(simulator_configuration):
    response = client.post(
        "/workspaces/",
        json=simulator_configuration,
    )
    assert response.status_code == 200
    simulator_id = response.json()["id"]

    resp = client.get(
        f"/workspaces/logs/{simulator_id}/0",
    )

    assert resp.json()["index"] == 0
