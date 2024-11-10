import pytest

from simaple.data.jobs.definitions.skill_improvement import SkillAdditiveImprovement
from simaple.data.jobs.patch import SkillImprovementPatch


def test_skill_improvement():
    improvement = SkillAdditiveImprovement.model_validate(
        {
            "name": "VV",
            "advantages": [
                {
                    "target_name": "x",
                    "target_field": "f",
                    "value": 10,
                },
                {
                    "target_name": "y",
                    "target_field": "f",
                    "value": 10,
                },
            ],
        }
    )

    original = {"name": "x", "f": 10, "g": 20}

    assert {
        "name": "x",
        "f": 20,
        "g": 20,
    } == improvement.modify(original)


def test_skill_improvement_fails_when_not_applied():
    improvement = SkillAdditiveImprovement.model_validate(
        {
            "name": "VV",
            "advantages": [
                {
                    "target_name": "x",
                    "target_field": "f",
                    "value": 10,
                },
                {
                    "target_name": "y",
                    "target_field": "f",
                    "value": 10,
                },
            ],
        }
    )

    patch = SkillImprovementPatch(improvements=[improvement])

    original = {"name": "z", "f": 10, "g": 20}

    with pytest.raises(ValueError):
        patch.apply(original)
