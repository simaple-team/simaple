from simaple.request.adapter.nexon_api import Token, get_character_id
from simaple.request.application.props import (
    get_character_ability,
    get_character_propensity,
)
from simaple.request.converter.ability import get_ability_stat


async def compute_character(
    character_name: str,
    token: Token,
):
    character_id = await get_character_id(token, character_name)

    ability_stat = get_ability_stat(await get_character_ability(token, character_id))

    propensity = await get_character_propensity(token, character_id)

    passive = ...

    def default_extended_stat(self): ...

    def gearset(self): ...

    def hyperstat(self): ...

    def links(self): ...

    def union_squad(self): ...

    def union_occupation(self): ...

    def artifact(self): ...

    def level(self): ...

    def level_stat(self): ...
