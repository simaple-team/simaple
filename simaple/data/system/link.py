from pathlib import Path

from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.system.link import LinkSkill, LinkSkillset

"""
TODO: migrate this into patch

def get_all_blocks(
    thief_cunning_utilization_rate: float = 0.5,
    cadena_link_stack: int = 2,
    ark_link_stack: int = 5,
    adele_link_membder_count: int = 4,
    kain_link_utilization_rate: float = 0.5,
) -> list[LinkSkill]:
    return get_skill_from_spec()
"""


def get_all_linkskills() -> list[LinkSkill]:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    loader = SpecBasedLoader(repository)

    link_skills: list[LinkSkill] = loader.load_all(
        query={"kind": "LinkSkill"},
    )
    return link_skills


def get_maximum_level():
    return [block.get_max_level() for block in get_all_linkskills()]


def get_kms_link_skill_set():
    return LinkSkillset(
        link_levels=get_maximum_level(),
        links=get_all_linkskills(),
    )
