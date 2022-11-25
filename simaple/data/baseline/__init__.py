from pathlib import Path
from typing import cast

from simaple.core import JobCategory
from simaple.data.baseline.patch import (
    GearIdPatch,
    Patch,
    all_att_patch,
    all_stat_patch,
    attack_patch,
    stat_patch,
)
from simaple.gear.blueprint.gearset_blueprint import GearsetBlueprint
from simaple.gear.gear_repository import GearRepository
from simaple.gear.gearset import Gearset
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository

__JOB_STAT_PRIORITY = {
    JobCategory.warrior: {
        "stat_priority": ("STR", "DEX", "INT", "LUK"),
        "attack_priority": ("attack_power", "magic_attack"),
    },
    JobCategory.magician: {
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


def jobtype_patches(job_category: JobCategory) -> list[Patch]:
    config = __JOB_STAT_PRIORITY[job_category]
    stat_priority = cast(tuple[str, str, str, str], config["stat_priority"])
    attack_priority = cast(tuple[str, str], config["attack_priority"])

    return [
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


def get_baseline_gearset(name: str, job_category: JobCategory) -> Gearset:
    patches = jobtype_patches(
        job_category=job_category,
    )

    repository = DirectorySpecRepository(str(Path(__file__).parent / "spec"))
    loader = SpecBasedLoader(repository)
    gear_repository = GearRepository()

    blueprint: GearsetBlueprint = loader.load(query={"name": name}, patches=patches)
    return blueprint.build(gear_repository)
