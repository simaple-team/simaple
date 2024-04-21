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
