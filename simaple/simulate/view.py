from abc import ABCMeta, abstractmethod
from typing import Any

from simaple.simulate.base import Store, View, ViewSet


class AggregationView(metaclass=ABCMeta):
    def __init__(self, children: list[View]):
        self._children: list[View] = children

    def __call__(self, store: Store):
        representations = [view(store) for view in self._children]
        return self.aggregate(representations)

    @abstractmethod
    def aggregate(self, representations: list[Any]):
        """A method to aggregate matching representations"""

    @classmethod
    @abstractmethod
    def get_installation_pattern(cls) -> str:
        """A Template-method to specify which pattern may used for installation."""

    @classmethod
    def build(cls, viewset: ViewSet):
        """Build from viewset's registered view."""
        pattern = cls.get_installation_pattern()
        views = viewset.get_views(pattern)
        return cls(views)
