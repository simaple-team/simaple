from simaple.core import Stat
from simaple.system.hexa_stat import HexaStat, HexaStatCore, HexaStatCoreType


def test_hexa_stat_core_type():
    core = HexaStatCoreType(
        name="core", basis={"STR": 5, "DEX": 3, "critical_damage": 0.2}
    )

    assert core.get_main_stat_effect(1) == Stat(STR=5, DEX=3, critical_damage=0.2)

    assert core.get_main_stat_effect(5) == Stat(STR=30, DEX=18, critical_damage=0.2 * 6)

    assert core.get_sub_stat_effect(1) == Stat(STR=5, DEX=3, critical_damage=0.2)

    assert core.get_sub_stat_effect(5) == Stat(STR=25, DEX=15, critical_damage=0.2 * 5)


def test_hexa_stat():
    core_types = [
        HexaStatCoreType(
            name="A",
            basis={
                "STR": 5,
            },
        ),
        HexaStatCoreType(
            name="B",
            basis={
                "DEX": 3,
            },
        ),
        HexaStatCoreType(
            name="C",
            basis={
                "critical_damage": 1,
            },
        ),
    ]

    core = HexaStatCore(
        main_stat_name="A",
        sub_stat_name_1="B",
        sub_stat_name_2="C",
        main_stat_level=7,
        sub_stat_level_1=6,
        sub_stat_level_2=6,
    )

    hexa_stat = HexaStat(core_types=core_types, cores=[core])

    assert hexa_stat.get_stat() == Stat(STR=50, DEX=18, critical_damage=6)
