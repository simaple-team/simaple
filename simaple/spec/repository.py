from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional

import yaml

from simaple.spec.spec import Spec


class SpecRepository(metaclass=ABCMeta):
    @abstractmethod
    def get(self, **kwargs) -> Optional[Spec]:
        """Get first Spec with given constraint"""

    @abstractmethod
    def get_all(self, **kwargs) -> list[Spec]:
        """Get every Spec with given constraint"""


class DirectorySpecRepository(SpecRepository):
    """In-source defined specification repository interface.
    This is simple inmemory document DB.
    """

    def __init__(
        self,
        relative_location: str,
        index_key: Optional[str] = None,
    ):
        self._db: list[Spec] = []
        self._index: dict[str, dict[str, Spec]] = {}

        self.load(relative_location)

        if index_key:
            self.create_index(index_key)

    def load(self, base_path):
        for path in self._get_specification_paths(base_path):
            for spec in self._load_specifications(path):
                self._db.append(spec)

    def create_index(self, index_key):
        index_map = {}
        for document in self._db:
            if document.metadata.label[index_key] in index_map:
                raise KeyError("Index must unique")
            index_map[document.metadata.label[index_key]] = document

        self._index[index_key] = index_map

    def _get_specification_paths(self, base_path: str):
        return Path(base_path).rglob("*.yaml")

    def _load_specifications(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                raw_configurations = yaml.safe_load_all(f)
                for raw_configuration in raw_configurations:
                    yield Spec.parse_obj(raw_configuration)
            except Exception as e:
                raise ValueError(f"{file_path} loading failed.") from e

    def get(self, kind=None, **kwargs) -> Optional[Spec]:
        for k, v in kwargs.items():
            if k in self._index:
                spec = self._index[k][v]
                return spec.copy()

        for spec in self._db:
            if kind is not None and spec.kind != kind:
                continue
            if spec.metadata.matches(**kwargs):
                return spec.copy()

        return None

    def get_all(self, kind=None, **kwargs) -> list[Spec]:
        specs = []
        for spec in self._db:
            if kind is not None and spec.kind != kind:
                continue
            if spec.metadata.matches(**kwargs):
                specs.append(spec.copy())

        return specs
