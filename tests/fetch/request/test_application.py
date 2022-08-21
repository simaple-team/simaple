import json

from simaple.fetch.application.base import KMSFetchApplication
from simaple.gear.slot_name import SlotName


def test_app():
    app = KMSFetchApplication()

    result = app.run("생분자")

    print(result.get_item(SlotName.cap))

    with open("mine.output.json", "w", encoding="utf-8") as f:
        json.dump(result.get_raw(), f, ensure_ascii=False, indent=2)
