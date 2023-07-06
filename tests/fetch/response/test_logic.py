import json

import pytest
from loguru import logger

from simaple.core import BaseStatType, JobType
from simaple.fetch.inference.attack_logic import predicate_attack_factor
from simaple.fetch.inference.builtin_settings import get_predefined_setting
from simaple.fetch.inference.logic import infer_stat
from simaple.fetch.inference.stat_logic import predicate_stat, predicate_stat_factor
from simaple.fetch.response.character import CharacterResponse
from simaple.fetch.translator.gear import GearTranslator
from simaple.fetch.translator.kms.gear import kms_gear_stat_translator
from simaple.fetch.translator.kms.potential import kms_potential_translator
from simaple.gear.gear_repository import GearRepository


def _get_file_path(file_name: str) -> str:
    return f"tests/fetch/response/dumped/{file_name}"


def _get_response(file_name: str) -> CharacterResponse:
    with open(file_name, encoding="utf-8") as f:
        raw = json.load(f)

    return CharacterResponse(
        raw,
        GearTranslator(
            gear_stat_translator=kms_gear_stat_translator(),
            potential_translator=kms_potential_translator(),
            gear_repository=GearRepository(),
        ),
    )


@pytest.fixture(name="new_data")
def fixture_new_data():
    return _get_response(_get_file_path("archmagefp2.json"))


def test_attack_predication(new_data):
    logger.disable("")

    setting = get_predefined_setting(JobType.archmagefb)
    result = predicate_attack_factor(new_data, setting)

    assert [v for v, score in result][0] == (96.0, 126.0, 3316)


def test_luminous():
    logger.disable("")

    setting = get_predefined_setting(JobType.luminous)
    result = predicate_attack_factor(
        _get_response(_get_file_path("luminous.json")), setting
    )

    assert result[0][0] == (77.0, 18.0, 827)


def test_infinity_triggered_predication():
    logger.disable("")

    setting = get_predefined_setting(JobType.archmagefb)
    results = predicate_attack_factor(
        _get_response(_get_file_path("archmagefp.json")), setting
    )

    assert results[0][0] == (96.0, 126.0, 3366)


@pytest.mark.parametrize(
    "filename",
    [
        _get_file_path("ilium.json"),
        _get_file_path("bishop.json"),
        _get_file_path("windbreaker.json"),
    ],
)
def test_from_dumped(filename):
    logger.disable("")

    response = _get_response(filename)
    setting = get_predefined_setting(response.get_jobtype())

    results = predicate_attack_factor(response, setting)
    assert len(results) > 0


def test_stat():
    logger.disable("")

    setting = get_predefined_setting(JobType.archmagefb)
    results = predicate_stat_factor(
        _get_response(_get_file_path("archmagefp2.json")),
        setting,
        270,
        BaseStatType.INT,
    )

    assert results[0][0] == (5902, 560, 20290)


def test_full_stat_predication():
    logger.disable("")

    setting = get_predefined_setting(JobType.archmagefb)
    results = predicate_stat(
        _get_response(_get_file_path("archmagefp2.json")),
        setting,
        270,
        size=1,
    )

    best_result = results[0][0]

    assert best_result.short_dict() == {
        "STR": 1704.0,
        "LUK": 2771.0,
        "INT": 5902.0,
        "DEX": 1707.0,
        "STR_multiplier": 175.0,
        "LUK_multiplier": 180.0,
        "INT_multiplier": 560.0,
        "DEX_multiplier": 173.0,
        "STR_static": 660.0,
        "LUK_static": 480.0,
        "INT_static": 20290.0,
        "DEX_static": 420.0,
    }


def test_full_stat_predication2():
    logger.disable("")

    setting = get_predefined_setting(JobType.windbreaker)
    results = predicate_stat(
        _get_response(_get_file_path("windbreaker.json")),
        setting,
        277,
        size=1,
    )

    best_result = results[0][0]

    assert best_result.short_dict() == {
        "STR": 2295.0,
        "LUK": 1251.0,
        "INT": 1138.0,
        "DEX": 5326.0,
        "STR_multiplier": 144.0,
        "LUK_multiplier": 135.0,
        "INT_multiplier": 159.0,
        "DEX_multiplier": 519.0,
        "STR_static": 733.0,
        "LUK_static": 386.0,
        "INT_static": 630.0,
        "DEX_static": 20210.0,
    }


def test_infer_stat():
    logger.disable("")

    setting = get_predefined_setting(JobType.windbreaker)
    results = infer_stat(
        _get_response(_get_file_path("windbreaker.json")),
        setting,
        authentic_force=270,
        size=5,
    )

    assert len(results) == 5
