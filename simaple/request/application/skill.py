from enum import Enum
from typing import cast

from simaple.request.application.base import (
    HOST,
    CharacterID,
    Token,
    get_character_id_param,
)
from simaple.request.schema.character import CharacterPropensity


class SkillOrder(Enum):
    zero: str = "0"
    first: str = "1"
    first_point_five: str = "1.5"
    second: str = "2"
    second_point_five: str = "2.5"
    third: str = "3"
    fourth: str = "4"
    hyperpassive: str = "hyperpassive"
    hyperactive: str = "hyperactive"
    fifth: str = "5"
    sixth: str = "6"


async def get_character_skill(
    token: Token, character_id: CharacterID, order: SkillOrder | str
) -> CharacterPropensity:
    if isinstance(order, SkillOrder):
        order = order.value

    uri = f"{HOST}/maplestory/v1/character/skill"

    param = get_character_id_param(character_id)

    param["character_skill_grade"] = order
    resp = await token.request(uri, param)
    return cast(CharacterPropensity, resp)
