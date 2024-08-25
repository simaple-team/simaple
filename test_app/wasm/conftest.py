import pytest

from simaple.app.wasm.base import createUow

@pytest.fixture
def wasm_uow():
    return createUow()
