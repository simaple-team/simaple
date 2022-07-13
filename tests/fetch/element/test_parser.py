from simaple.fetch.element.item import StatKeywordProvider
from simaple.core.base import StatProps

import pytest


@pytest.mark.parametrize("name, value, expected", [
    ("INT", "+129 (60 + 20 + 49)", (129, 60, 20, 49))
])
def test_parser(name, value, expected):
    provider = StatKeywordProvider(
        target="INT",
        prop=StatProps.INT,
        value=value,
    )
    _, base, bonus, increment = expected

    assert base == provider.get_base(value)
    assert bonus == provider.get_bonus(value)
    assert increment == provider.get_increment(value)
