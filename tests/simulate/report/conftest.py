import os
import pathlib

import pytest

from simaple.core import Stat


@pytest.fixture
def character_stat():
    return Stat.parse_file(pathlib.Path(os.path.dirname(__file__)) / "legendary_magician.json")
