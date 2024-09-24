import pydantic

from simaple.simulate.strategy.base import PolicyWrapper
from simaple.simulate.strategy.default import normal_default_ordered_policy
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class BuiltinStrategy(pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="BuiltinStrategy")):
    """
    BuiltinStrategy
    Pre-defined Operation generation strategy for
    Fast tutorial and easy execution

    normal_default_order:
      Define normal-default-skill order (maplestory_dpm_calc - style order)
    """

    normal_default_order: list[str] = pydantic.Field(default_factory=list)

    def get_priority_based_policy(self) -> PolicyWrapper:
        return PolicyWrapper(normal_default_ordered_policy(order=self.normal_default_order))
