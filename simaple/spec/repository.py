import copy
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, Optional

import yaml


class SpecRepository(metaclass=ABCMeta):
    @abstractmethod
    def get(self, **kwargs) -> dict[Any, Any]:
        ...


class DirectorySpecRepository(SpecRepository):
    """In-source defined specification repository interface.
    This is simple inmemory document DB.
    """

    def __init__(
        self,
        relative_location: str,
        index_key: Optional[str] = None,
        metadata_key="metadata",
    ):
        self._db = []
        self._index: dict[str, dict[str, Any]] = {}
        self._metadata_key = metadata_key

        self.load(relative_location)

        if index_key:
            self.create_index(index_key)

    def load(self, base_path):
        for path in self._get_specification_paths(base_path):
            self._db.append(self._load_specification(path))

    def create_index(self, index_key):
        index_map = {}
        for document in self._db:
            if document[self._metadata_key][index_key] in index_map:
                raise KeyError("Index must unique")
            index_map[document[self._metadata_key][index_key]] = document

        self._index[index_key] = index_map

    def _get_specification_paths(self, base_path: str):
        return Path(base_path).rglob("*.yaml")

    def _load_specification(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8") as f:
            raw_configuration = yaml.safe_load(f)

        return raw_configuration

    def get(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._index:
                value = self._index[k][v]
                return copy.deepcopy(value)

        for document in self._db:
            if all(document[self._metadata_key].get(k) == v for k, v in kwargs.items()):
                return document

        return None
