from simaple.core import ActionStat, Stat
from simaple.gear.gear_repository import GearRepository
from simaple.request.adapter.item import get_gears, get_gearset, get_symbols
from simaple.request.schema.item import CharacterItemEquipment, CharacterSymbolEquipment


def test_item_equipment(character_item_equipment_response: CharacterItemEquipment):
    gear_repository = GearRepository()
    gears = get_gears(character_item_equipment_response, gear_repository)

    gear = gears[0][0]
    assert gear.stat == Stat.model_validate(
        {
            "STR": 5.0,
            "LUK": 178.0,
            "INT": 226.0,
            "DEX": 45.0,
            "attack_power": 85.0,
            "magic_attack": 87.0,
            "ignored_defence": 10.0,
            "MHP": 615.0,
            "MMP": 360.0,
        }
    )

    assert gear.potential.get_stat() == Stat(INT_multiplier=18)
    assert gear.potential.get_action_stat() == ActionStat(cooltime_reduce=2)


def test_get_symbols(character_symbol_equipment_response: CharacterSymbolEquipment):
    symbols = get_symbols(character_symbol_equipment_response)
    total_stat = sum([symbol.stat for symbol in symbols], Stat())
    assert total_stat == Stat(INT_static=21200)


def test_get_gearset(
    character_item_equipment_response: CharacterItemEquipment,
    character_symbol_equipment_response: CharacterSymbolEquipment,
):
    gearset = get_gearset(
        character_item_equipment_response,
        character_symbol_equipment_response,
        GearRepository(),
    )
