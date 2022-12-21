import json


def test_read_main(simulator_configuration, record_file_name, client):
    response = client.post(
        "/workspaces/",
        json=simulator_configuration,
    )
    assert response.status_code == 200
    simulator_id = response.json()["id"]

    with open(record_file_name, encoding="utf-8") as f:
        for line in f:
            timing, action = line.split("\t")
            action = json.loads(action)

            if action["method"] == "use":
                resp = client.post(
                    f"/workspaces/use_and_elapse/{simulator_id}",
                    json={"name": action["name"]},
                )

            given_delay = resp.json()["delay"]
            assert given_delay == 0
