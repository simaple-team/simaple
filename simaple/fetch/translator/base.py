from abc import ABCMeta, abstractmethod

import pydantic

from simaple.core.base import ExtendedStat


class AbstractStatProvider(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def provide(self, dependency: float) -> ExtendedStat:
        ...


class NoMatchedStringError(Exception):
    ...
