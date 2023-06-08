import json

import pytest
from loguru import logger

from simaple.core import JobType
from simaple.fetch.inference.builtin_settings import get_predefined_setting
from simaple.fetch.inference.logic import predicate_attack
from simaple.fetch.inference.stat_logic import predicate_stat
from simaple.fetch.response.character import CharacterResponse
from simaple.fetch.translator.gear import GearTranslator
from simaple.fetch.translator.kms.gear import kms_gear_stat_translator
from simaple.fetch.translator.kms.potential import kms_potential_translator
from simaple.gear.gear_repository import GearRepository


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
    return _get_response("tests/fetch/response/fp.json")


def test_attack_predication(new_data):
    logger.disable("")

    setting = get_predefined_setting(JobType.archmagefb)
    result = predicate_attack(new_data, setting)

    assert [v for v, score in result][0] == (96.0, 126.0, 3316)


def test_luminous():
    logger.disable("")

    setting = get_predefined_setting(JobType.luminous)
    result = predicate_attack(
        _get_response("tests/fetch/response/backend.json"), setting
    )

    assert result[0][0] == (77.0, 18.0, 827)


def test_infinity_triggered_predication():
    logger.disable("")

    setting = get_predefined_setting(JobType.archmagefb)
    results = predicate_attack(
        _get_response("tests/fetch/response/biomolecule.json"), setting
    )

    assert results[0][0] == (96.0, 126.0, 3366)


@pytest.mark.parametrize(
    "filename",
    [
        "tests/fetch/response/dumped/ilium.json",
        "tests/fetch/response/dumped/bishop.json",
    ],
)
def test_from_dumped(filename):
    logger.disable("")

    response = _get_response(filename)
    setting = get_predefined_setting(response.get_jobtype())

    results = predicate_attack(response, setting)
    assert len(results) > 0


def test_stat():
    logger.disable("")

    setting = get_predefined_setting(JobType.archmagefb)
    results = predicate_stat(
        _get_response("tests/fetch/response/fp.json"), setting, 270
    )

    assert results[0][0] == (5902, 560, 20290)
