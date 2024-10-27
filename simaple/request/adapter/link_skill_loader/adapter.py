import datetime

from simaple.data.system.link import get_all_linkskills
from simaple.request.external.nexon.api.character.link_skill import (
    LinkSkillResponse,
    get_link_skill,
)
from simaple.request.external.nexon.api.ocid import (
    as_nexon_datetime,
    get_character_ocid,
)
from simaple.request.service.loader import LinkSkillLoader
from simaple.system.link import LinkSkillset


class NexonAPILinkSkillLoader(LinkSkillLoader):
    def __init__(self, host: str, access_token: str, date: datetime.date):
        self._host = host
        self._access_token = access_token
        self._date = date

    def load_link_skill(self, character_name: str) -> LinkSkillset:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        resp = get_link_skill(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
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
