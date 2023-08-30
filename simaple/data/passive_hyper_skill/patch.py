from simaple.data.passive_hyper_skill.spec import PassiveHyperskillInterface
from simaple.spec.patch import Patch


class PassiveHyperskillPatch(Patch):
    hyper_skills: list[PassiveHyperskillInterface]

    def apply(self, raw: dict) -> dict:
        output = raw
        skill_name = raw["name"]
        for hyper_skill in self.hyper_skills:
            if hyper_skill.get_target_name() == skill_name:
                output = hyper_skill.modify(output)

        return output
