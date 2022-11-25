from pathlib import Path

from simaple.job.description import GeneralJobArgument
from simaple.job.spec.patch import SkillLevelPatch
from simaple.job.static_property import StaticProperty
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch, Patch
from simaple.spec.repository import DirectorySpecRepository


def get_patches(
    job_argument: GeneralJobArgument,
) -> list[Patch]:
    return [
        SkillLevelPatch(
            job_argument=job_argument,
        ),
        EvalPatch(
            injected_values={
                "character_level": job_argument.character_level,
            }
        ),
    ]


def get_passive_skills(
    group: str,
    job_argument: GeneralJobArgument,
):
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    patches = get_patches(job_argument)
    return loader.load_all(
        query={"group": group, "kind": "PassiveSkill"}, patches=patches
    )


def get_default_active_skills(
    group: str,
    job_argument: GeneralJobArgument,
):
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    patches = get_patches(job_argument)

    return loader.load_all(
        query={"group": group, "kind": "DefaultActiveSkill"}, patches=patches
    )


def get_static_propery(
    group: str,
    job_argument: GeneralJobArgument,
):
    return StaticProperty(
        passive_skillset=get_passive_skills(group, job_argument),
        default_active_skillset=get_default_active_skills(group, job_argument),
    )
