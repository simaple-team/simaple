"""
Passive is no-state no-change property of user-class.
"""

import math  # pylint: disable=W0611
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel

from simaple.core.base import Stat
from simaple.resource import Description, DescriptionArgument, SimapleResource


class PassiveSkill(BaseModel):
    stat: Stat
    name: str


class PassiveSkillArgument(DescriptionArgument):
    combat_orders_level: int
    passive_skill_level: int


class PassiveSkillDescription(Description[PassiveSkill, PassiveSkillArgument]):
    stat: Dict[str, Any]
    name: str
    passive_skill_enabled: bool = False
    combat_orders_enabled: bool = False
    default_skill_level: int = 0

    def _parse_stat_expression(self, expression: str, lv: int):
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
                k: self._parse_stat_expression(v, skill_level)
                for k, v in self.stat.items()
            }
        )

        return PassiveSkill(name=self.name, stat=stat)


class PassiveSkillResource(SimapleResource[PassiveSkillDescription]):
    data: List[PassiveSkillDescription]


class PassiveSkillRepository:
    def __init__(self, resource: PassiveSkillResource):
        self.resource = resource
        self._indexed_by_name = {d.name: d for d in resource.data}

    @classmethod
    def from_file(cls, fname: str):
        with open(fname, "r", encoding="utf-8") as f:
            raw_configuration = yaml.safe_load(f)
        resource = PassiveSkillResource.parse_obj(raw_configuration)
        return PassiveSkillRepository(resource)

    def get(self, skill_name: str, argument: PassiveSkillArgument) -> PassiveSkill:
        return self._indexed_by_name[skill_name].interpret(argument)
