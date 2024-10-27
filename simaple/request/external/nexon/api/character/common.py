from typing import TypedDict


class CharacterIDWithDate(TypedDict):
    ocid: str
    date: str


def get_nexon_api_header(access_token: str):
    return {
        "X-Nxopen-Api-Key": access_token,
        "Accept": "application/json",
    }
