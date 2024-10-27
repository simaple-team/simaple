import datetime
from typing import TypedDict, cast

import requests


def _get_nexon_api_header(access_token: str):
    return {
        "X-Nxopen-Api-Key": access_token,
        "Accept": "application/json",
    }


def as_nexon_datetime(date: datetime.date) -> str:
    return date.strftime("%Y-%m-%d")


class CharacterIDWithDate(TypedDict):
    ocid: str
    date: str


def get_character_ocid(
    host: str,
    access_token: str,
    name: str,
) -> str:
    resp = requests.get(
        f"{host}/maplestory/v1/id",
        headers=_get_nexon_api_header(access_token),
        params={"character_name": name},
        allow_redirects=True,
    ).json()

    return cast(str, resp["ocid"])
