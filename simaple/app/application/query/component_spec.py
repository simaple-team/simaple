from simaple.app.domain.component_schema import ComponentSchema
from simaple.app.domain.uow import UnitOfWork


def query_all_component_schemas(uow: UnitOfWork) -> dict[str, ComponentSchema]:
    schemas = uow.component_schema_repository().get_all()
    return {schema.name: schema.value for schema in schemas}
