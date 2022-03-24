from simaple.gear.arcane_symbol import ArcaneSymbol
from simaple.core import BaseStatType

def test_arcane_symbol_stat():
    symbol = ArcaneSymbol(
        level=3,
        stat_type=BaseStatType.STR
    )

    assert symbol.get_stat().STR == 500


def test_arcane_symbol_force():
    symbol = ArcaneSymbol(
        level=3,
        stat_type=BaseStatType.STR
    )

    assert symbol.get_force() == 50
