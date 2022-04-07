"""
Passive is no-state no-change property of user-class.
"""

import math  # pylint: disable=W0611
from typing import Any, Dict, Iterator, List, Literal

import yaml
from pydantic import BaseModel, Field

from simaple.core import ActionStat, Stat
from simaple.job.description import GeneralJobArgument
from simaple.resource import Description, SimapleResource


class PassiveSkill(BaseModel):
    stat: Stat = Field(default_factory=Stat)
    action_stat: ActionStat = Field(default_factory=ActionStat)
    name: str


class PassiveSkillArgument(GeneralJobArgument):
    ...


class PassiveSkillDescription(Description[PassiveSkill, PassiveSkillArgument]):
    stat: Dict[str, Any] = Field(default_factory=dict)
    action_stat: Dict[str, Any] = Field(default_factory=dict)
    name: str
    passive_skill_enabled: bool = False
    combat_orders_enabled: bool = False
    default_skill_level: int = 0

    def _parse_stat_expression(self, expression: str, lv: int, character_level: int):
        if not isinstance(expression, str):
            return expression

        return eval(expression)  # pylint: disable=W0123

    def interpret(self, argument: PassiveSkillArgument) -> PassiveSkill:
        skill_level = self.default_skill_level
        if self.passive_skill_enabled:
            skill_level += argument.passive_skill_level
        if self.combat_orders_enabled:
            skill_level += argument.combat_orders_level

        stat = Stat.parse_obj(
            {
                k: self._parse_stat_expression(v, skill_level, argument.character_level)
                for k, v in self.stat.items()
            }
        )
        action_stat = ActionStat.parse_obj(
            {
                k: self._parse_stat_expression(v, skill_level, argument.character_level)
                for k, v in self.action_stat.items()
            }
        )

        return PassiveSkill(name=self.name, stat=stat, action_stat=action_stat)


class PassiveSkillResource(SimapleResource[PassiveSkillDescription]):
    data: List[PassiveSkillDescription]
    kind: Literal["PassiveSkill"]


class PassiveSkillset:
    def __init__(self, resource: PassiveSkillResource):
        self.resource = resource
        self._indexed_by_name = {d.name: d for d in resource.data}

    @classmethod
    def from_resource_file(cls, fname: str):
        with open(fname, "r", encoding="utf-8") as f:
            raw_configuration = yaml.safe_load(f)
        resource = PassiveSkillResource.parse_obj(raw_configuration)
        return PassiveSkillset(resource)

    def get(self, skill_name: str, argument: PassiveSkillArgument) -> PassiveSkill:
        return self._indexed_by_name[skill_name].interpret(argument)

    def iterate(self, argument: PassiveSkillArgument) -> Iterator[PassiveSkill]:
        for resource in self._indexed_by_name.values():
            yield resource.interpret(argument)

    def all(self, argument: PassiveSkillArgument) -> List[PassiveSkill]:
        return list(self.iterate(argument))
