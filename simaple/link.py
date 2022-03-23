from typing import List

from pydantic import BaseModel, Field

from simaple.core.base import Stat
from simaple.core.jobtype import JobType


def empty_options(length):
    return [Stat() for v in range(length)]


class LinkSkill(BaseModel):
    providing_jobs: List[JobType]
    options: List[Stat]

    def get_stat(self, size: int) -> Stat:
        if size == 0:
            return Stat()
        return self.options[size - 1].copy()

    def get_max_level(self) -> int:
        return len(self.options)


def get_all_blocks(
    theif_cunning_utilization_rate: float = 0.5,
    cadena_link_stack: int = 2,
    ark_link_stack: int = 5,
    adele_link_membder_count: int = 4,
    kain_link_utilization_rate: float = 0.5,
):
    return [
        LinkSkill(
            providing_jobs=[JobType.mercedes],
            options=empty_options(2),
        ),
        LinkSkill(
            providing_jobs=[JobType.evan],
            options=empty_options(2),
        ),
        LinkSkill(
            providing_jobs=[JobType.aran],
            options=empty_options(2),
        ),
        LinkSkill(
            providing_jobs=[JobType.archmagefb, JobType.archmagetc, JobType.bishop],
            options=[
                Stat(damage_multiplier=(i + 1) // 2, ignored_defence=(i + 1) // 2)
                for i in range(6)
            ],
        ),
        LinkSkill(
            providing_jobs=[JobType.bowmaster, JobType.sniper, JobType.pathfinder],
            options=[Stat(critical_rate=v) for v in (3, 4, 5, 7, 8, 10)],
        ),
        LinkSkill(
            providing_jobs=[JobType.shadower, JobType.corsair, JobType.dualblade],
            options=[
                Stat(damage_multiplier=(v + 1) * 3 * theif_cunning_utilization_rate)
                for v in range(6)
            ],
        ),
        LinkSkill(
            providing_jobs=[JobType.buccaneer, JobType.corsair, JobType.cannoneer],
            options=[Stat.all_stat(v * 10) + Stat(MHP=v * 175) for v in range(2, 8)],
        ),
        LinkSkill(
            providing_jobs=[JobType.demonslayer],
            options=[Stat(boss_damage_multiplier=v) for v in (10, 15)],
        ),
        LinkSkill(
            providing_jobs=[JobType.luminous],
            options=[Stat(ignored_defence=v) for v in (10, 15)],
        ),
        LinkSkill(
            providing_jobs=[JobType.phantom],
            options=[Stat(critical_rate=v) for v in (10, 15)],
        ),
        LinkSkill(
            providing_jobs=[JobType.kinesis],
            options=[Stat(critical_damage=v) for v in (2, 4)],
        ),
        LinkSkill(
            providing_jobs=[JobType.angelicbuster],
            options=empty_options(2),  # Soul Contract; TODO
        ),
        LinkSkill(
            providing_jobs=[JobType.zero],
            options=[Stat(ignored_defence=v) for v in (2, 4, 6, 8, 10)],
        ),
        LinkSkill(
            providing_jobs=[JobType.zenon],
            options=[Stat.all_stat_multiplier(v) for v in (5, 10)],
        ),
        LinkSkill(
            providing_jobs=[JobType.cadena],
            options=[Stat(damage_multiplier=cadena_link_stack * v) for v in (3, 6)],
        ),
        LinkSkill(
            providing_jobs=[JobType.ark],
            options=[Stat(damage_multiplier=ark_link_stack * v + 1) for v in (1, 2)],
        ),
        LinkSkill(
            providing_jobs=[JobType.hoyoung],
            options=[Stat(ignored_defence=v) for v in (5, 10)],
        ),
        LinkSkill(
            providing_jobs=[JobType.adele],
            options=[
                Stat(
                    boss_damage_multiplier=v * 2,
                    damage_multiplier=v * adele_link_membder_count,
                )
                for v in (1, 2)
            ],
        ),
        LinkSkill(
            providing_jobs=[JobType.kain],
            options=[
                Stat(damage_multiplier=v * kain_link_utilization_rate) for v in (9, 17)
            ],
        ),
        LinkSkill(
            providing_jobs=[JobType.paladin, JobType.hero, JobType.darkknight],
            options=empty_options(6),
        ),
        LinkSkill(providing_jobs=[JobType.mihile], options=empty_options(2)),
        LinkSkill(
            providing_jobs=[
                JobType.blaster,
                JobType.battlemage,
                JobType.mechanic,
                JobType.wildhunter,
            ],
            options=empty_options(8),
        ),
        LinkSkill(
            providing_jobs=[
                JobType.soulmaster,
                JobType.flamewizard,
                JobType.windbreaker,
                JobType.nightwalker,
                JobType.striker,
            ],
            options=[Stat(damage_multiplier=v * 2 + 7) for v in range(10)],
        ),
        LinkSkill(providing_jobs=[JobType.kaiser], options=empty_options(2)),
        LinkSkill(providing_jobs=[JobType.eunwol], options=empty_options(2)),
    ]


def get_maximum_level():
    return [block.get_max_level() for block in get_all_blocks()]


LINK_TYPES = len(get_all_blocks())


class LinkSkillset(BaseModel):
    link_levels: List[int] = Field(default_factory=get_maximum_level)
    links: List[LinkSkill] = Field(default_factory=get_all_blocks)

    @classmethod
    def get_length(cls):
        return LINK_TYPES

    def get_index(self, jobtype: JobType):
        for idx, link in enumerate(self.links):
            if jobtype in link.providing_jobs:
                return idx

        raise KeyError

    def get_stat(self, mask: List[int]) -> Stat:
        stat = Stat()
        for enabled, block, size in zip(mask, self.links, self.link_levels):
            if enabled:
                stat += block.get_stat(size)

        return stat
