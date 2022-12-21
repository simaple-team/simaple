import json


def test_read_main(simulator_configuration, record_file_name, client):
    response = client.post(
        "/workspaces/",
        json=simulator_configuration,
    )
    assert response.status_code == 200
    simulator_id = response.json()["id"]

    requests = 0
    previous_delay = 0

    with open(record_file_name, encoding="utf-8") as f:
        for line in f:
            timing, action = line.split("\t")
            resp = client.post(
                f"/workspaces/play/{simulator_id}",
                json=json.loads(action),
            )

            given_delay = resp.json()["delay"]

            if previous_delay != 0:
                assert given_delay == 0

            previous_delay = given_delay

            requests += 1
