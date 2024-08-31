from simaple.app.wasm.skill import (
    getAllSkillSpec,
    getSkillSpec,
)
import pytest

def test_get_all_skill_spec(wasm_uow):
    skill_specs = getAllSkillSpec(wasm_uow)
    assert len(skill_specs) > 1


def test_get_skill_spec(wasm_uow):
    skill_spec = getSkillSpec("2121006-0", wasm_uow)
    assert skill_spec

    with pytest.raises(ValueError):
        skill_spec = getSkillSpec("1", wasm_uow)
        assert skill_spec
