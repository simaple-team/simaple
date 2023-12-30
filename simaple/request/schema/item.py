from typing import TypedDict

IntStat = int  # use this since "int" option in included in CharacterItemElementOption


class CharacterItemElementOption(TypedDict, total=False):
    str: IntStat
    dex: IntStat
    int: IntStat
    luk: IntStat
    max_hp: IntStat
    max_mp: IntStat
    attack_power: IntStat
    magic_power: IntStat
    armor: IntStat
    speed: IntStat
    jump: IntStat
    boss_damage: IntStat
    ignore_monster_armor: IntStat
    all_stat: IntStat
    damage: IntStat
    equipment_level_decrease: IntStat
    max_hp_rate: IntStat
    max_mp_rate: IntStat


class CharacterItemElement(TypedDict):
    item_equipment_part: str
    item_equipment_slot: str
    item_name: str
    item_icon: str
    item_description: str | None
    item_shape_name: str
    item_shape_icon: str
    item_gender: str | None

    item_total_option: CharacterItemElementOption
    item_base_option: CharacterItemElementOption

    potential_option_grade: str | None
    additional_potential_option_grade: str | None
    potential_option_1: str | None
    potential_option_2: str | None
    potential_option_3: str | None
    additional_potential_option_1: str | None
    additional_potential_option_2: str | None
    additional_potential_option_3: str | None

    equipment_level_increase: int

    item_exceptional_option: CharacterItemElementOption
    item_add_option: CharacterItemElementOption

    growth_exp: int
    growth_level: int

    scroll_upgrade: int
    cuttable_count: int
    golden_hammer_flag: str
    scroll_resilience_count: int
    scroll_upgradeable_count: int
    soul_name: str | None
    soul_option: str | None

    item_etc_option: CharacterItemElementOption
    starforce: int
    starforce_scroll_flag: str
    item_starforce_option: CharacterItemElementOption

    special_ring_level: int  # 시드링 레벨
    date_expire: str | None


class CharacterItemTitleElement(TypedDict):
    title_name: str
    title_icon: str
    title_description: str
    date_expire: str | None
    date_option_expire: str | None


class CharacterItemEquipment(TypedDict):
    item_equipment: list[CharacterItemElement]
    date: str
    character_gender: str
    character_class: str
    title: CharacterItemTitleElement
    dragon_equipment: list[CharacterItemElement]
    mechanic_equipment: list[CharacterItemElement]


class CharacterSymbolElement(TypedDict):
    symbol_name: str
    symbol_icon: str
    symbol_description: str
    symbol_force: int
    symbol_level: int
    symbol_str: int
    symbol_dex: int
    symbol_int: int
    symbol_luk: int
    symbol_hp: int
    symbol_growth_count: int
    symbol_require_growth_count: int


class CharacterSymbolEquipment(TypedDict):
    date: str
    character_class: str
    symbol: list[CharacterSymbolElement]
