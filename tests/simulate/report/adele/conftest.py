# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.simulate.kms import get_client


@pytest.fixture
def adele_client():
    return get_client(
        ActionStat(),
        ["adele", "common", "flora", "str_based", "warrior"],
        {
            "character_level": 260,
            "weapon_attack_power": 700,
            "weapon_pure_attack_power": 295,
        },
        {},
        {},
    )
