import pytest

from simaple.core import Stat
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements.base import InvalidImprovementException
from simaple.gear.improvements.exceptional_enhancement import ExceptionalEnhancement


def test_exceptional_enhancement(test_gear_repository: GearRepository):
    increment = Stat(attack_power=9, STR=15, INT=15, DEX=15, LUK=15, magic_attack=9)
    enhancement = ExceptionalEnhancement(stat=increment)

    gear = test_gear_repository.get_by_name("루즈 컨트롤 머신 마크")

    assert increment == enhancement.calculate_improvement(gear.meta)


def test_prevent_improper_gear_applies_exceptional_enhancement(
    test_gear_repository: GearRepository,
):
    increment = Stat(attack_power=9, STR=15, INT=15, DEX=15, LUK=15, magic_attack=9)
    enhancement = ExceptionalEnhancement(stat=increment)
    gear = test_gear_repository.get_by_name("하이네스 던위치햇")

    with pytest.raises(InvalidImprovementException):
        enhancement.calculate_improvement(gear.meta)
