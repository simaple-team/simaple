from simaple.core import ExtendedStat, StatProps
from simaple.data.system.hyperstat import get_kms_hyperstat
from simaple.request.adapter.hyperstat_loader.adapter import get_hyperstat


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
