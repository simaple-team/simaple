import datetime
from typing import Any, TypedDict, cast

import requests

HOST = "https://open.api.nexon.com"


class CharacterID(TypedDict):
    ocid: str
    date: datetime.date


def nexon_today() -> str:
    return (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")


def get_character_id_param(character_id: CharacterID) -> dict:
    return {
        "ocid": character_id["ocid"],
        "date": character_id["date"].strftime("%Y-%m-%d"),
    }


def as_python_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, "%Y-%m-%d%H:%M:%S+09:00")


class NexonRequestPayload(TypedDict): ...


class NexonRequestAgent:
    def __init__(self, host: str, token_value: str):
        self._token = Token(token_value)
        self._host = host

    def request(self, uri: str, param: NexonRequestPayload) -> dict:
        return self._token.request(f"{self._host}/{uri}", cast(dict, param))


class Token:
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    @property
    def access_token(self) -> str:
        return self._access_token

    def request(self, uri: str, param: dict[str, Any]) -> dict:
        resp = requests.get(
            f"{uri}",
            headers={
                "X-Nxopen-Api-Key": self._access_token,
                "Accept": "application/json",
            },
            params=param,
            allow_redirects=True,
        )
        return cast(dict, resp.json())


def get_character_id(
    token: Token, name: str, date: datetime.date | None = None
) -> CharacterID:
    if date is None:
        date = datetime.date.today() - datetime.timedelta(days=2)

    uri = f"{HOST}/maplestory/v1/id"

    resp = token.request(uri, {"character_name": name})
    return {
        "ocid": resp["ocid"],
        "date": date,
    }
