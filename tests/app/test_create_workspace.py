from fastapi.testclient import TestClient

from simaple.app.interface.web import app

client = TestClient(app)


def test_read_main(workspace_configuration):
    response = client.post(
        "/workspaces/",
        json=workspace_configuration,
    )
    assert response.status_code == 200
    workspace_id = response.json()["id"]

    resp = client.get(
        f"/workspaces/logs/{workspace_id}/0",
    )

    assert resp.json()["index"] == 0
