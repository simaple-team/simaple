import pytest

from simaple.core.base import ActionStat
from simaple.simulate.global_property import Dynamics


@pytest.fixture
def dynamics():
    return Dynamics(stat=ActionStat())
