import pytest

from simaple.benchmark.interpreter import (
    BenchmarkConfigurationInterpreter,
    BenchmarkInterpreterOption,
)
from simaple.core import BaseStatType, JobCategory, JobType, Stat
from simaple.core.damage import STRBasedDamageLogic
from simaple.gear.gear_repository import GearRepository
from simaple.gear.potential import Potential, PotentialTier
from simaple.preset.base import PresetOptimizer


def test_empty_preset():
    preset = Preset()

    assert preset.get_total_stat() == Stat()
