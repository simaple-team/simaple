from simaple.core import StatProps
from simaple.request.adapter.hyperstat import get_hyperstat
from simaple.request.adapter.propensity import get_propensity
from simaple.request.adapter.union import get_union_squad, get_union_squad_effect
from simaple.system.hyperstat import get_kms_hyperstat
from simaple.system.propensity import Propensity


def test_hyperstat_adapter(character_hyper_stat_response):
    hyperstat = get_hyperstat(character_hyper_stat_response)

    expected = get_kms_hyperstat()
    expected.options = hyperstat.options
    for stat_props, level in [
        (StatProps.INT_static, 5),
        (StatProps.LUK_static, 1),
        (StatProps.attack_power, 5),
        (StatProps.damage_multiplier, 11),
        (StatProps.boss_damage_multiplier, 12),
        (StatProps.critical_damage, 11),
        (StatProps.ignored_defence, 11),
        (StatProps.critical_rate, 6),
    ]:
        expected = expected.set_level(stat_props, level)

    assert hyperstat.get_stat().short_dict() == expected.get_stat().short_dict()


def test_propensity_response(character_propensity_response):
    propensity = get_propensity(character_propensity_response)

    assert propensity == Propensity(
        ambition=100,
        insight=100,
        empathy=100,
        willpower=73,
        diligence=66,
        charm=58,
    )


def test_union_raiders_response(character_union_raiders_response):
    union_squad = get_union_squad(character_union_raiders_response)
    squad_effect = get_union_squad_effect(character_union_raiders_response)

    assert union_squad.get_stat().short_dict() == squad_effect.stat.short_dict()
