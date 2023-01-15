# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
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
