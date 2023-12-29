from simaple.core import ActionStat, ExtendedStat, Stat
from simaple.gear.potential import Potential


def test_potential():
    potential = Potential(
        options=[
            ExtendedStat(stat=Stat(attack_power=3)),
            ExtendedStat(stat=Stat(attack_power=4)),
            ExtendedStat(action_stat=ActionStat(cooltime_reduce=3)),
        ]
    )
    for v in potential.options:
        print(v)

    assert potential.get_stat() == Stat(attack_power=7)
    assert potential.get_action_stat() == ActionStat(cooltime_reduce=3)
    assert potential.get_extended_stat() == ExtendedStat(
        stat=Stat(attack_power=7), action_stat=ActionStat(cooltime_reduce=3)
    )
