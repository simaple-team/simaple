from pydantic import BaseModel



class AbstractStat(BaseModel):
    ...


class Stat(AbstractStat):
    STR: float
    LUK: float
    INT: float
    DEX: float

    attack_power: float
    magic_attack: float

    critical_rate: float
    critical_damage: float

    boss_damage: float
    damage: float

    ignored_defence: float
