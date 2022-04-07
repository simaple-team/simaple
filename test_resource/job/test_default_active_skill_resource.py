import os

import pytest
from loguru import logger

from simaple.job.passive_skill import (
    PassiveSkillArgument,
    PassiveSkillDescription,
    PassiveSkillResource,
    PassiveSkillset,
)

RESOURCE_DIR = "./simaple/job/builtin/resources/default_active_skill"


@pytest.fixture
def passive_skill_argument():
    return PassiveSkillArgument(
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )


@pytest.mark.parametrize(
    "resource_file_name",
    [
        "archmagefb.yaml",
        "archmagetc.yaml",
        "bishop.yaml",
    ],
)
def test_passive_skill(resource_file_name, passive_skill_argument):

    skill_set = PassiveSkillset.from_resource_file(
        os.path.join(RESOURCE_DIR, resource_file_name)
    )

    for passive_skill in skill_set.iterate(passive_skill_argument):
        logger.info(passive_skill.name)
