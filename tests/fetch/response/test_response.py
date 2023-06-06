import json

import pytest

from simaple.core import JobType
from simaple.fetch.response.character import CharacterResponse
from simaple.fetch.translator.gear import GearTranslator
from simaple.fetch.translator.kms.gear import kms_gear_stat_translator
from simaple.fetch.translator.kms.potential import kms_potential_translator
from simaple.gear.gear_repository import GearRepository
from simaple.gear.slot_name import SlotName


@pytest.fixture(name="raw_data")
def fixture_raw_data():
    with open("tests/fetch/response/output.json", encoding="utf-8") as f:
        raw = json.load(f)

    return raw


@pytest.fixture(name="new_data")
def fixture_new_data():
    with open("tests/fetch/response/fp.json", encoding="utf-8") as f:
        raw = json.load(f)

    return raw


def test_response(raw_data):
    response = CharacterResponse(
        raw_data,
        GearTranslator(
            gear_stat_translator=kms_gear_stat_translator(),
            potential_translator=kms_potential_translator(),
            gear_repository=GearRepository(),
        ),
    )

    item = response.get_item(SlotName.eye_accessory)


def test_raw(raw_data):
    response = CharacterResponse(
        raw_data,
        GearTranslator(
            gear_stat_translator=kms_gear_stat_translator(),
            potential_translator=kms_potential_translator(),
            gear_repository=GearRepository(),
        ),
    )

    expected_raw = response.get_raw()

    assert expected_raw == raw_data


def test_arcane_symbol(raw_data):
    response = CharacterResponse(
        raw_data,
        GearTranslator(
            gear_stat_translator=kms_gear_stat_translator(),
            potential_translator=kms_potential_translator(),
            gear_repository=GearRepository(),
        ),
    )

    symbol = response.get_item(SlotName.arcane1)

    assert symbol.stat.DEX_static == 2200


def test_all_items(new_data):
    response = CharacterResponse(
        new_data,
        GearTranslator(
            gear_stat_translator=kms_gear_stat_translator(),
            potential_translator=kms_potential_translator(),
            gear_repository=GearRepository(),
        ),
    )

    print(response.get_all_item_stat().short_dict())


def test_jobtype(new_data):
    response = CharacterResponse(
        new_data,
        GearTranslator(
            gear_stat_translator=kms_gear_stat_translator(),
            potential_translator=kms_potential_translator(),
            gear_repository=GearRepository(),
        ),
    )

    assert response.get_jobtype() == JobType.archmagefb
