# pylint: disable=W0621
import pytest

import simaple.simulate.component.common  # noqa: F401
import simaple.simulate.component.specific  # noqa: F401
from simaple.core.base import ActionStat
from simaple.simulate.component.entity import Periodic
from simaple.simulate.component.specific.archmagetc import FrostEffect
from simaple.simulate.global_property import Dynamics, GlobalProperty


@pytest.fixture
def global_property():
    return GlobalProperty(
        ActionStat(
            buff_duration=185,
            cooltime_reduce=2_000,
            summon_duration=40,
            cooltime_reduce_rate=5.0,
        )
    )


@pytest.fixture
def dynamics():
    return Dynamics(
        stat=ActionStat(
            buff_duration=185,
            cooltime_reduce=2_000,
            summon_duration=40,
            cooltime_reduce_rate=5.0,
        )
    )


@pytest.fixture
def jupyter_thunder_periodic():
    return Periodic(interval=120)


@pytest.fixture
def frost_effect():
    return FrostEffect(
        id="dummy",
        name="프로스트 이펙트",
        critical_damage_per_stack=3,
        maximum_stack=5,
    )


@pytest.fixture
def frost_effect_state(frost_effect: FrostEffect):
    return frost_effect.get_default_state()
