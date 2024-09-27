import pytest

from simaple.spec._math import evaluate_expression


@pytest.mark.parametrize(
    "arithmetic_expr, variables, expected",
    [
        (
            "3 + 4 * (2 - 1) / 5",
            {},
            3.8,
        ),
        (
            "val + 4 * (2 - 1) / 5",
            {"val": 3},
            3.8,
        ),
        ("(35 + skill_level // 2) * 0.01", {"skill_level": 31}, 0.5),
        ("min(35, 15) * 0.01", {}, 0.15),
        ("min(15, 45) * 0.01", {}, 0.15),
        (
            "(200 + skill_level * 3) * (1 - 0.01 * (10 + skill_level // 3)) + (300 + skill_level * 3) * 0.01 * (10 + skill_level // 3)",
            {"skill_level": 30},
            310,
        ),
        (
            "min(character_stat.INT // 2500, 15 + skill_level)",
            {"character_stat.INT": 30000, "skill_level": 10},
            12,
        ),
        (
            "ceil(3 + 4 * (2 - 1) / 5)",
            {"character_stat.INT": 30000, "skill_level": 10},
            4,
        ),
        (
            "apply_attack_speed(180)",
            {},
            150,
        ),
        (
            "apply_attack_speed(240)",
            {},
            180,
        ),
        (
            "apply_attack_speed(600)",
            {},
            450,
        ),
        (
            "apply_attack_speed(620)",
            {},
            480,
        ),
    ],
)
def test_math_expr(arithmetic_expr, variables, expected):
    result = evaluate_expression(arithmetic_expr, variables)
    assert pytest.approx(result) == expected
