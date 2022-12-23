import pytest

from simaple.core import ActionStat, ElementalResistance, Stat
from simaple.system.trait import CharacterTrait


@pytest.mark.parametrize(
    "trait, stat, action_stat, elemental_resistance",
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
            ElementalResistance(value=0),
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
            ElementalResistance(value=0),
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
            Stat(MHP=500, MMP=400),
            ActionStat(buff_duration=2),
            ElementalResistance(value=1),
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
            Stat(MHP=2000, MMP=2000, ignored_defence=10),
            ActionStat(buff_duration=10),
            ElementalResistance(value=5),
        ),
    ],
)
def test_trait_and_stat(
    trait: CharacterTrait,
    stat: Stat,
    action_stat: ActionStat,
    elemental_resistance: ElementalResistance,
):
    assert trait.get_stat() == stat
    assert trait.get_action_stat() == action_stat
    assert trait.get_elemental_resistance() == elemental_resistance
