from pydantic import BaseModel

from simaple.core import BaseStatType, Stat


class AuthenticSymbol(BaseModel):
    level: int
    stat_type: BaseStatType

    def get_stat(self):
        if self.level == 0:
            return Stat()

        if self.stat_type.value in ["INT", "LUK", "DEX", "STR"]:
            return Stat.parse_obj(
                {self.stat_type.value + "_static": (self.level * 2 + 3) * 100}
            )

        raise ValueError

    def get_force(self):
        return self.level * 10
