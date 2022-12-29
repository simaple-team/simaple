# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.spec.repository import DirectorySpecRepository


@pytest.fixture(scope="package")
def component_repository():
    return DirectorySpecRepository("simaple/data/skill/resources/components")
