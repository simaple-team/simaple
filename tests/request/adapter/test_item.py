from simaple.core import ActionStat, Stat
from simaple.gear.gear_repository import GearRepository
from simaple.request.adapter.gear_loader._cashitem_converter import get_cash_item_stat
from simaple.request.adapter.gear_loader._converter import (
    _get_regularized_weapon,
    get_equipments,
    get_symbols,
    get_weapon_replacement,
)
from simaple.request.adapter.gear_loader._gearset_converter import get_equipment_stat
from simaple.request.adapter.gear_loader._pet_converter import (
    get_pet_equip_stat_from_response,
)
from simaple.request.adapter.gear_loader._set_item_converter import get_set_item_stats
from simaple.request.external.nexon.api.character.item import (
    CashItemResponse,
    CharacterItemEquipment,
    CharacterSymbolEquipment,
    PetResponse,
    SetEffectResponse,
)


def test_item_equipment(character_item_equipment_response: CharacterItemEquipment):
    gear_repository = GearRepository()
    gears = get_equipments(character_item_equipment_response, gear_repository)

    gear = gears[0][0]
    assert gear.stat == Stat.model_validate(
        {
            "STR": 0.0,
            "LUK": 173.0,
            "INT": 221.0,
            "DEX": 40.0,
            "attack_power": 85.0,
            "magic_attack": 87.0,
            "ignored_defence": 10.0,
            "MHP": 615.0,
            "MMP": 360.0,
            "STR_multiplier": 5.0,
            "LUK_multiplier": 5.0,
            "INT_multiplier": 5.0,
            "DEX_multiplier": 5.0,
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


def test_get_cash_item_stat(cashitem_equipment_response: CashItemResponse):
    stat = get_cash_item_stat(cashitem_equipment_response)
    assert stat == Stat(
        STR=60,
        LUK=30,
        DEX=60,
        magic_attack=30,
        attack_power=30,
    )


def test_get_equipment_stat(character_item_equipment_response: CharacterItemEquipment):
    gear_repository = GearRepository()
    get_equipment_stat(character_item_equipment_response, gear_repository)


def test_get_set_item_stats(set_effect_response: SetEffectResponse):
    stat = get_set_item_stats(set_effect_response)
    assert stat.critical_damage == 5


def test_get_regularized_weapon() -> None:
    gear_repository = GearRepository()

    regularized_weapon = _get_regularized_weapon(
        "제네시스 스태프",
        Stat.model_validate(
            {
                "INT": 55,
                "MMP": 3000,
                "attack_power": 92,
                "magic_attack": 250,
            }
        ),
        22,
        Stat(magic_attack=72),
    )
    assert regularized_weapon.sum_stat() == Stat(
        INT=350.0,
        LUK=295.0,
        MHP=255.0,
        MMP=3255.0,
        attack_power=541.0,
        boss_damage_multiplier=30.0,
        magic_attack=832.0,
        ignored_defence=20.0,
    )


def test_get_weapon_replacement(
    character_item_equipment_response: CharacterItemEquipment,
):
    gear_repository = GearRepository()
    resp = get_weapon_replacement(character_item_equipment_response, gear_repository)
    assert resp == Stat(
        magic_attack=-173.0,
    )
