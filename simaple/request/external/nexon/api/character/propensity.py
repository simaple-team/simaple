from typing import TypedDict, cast

import requests

from simaple.request.external.nexon.api.character.common import (
    CharacterIDWithDate,
    get_nexon_api_header,
)


class CharacterPropensityResponse(TypedDict):
    date: str
    charisma_level: int
    sensibility_level: int
    insight_level: int
    willingness_level: int
    handicraft_level: int
    charm_level: int


def get_propensity_response(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterPropensityResponse:
    return cast(
        CharacterPropensityResponse,
        requests.get(
            f"{host}/maplestory/v1/character/propensity",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )
