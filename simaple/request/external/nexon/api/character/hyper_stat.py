from typing import Optional, TypedDict, cast

import requests

from simaple.request.external.nexon.api.character.common import (
    CharacterIDWithDate,
    get_nexon_api_header,
)


class HyperStatResponseColumnResponse(TypedDict):
    stat_type: str
    stat_point: Optional[int]
    stat_level: int
    stat_increase: str


class CharacterHyperStatResponse(TypedDict):
    date: str
    character_class: str
    use_preset_no: int
    use_available_hyper_stat: int
    hyper_stat_preset_1: list[HyperStatResponseColumnResponse]
    hyper_stat_preset_1_remain_point: int
    hyper_stat_preset_2: list[HyperStatResponseColumnResponse]
    hyper_stat_preset_2_remain_point: int
    hyper_stat_preset_3: list[HyperStatResponseColumnResponse]
    hyper_stat_preset_3_remain_point: int


def get_hyper_stat(
    host: str, access_token: str, payload: CharacterIDWithDate
) -> CharacterHyperStatResponse:
    return cast(
        CharacterHyperStatResponse,
        requests.get(
            f"{host}/maplestory/v1/character/hyper-stat",
            headers=get_nexon_api_header(access_token),
            params=cast(dict, payload),
            allow_redirects=True,
        ).json(),
    )
