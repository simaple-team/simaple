import pytest
from loguru import logger

from simaple.core import Stat, StatProps
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements.spell_trace import SpellTrace

TEST_CASES = [
    (1005197, 100, StatProps.INT, Stat(INT=3, MHP=30)),
    (1005197, 70, StatProps.STR, Stat(STR=4, MHP=70)),
    (1005197, 30, StatProps.MHP, Stat(MHP=470)),
    (1102057, 100, StatProps.INT, Stat(INT=2, MHP=20)),
    (1102057, 70, StatProps.STR, Stat(STR=3, MHP=40)),
    (1102057, 30, StatProps.MHP, Stat(MHP=320)),
    (1082637, 100, StatProps.INT, Stat(magic_attack=1)),
    (1082637, 70, StatProps.DEX, Stat(attack_power=2)),
    (1082637, 30, StatProps.LUK, Stat(attack_power=3)),
    (1082636, 100, StatProps.INT, Stat(magic_attack=1)),
    (1082636, 70, StatProps.DEX, Stat(attack_power=2)),
    (1082636, 30, StatProps.LUK, Stat(attack_power=3)),
    (1372228, 100, StatProps.INT, Stat(magic_attack=3, INT=1)),
    (1372228, 30, StatProps.DEX, Stat(attack_power=7, DEX=3)),
    (1372228, 15, StatProps.LUK, Stat(attack_power=9, LUK=4)),
    (1332279, 100, StatProps.INT, Stat(magic_attack=3, INT=1)),
    (1332279, 70, StatProps.DEX, Stat(attack_power=5, DEX=2)),
    (1332279, 15, StatProps.MHP, Stat(attack_power=9, MHP=200)),
    (1113149, 100, StatProps.INT, Stat(INT=1)),
    (1113149, 70, StatProps.STR, Stat(STR=2)),
    (1113149, 30, StatProps.MHP, Stat(MHP=200)),
    (1032241, 100, StatProps.INT, Stat(INT=2)),
    (1032241, 70, StatProps.STR, Stat(STR=3)),
    (1032241, 30, StatProps.MHP, Stat(MHP=250)),
]


@pytest.mark.parametrize("gear_id, prob, stat_prop, expected", TEST_CASES)
def test_armor_bonus(gear_id, prob, stat_prop, expected):
    repository = GearRepository()

    gear = repository.get_by_id(gear_id)
    spell_trace = SpellTrace(probability=prob, stat_prop_type=stat_prop)

    improvement = spell_trace.calculate_improvement(gear)
    logger.info(gear)

    assert improvement == expected
