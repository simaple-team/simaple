from simaple.request.external.nexon.api.character.propensity import (
    CharacterPropensityResponse,
    get_propensity_response,
)
from simaple.request.external.nexon.client import NexonAPIClient
from simaple.request.service.loader import PropensityLoader
from simaple.system.propensity import Propensity


class NexonAPIPropensityLoader(PropensityLoader):
    def __init__(self, client: NexonAPIClient):
        self._client = client

    def load_propensity(self, character_name: str) -> Propensity:
        resp = self._client.session(character_name).request(get_propensity_response)
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
