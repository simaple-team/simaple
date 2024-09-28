from typing import TypedDict


class PetOptionValueAndType(TypedDict):
    option_type: str
    option_value: int


class PetEquipment(TypedDict):
    item_name: str
    item_icon: str
    item_description: str
    item_option: list[PetOptionValueAndType]
    scroll_upgrade: int
    scroll_upgradable: int
    item_shape: str
    item_shape_icon: str


class PetSkill(TypedDict):
    skill_1: str | None
    skill_1_icon: str | None
    skill_2: str | None
    skill_2_icon: str | None


class PetResponse(TypedDict):
    date: str
    pet_1_name: str
    pet_1_nickname: str
    pet_1_icon: str
    pet_1_description: str
    pet_1_equipment: PetEquipment
    pet_1_auto_skill: PetSkill
    pet_1_pet_type: str
    pet_1_skill: list[str]
    pet_1_date_expire: str
    pet_1_appearance: str
    pet_1_appearance_icon: str

    pet_2_name: str
    pet_2_nickname: str
    pet_2_icon: str
    pet_2_description: str
    pet_2_equipment: PetEquipment
    pet_2_auto_skill: PetSkill
    pet_2_pet_type: str
    pet_2_skill: list[str]
    pet_2_date_expire: str
    pet_2_appearance: str
    pet_2_appearance_icon: str

    pet_3_name: str
    pet_3_nickname: str
    pet_3_icon: str
    pet_3_description: str
    pet_3_equipment: PetEquipment
    pet_3_auto_skill: PetSkill
    pet_3_pet_type: str
    pet_3_skill: list[str]
    pet_3_date_expire: str
    pet_3_appearance: str
    pet_3_appearance_icon: str




