from enum import Enum

import pydantic

from simaple.core import Stat
from simaple.request.adapter.gear_loader._schema import PetEquipment, PetResponse


class PetOptionTypes(Enum):
    attack_power = "공격력"
    magic_attack = "마력"
    speed = "이동속도"


class PetItem(pydantic.BaseModel):
    item_name: str
    item_icon: str


def get_pet_equipment_stat_from_equipment_response(pet_equipment: PetEquipment) -> Stat:
    pet_item_stat = Stat()
    for option in pet_equipment["item_option"]:
        match PetOptionTypes(option["option_type"]):
            case PetOptionTypes.attack_power:
                pet_item_stat += Stat(
                    attack_power=option["option_value"],
                )
            case PetOptionTypes.magic_attack:
                pet_item_stat += Stat(
                    magic_attack=option["option_value"],
                )
            case PetOptionTypes.speed:
                pass
            case _:
                raise ValueError(f"Unknown option type: {option['option_type']}")

    return pet_item_stat


def get_pet_equip_stat_from_response(response: PetResponse):
    total_pet_equipment_stat = Stat()
    for i in range(1, 4):
        pet_equipment = response[f"pet_{i}_equipment"]
        if pet_equipment is None:
            continue
        total_pet_equipment_stat += get_pet_equipment_stat_from_equipment_response(
            pet_equipment
        )

    return total_pet_equipment_stat
