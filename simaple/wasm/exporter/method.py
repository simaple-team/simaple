import inspect

import simaple.wasm as wasm_api

method = wasm_api.runSimulatorWithPlanConfig

print(inspect.signature(method).parameters)
print(inspect.signature(method).return_annotation)
v = inspect.signature(method).return_annotation
print(type(v))
type(v)
x = v.__args__
print(x)

annots = []

for method in methods:
    for k, v in inspect.signature(method).parameters.items():
        annots.append(v.annotation)

    annots.append(inspect.signature(method).return_annotation)


pydantic_types_only = list(
    set([annot for annot in _unpack_annot(annots) if type(annot) != type])
)
for pydantic_type in pydantic_types_only:
    json_schema = pydantic_type.model_json_schema()
    import json

    with open(
        "/Users/meson324/program/simaple/gen/jsonschema/"
        + str(pydantic_type.__name__)
        + ".schema.json",
        "w",
    ) as f:
        json.dump(json_schema, f, indent=2)
