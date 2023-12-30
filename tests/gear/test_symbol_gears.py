from simaple.gear.symbol_gear import (
    ArcaneSymbolTemplate,
    AuthenticSymbolTemplate,
    SymbolIndicator,
)


def test_arcane_symbol_stat():
    symbol = ArcaneSymbolTemplate(level=3, stat_type=SymbolIndicator.STR).get_symbol()

    assert symbol.get_stat().STR_static == 500


def test_arcane_symbol_force():
    symbol = ArcaneSymbolTemplate(level=3, stat_type=SymbolIndicator.STR).get_symbol()

    assert symbol.get_force() == 50


def test_authentic_symbol_stat():
    symbol = AuthenticSymbolTemplate(
        level=3, stat_type=SymbolIndicator.STR
    ).get_symbol()

    assert symbol.get_stat().STR_static == 900


def test_authentic_symbol_force():
    symbol = AuthenticSymbolTemplate(
        level=3, stat_type=SymbolIndicator.STR
    ).get_symbol()

    assert symbol.get_force() == 30
