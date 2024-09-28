from simaple.core import ActionStat, Stat
from simaple.gear.gear_repository import GearRepository

from simaple.request.adapter.gear_loader._converter import (
    get_equipments, get_symbols
)
from simaple.request.adapter.gear_loader._gearset_converter import (
    get_gearset
)
from simaple.request.adapter.gear_loader._pet_converter import (
    get_pet_equip_stat_from_response
)
from simaple.request.adapter.gear_loader._schema import (
    PetResponse,
    CharacterItemEquipment,
    CharacterSymbolEquipment,
)


def test_item_equipment(character_item_equipment_response: CharacterItemEquipment):
    gear_repository = GearRepository()
    gears = get_equipments(character_item_equipment_response, gear_repository)

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


def test_get_pet_stat(pet_response: PetResponse):
    stat = get_pet_equip_stat_from_response(pet_response)
    assert stat == Stat(attack_power=20, magic_attack=127)


def test_get_gearset(
    character_item_equipment_response: CharacterItemEquipment,
    character_symbol_equipment_response: CharacterSymbolEquipment,
    pet_response: PetResponse,
):
    gearset = get_gearset(
        character_item_equipment_response,
        character_symbol_equipment_response,
        pet_response,
        GearRepository(),
    )
