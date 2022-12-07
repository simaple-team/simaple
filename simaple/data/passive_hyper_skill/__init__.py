from pathlib import Path
from typing import Optional

from simaple.core import Stat
from simaple.data.passive_hyper_skill.patch import PassiveHyperskillPatch
from simaple.data.passive_hyper_skill.spec import PassiveHyperskillInterface
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch, Patch
from simaple.spec.repository import DirectorySpecRepository


def get_every_hyper_skills(group: str) -> list[PassiveHyperskillInterface]:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return loader.load_all(
        query={"group": group, "kind": "PassiveHyperskill"},
    )


def get_hyper_skill_patch(
    group: str,
    skill_names: Optional[list[str]] = None,
    count=5,
):
    hyper_skills = get_every_hyper_skills(group)

    if skill_names is None:
        hyper_skills = hyper_skills[:count]
    else:
        hyper_skills = [sk for sk in hyper_skills if sk.get_name() in skill_names]

    return PassiveHyperskillPatch(hyper_skills=hyper_skills)
