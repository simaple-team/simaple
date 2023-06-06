import copy

from simaple.character.character import AbstractCharacter
from simaple.core import JobType
from simaple.core.base import Stat
from simaple.fetch.translator.gear import GearTranslator
from simaple.gear.gear import Gear
from simaple.gear.setitem import KMSSetItemRepository
from simaple.gear.slot_name import SlotName

RawType = dict


def _get_level(raw_data: RawType) -> int:
    return raw_data["character"]["level"]


def _get_ability_stat(raw_data: RawType) -> Stat:
    ability = raw_data["character"]["ability"]
    level = _get_level(raw_data)

    base_stat = Stat(
        STR_static=ability["STR_static"],
        DEX_static=ability["DEX_static"],
        INT_static=ability["INT_static"],
        LUK_static=ability["LUK_static"],
        MHP=ability["MHP"],
        MMP=ability["MMP"],
        attack_power=ability["attack_power"],
        magic_attack=ability["magic_attack"],
        critical_rate=ability["critical_rate"],
        boss_damage_multiplier=ability["boss_damage_multiplier"],
    )

    if ability["relativeAttackPower"] > 0:
        base_stat += Stat(attack_power=level // ability["relativeAttackPower"])

    if ability["relativeMagicAttack"] > 0:
        base_stat += Stat(attack_power=level // ability["relativeMagicAttack"])

    return base_stat


def _get_hyperstat(raw_data: RawType) -> Stat:
    hyperstat = raw_data["character"]["hyperstat"]

    return Stat(
        STR_static=hyperstat["STR_static"],
        DEX_static=hyperstat["DEX_static"],
        INT_static=hyperstat["INT_static"],
        LUK_static=hyperstat["LUK_static"],
        MHP_multiplier=hyperstat["MHP_multiplier"],
        MMP_multiplier=hyperstat["MMP_multiplier"],
        attack_power=hyperstat["attack_power"],
        magic_attack=hyperstat["magic_attack"],
        critical_rate=hyperstat["critical_rate"],
        critical_damage=hyperstat["critical_damage"],
        boss_damage_multiplier=hyperstat["boss_damage_multiplier"],
        ignored_defence=hyperstat["ignored_defence"],
        damage_multiplier=hyperstat["damage_multiplier"],
    )


_kms_job_names: dict[str, JobType] = {
    "아크메이지(불,독)": JobType.archmagefb,
    "아크메이지(썬,콜)": JobType.archmagetc,
    "히어로": JobType.hero,
    "팔라딘": JobType.paladin,
    "신궁": JobType.sniper,
    "윈드브레이커": JobType.windbreaker,
    "소울마스터": JobType.soulmaster,
    "바이퍼": JobType.buccaneer,
    "플레임위자드": JobType.flamewizard,
    "나이트로드": JobType.nightlord,
    "메르세데스": JobType.mercedes,
    "루미너스": JobType.luminous,
    "비숍": JobType.bishop,
    "배틀메이지": JobType.battlemage,
    "메카닉": JobType.mechanic,
    "데몬슬레이어": JobType.demonslayer,
    "다크나이트": JobType.darkknight,
    "와일드헌터": JobType.wildhunter,
    "섀도어": JobType.shadower,
    "캐논슈터": JobType.cannoneer,
    "미하일": JobType.mihile,
    "듀얼블레이더": JobType.dualblade,
    "카이저": JobType.kaiser,
    "캡틴": JobType.corsair,
    "엔젤릭버스터": JobType.angelicbuster,
    "팬텀": JobType.phantom,
    "은월": JobType.eunwol,
    "나이트워커": JobType.nightwalker,
    "스트라이커": JobType.striker,
    "에반": JobType.evan,
    "보우마스터": JobType.bowmaster,
    "제로": JobType.zero,
    "키네시스": JobType.kinesis,
    "일리움": JobType.illium,
    "패스파인더": JobType.pathfinder,
    "카데나": JobType.cadena,
    "아크": JobType.ark,
    "블래스터": JobType.blaster,
    "아란": JobType.aran,
    "데몬어벤져": JobType.demonavenger,
    "제논": JobType.zenon,
    "아델": JobType.adele,
}


def _get_jobtype(raw_data: RawType) -> JobType:
    job_class, korean_job_name = raw_data["character"]["overview"]["job"].split("/")
    return _kms_job_names[korean_job_name]


class CharacterResponse(AbstractCharacter):
    def __init__(self, raw: RawType, gear_translator: GearTranslator):
        self._raw = raw
        self._gear_translator = gear_translator

    def get_jobtype(self) -> JobType:
        return _get_jobtype(self._raw)

    def get_character_base_stat(self):
        return self._raw["character"]["stat"]

    def get_maximum_attack_range(self) -> int:
        return self._raw["character"]["stat"]["max_damage_factor"]

    def get_level(self) -> int:
        return self._raw["character"]["level"]

    def is_reboot(self) -> bool:
        return "리부트" in self._raw["character"]["overview"]["world"]

    def get_item(self, slot_name: SlotName) -> Gear:
        dumped = self._raw["item"].get(slot_name.value)
        return self._gear_translator.translate(dumped)

    def get_raw(self):
        return copy.deepcopy(self._raw)

    def get_ability_stat(self) -> Stat:
        return _get_ability_stat(self._raw)

    def get_hyperstat(self) -> Stat:
        return _get_hyperstat(self._raw)

    def get_all_item_stat(self) -> Stat:
        gears: list[Gear] = []

        for k, v in self._raw["item"].items():
            if k.startswith("cash"):
                continue

            gears.append(self._gear_translator.translate(v))

        for k, v in self._raw["pet"].items():
            gears.append(self._gear_translator.translate(v))

        total_stat = Stat()
        for gear in gears:
            total_stat += gear.sum_stat()

        set_items = KMSSetItemRepository().get_set_item_counts(gears)

        for set_item, count in set_items:
            effect = set_item.get_effect(count)
            total_stat += effect

        return total_stat
