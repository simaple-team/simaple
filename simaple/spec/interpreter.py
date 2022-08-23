import pydantic

from simaple.spec.patch import Patch


class Interpreter(pydantic.BaseModel):
    patches: list[Patch]

    def interpret(self, raw):
        spec = raw["spec"]
        for patch in self.patches:
            spec = patch.apply(spec)

        return spec
