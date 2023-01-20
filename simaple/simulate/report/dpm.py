import pydantic

from simaple.core.base import Stat
from simaple.core.damage import DamageLogic
from simaple.simulate.report.base import DamageLog, Report
from simaple.simulate.reserved_names import Tag


class LevelAdvantage:
    def __init__(self):
        self._advantage_table: list[float] = [
            # fmt: off
            1.2, 1.18, 1.16, 1.14, 1.12, 1.1,
            1.0584, 1.0070, 0.9672, 0.9180, 0.88,
            .85, .83, .80, .78, .75,
            .73, .70, .68, .65, .63,
            .60, .58, .55, .53, .50,
            .48, .45, .43, .40, .38,
            .35, .33, .30, .28, .25,
            .23, .20, .18, .15, .13,
            .10, .08, .05, .02, .00
        ]
        # fmt: on
        self._bias = 5

    def get_advantage(self, mob_level: int, character_level: int) -> float:
        advantage_index = mob_level - character_level + self._bias
        if advantage_index < 0:
            return self._advantage_table[0]
        if advantage_index > len(self._advantage_table):
            return 0.0

        return float(self._advantage_table[advantage_index])


class DamageCalculator(pydantic.BaseModel):
    character_spec: Stat
    damage_logic: DamageLogic
    armor: int = 300
    level_advantage: float = 1.0
    force_advantage: float = 1.0

    class Config:
        extra = "forbid"

    def get_damage(self, log: DamageLog):
        buffed_stat = self.character_spec + log.buff
        if log.tag == Tag.DAMAGE:
            damage_factor = self.damage_logic.get_damage_factor(buffed_stat, self.armor)
        elif log.tag == Tag.DOT:
            damage_factor = self.damage_logic.get_dot_factor(buffed_stat, self.armor)
        else:
            raise ValueError

        return (
            (log.damage * 0.01)
            * log.hit
            * damage_factor
            * self.level_advantage
            * self.force_advantage
        )

    def calculate_damage(self, damage_report: Report):
        total_damage = 0
        for log in damage_report:
            total_damage += self.get_damage(log)

        return total_damage

    def calculate_dpm(self, damage_report: Report):
        return (
            self.calculate_damage(damage_report) / damage_report.total_time() * 60_000
        )
