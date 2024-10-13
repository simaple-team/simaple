import re
from typing import Any, Callable

from simaple.simulate.core.store import Checkpoint, Store

View = Callable[[Store], Any]
ViewerType = Callable[[str], Any]


class ViewSet:
    def __init__(self) -> None:
        self._views: dict[str, View] = {}

    def add_view(self, view_name: str, view: View) -> None:
        self._views[view_name] = view

    def show(self, view_name: str, store: Store) -> Any:
        return self._views[view_name](store)

    def get_views(self, view_name_pattern: str) -> list[View]:
        regex = re.compile(view_name_pattern)
        return [
            view for view_name, view in self._views.items() if regex.match(view_name)
        ]

    def get_viewer_from_ckpt(self, ckpt: Checkpoint) -> ViewerType:
        return self.get_viewer(ckpt.restore())

    def get_viewer(self, store: Store) -> ViewerType:
        def _viewer(view_name: str) -> Any:
            return self.show(view_name, store)

        return _viewer
