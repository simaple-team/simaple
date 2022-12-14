import json

from fastapi.testclient import TestClient

from simaple.app.interface.web import app

client = TestClient(app)


def test_read_main(workspace_configuration, record_file_name):
    response = client.post(
        "/workspaces/",
        json=workspace_configuration,
    )
    assert response.status_code == 200
    workspace_id = response.json()["id"]

    resp = client.get(
        f"/statistics/graph/{workspace_id}",
    )

    requests = 0
    with open(record_file_name, encoding="utf-8") as f:
        for line in f:
            timing, action = line.split("\t")
            resp = client.post(
                f"/workspaces/play/{workspace_id}",
                json=json.loads(action),
            )
            requests += 1
            if requests > 50:
                break

    resp = client.get(
        f"/statistics/graph/{workspace_id}",
    )
