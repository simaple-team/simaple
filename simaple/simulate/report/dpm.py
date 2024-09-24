import pydantic

from simaple.core.base import Stat
from simaple.core.damage import DamageLogic
from simaple.simulate.report.base import DamageLog, SimulationEntry
from simaple.simulate.reserved_names import Tag


class LevelAdvantage:
    def __init__(self) -> None:
        self._advantage_table: list[float] = [
            # fmt: off
            1.2,
            1.18,
            1.16,
            1.14,
            1.12,
            1.1,
            1.0584,
            1.0070,
            0.9672,
            0.9180,
            0.88,
            0.85,
            0.83,
            0.80,
            0.78,
            0.75,
            0.73,
            0.70,
            0.68,
            0.65,
            0.63,
            0.60,
            0.58,
            0.55,
            0.53,
            0.50,
            0.48,
            0.45,
            0.43,
            0.40,
            0.38,
            0.35,
            0.33,
            0.30,
            0.28,
            0.25,
            0.23,
            0.20,
            0.18,
            0.15,
            0.13,
            0.10,
            0.08,
            0.05,
            0.02,
            0.00,
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

    def get_damage(self, log: DamageLog):
        buffed_stat = self.character_spec + log.buff
        if log.tag == Tag.DAMAGE:
            damage_factor = self.damage_logic.get_damage_factor(buffed_stat, self.armor)
        elif log.tag == Tag.DOT:
            damage_factor = self.damage_logic.get_dot_factor(buffed_stat, self.armor)
        else:
            raise ValueError

        return (log.damage * 0.01) * log.hit * damage_factor * self.level_advantage * self.force_advantage

    def calculate_damage(self, entry: SimulationEntry) -> float:
        total_damage = 0
        for log in entry.damage_logs:
            total_damage += self.get_damage(log)

        return total_damage

    def calculate_total_damage(self, entries: list[SimulationEntry]) -> float:
        return sum([self.calculate_damage(entry) for entry in entries])

    def calculate_dpm(self, entries: list[SimulationEntry]) -> float:
        total_damage = sum([self.calculate_damage(entry) for entry in entries])
        return total_damage / entries[-1].clock * 60_000
