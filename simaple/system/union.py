from __future__ import annotations

from typing import List, Tuple

from pydantic import BaseModel, Field

from simaple.core import ActionStat, JobType, Stat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


def _empty_options():
    return [Stat() for v in range(5)]


def _empty_action_stats():
    return [ActionStat() for v in range(5)]


class UnionBlock(BaseModel, metaclass=TaggedNamespacedABCMeta(kind="UnionBlock")):
    job: JobType
    options: list[Stat] = _empty_options()
    action_stat_options: list[ActionStat] = _empty_action_stats()

    def get_stat(self, size: int) -> Stat:
        if size == 0:
            return Stat()
        return self.options[size - 1].model_copy()

    def get_action_stat(self, size: int) -> ActionStat:
        if self.action_stat_options is None or size == 0:
            return ActionStat()

        return self.action_stat_options[size - 1].model_copy()


# TODO: att / stat occupation
class UnionSquad(BaseModel):
    block_size: List[int]
    blocks: List[UnionBlock]

    @classmethod
    def empty(cls):
        return UnionSquad(
            block_size=[],
            blocks=[],
        )

    def length(self):
        return len(self.blocks)

    def get_index(self, jobtype: JobType):
        for idx, block in enumerate(self.blocks):
            if block.job == jobtype:
                return idx

        raise KeyError

    def get_masked(self, mask: List[int]) -> UnionSquad:
        return UnionSquad(
            block_size=[
                size for enabled, size in zip(mask, self.block_size) if enabled
            ],
            blocks=[block for enabled, block in zip(mask, self.blocks) if enabled],
        )

    def get_stat(self) -> Stat:
        stat = Stat()
        for block, size in zip(self.blocks, self.block_size):
            stat += block.get_stat(size)

        return stat

    def get_action_stat(self) -> ActionStat:
        stat = ActionStat()
        for block, size in zip(self.blocks, self.block_size):
            stat += block.get_action_stat(size)

        return stat

    def get_occupation_count(self) -> int:
        return sum(self.block_size)


def get_union_occupation_values():
    return [
        [(Stat(boss_damage_multiplier=v), ActionStat()) for v in range(41)],
        [(Stat(ignored_defence=v), ActionStat()) for v in range(41)],
        [(Stat(critical_damage=v), ActionStat()) for v in range(41)],
        [(Stat(critical_rate=v), ActionStat()) for v in range(41)],
        [(Stat(), ActionStat(buff_duration=v)) for v in range(41)],
    ]


def get_empty_union_occupation_state():
    return [0, 0, 0, 0, 0]


def get_buff_duration_preempted_union_occupation_state():
    return [0, 0, 0, 0, 40]


class UnionOccupation(BaseModel):
    occupation_state: List[int] = Field(
        default_factory=get_empty_union_occupation_state
    )
    occupation_value: List[List[Tuple[Stat, ActionStat]]] = Field(
        default_factory=get_union_occupation_values
    )

    def get_occupation_rearranged(self, state: List[int]) -> UnionOccupation:
        assert len(state) == self.length()

        return UnionOccupation(
            occupation_value=self.occupation_value,
            occupation_state=state,
        )

    def length(self):
        return len(self.occupation_value)

    def get_stat(self) -> Stat:
        return sum(
            [
                value[occupation][0]
                for value, occupation in zip(
                    self.occupation_value, self.occupation_state
                )
            ],
            Stat(),
        )

    def get_action_stat(self) -> ActionStat:
        return sum(
            [
                value[occupation][1]
                for value, occupation in zip(
                    self.occupation_value, self.occupation_state
                )
            ],
            ActionStat(),
        )
