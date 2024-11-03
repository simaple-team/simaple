import datetime
from typing import Any, Callable, TypeVar, cast

from simaple.request.external.nexon.api.character.common import (
    CharacterIDWithDate,
    get_character_ocid,
)

T = TypeVar("T")
PayloadT = TypeVar("PayloadT", bound=CharacterIDWithDate)


def as_nexon_datetime(date: datetime.date) -> str:
    return date.strftime("%Y-%m-%d")


class NexonAPIAuthenticatedSession:
    def __init__(self, host: str, access_token: str, ocid: str, date: datetime.date):
        self._host = host
        self._access_token = access_token
        self._ocid = ocid
        self._date = date

    def request(
        self,
        request: Callable[[str, str, PayloadT], T],
        payload: dict[str, Any] | None = None,
    ) -> T:
        payload = payload or {}
        _payload = {
            "ocid": self._ocid,
            "date": as_nexon_datetime(self._date),
        }
        for key, value in payload.items():
            _payload[key] = value

        return request(self._host, self._access_token, cast(PayloadT, _payload))


class NexonAPIClient:
    def __init__(self, host: str, access_token: str, date: datetime.date):
        self._host = host
        self._access_token = access_token
        self._date = date

    def session(self, character_name: str) -> NexonAPIAuthenticatedSession:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        return NexonAPIAuthenticatedSession(
            self._host, self._access_token, ocid, self._date
        )
