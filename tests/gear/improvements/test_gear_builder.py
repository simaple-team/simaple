from simaple.gear.builder import GearMetadata, GearBuilder
from simaple.gear.improvements.spell_trace import SpellTrace
from simaple.gear.improvements.scroll import Scroll
from simaple.gear.improvements.starforce import Starforce
from simaple.gear.improvements.bonus import Bonus, BonusType
from simaple.core.base import Stat, StatProps
from simaple.gear.gear_repository import GearRepository
from simaple.gear.gear_type import GearType
from simaple.gear.gear import Gear
from simaple.gear.improvements.base import GearImprovement
from typing import Literal, List

from loguru import logger
import json
import os
from json import JSONEncoder
import pytest


class MetadataJsonJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BonusType):
            return obj.value
        if isinstance(obj, StatProps):
            return obj.value
        else:
            return json.JSONEncoder.default(self, obj)


@pytest.mark.parametrize(
    'test_case_file',
    ['absolab_glove_21_p30.json', 'arcane_breath_shooter_19_p30.json', 'absolab_cape_21_p30.json', 'absolab_tunner_21_p70.json', 'arcane_polearm_19_p30.json', 'arcane_polearm_13_p100.json', 'absolab_cape_16_p70.json', 'absolab_glove_17_p30.json', 'absolab_tunner_21_p15.json', 'absolab_tunner_16_p70.json']
)
def test_absolab_17_p30_full(test_case_file):
    builder = GearBuilder(GearRepository())
    base_path = 'tests/gear/improvements/builder_test_cases/'

    with open(os.path.join(base_path, test_case_file)) as f:
        test_case = json.load(f)

    metadata = GearMetadata.parse_obj(test_case['given'])
    
    gear = builder.build(metadata)
    expected_gear = Gear.parse_obj(test_case['expected'])
    
    assert gear == expected_gear
