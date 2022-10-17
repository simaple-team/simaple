import os
import pathlib

from simaple.spec.repository import DirectorySpecRepository

CURRENT_PATH = pathlib.Path(os.path.dirname(__file__))


def test_repository():
    spec_path = CURRENT_PATH / "resources" / "specs"

    repository = DirectorySpecRepository(spec_path)
    assert repository.get(name="A").metadata.label.get("name") == "A"
    assert repository.get(name="B").metadata.label.get("name") == "B"


def test_repository_index():
    spec_path = CURRENT_PATH / "resources" / "specs"

    repository = DirectorySpecRepository(spec_path, index_key="name")
    assert repository.get(name="A").metadata.label.get("name") == "A"
    assert repository.get(name="B").metadata.label.get("name") == "B"


def test_repository_all():
    spec_path = CURRENT_PATH / "resources" / "specs"

    repository = DirectorySpecRepository(spec_path, index_key="name")
    assert len(repository.get_all(group="test_group")) == 4
