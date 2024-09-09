from simaple.core import Stat
from simaple.data.jobs.definitions import (
    MultiplierPassiveHyperskill,
    StatIncreasePassiveHyperskill,
    ValueIncreasePassiveHyperskill,
)


def test_value_increase():
    skill = ValueIncreasePassiveHyperskill(
        name="sample-name-hyper",
        target="sample-name",
        key="prop-key",
        increment=3,
    )

    origin = {"other-key": 4, "prop-key": 4, "not-matching-name": "NAME"}

    assert skill.modify(origin) == {
        "other-key": 4,
        "prop-key": 7,
        "not-matching-name": "NAME",
    }


def test_stat_increase():
    skill = StatIncreasePassiveHyperskill(
        name="sample-name-hyper",
        target="sample-name",
        key="prop-key",
        increment=Stat(
            attack_power=7,
            final_damage_multiplier=50,
        ),
    )

    origin = {
        "other-key": 4,
        "prop-key": {
            "final_damage_multiplier": 50,
        },
        "not-matching-name": "NAME",
    }

    assert skill.modify(origin) == {
        "other-key": 4,
        "prop-key": {"attack_power": 7, "final_damage_multiplier": 125},
        "not-matching-name": "NAME",
    }


def test_value_multiply():
    skill = MultiplierPassiveHyperskill(
        name="sample-name-hyper",
        target="sample-name",
        key="prop-key",
        multiplier=2,
    )

    origin = {"other-key": 4, "prop-key": 4, "not-matching-name": "NAME"}

    assert skill.modify(origin) == {
        "other-key": 4,
        "prop-key": 8,
        "not-matching-name": "NAME",
    }
