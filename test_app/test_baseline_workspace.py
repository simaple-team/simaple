def test_initial_workspace(baseline_configuration, client):
    response = client.post(
        "/workspaces/baseline",
        json=baseline_configuration,
    )
    print(response.json())

    assert response.status_code == 200
    simulator_id = response.json()["id"]

    resp = client.get(
        f"/workspaces/logs/{simulator_id}/0",
    )
    assert resp.json()["index"] == 0
