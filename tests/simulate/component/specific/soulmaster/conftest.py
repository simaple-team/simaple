import pytest

import simaple.simulate.component.skill  # noqa: F401
import simaple.simulate.component.specific  # noqa: F401
from simaple.core.base import ActionStat
from simaple.simulate.global_property import Dynamics


@pytest.fixture
def dynamics():
    return Dynamics(
        stat=ActionStat(
            buff_duration=20,
            cooltime_reduce=0,
            summon_duration=40,
            cooltime_reduce_rate=5.0,
        )
    )
