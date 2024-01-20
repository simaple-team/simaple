import pytest

from simaple.simulate.report.feature import MaximumDealingIntervalFeature


def test_maximum_interval():
    feature = MaximumDealingIntervalFeature(3)

    sample_damage_seq = [
        (0, 100),
        (1, 100),
        (2, 100),
        (3, 300),
        (4, 200),
        (5, 400),
        (6, 100),
        (7, 100),
    ]

    assert (300.0, 3, 6) == feature._find_maximum_dealing_interval(sample_damage_seq)


def test_duplicated_maximum_interval():
    feature = MaximumDealingIntervalFeature(3)

    sample_damage_seq = [
        (0, 100),
        (1, 100),
        (2, 100),
        (3, 300),
        (3, 300),
        (4, 200),
        (5, 400),
        (5, 300),
        (6, 100),
        (7, 100),
    ]

    assert (500.0, 3, 8) == feature._find_maximum_dealing_interval(sample_damage_seq)


def test_multiple_zone():
    feature = MaximumDealingIntervalFeature(3)

    sample_damage_seq = [
        (0, 100),
        (1, 100),
        (2, 100),
        (3, 300),
        (4, 200),
        (5, 400),
        (6, 100),
        (7, 100),
        (8, 1300),
        (9, 1200),
        (10, 1400),
        (11, 0),
    ]

    assert (1300.0, 8, 11) == feature._find_maximum_dealing_interval(sample_damage_seq)


def test_dynamic_time():
    feature = MaximumDealingIntervalFeature(3)

    sample_damage_seq = [
        (0, 100),
        (1, 100),
        (2.1, 100),
        (2.9, 300),
        (4.1, 200),
        (5, 400),
        (6.1, 100),
        (7, 100),
    ]

    assert (pytest.approx(900 / 3.2), 3, 6) == feature._find_maximum_dealing_interval(
        sample_damage_seq
    )


def test_short_time():
    feature = MaximumDealingIntervalFeature(3)

    sample_damage_seq = [
        (0, 100),
        (1, 100),
        (2.1, 100),
        (3.0, 300),
        (4.1, 200),
        (5, 400),
        (5.9, 100),
        (7, 100),
    ]

    assert (pytest.approx(1000 / 3.8), 2, 6) == feature._find_maximum_dealing_interval(
        sample_damage_seq
    )
