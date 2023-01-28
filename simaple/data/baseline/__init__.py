from pathlib import Path
from typing import cast

from simaple.core import JobCategory, JobType
from simaple.data.baseline.patch import (
    DoubleBonusRefinePatch,
    GearIdPatch,
    Patch,
    all_att_patch,
    all_stat_patch,
    attack_patch,
    stat_patch,
)
from simaple.gear.blueprint.gearset_blueprint import GearsetBlueprint
from simaple.gear.gearset import Gearset
from simaple.gear.setitem import KMSSetItemRepository
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository

__JOB_STAT_PRIORITY = {
    JobCategory.warrior: {
        "stat_priority": ("STR", "DEX", "INT", "LUK"),
        "attack_priority": ("attack_power", "magic_attack"),
    },
    JobCategory.magician: {
        "stat_priority": ("INT", "LUK", "STR", "DEX"),
        "attack_priority": ("magic_attack", "attack_power"),
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
DEX_PIRATE = [JobType.mechanic]


def jobtype_patches(job_category: JobCategory, job_type: JobType) -> list[Patch]:
    if job_category == JobCategory.pirate and job_type in DEX_PIRATE:
        config = __JOB_STAT_PRIORITY[JobCategory.archer]
    else:
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
        GearIdPatch(job_type=job_type, job_category=job_category),
        DoubleBonusRefinePatch(),
    ]


def get_baseline_gearset(
    name: str, job_category: JobCategory, job_type: JobType
) -> Gearset:
    patches = jobtype_patches(
        job_category=job_category,
        job_type=job_type,
    )

    repository = DirectorySpecRepository(str(Path(__file__).parent / "spec"))
    loader = SpecBasedLoader(repository)
    set_item_repository = KMSSetItemRepository()

    blueprint: GearsetBlueprint = loader.load(query={"name": name}, patches=patches)
    return blueprint.build(set_item_repository)
