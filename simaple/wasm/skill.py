from simaple.data.jobs.builtin import get_kms_jobs_repository
from simaple.simulate.component.base import Component


def getAllComponent() -> list[Component]:
    skill_specs = get_kms_jobs_repository().get_all(kind="Component")

    return [skill_spec.data for skill_spec in skill_specs]
