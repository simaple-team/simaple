from pathlib import Path
from typing import cast

import pydantic
import yaml

from simaple.system.artifact import ArtifactCard


class _ArtifactCardChoice(pydantic.BaseModel):
    targets: tuple[int, int, int]
    level: int


class _OptimalChoice(pydantic.BaseModel):
    artifact_level: int
    distribution: list[_ArtifactCardChoice]


def _load_optimal_artifact_from_yaml(path: str) -> list[_OptimalChoice]:
    with open(Path(__file__).parent / path) as file:
        objects = yaml.safe_load(file)

    return [_OptimalChoice.model_validate(obj) for obj in objects]


class OptimalArtifactGenerator:
    def __init__(self, optimal_choices: list[_OptimalChoice]):
        self.optimal_choices = list(
            sorted(optimal_choices, key=lambda x: x.artifact_level)
        )

    def _choice_to_artifact_card(
        self, choice: _ArtifactCardChoice, card_priorities: list[str]
    ) -> ArtifactCard:
        return ArtifactCard(
            effects=cast(
                tuple[str, str, str],
                [
                    card_priorities[idx - 1]
                    for idx in choice.targets  # 1-indexed to 0-indexed
                ],
            ),
            level=choice.level,
        )

    def get_optimal_artifact(
        self, artifact_level: int, card_priorities: list[str]
    ) -> list[ArtifactCard]:
        if self.optimal_choices[0].artifact_level > artifact_level:
            return []

        for choice in self.optimal_choices:
            if choice.artifact_level <= artifact_level:
                target_choice = choice
            else:
                break

        return [
            self._choice_to_artifact_card(choice, card_priorities)
            for choice in target_choice.distribution
        ]


# Static file replaces complex algorithm
_FILE_NAME = "artifact_distribution.yaml"
_optimal_artifact_generator: OptimalArtifactGenerator = OptimalArtifactGenerator(
    _load_optimal_artifact_from_yaml(_FILE_NAME)
)


def get_optimal_artifact_generator() -> OptimalArtifactGenerator:
    """
    Returns the optimal artifact generator.
    This caches the generator for multiple calls.
    """
    return _optimal_artifact_generator
