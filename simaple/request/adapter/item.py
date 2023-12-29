from loguru import logger

from simaple.core import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.symbol_gear import SymbolGear
from simaple.request.schema.item import (
    CharacterItemElement,
    CharacterItemElementOption,
    CharacterItemEquipment,
    CharacterSymbolElement,
    CharacterSymbolEquipment,
)
from simaple.request.translator.kms.potential import kms_potential_translator

_potential_translator = kms_potential_translator()


def _get_stat(item_option: CharacterItemElementOption) -> Stat:
    return Stat(
        STR=item_option.get("str", 0),
        DEX=item_option.get("dex", 0),
        INT=item_option.get("int", 0),
        LUK=item_option.get("luk", 0),
        MHP=item_option.get("max_hp", 0),
        MMP=item_option.get("max_mp", 0),
        attack_power=item_option.get("attack_power", 0),
        magic_attack=item_option.get("magic_power", 0),
        boss_damage_multiplier=item_option.get("boss_damage", 0),
        ignored_defence=item_option.get("ignore_monster_armor", 0),
        damage_multiplier=item_option.get("damage", 0),
        MHP_multiplier=item_option.get("max_hp_rate", 0),
        MMP_multiplier=item_option.get("max_mp_rate", 0),
    ) + Stat.all_stat(item_option.get("all_stat", 0))


def _get_gear(
    item_element: CharacterItemElement, gear_repository: GearRepository
) -> Gear:
    base_gear = gear_repository.get_by_name(item_element["item_name"])
    assert base_gear.meta.base_stat == _get_stat(item_element["item_base_option"])

    base_gear = Gear(
        meta=base_gear.meta,
        stat=base_gear.stat,
        scroll_chance=item_element["scroll_upgradeable_count"],
    )

    base_gear = base_gear.add_stat(_get_stat(item_element["item_add_option"]))
    base_gear = base_gear.add_stat(_get_stat(item_element["item_exceptional_option"]))
    base_gear = base_gear.add_stat(_get_stat(item_element["item_etc_option"]))
    base_gear = base_gear.add_stat(_get_stat(item_element["item_starforce_option"]))

    if base_gear.stat != _get_stat(item_element["item_total_option"]):
        logger.warning(
            f"Item {base_gear.meta.name} stat not matched. Maybe special item?"
        )
        base_gear = Gear(
            meta=base_gear.meta,
            stat=_get_stat(item_element["item_total_option"]),
            scroll_chance=base_gear.scroll_chance,
        )

    base_gear = base_gear.set_potential(
        _potential_translator.translate(
            [
                expression
                for expression in [
                    item_element["potential_option_1"],
                    item_element["potential_option_2"],
                    item_element["potential_option_3"],
                ]
                if expression
            ]
        )
    )

    base_gear = base_gear.set_additional_potential(
        _potential_translator.translate(
            [
                expression
                for expression in [
                    item_element["additional_potential_option_1"],
                    item_element["additional_potential_option_2"],
                    item_element["additional_potential_option_3"],
                ]
                if expression
            ]
        )
    )

    return base_gear


def get_gears(
    item_equipment: CharacterItemEquipment, gear_repository: GearRepository
) -> list[Gear]:
    gears = [
        _get_gear(item_element, gear_repository)
        for item_element in item_equipment["item_equipment"]
    ]
    return gears


def _get_symbol(symbol_element: CharacterSymbolElement) -> SymbolGear:
    return SymbolGear(
        stat=Stat(
            STR_static=symbol_element["symbol_str"],
            DEX_static=symbol_element["symbol_dex"],
            INT_static=symbol_element["symbol_int"],
            LUK_static=symbol_element["symbol_luk"],
            MHP=symbol_element["symbol_hp"],
        ),
        force=symbol_element["symbol_force"],
    )


def get_symbols(symbol_equipment: CharacterSymbolEquipment) -> list[SymbolGear]:
    return [
        _get_symbol(symbol_element) for symbol_element in symbol_equipment["symbol"]
    ]
