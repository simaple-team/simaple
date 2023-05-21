from simaple.app.application.query.component_spec import query_all_component_schemas
from simaple.app.application.query.snapshot import query_all_snapshot
from simaple.app.domain.uow import UnitOfWork
from simaple.app.application.query.skill import get_skill
from simaple.spec.spec import Spec


def test_query_all_snapshot(uow: UnitOfWork):
    assert query_all_snapshot(uow) == []


def test_query_component_schemas(uow: UnitOfWork):
    schemas = query_all_component_schemas(uow)
    assert isinstance(schemas, dict)


def test_query_skill(uow: UnitOfWork):
    skill_spec = get_skill(uow, "2121006-0")
    assert isinstance(skill_spec, Spec)
