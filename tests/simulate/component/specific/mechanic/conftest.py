# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.simulate.component.specific.mechanic import RobotMastery
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


@pytest.fixture
def robot_mastery():
    return RobotMastery(
        summon_increment=40,
        robot_damage_increment=5,
        robot_buff_damage_multiplier=100,
    )
