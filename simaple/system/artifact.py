from collections import defaultdict

from pydantic import BaseModel, Field, model_validator

from simaple.core import ExtendedStat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class ArtifactEffect(
    BaseModel, metaclass=TaggedNamespacedABCMeta(kind="ArtifactEffect")
):
    name: str
    effects: list[ExtendedStat]


class ArtifactCard(BaseModel):
    effects: tuple[str, str, str]
    level: int = Field(ge=1, le=5)

    def get_levels(self) -> dict[str, int]:
        return {effect: self.level for effect in self.effects}


class Artifact(BaseModel):
    cards: list[ArtifactCard]
    effects: list[ArtifactEffect]

    @model_validator(mode="after")
    def check_cards_only_contain_included_effects(self):
        all_effects = {effect.name for effect in self.effects}

        for card in self.cards:
            for effect in card.effects:
                if effect not in all_effects:
                    raise ValueError(f"effect {effect} not found in effects")
        return self

    def get_levels(self) -> dict[str, int]:
        levels: dict[str, int] = defaultdict(int)

        for card in self.cards:
            for effect, level in card.get_levels().items():
                levels[effect] = min(10, levels[effect] + level)

        return dict(levels)

    def get_extended_stat(self) -> ExtendedStat:
        _effect_map = {effect.name: effect for effect in self.effects}

        levels = self.get_levels()

        extended_stat = ExtendedStat()
        for effect_name, level in levels.items():
            effect = _effect_map[effect_name]
            extended_stat += effect.effects[level]

        return extended_stat
