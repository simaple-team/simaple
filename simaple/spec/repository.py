from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional

import yaml

from simaple.spec.spec import Spec


class SpecRepository(metaclass=ABCMeta):
    @abstractmethod
    def get(self, **kwargs) -> Spec:
        ...


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
            self._db.append(self._load_specification(path))

    def create_index(self, index_key):
        index_map = {}
        for document in self._db:
            if document.metadata.label[index_key] in index_map:
                raise KeyError("Index must unique")
            index_map[document.metadata.label[index_key]] = document

        self._index[index_key] = index_map

    def _get_specification_paths(self, base_path: str):
        return Path(base_path).rglob("*.yaml")

    def _load_specification(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8") as f:
            raw_configuration = yaml.safe_load(f)

        return Spec.parse_obj(raw_configuration)

    def get(self, **kwargs) -> Spec:
        for k, v in kwargs.items():
            if k in self._index:
                spec = self._index[k][v]
                return spec.copy()

        for spec in self._db:
            if spec.metadata.matches(**kwargs):
                return spec.copy()

        return None
