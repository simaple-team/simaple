from simaple.data.jobs.patch import VSkillImprovementPatch


def test_v_patch():
    target = {
        "name": "flame swip",
        "v_improvement": 13,
        "modifier": {
            "attack_power": 30,
        },
    }

    patch = VSkillImprovementPatch(improvements={"flame swip": 52})

    output = patch.apply(target)

    assert output == {
        "name": "flame swip",
        "modifier": {
            "ignored_defence": 20,
            "attack_power": 30,
            "final_damage_multiplier": 52 * 13,
        },
    }


def test_v_patch_with_existing_multiplier():
    target = {
        "name": "flame swip",
        "v_improvement": 10,
        "modifier": {
            "final_damage_multiplier": 100,
        },
    }

    patch = VSkillImprovementPatch(improvements={"flame swip": 10})

    output = patch.apply(target)

    assert output == {
        "name": "flame swip",
        "modifier": {"final_damage_multiplier": 300},
    }
