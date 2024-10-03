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
