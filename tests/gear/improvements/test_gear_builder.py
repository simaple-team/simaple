import json
import os
from json import JSONEncoder

import pytest

from simaple.core import StatProps
from simaple.gear.blueprint.gear_blueprint import GeneralizedGearBlueprint
from simaple.gear.bonus_factory import BonusType
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository


class MetadataJsonJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, BonusType):
            return o.value
        if isinstance(o, StatProps):
            return o.value

        return json.JSONEncoder.default(self, o)


@pytest.mark.parametrize(
    "test_case_file",
    [
        "absolab_glove_21_p30.json",
        "arcane_breath_shooter_19_p30.json",
        "absolab_cape_21_p30.json",
        "absolab_tunner_21_p70.json",
        "arcane_polearm_19_p30.json",
        "arcane_polearm_13_p100.json",
        "absolab_cape_16_p70.json",
        "absolab_glove_17_p30.json",
        "absolab_tunner_21_p15.json",
        "absolab_tunner_16_p70.json",
    ],
)
def test_absolab_17_p30_full(test_case_file):
    gear_repository = GearRepository()
    base_path = "tests/gear/improvements/blueprint_test_cases/"

    with open(os.path.join(base_path, test_case_file), encoding="utf-8") as f:
        test_case = json.load(f)

    test_case["expected"]["meta"] = {}
    test_case["expected"]["meta"]["id"] = test_case["expected"].pop("id")
    test_case["expected"]["meta"]["name"] = test_case["expected"].pop("name")
    test_case["expected"]["meta"]["req_level"] = test_case["expected"].pop("req_level")
    test_case["expected"]["meta"]["boss_reward"] = test_case["expected"].pop(
        "boss_reward"
    )
    test_case["expected"]["meta"]["superior_eqp"] = test_case["expected"].pop(
        "superior_eqp"
    )
    test_case["expected"]["meta"]["req_job"] = test_case["expected"].pop("req_job")
    test_case["expected"]["meta"]["set_item_id"] = test_case["expected"].pop(
        "set_item_id"
    )
    test_case["expected"]["meta"]["type"] = test_case["expected"].pop("type")
    test_case["expected"]["meta"]["base_stat"] = gear_repository.get_by_id(
        test_case["expected"]["meta"]["id"]
    ).stat.short_dict()
    test_case["expected"]["meta"]["max_scroll_chance"] = test_case["expected"][
        "scroll_chance"
    ]

    test_case["given"]["meta"] = test_case["expected"]["meta"]
    test_case["given"].pop("gear_id")

    blueprint = GeneralizedGearBlueprint.parse_obj(test_case["given"])

    gear = blueprint.build()
    expected_gear = Gear.parse_obj(test_case["expected"])

    assert gear == expected_gear
