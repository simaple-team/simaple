import pydantic

from simaple.core import Stat
from simaple.request.adapter.gear_loader._converter import (
    get_stat_from_option_value_and_type,
)
from simaple.request.external.nexon.api.character.item import PetEquipment, PetResponse


class PetItem(pydantic.BaseModel):
    item_name: str
    item_icon: str


def get_pet_equipment_stat_from_equipment_response(pet_equipment: PetEquipment) -> Stat:
    pet_item_stat = Stat()
    for option in pet_equipment["item_option"]:
        pet_item_stat += get_stat_from_option_value_and_type(option)

    return pet_item_stat


def get_pet_equip_stat_from_response(response: PetResponse) -> Stat:
    total_pet_equipment_stat = Stat()
    for i in range(1, 4):
        pet_equipment: PetEquipment = response[f"pet_{i}_equipment"]  # type: ignore[literal-required]
        if pet_equipment is None:
            continue
        total_pet_equipment_stat += get_pet_equipment_stat_from_equipment_response(
            pet_equipment
        )

    return total_pet_equipment_stat
