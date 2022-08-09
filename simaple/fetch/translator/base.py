from abc import ABCMeta, abstractmethod

import pydantic

from simaple.core.base import AnyStat


class AbstractStatProvider(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def provide(self, dependency: int) -> AnyStat:
        ...


class NoMatchedStringError(Exception):
    ...
