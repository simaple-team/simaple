from simaple.app.application.query.snapshot import query_all_snapshot
from simaple.app.domain.uow import UnitOfWork


def test_query_all_snapshot(uow: UnitOfWork):
    assert query_all_snapshot(uow) == []
