from loguru import logger

from simaple.core import ExtendedStat, Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.symbol_gear import SymbolGear
from simaple.request.adapter.gear_loader._schema import (
    CharacterItemElement,
    CharacterItemElementOption,
    CharacterItemEquipment,
    CharacterSymbolElement,
    CharacterSymbolEquipment,
)
from simaple.request.adapter.translator.kms.potential import kms_potential_translator

from simaple.gear.gearset import Gearset
from simaple.gear.slot_name import SlotName
from simaple.request.adapter.gear_loader._schema import PetEquipment, PetResponse
from simaple.request.adapter.gear_loader._pet_converter import get_pet_equip_stat_from_response
from simaple.request.adapter.gear_loader._converter import get_equipments, get_symbols


_kr_slotname_to_slotname = {
    "모자": SlotName.cap,
    "상의": SlotName.coat,
    "하의": SlotName.pants,
    "망토": SlotName.cape,
    "장갑": SlotName.glove,
    "신발": SlotName.shoes,
    "반지1": SlotName.ring1,
    "반지2": SlotName.ring2,
    "반지3": SlotName.ring3,
    "반지4": SlotName.ring4,
    "펜던트": SlotName.pendant1,
    "펜던트2": SlotName.pendant2,
    "얼굴장식": SlotName.face_accessory,
    "눈장식": SlotName.eye_accessory,
    "귀고리": SlotName.earrings,
    "어깨장식": SlotName.shoulder_pad,
    "뱃지": SlotName.badge,
    "벨트": SlotName.belt,
    "훈장": SlotName.medal,
    "무기": SlotName.weapon,
    "보조무기": SlotName.subweapon,
    "엠블렘": SlotName.emblem,
    "포켓 아이템": SlotName.pocket,
    "기계 심장": SlotName.machine_heart,
}


def _get_title_stat(title_name: str, title_description: str) -> ExtendedStat:
    if title_name == "예티X핑크빈":
        return ExtendedStat(
            stat=Stat(
                attack_power=10,
                magic_attack=10,
                boss_damage_multiplier=10,
            )
        )

    raise NotImplementedError(f"Title {title_name} not implemented")


def get_gearset(
    item_equipment: CharacterItemEquipment,
    symbol_equipment: CharacterSymbolEquipment,
    pet_response: PetResponse,
    gear_repository: GearRepository,
) -> Gearset:
    item_gears = get_equipments(item_equipment, gear_repository)
    symbols = get_symbols(symbol_equipment)

    gearset = Gearset()
    for gear, kr_slotname in item_gears:
        gearset.equip(gear, _kr_slotname_to_slotname[kr_slotname])

    gearset.set_symbols(symbols)

    ### below may imple.

    gearset.set_title_stat(
        _get_title_stat(
            item_equipment["title"]["title_name"],
            item_equipment["title"]["title_description"],
        ).stat
    )

    # gearset.annotate_weapon_potential_tiers(self.weapon_potential_tiers)
    gearset.set_pet_equip_stat(get_pet_equip_stat_from_response(pet_response))

    # TODO
    """
    gearset.set_pet_set_option(self.pet_set)
    gearset.set_cash_item_stat(self.cash)

    gearset.set_set_items(set_item_repository.get_all(gearset.get_gears()))

    return gearset
    """
    return gearset
