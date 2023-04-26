from typing import Optional

from simaple.app.domain.uow import UnitOfWork
from simaple.spec.spec import Spec


def get_skill(uow: UnitOfWork, skill_id: int) -> Optional[Spec]:
    skill_spec = uow.spec_repository().get(id=skill_id)

    return skill_spec
