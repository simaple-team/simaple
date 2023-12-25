import json
import os
from typing import Any

import pytest


def _macro_get_response(file_name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "resource", file_name)
    with open(path, "r", encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def character_hyper_stat_response() -> dict[str, Any]:
    return _macro_get_response("hyperstat.json")


@pytest.fixture
def character_propensity_response() -> dict[str, Any]:
    return _macro_get_response("propensity.json")
