from __future__ import annotations

from typing import List

from pydantic import BaseModel

from simaple.core import JobType, Stat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class LinkSkill(BaseModel, metaclass=TaggedNamespacedABCMeta(kind="LinkSkill")):
    providing_jobs: List[JobType]
    options: List[Stat]

    def get_stat(self, size: int) -> Stat:
        if size == 0:
            return Stat()
        return self.options[size - 1].model_copy()

    def get_max_level(self) -> int:
        return len(self.options)


class LinkSkillset(BaseModel):
    link_levels: List[int]
    links: List[LinkSkill]

    @classmethod
    def empty(cls):
        return LinkSkillset(
            link_levels=[],
            links=[],
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
