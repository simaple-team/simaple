from simaple.job.builtin.archmagefb import job_archmagefb
from simaple.job.passive_skill import PassiveSkillArgument


def test_archmagefb():
    argument = PassiveSkillArgument(
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )
    job = job_archmagefb(argument)
