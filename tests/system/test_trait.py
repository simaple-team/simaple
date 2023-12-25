import pytest

from simaple.core import ActionStat, Stat
from simaple.system.propensity import Propensity


@pytest.mark.parametrize(
    "propensity, stat, action_stat",
    [
        (
            Propensity(
                ambition=0,
                insight=0,
                empathy=0,
                willpower=0,
                diligence=0,
                charm=0,
            ),
            Stat(),
            ActionStat(),
        ),
        (
            Propensity(
                ambition=50,
                insight=0,
                empathy=0,
                willpower=0,
                diligence=0,
                charm=0,
            ),
            Stat(ignored_defence=5),
            ActionStat(),
        ),
        (
            Propensity(
                ambition=0,
                insight=20,
                empathy=20,
                willpower=25,
                diligence=0,
                charm=0,
            ),
            Stat(MHP=500, MMP=400, elemental_resistance=1),
            ActionStat(buff_duration=2),
        ),
        (
            Propensity(
                ambition=100,
                insight=100,
                empathy=100,
                willpower=100,
                diligence=100,
                charm=100,
            ),
            Stat(MHP=2000, MMP=2000, ignored_defence=10, elemental_resistance=5),
            ActionStat(buff_duration=10),
        ),
    ],
)
def test_propensity_and_stat(
    propensity: Propensity,
    stat: Stat,
    action_stat: ActionStat,
):
    assert propensity.get_stat() == stat
    assert propensity.get_action_stat() == action_stat
