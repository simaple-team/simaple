# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.simulate.kms import get_client


@pytest.fixture
def dualblade_client():
    return get_client(
        ActionStat(),
        ["dualblade", "common", "adventurer.thief", "luk_based", "thief"],
        {
            "character_level": 260,
            "weapon_attack_power": 700,
            "weapon_pure_attack_power": 295,
        },
        {},
        {},
    )
