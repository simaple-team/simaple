import os

from simaple.core import JobType


def _get_example_files() -> dict[JobType, str]:
    example_dir = os.path.join(os.path.dirname(__file__), "examples", "30s")
    example_plan_files = os.listdir(example_dir)

    example_plans = {}
    for file_name in example_plan_files:
        with open(os.path.join(example_dir, file_name), encoding="utf-8") as f:
            plan = f.read()

        example_plans[JobType(file_name.split(".")[0])] = plan

    return example_plans


_EXAMPLE_FILES = _get_example_files()


def get_example_plan(jobtype: JobType) -> str:
    return _EXAMPLE_FILES[jobtype]
