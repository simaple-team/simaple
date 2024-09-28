from simaple.request.adapter.propensity_loader.adapter import get_propensity
from simaple.system.propensity import Propensity


def test_propensity_response(character_propensity_response):
    propensity = get_propensity(character_propensity_response)

    assert propensity == Propensity(
        ambition=100,
        insight=100,
        empathy=100,
        willpower=73,
        diligence=66,
        charm=58,
    )
