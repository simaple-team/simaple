import os
import pathlib
from typing import Any

from simaple.spec.repository import DirectorySpecRepository
from simaple.spec.loadable import TaggedNamespacedABCMeta
from simaple.spec.loader import SpecBasedLoader
import pydantic


CURRENT_PATH = pathlib.Path(os.path.dirname(__file__))


class ATestClass(pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta("TestClass")):
    name: str


class BTestClass(pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta("TestClass")):
    name: str
    stat: dict[str, Any]
    passive_skill_enabled: bool
    combat_orders_enabled: bool
    default_skill_level: int
    stat: dict[str, Any]


def test_repository():
    spec_path = CURRENT_PATH / "resources" / "specs"

    repository = DirectorySpecRepository(spec_path)
    loader = SpecBasedLoader(repository)

    loaded_class_a = loader.load(query={"group": "test_group", "name": "A"})
    loaded_class_b = loader.load(query={"group": "test_group", "name": "B"})

    assert isinstance(loaded_class_a, ATestClass)
    assert isinstance(loaded_class_b, BTestClass)
