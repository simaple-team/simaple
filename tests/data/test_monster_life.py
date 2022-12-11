from simaple.core import Stat
from simaple.data.monster_life import get_normal_monsterlife_stat


def test_normal_monster_life_data():
    normal_monsterlife_stat = get_normal_monsterlife_stat()
    assert isinstance(normal_monsterlife_stat, Stat)
    assert normal_monsterlife_stat != Stat()
    print(normal_monsterlife_stat)
