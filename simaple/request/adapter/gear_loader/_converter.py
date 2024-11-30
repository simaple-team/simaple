from loguru import logger

from simaple.core import Stat
from simaple.core.base import AttackType
from simaple.data.baseline.patch import kms_weapon_alias
from simaple.gear.compute.bonus import BonusCalculator
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements.bonus import AttackTypeBonus
from simaple.gear.improvements.starforce import Starforce
from simaple.gear.symbol_gear import SymbolGear
from simaple.request.adapter.gear_loader._potential_converter import (
    get_potential,
    translate_kms_potential_pattern,
)
from simaple.request.external.nexon.api.character.item import (
    CharacterItemElement,
    CharacterItemElementOption,
    CharacterItemEquipment,
    CharacterSymbolElement,
    CharacterSymbolEquipment,
    OptionValueAndType,
)


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
    ) + Stat.all_stat_multiplier(item_option.get("all_stat", 0))


def _get_gear(
    item_element: CharacterItemElement, gear_repository: GearRepository
) -> Gear:
    base_gear = gear_repository.get_by_name(item_element["item_name"])
    if base_gear.meta.base_stat != _get_stat(item_element["item_base_option"]):
        logger.warning(
            f"Item {base_gear.meta.name} stat not matched. Maybe special item?"
        )

    base_gear = Gear(
        meta=base_gear.meta,
        stat=_get_stat(item_element["item_base_option"]),
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
        get_potential(
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
        get_potential(
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

    # soul option
    if item_element["soul_option"] is not None:
        base_gear = base_gear.add_stat(
            translate_kms_potential_pattern(item_element["soul_option"]).stat
        )

    return base_gear


def get_equipments(
    item_equipment: CharacterItemEquipment, gear_repository: GearRepository
) -> list[tuple[Gear, str]]:
    gears = [
        (_get_gear(item_element, gear_repository), item_element["item_equipment_slot"])
        for item_element in item_equipment["item_equipment"]
    ]
    return gears


def _get_regularized_weapon(
    weapon_name: str, add_option: Stat, starforce: int, etc_option: Stat
):
    gear_repository = GearRepository()
    calculator = BonusCalculator()

    weapon_class = f"{weapon_name.split()[0]} 무기"
    weapon = gear_repository.get_by_name(weapon_name)
    reference_weapon = gear_repository.get_by_name(
        kms_weapon_alias()[weapon_class]["bowmaster"]
    )

    bonuses = calculator.compute(add_option, weapon)
    uses_magic = weapon.meta.base_stat.magic_attack > 0

    my_weapon_attack_ref = (
        weapon.meta.base_stat.magic_attack
        if uses_magic
        else weapon.meta.base_stat.attack_power
    )
    reference_weapon_attack_ref = reference_weapon.meta.base_stat.attack_power
    delta = reference_weapon_attack_ref - my_weapon_attack_ref
    base_stat_delta = (
        Stat(magic_attack=delta) if uses_magic else Stat(attack_power=delta)
    )
    weapon = weapon.add_stat(base_stat_delta)

    weapon = weapon.add_stat(etc_option)
    improvement = Starforce(star=starforce).calculate_improvement(
        weapon.meta, weapon.sum_stat()
    )
    weapon = weapon.add_stat(improvement)

    attack_power_bonus = 0
    for bonus in bonuses:
        if not isinstance(bonus, AttackTypeBonus):
            continue

        bonus.attack_type = AttackType.attack_power
        attack_power_bonus = bonus.calculate_improvement(
            reference_weapon.meta
        ).attack_power

    if uses_magic:
        add_option = add_option + Stat(
            magic_attack=(attack_power_bonus - add_option.magic_attack)
        )
    else:
        add_option = add_option + Stat(
            attack_power=(attack_power_bonus - add_option.attack_power)
        )

    weapon = weapon.add_stat(add_option)
    return weapon


def get_weapon_replacement(
    item_equipment: CharacterItemEquipment, gear_repository: GearRepository
) -> Stat:
    gear_response = [
        equipment
        for equipment in item_equipment["item_equipment"]
        if equipment["item_equipment_slot"] == "무기"
    ]
    assert len(gear_response) == 1, "Only one weapon is allowed"
    weapon_item_element = gear_response[0]

    original_weapon = _get_gear(weapon_item_element, gear_repository)
    regularized_weapon = _get_regularized_weapon(
        weapon_item_element["item_name"],
        _get_stat(weapon_item_element["item_add_option"]),
        weapon_item_element["starforce"],
        _get_stat(weapon_item_element["item_etc_option"]),
    )

    return Stat(
        attack_power=regularized_weapon.stat.attack_power
        - original_weapon.stat.attack_power,
        magic_attack=regularized_weapon.stat.magic_attack
        - original_weapon.stat.magic_attack,
        INT=regularized_weapon.stat.INT - original_weapon.stat.INT,
        DEX=regularized_weapon.stat.DEX - original_weapon.stat.DEX,
        STR=regularized_weapon.stat.STR - original_weapon.stat.STR,
        LUK=regularized_weapon.stat.LUK - original_weapon.stat.LUK,
    )


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


def get_stat_from_option_value_and_type(
    option_value_and_type: OptionValueAndType,
) -> Stat:
    option_type = option_value_and_type["option_type"]
    option_value = option_value_and_type["option_value"]

    match option_type:
        case "공격력":
            return Stat(
                attack_power=option_value,
            )
        case "마력":
            return Stat(
                magic_attack=option_value,
            )
        case "이동속도":
            return Stat()
        case "올스탯":
            return Stat.all_stat(option_value)
        case "STR":
            return Stat(STR=option_value)
        case "DEX":
            return Stat(DEX=option_value)
        case "INT":
            return Stat(INT=option_value)
        case "LUK":
            return Stat(LUK=option_value)
        case "HP":
            return Stat(MHP=option_value)
        case "MP":
            return Stat(MMP=option_value)
        case "방어력":
            return Stat()
        case "점프력":
            return Stat()
        case _:
            raise ValueError(f"Unknown option type: {option_type}")
