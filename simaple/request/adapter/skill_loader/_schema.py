from typing import TypedDict


class CharacterSkillDescription(TypedDict):
    skill_name: str
    skill_description: str
    skill_level: int
    skill_effect: str
    skill_icon: str
    skill_effect_next: str


class CharacterSkillResponse(TypedDict):
    date: str
    character_class: str
    character_skill_grade: str
    character_skill: list[CharacterSkillDescription]


class AggregatedCharacterSkillResponse(TypedDict):
    response_at_0: CharacterSkillResponse
    response_at_1: CharacterSkillResponse
    response_at_1_and_half: CharacterSkillResponse
    response_at_2: CharacterSkillResponse
    response_at_2_and_half: CharacterSkillResponse
    response_at_3: CharacterSkillResponse
    response_at_4: CharacterSkillResponse
    response_at_hyper_passive: CharacterSkillResponse
    response_at_hyper_active: CharacterSkillResponse
    response_at_5: CharacterSkillResponse
    response_at_6: CharacterSkillResponse



class _HexaStatCore(TypedDict):
    slot_id: str
    main_stat_name: str
    sub_stat_name_1: str
    sub_stat_name_2: str
    main_stat_level: int
    sub_stat_level_1: int
    sub_stat_level_2: int
    stat_grade: int


class HexaStatResponse(TypedDict):
    date: str
    character_class: str
    character_hexa_stat_core: list[_HexaStatCore]  # always length 1
    character_hexa_stat_core_2: list[_HexaStatCore]  # always length 1
    preset_hexa_stat_core: list[_HexaStatCore]
    preset_hexa_stat_core_2: list[_HexaStatCore]
