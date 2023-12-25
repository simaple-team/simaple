from simaple.request.schema.character import CharacterPropensity
from simaple.system.propensity import Propensity


def get_propensity(propensity_response: CharacterPropensity):
    return Propensity(
        ambition=propensity_response["charisma_level"],
        insight=propensity_response["insight_level"],
        empathy=propensity_response["sensibility_level"],
        willpower=propensity_response["willingness_level"],
        diligence=propensity_response["handicraft_level"],
        charm=propensity_response["charm_level"],
    )
