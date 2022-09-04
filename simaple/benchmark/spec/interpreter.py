from pathlib import Path
from typing import cast

import yaml

from simaple.benchmark.gearset_blueprint import UserGearsetBlueprint
from simaple.benchmark.spec.patch import (
    GearIdPatch,
    all_att_patch,
    all_stat_patch,
    attack_patch,
    stat_patch,
)
from simaple.core import JobCategory
from simaple.spec.interpreter import Interpreter

__JOB_STAT_PRIORITY = {
    JobCategory.warrior: {
        "stat_priority": ("STR", "DEX", "INT", "LUK"),
        "attack_priority": ("attack_power", "magic_attack"),
    },
    JobCategory.mage: {
        "stat_priority": ("INT", "LUK", "STR", "DEX"),
        "attack_priority": ("magic_attack", "magic_attack"),
    },
    JobCategory.thief: {
        "stat_priority": ("LUK", "DEX", "STR", "INT"),
        "attack_priority": ("attack_power", "magic_attack"),
    },
    JobCategory.archer: {
        "stat_priority": ("DEX", "STR", "LUK", "INT"),
        "attack_priority": ("attack_power", "magic_attack"),
    },
    JobCategory.pirate: {
        "stat_priority": ("STR", "DEX", "LUK", "INT"),
        "attack_priority": ("attack_power", "magic_attack"),
    },
}

# TODO: dex-pirate.


def benchmark_interpreter(job_category: JobCategory):
    config = __JOB_STAT_PRIORITY[job_category]
    stat_priority = cast(tuple[str, str, str, str], config["stat_priority"])
    attack_priority = cast(tuple[str, str], config["attack_priority"])

    return Interpreter(
        patches=[
            all_stat_patch(),
            all_att_patch(),
            stat_patch(
                stat_priority=stat_priority,
            ),
            attack_patch(
                attack_priority=attack_priority,
            ),
            GearIdPatch(job_category=job_category),
        ]
    )


def builtin_blueprint(name: str, job_category: JobCategory):
    interpreter = benchmark_interpreter(
        job_category=job_category,
    )
    file_path = Path(__file__).parent / "builtin" / f"{name}.yaml"

    with open(file_path, encoding="utf-8") as f:
        raw_configuration = yaml.safe_load(f)

    user_gearset_blueprint_config = interpreter.interpret(raw_configuration)
    user_gearset_blueprint = UserGearsetBlueprint.parse_obj(
        user_gearset_blueprint_config
    )
    return user_gearset_blueprint
