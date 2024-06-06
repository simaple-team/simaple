def test_snapshot_consistency(simulator_configuration, client):
    resp = client.post(
        "/workspaces/",
        json=simulator_configuration,
    )

    simulator_id = resp.json()["id"]

    response = client.post(
        "/snapshots/",
        json={
            "simulator_id": simulator_id,
            "name": "test-snapshot",
        },
    )
    assert response.status_code == 200

    response = client.get("/snapshots/")

    assert response.status_code == 200
    assert len(response.json()) == 1

    snapshot_id = response.json()[0]["id"]
    response = client.post(
        f"/snapshots/{snapshot_id}/load",
    )

    assert response.status_code == 200

    response = client.get(
        "/workspaces/",
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
