import pytest

from simaple.spec.patch import ArithmeticPatch


@pytest.mark.parametrize(
    "target, expected",
    [
        ("no-match", "no-match"),
        ("{{ level }}", 3),
        ("{{ level * 4 + 5 }}", 17),
        ({"nested": "value", "a": 3}, {"nested": "value", "a": 3}),
        ({"nested": "{{ level }}", "a": 3}, {"nested": 3, "a": 3}),
        ({"nested": "{{ string_inject }}", "a": 3}, {"nested": "string", "a": 3}),
        ({"nested": "{{ level + arg }}", "a": 3}, {"nested": 7, "a": 3}),
    ],
)
def test_eval_patch(target, expected):
    inject = {"level": 3, "string_inject": "string", "arg": 4}

    patch = ArithmeticPatch(injected_values=inject)
    assert patch.apply(target) == expected
