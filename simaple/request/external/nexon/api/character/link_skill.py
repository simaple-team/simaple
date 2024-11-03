from typing import Any, TypedDict, cast

import requests

from simaple.request.external.nexon.api.character.common import (
    CharacterIDWithDate,
    get_nexon_api_header,
)


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


def get_link_skill(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> LinkSkillResponse:
    return cast(
        LinkSkillResponse,
        requests.get(
            f"{host}/maplestory/v1/character/link-skill",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )
