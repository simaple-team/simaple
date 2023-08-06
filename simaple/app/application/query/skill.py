from typing import Optional

from simaple.app.domain.uow import UnitOfWork
from simaple.spec.spec import Spec


def get_skill(uow: UnitOfWork, skill_id: str) -> Optional[Spec]:
    skill_spec = uow.spec_repository().get(id=skill_id)

    return skill_spec


def get_all_skill(uow: UnitOfWork) -> list[Spec]:
    skill_specs = uow.spec_repository().get_all()

    return skill_specs
