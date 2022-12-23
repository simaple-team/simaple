import pydantic

from simaple.core import ActionStat, ElementalResistance, Stat


class CharacterTrait(pydantic.BaseModel):
    ambition: int
    insight: int
    empathy: int
    willpower: int
    diligence: int
    charm: int

    def get_stat(self) -> Stat:
        return Stat(
            MMP=(self.empathy // 5) * 100,
            MHP=(self.willpower // 5) * 100,
            ignored_defence=(self.ambition // 5) * 0.5,
        )

    def get_action_stat(self) -> ActionStat:
        return ActionStat(buff_duration=(self.empathy // 10))

    def get_elemental_resistance(self) -> ElementalResistance:
        return ElementalResistance(value=(self.insight // 10) * 0.5)
