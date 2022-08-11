import json

import pytest

from simaple.fetch.translator.gear import GearTranslator
from simaple.fetch.translator.kms.gear import kms_gear_stat_translator
from simaple.fetch.translator.kms.potential import kms_potential_translator
from simaple.gear.gear_repository import GearRepository


@pytest.mark.parametrize(
    "gear_dump_file",
    [
        ("tests/fetch/translator/fixture/cap.json"),
        ("tests/fetch/translator/fixture/emblem.json"),
        ("tests/fetch/translator/fixture/ring.json"),
    ],
)
def test_gear(gear_dump_file):
    translator = GearTranslator(
        gear_stat_translator=kms_gear_stat_translator(),
        potential_translator=kms_potential_translator(),
        gear_repository=GearRepository(),
    )

    with open(gear_dump_file, encoding="utf-8") as f:
        dumped = json.load(f)

    gear = translator.translate(dumped)

    # print(gear)
