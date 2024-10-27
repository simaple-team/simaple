import datetime

from simaple.request.external.nexon.api.character.propensity import (
    CharacterPropensityResponse,
    get_propensity_response,
)
from simaple.request.external.nexon.api.ocid import (
    as_nexon_datetime,
    get_character_ocid,
)
from simaple.request.service.loader import PropensityLoader
from simaple.system.propensity import Propensity


class NexonAPIPropensityLoader(PropensityLoader):
    def __init__(self, host: str, access_token: str, date: datetime.date):
        self._host = host
        self._access_token = access_token
        self._date = date

    def load_propensity(self, character_name: str) -> Propensity:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        resp = get_propensity_response(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )
        return get_propensity(resp)


def get_propensity(propensity_response: CharacterPropensityResponse) -> Propensity:
    return Propensity(
        ambition=propensity_response["charisma_level"],
        insight=propensity_response["insight_level"],
        empathy=propensity_response["sensibility_level"],
        willpower=propensity_response["willingness_level"],
        diligence=propensity_response["handicraft_level"],
        charm=propensity_response["charm_level"],
    )
