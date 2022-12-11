import json
import os

from fastapi.testclient import TestClient

from simaple.app.web import app

client = TestClient(app)


def test_read_main():
    response = client.post(
        "/workspaces/",
        json={
            "action_stat": {},
            "groups": ["archmagefb", "common", "adventurer.magician"],
            "injected_values": {"character_level": 260},
            "skill_levels": {},
            "v_improvements": {},
            "character_stat": {
                "STR": 907.0,
                "LUK": 2224.0,
                "INT": 4932.0,
                "DEX": 832.0,
                "STR_multiplier": 86.0,
                "LUK_multiplier": 86.0,
                "INT_multiplier": 573.0,
                "DEX_multiplier": 86.0,
                "STR_static": 420.0,
                "LUK_static": 500.0,
                "INT_static": 15460.0,
                "DEX_static": 200.0,
                "attack_power": 1200.0,
                "magic_attack": 2075.0,
                "attack_power_multiplier": 0.0,
                "magic_attack_multiplier": 81.0,
                "critical_rate": 100.0,
                "critical_damage": 83.0,
                "boss_damage_multiplier": 144.0,
                "damage_multiplier": 167.7,
                "final_damage_multiplier": 110.0,
                "ignored_defence": 94.72006176400876,
                "MHP": 23105.0,
                "MMP": 12705.0,
                "MHP_multiplier": 0.0,
                "MMP_multiplier": 0.0,
            },
        },
    )
    assert response.status_code == 200
    workspace_id = response.json()["id"]

    requests = 0
    previous_delay = 0

    with open(os.path.join(os.path.dirname(__file__), "record.tsv")) as f:
        for line in f:
            timing, action = line.split("\t")
            action = json.loads(action)

            if action["method"] == "use":
                resp = client.post(
                    f"/workspaces/use/{workspace_id}",
                    json={"name": action["name"]},
                )
            elif action["method"] == "elapse":
                resp = client.post(
                    f"/workspaces/elapse/{workspace_id}",
                    json={"time": action["payload"]},
                )

            given_delay = resp.json()["delay"]

            if previous_delay != 0:
                assert given_delay == 0

            previous_delay = given_delay

            requests += 1
