# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.simulate.kms import get_client


@pytest.fixture
def mechanic_client():
    return get_client(
        ActionStat(),
        ["mechanic", "common", "resistance", "pirate"],
        {
            "character_level": 260,
            "weapon_pure_attack_power": 500,
        },
        {},
        {},
    )
