import os

import pytest

from simaple.job.builtin.util import parse_resource_path


def test_parse_resource():
    parse_resource_path("passive_skill/archmagefb")


def test_parse_not_existing_resource():
    with pytest.raises(FileNotFoundError):
        parse_resource_path("passive_skill/archmagefb-not-existing-dummy")
