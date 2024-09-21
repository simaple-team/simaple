import simaple.wasm as wasm_api
from simaple.wasm.base import ErrorResponse, SuccessResponse
from simaple.wasm.exporter.generate import (
    export_json_schemas,
    get_every_methods_in_module,
    get_pydantic_annotations,
)


def get_manual_annotations():
    '''
    This function is used to add manual annotations that are not detected by the get_pydantic_annotations function.
    Especially for decorator-related annotations.
    '''
    return [ErrorResponse]


def get_disallowed_annotations():
    '''
    This function is used to filter out annotations that are not allowed to be exported to JSON schema.
    Especially for generics.
    '''
    return [SuccessResponse]


def get_wasm_signatures_in_defined_methods():
    methods = get_every_methods_in_module(wasm_api)
    pydantic_annotations = set(get_pydantic_annotations(methods) + get_manual_annotations()) - set(get_disallowed_annotations())

    export_json_schemas(list(pydantic_annotations), "gen/jsonschema")


get_wasm_signatures_in_defined_methods()

