from pydantic import BaseModel


class GeneralJobArgument(BaseModel):
    combat_orders_level: int
    passive_skill_level: int
    character_level: int
