from typing import TypedDict, Any


class _LinkSkillDescription(TypedDict):
    skill_name: str
    skill_description: str
    skill_level: int
    skill_effect: str
    skill_icon: str
    skill_effect_next: Any


class LinkSkillResponse(TypedDict):
    date: str
    character_class: str
    character_link_skill: list[_LinkSkillDescription]
    character_link_skill_preset_1: list[_LinkSkillDescription]
    character_link_skill_preset_2: list[_LinkSkillDescription]
    character_link_skill_preset_3: list[_LinkSkillDescription]
    character_owned_link_skill: _LinkSkillDescription
    character_owned_link_skill_preset_1: _LinkSkillDescription
    character_owned_link_skill_preset_2: _LinkSkillDescription
    character_owned_link_skill_preset_3: _LinkSkillDescription
