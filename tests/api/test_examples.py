from simaple.api.examples import get_example_plan
from simaple.core import JobType


def test_get_example_plans():
    result = get_example_plan(JobType("archmagetc"))
    assert len(result) > 0
