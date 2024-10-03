from simaple.core import Stat
from simaple.request.adapter.link_skill_loader.adapter import get_link_skillset


def test_link_skill(link_skill_response):
    link_skillset = get_link_skillset(link_skill_response)

    assert link_skillset.get_stat() == Stat(
        boss_damage_multiplier=15 + 4,
        STR_multiplier=10,
        DEX_multiplier=10,
        INT_multiplier=10,
        LUK_multiplier=10,
        damage_multiplier=10 + 12 + 12 + 11 + 2 * 4,
        critical_damage=4,
        critical_rate=10,
    )
