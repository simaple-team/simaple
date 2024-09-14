from simaple.data.jobs.definitions.skill_improvement import SkillAdditiveImprovement


def test_skill_improvement():
    improvement = SkillAdditiveImprovement.model_validate(
        {
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
            ]
        }
    )

    original = {"name": "x", "f": 10, "g": 20}

    assert {
        "name": "x",
        "f": 20,
        "g": 20,
    } == improvement.modify(original)
