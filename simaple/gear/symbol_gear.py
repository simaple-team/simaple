import enum

from pydantic import BaseModel

from simaple.core import Stat


class SymbolGear(BaseModel):
    stat: Stat
    force: int

    def get_stat(self) -> Stat:
        return self.stat

    def get_force(self) -> int:
        return self.force


class SymbolIndicator(enum.Enum):
    STR = "STR"
    LUK = "LUK"
    INT = "INT"
    DEX = "DEX"
    ALL_STAT = "ALL_STAT"
    HP = "HP"


class ArcaneSymbolTemplate(BaseModel):
    level: int
    stat_type: SymbolIndicator

    def get_stat(self) -> Stat:
        if self.level == 0:
            return Stat()

        if self.stat_type.value in ["INT", "LUK", "DEX", "STR"]:
            return Stat.model_validate(
                {self.stat_type.value + "_static": (self.level + 2) * 100}
            )

        raise ValueError

    def get_symbol(self) -> SymbolGear:
        return SymbolGear(stat=self.get_stat(), force=(self.level + 2) * 10)


class AuthenticSymbolTemplate(BaseModel):
    level: int
    stat_type: SymbolIndicator

    def get_stat(self):
        if self.level == 0:
            return Stat()

        if self.stat_type.value in ["INT", "LUK", "DEX", "STR"]:
            return Stat.model_validate(
                {self.stat_type.value + "_static": (self.level * 2 + 3) * 100}
            )

        raise ValueError

    def get_symbol(self) -> SymbolGear:
        return SymbolGear(stat=self.get_stat(), force=self.level * 10)
