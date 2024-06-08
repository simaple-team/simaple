from __future__ import annotations

from typing import List

from pydantic import BaseModel

from simaple.core import JobType, Stat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


def empty_options(length):
    return [Stat() for v in range(length)]


class LinkSkill(BaseModel, metaclass=TaggedNamespacedABCMeta(kind="LinkSkill")):
    providing_jobs: List[JobType]
    options: List[Stat]

    def get_stat(self, size: int) -> Stat:
        if size == 0:
            return Stat()
        return self.options[size - 1].model_copy()

    def get_max_level(self) -> int:
        return len(self.options)


def get_skill_from_spec():
    from pydantic import BaseModel

    from simaple.core import Stat, StatProps
    from simaple.spec.loader import SpecBasedLoader
    from simaple.spec.repository import DirectorySpecRepository
    from simaple.system.hyperstat import Hyperstat, HyperStatBasis

    repository = DirectorySpecRepository("simaple/data/system")
    loader = SpecBasedLoader(repository)

    link_skills: list[HyperStatBasis] = loader.load_all(
        query={"kind": "LinkSkill"},
    )
    return link_skills


def get_all_blocks(
    thief_cunning_utilization_rate: float = 0.5,
    cadena_link_stack: int = 2,
    ark_link_stack: int = 5,
    adele_link_membder_count: int = 4,
    kain_link_utilization_rate: float = 0.5,
):
    return get_skill_from_spec() + [
    ]


def get_maximum_level():
    return [block.get_max_level() for block in get_all_blocks()]


LINK_TYPES = len(get_all_blocks())


class LinkSkillset(BaseModel):
    link_levels: List[int]
    links: List[LinkSkill]

    @classmethod
    def empty(cls):
        return LinkSkillset(
            link_levels=[],
            links=[],
        )

    @classmethod
    def KMS(cls):
        return LinkSkillset(
            link_levels=get_maximum_level(),
            links=get_all_blocks(),
        )

    def length(self):
        return len(self.links)

    def get_index(self, jobtype: JobType):
        for idx, link in enumerate(self.links):
            if jobtype in link.providing_jobs:
                return idx

        raise KeyError

    def get_masked(self, mask: List[int]) -> LinkSkillset:
        return LinkSkillset(
            link_levels=[
                level for enabled, level in zip(mask, self.link_levels) if enabled
            ],
            links=[link for enabled, link in zip(mask, self.links) if enabled],
        )

    def get_stat(self) -> Stat:
        stat = Stat()
        for block, size in zip(self.links, self.link_levels):
            stat += block.get_stat(size)

        return stat
