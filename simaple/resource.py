from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Extra

T = TypeVar("T")


class DescriptionArgument(BaseModel):
    ...


U = TypeVar("U", bound=DescriptionArgument)


class Description(BaseModel, Generic[T, U]):
    class Config:
        extra = Extra.forbid

    def interpret(self, argument: U) -> T:
        ...


D = TypeVar("D", bound=Description)


class SimapleMetadata(BaseModel):
    group: Optional[str]


class SimapleResource(BaseModel, Generic[D]):
    class Config:
        extra = Extra.forbid

    kind: str
    version: str
    metadata: SimapleMetadata
    data: List[D]
