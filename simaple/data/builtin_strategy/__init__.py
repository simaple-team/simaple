from pathlib import Path
from typing import cast

import pydantic

from simaple.core import JobType
from simaple.simulate.strategy.base import PolicyWrapper
from simaple.simulate.strategy.default import normal_default_ordered_policy
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository


class BuiltinStrategy(
    pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="BuiltinStrategy")
):
    """
    BuiltinStrategy
    Pre-defined Operation generation strategy for
    Fast tutorial and easy execution

    normal_default_order:
      Define normal-default-skill order (maplestory_dpm_calc - style order)
    """

    normal_default_order: list[str] = pydantic.Field(default_factory=list)

    def get_priority_based_policy(self) -> PolicyWrapper:
        return PolicyWrapper(
            normal_default_ordered_policy(order=self.normal_default_order)
        )


def get_builtin_strategy(jobtype: JobType) -> BuiltinStrategy:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return cast(
        BuiltinStrategy,
        loader.load(
            query={"group": jobtype.value, "kind": "BuiltinStrategy"},
        ),
    )
