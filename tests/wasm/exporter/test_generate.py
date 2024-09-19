import tests.wasm.exporter.sample_module as some_test_module
from simaple.wasm.exporter.generate import (
    get_every_methods_in_module,
    get_pydantic_annotations,
    export_json_schemas,
)
import tempfile
import os


def test_get_every_methods_in_module():
    all_methods = get_every_methods_in_module(some_test_module)
    assert len(all_methods) == 5


def test_get_every_pydantic_annotations():
    all_methods = get_every_methods_in_module(some_test_module)
    all_pydantic_annotations = get_pydantic_annotations(all_methods)
    assert set(
        annot.__name__
        for annot in all_pydantic_annotations
    ) == {"A", "B", "C"}


def test_write_down_json_schemas():
    with tempfile.TemporaryDirectory() as tmpdirname:
        all_methods = get_every_methods_in_module(some_test_module)
        all_pydantic_annotations = get_pydantic_annotations(all_methods)
        export_json_schemas(all_pydantic_annotations, tmpdirname)
        assert set(os.listdir(tmpdirname)) == {"A.schema.json", "B.schema.json", "C.schema.json"}
