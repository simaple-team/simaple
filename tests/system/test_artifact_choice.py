import pytest

from simaple.core import ExtendedStat, Stat
from simaple.system.artifact import Artifact, ArtifactCard, ArtifactEffect
from simaple.system.optimal_artifact import get_optimal_artifact_generator


def test_artifact_generator():
    generator = get_optimal_artifact_generator()

    generator.get_optimal_artifact(
        12, ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    )


def test_artifact():
    artifact = Artifact(
        cards=[
            ArtifactCard(effects=("A", "B", "C"), level=1),
            ArtifactCard(effects=("D", "E", "F"), level=2),
        ],
        effects=[
            ArtifactEffect(
                name=effect_name,
                effects=[
                    ExtendedStat(stat=Stat(INT=idx * effect_idx)) for idx in range(11)
                ],
            )
            for effect_idx, effect_name in enumerate("ABCDEFGHI")
        ],
    )

    assert artifact.get_extended_stat() == ExtendedStat(
        stat=Stat(INT=1 * (0 + 1 + 2) + 2 * (3 + 4 + 5))
    )


def test_artifact_fails_validation():
    with pytest.raises(ValueError):
        Artifact(
            cards=[
                ArtifactCard(effects=("A", "B", "C"), level=1),
                ArtifactCard(effects=("D", "E", "F"), level=2),
            ],
            effects=[
                ArtifactEffect(
                    name=effect_name,
                    effects=[
                        ExtendedStat(stat=Stat(INT=idx * effect_idx))
                        for idx in range(11)
                    ],
                )
                for effect_idx, effect_name in enumerate("ABCDE")
            ],
        )
