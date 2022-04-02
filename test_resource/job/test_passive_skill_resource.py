import os

import pytest
from loguru import logger

from simaple.job.passive_skill import (
    PassiveSkillArgument,
    PassiveSkillDescription,
    PassiveSkillRepository,
    PassiveSkillResource,
)

RESOURCE_DIR = "./simaple/job/builtin/resources/passive_skill"


@pytest.fixture
def passive_skill_argument():
    return PassiveSkillArgument(
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )


@pytest.mark.parametrize("resource_file_name", ["archmagefb.yaml"])
def test_passive_skill(resource_file_name, passive_skill_argument):

    repository = PassiveSkillRepository.from_file(
        os.path.join(RESOURCE_DIR, resource_file_name)
    )

    for passive_skill in repository.iterate(passive_skill_argument):
        logger.info(passive_skill.name)
