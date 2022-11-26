import pydantic

from simaple.core.base import Stat
from simaple.core.damage import DamageLogic
from simaple.simulate.report.base import DamageLog, Report


class DPMCalculator(pydantic.BaseModel):
    character_spec: Stat
    damage_logic: DamageLogic
    armor: int = 300

    def get_damage(self, log: DamageLog):
        buffed_stat = self.character_spec + log.buff
        damage_factor = self.damage_logic.get_damage_factor(buffed_stat, self.armor)
        return (log.damage * 0.01) * log.hit * damage_factor

    def calculate_damage(self, damage_report: Report):
        total_damage = 0
        for log in damage_report:
            total_damage += self.get_damage(log)

        return total_damage

    def calculate_dpm(self, damage_report: Report):
        return (
            self.calculate_damage(damage_report) / damage_report.total_time() * 60_000
        )
