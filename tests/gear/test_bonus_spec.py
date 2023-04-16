import pytest
from pydantic import ValidationError

from simaple.gear.blueprint.gear_blueprint import BonusSpec
from simaple.gear.bonus_factory import BonusFactory, BonusType


def test_bonus_spec_block_grade_and_rank_given_together():
    with pytest.raises(ValueError):
        _ = BonusSpec(bonus_type=BonusType.all_stat_multiplier, grade=6, rank=2)


@pytest.mark.parametrize("value", [0, 8])
def test_bonus_spec_prevent_value_out_of_range(value):
    with pytest.raises(ValidationError):
        _ = BonusSpec(
            bonus_type=BonusType.all_stat_multiplier,
            grade=value,
        )
