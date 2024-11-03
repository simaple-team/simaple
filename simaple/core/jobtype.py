import enum

from simaple.core.job_category import JobCategory


class JobType(enum.Enum):
    hero = "hero"
    darkknight = "darkknight"
    paladin = "paladin"

    bishop = "bishop"
    archmagefb = "archmagefb"
    archmagetc = "archmagetc"

    nightlord = "nightlord"
    shadower = "shadower"
    dualblade = "dualblade"

    bowmaster = "bowmaster"
    sniper = "sniper"
    pathfinder = "pathfinder"

    corsair = "corsair"  # Captain
    buccaneer = "buccaneer"  # viper
    cannoneer = "cannoneer"  # Cannon shooter

    soulmaster = "soulmaster"
    flamewizard = "flamewizard"
    windbreaker = "windbreaker"
    nightwalker = "nightwalker"
    striker = "striker"

    mihile = "mihile"

    demonavenger = "demonavenger"
    demonslayer = "demonslayer"

    battlemage = "battlemage"
    wildhunter = "wildhunter"
    mechanic = "mechanic"
    zenon = "zenon"
    blaster = "blaster"

    evan = "evan"
    luminous = "luminous"
    mercedes = "mercedes"
    phantom = "phantom"
    eunwol = "eunwol"
    aran = "aran"

    kaiser = "kaiser"
    kain = "kain"
    cadena = "cadena"
    angelicbuster = "angelicbuster"

    adele = "adele"
    illium = "illium"
    ark = "ark"

    lara = "lara"
    hoyoung = "hoyoung"
    khali = "khali"

    zero = "zero"
    kinesis = "kinesis"

    virtual_maplestory_m = "virtual_maplestory_m"


__JOB_CATEGORY_FROM_TYPE: dict[JobType, JobCategory] = {
    JobType.hero: JobCategory.warrior,
    JobType.darkknight: JobCategory.warrior,
    JobType.paladin: JobCategory.warrior,
    JobType.bishop: JobCategory.magician,
    JobType.archmagefb: JobCategory.magician,
    JobType.archmagetc: JobCategory.magician,
    JobType.nightlord: JobCategory.thief,
    JobType.shadower: JobCategory.thief,
    JobType.dualblade: JobCategory.thief,
    JobType.bowmaster: JobCategory.archer,
    JobType.sniper: JobCategory.archer,
    JobType.pathfinder: JobCategory.archer,
    JobType.corsair: JobCategory.pirate,
    JobType.buccaneer: JobCategory.pirate,
    JobType.cannoneer: JobCategory.pirate,
    JobType.soulmaster: JobCategory.warrior,
    JobType.flamewizard: JobCategory.magician,
    JobType.windbreaker: JobCategory.archer,
    JobType.nightwalker: JobCategory.thief,
    JobType.striker: JobCategory.pirate,
    JobType.mihile: JobCategory.warrior,
    JobType.demonavenger: JobCategory.warrior,
    JobType.demonslayer: JobCategory.warrior,
    JobType.battlemage: JobCategory.magician,
    JobType.wildhunter: JobCategory.archer,
    JobType.mechanic: JobCategory.pirate,
    JobType.zenon: JobCategory.pirate,  # Zenon ?
    JobType.blaster: JobCategory.warrior,
    JobType.evan: JobCategory.magician,
    JobType.luminous: JobCategory.magician,
    JobType.mercedes: JobCategory.archer,
    JobType.phantom: JobCategory.thief,
    JobType.eunwol: JobCategory.thief,
    JobType.aran: JobCategory.warrior,
    JobType.kaiser: JobCategory.warrior,
    JobType.kain: JobCategory.archer,
    JobType.cadena: JobCategory.thief,
    JobType.angelicbuster: JobCategory.pirate,
    JobType.adele: JobCategory.warrior,
    JobType.illium: JobCategory.magician,
    JobType.ark: JobCategory.pirate,
    JobType.lara: JobCategory.magician,
    JobType.hoyoung: JobCategory.thief,
    JobType.khali: JobCategory.thief,
    JobType.zero: JobCategory.warrior,
    JobType.kinesis: JobCategory.magician,
}


def get_job_category(jobtype: JobType) -> JobCategory:
    return __JOB_CATEGORY_FROM_TYPE[jobtype]


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
    "캐논마스터": JobType.cannoneer,
    "미하일": JobType.mihile,
    "듀얼블레이더": JobType.dualblade,
    "듀얼블레이드": JobType.dualblade,
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
    "라라": JobType.lara,
    "카인": JobType.kain,
    "호영": JobType.hoyoung,
    "칼리": JobType.khali,
    "모바일 캐릭터": JobType.virtual_maplestory_m,
}


def translate_kms_name(job_name: str) -> JobType:
    return _kms_job_names[job_name]
