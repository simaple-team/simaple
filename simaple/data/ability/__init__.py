import json
from pathlib import Path

from simaple.core.jobtype import JobType
from simaple.system.ability import AbilityLine


def get_best_ability(jobtype: JobType) -> list[AbilityLine]:
    with open(Path(__file__).parent / "best.json", encoding="utf-8") as f:
        best_abilities = json.load(f)

    ability_lines = best_abilities[jobtype.value]

    return [AbilityLine.parse_obj(line) for line in ability_lines]
