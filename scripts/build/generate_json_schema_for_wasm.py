import simaple.api as wasm_api
from simaple.api.exporter.generate import (
    export_json_schemas,
    get_every_methods_in_module,
    get_pydantic_annotations,
)


def get_wasm_signatures_in_defined_methods():
    methods = get_every_methods_in_module(wasm_api)
    pydantic_annotations = set(get_pydantic_annotations(methods))

    export_json_schemas(list(pydantic_annotations), "gen/jsonschema")


get_wasm_signatures_in_defined_methods()

