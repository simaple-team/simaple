import simaple.wasm as wasm_api
from simaple.wasm.exporter.generate import (
    export_json_schemas,
    get_every_methods_in_module,
    get_pydantic_annotations,
)


def get_wasm_signatures_in_defined_methods():
    methods = get_every_methods_in_module(wasm_api)
    pydantic_annotations = get_pydantic_annotations(methods)

    export_json_schemas(pydantic_annotations, "gen/jsonschema")


get_wasm_signatures_in_defined_methods()

