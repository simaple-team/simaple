from simaple.gear.authentic_symbol import AuthenticSymbol
from simaple.core import BaseStatType

def test_authentic_symbol_stat():
    symbol = AuthenticSymbol(
        level=3,
        stat_type=BaseStatType.STR
    )

    assert symbol.get_stat().STR == 900


def test_authentic_symbol_force():
    symbol = AuthenticSymbol(
        level=3,
        stat_type=BaseStatType.STR
    )

    assert symbol.get_force() == 30
