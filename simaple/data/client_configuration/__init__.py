from pathlib import Path
from typing import cast

import pydantic

from simaple.core.jobtype import JobType
from simaple.simulate.actor import DefaultMDCActor
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository


class ClientConfiguration(
    pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="ClientConfiguration")
):
    """
    ClientConfiguration
    A pre-assigned information to create specific job's components easier
    """

    v_skill_names: list[str]
    v_improvement_names: list[str]
    component_groups: list[str]
    mdc_order: list[str]

    def validate_v_skills(self, v_skills) -> bool:
        return all((k in self.v_skill_names) for k in v_skills.keys())

    def validate_v_improvements(self, v_improvements) -> bool:
        return all((k in self.v_improvement_names) for k in v_improvements.keys())

    def get_filled_v_skill(self, level: int = 30) -> dict[str, int]:
        return {k: level for k in self.v_skill_names}

    def get_filled_v_improvements(self, level: int = 60) -> dict[str, int]:
        return {k: level for k in self.v_improvement_names}

    def get_groups(self) -> list[str]:
        return self.component_groups

    def get_mdc_actor(self) -> DefaultMDCActor:
        return DefaultMDCActor(order=self.mdc_order)


def get_client_configuration(jobtype: JobType) -> ClientConfiguration:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return cast(
        ClientConfiguration,
        loader.load(
            query={"group": jobtype.value, "kind": "ClientConfiguration"},
        ),
    )
