import pytest

from simaple.app.wasm.base import createUow

@pytest.fixture
def wasm_uow(character_provider_cache_location: str):
    return createUow(character_provider_cache_location)
