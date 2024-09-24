import inspect
import json
import os
import types
from typing import Type

import pydantic


def get_every_methods_in_module(module):
    methods = []
    for method_names in module.__all__:
        methods.append(getattr(module, method_names))

    return methods


def _unpack_annot(annotations: list):
    unpacked_annotations: list = []

    for annotation in annotations:
        if type(annotation) == type:
            unpacked_annotations += [annotation]

        elif isinstance(annotation, types.GenericAlias):
            unpacked_annotations += _unpack_annot([generic_types for generic_types in annotation.__args__ if generic_types is not None])
        else:
            unpacked_annotations.append(annotation)

    return unpacked_annotations


def get_pydantic_annotations(methods: list) -> list[Type[pydantic.BaseModel]]:
    annots = []
    for method in methods:
        for k, v in inspect.signature(method).parameters.items():
            annots.append(v.annotation)

        annots.append(inspect.signature(method).return_annotation)

    pydantic_types_only = list(set([annot for annot in _unpack_annot(annots) if type(annot) != type and annot is not None]))

    return pydantic_types_only


def export_json_schemas(pydantic_types: list[Type[pydantic.BaseModel]], dirname: str):
    for pydantic_type in pydantic_types:
        json_schema = pydantic_type.model_json_schema()
        with open(os.path.join(dirname, str(pydantic_type.__name__) + ".schema.json"), "w") as f:
            json.dump(json_schema, f, indent=2)
