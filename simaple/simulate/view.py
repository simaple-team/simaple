from abc import ABCMeta, abstractmethod
from typing import Any

from simaple.simulate.base import Environment, Store, View


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
    def build(cls, environment: Environment):
        """Build from environment's registered view."""
        pattern = cls.get_installation_pattern()
        views = environment.get_views(pattern)
        return cls(views)

    @classmethod
    def build_and_install(cls, environment: Environment, name: str):
        """Build from environment's registered view, and install into environment.
        This is utility-level function; this only prevent code duplication.
        """
        my_view = cls.build(environment)
        environment.add_view(name, my_view)
