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

    @view_method
    def info(self, _: Any) -> ComponentInformation:
        return cast(ComponentInformation, self.model_dump())
