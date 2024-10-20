from typing import Any, Optional, cast

from simaple.core.base import Stat
from simaple.simulate.component.base import Component, view_method
from simaple.simulate.component.view import ComponentInformation, Validity
from simaple.simulate.event import NamedEventProvider


class SkillComponent(Component):
    disable_validity: bool = False
    modifier: Optional[Stat] = None
    cooldown_duration: float
    delay: float
    id: str

    @property
    def event_provider(self) -> NamedEventProvider:
        return NamedEventProvider(self.name, self.modifier)

    def invalidate_if_disabled(self, validity: Validity):
        if self.disable_validity:
            validity = validity.model_copy()
            validity.valid = False
            return validity

        return validity

    @view_method
    def info(self, _: Any) -> ComponentInformation:
        return cast(ComponentInformation, self.model_dump())
