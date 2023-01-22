import pytest

from simaple.core import ActionStat, Stat
from simaple.system.trait import CharacterTrait


@pytest.mark.parametrize(
    "trait, stat, action_stat",
    [
        (
            CharacterTrait(
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
            CharacterTrait(
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
            CharacterTrait(
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
            CharacterTrait(
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
def test_trait_and_stat(
    trait: CharacterTrait,
    stat: Stat,
    action_stat: ActionStat,
):
    assert trait.get_stat() == stat
    assert trait.get_action_stat() == action_stat
