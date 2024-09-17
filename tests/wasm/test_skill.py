import pytest

from simaple.wasm.skill import getAllSkillSpec, getSkillSpec


def test_get_all_skill_spec():
    skill_specs = getAllSkillSpec()
    assert len(skill_specs) > 1


def test_get_skill_spec():
    skill_spec = getSkillSpec("2121006-0")
    assert skill_spec

    with pytest.raises(ValueError):
        skill_spec = getSkillSpec("1")
        assert skill_spec
