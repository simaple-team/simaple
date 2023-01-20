from simaple.core import ExtendedStat
from simaple.data.monster_life import get_normal_monsterlife


def test_normal_monster_life_data():
    normal_monsterlife_stat = get_normal_monsterlife()
    assert isinstance(normal_monsterlife_stat, ExtendedStat)
    assert normal_monsterlife_stat != ExtendedStat()
    print(normal_monsterlife_stat)
