from typing import cast

from simaple.request.adapter.nexon_api import (
    HOST,
    Token,
    get_character_id,
    get_character_id_param,
)
from simaple.request.adapter.propensity_loader._schema import (
    CharacterPropensityResponse,
)
from simaple.request.service.loader import PropensityLoader
from simaple.system.propensity import Propensity


class NexonAPIPropensityLoader(PropensityLoader):
    def __init__(self, token_value: str):
        self._token = Token(token_value)

    def load_propensity(self, character_name: str) -> Propensity:
        character_id = get_character_id(self._token, character_name)
        uri = f"{HOST}/maplestory/v1/character/propensity"
        resp = cast(
            CharacterPropensityResponse,
            self._token.request(uri, get_character_id_param(character_id)),
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
