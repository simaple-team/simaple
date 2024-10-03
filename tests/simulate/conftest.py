import pytest

import simaple.simulate.component.common  # noqa: F401
import simaple.simulate.component.specific  # noqa: F401
from simaple.spec.repository import DirectorySpecRepository


@pytest.fixture(scope="package")
def component_repository():
    return DirectorySpecRepository("simaple/data/skill/resources/components")
