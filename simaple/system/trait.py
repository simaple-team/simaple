import pydantic

from simaple.core import ActionStat, ExtendedStat, Stat


class CharacterTrait(pydantic.BaseModel):
    ambition: int
    insight: int
    empathy: int
    willpower: int
    diligence: int
    charm: int

    def get_extended_stat(self) -> ExtendedStat:
        return ExtendedStat(
            stat=self.get_stat(),
            action_stat=self.get_action_stat(),
        )

    def get_stat(self) -> Stat:
        return Stat(
            MMP=(self.empathy // 5) * 100,
            MHP=(self.willpower // 5) * 100,
            ignored_defence=(self.ambition // 5) * 0.5,
            elemental_resistance=(self.insight // 10) * 0.5,
        )

    def get_action_stat(self) -> ActionStat:
        return ActionStat(buff_duration=(self.empathy // 10))
