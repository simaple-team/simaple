from typing import Optional, TypedDict

from simaple.core.base import Stat
from simaple.simulate.component.base import Component, view_method
from simaple.simulate.component.view import Running


class NoState(TypedDict):
    ...


class AlwaysEnabledComponent(Component):
    id: str
    stat: Stat

    def get_default_state(self) -> NoState:
        return {}

    @view_method
    def buff(self, _: NoState) -> Optional[Stat]:
        return self.stat

    @view_method
    def running(self, _: NoState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=999_999_999,
            lasting_duration=999_999_999,
        )
