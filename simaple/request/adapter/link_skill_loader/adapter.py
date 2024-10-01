from simaple.request.adapter.nexon_api import (
    HOST,
    Token,
    get_character_id,
    get_character_id_param,
)
from typing import cast

from simaple.request.service.loader import LinkSkillLoader
from simaple.system.link import LinkSkill, LinkSkillset
from simaple.request.adapter.link_skill_loader._schema import LinkSkillResponse
from simaple.data.system.link import get_all_linkskills


class NexonAPILinkSkillLoader(LinkSkillLoader):
    def __init__(self, token_value: str):
        self._token = Token(token_value)

    def load_link_skill(self, character_name: str) -> LinkSkillset:
        character_id = get_character_id(self._token, character_name)
        uri = f"{HOST}/maplestory/v1/user/link-skill"
        resp = cast(
            LinkSkillResponse,
            self._token.request(uri, get_character_id_param(character_id)),
        )
        return get_link_skillset(resp)


def get_link_skillset(resp: LinkSkillResponse) -> LinkSkillset:
    link_skill_list: list[tuple[str, int]] = [
        (skill["skill_name"], skill["skill_level"])
        for skill in resp["character_link_skill"]
    ]

    every_link_skills = get_all_linkskills()
    link_skill_map = {link_skill.name: link_skill for link_skill in every_link_skills}
    link_levels, links = [], []

    for skill_name, skill_level in link_skill_list:
        if skill_name in link_skill_map:
            link_levels.append(skill_level)
            links.append(link_skill_map[skill_name])
        else:
            raise ValueError(f"Unknown link skill: {skill_name}")

    return LinkSkillset(link_levels=link_levels, links=links)
