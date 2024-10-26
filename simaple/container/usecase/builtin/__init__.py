from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.builtin import archmagefb, mechanic
from simaple.core import ActionStat, ExtendedStat, JobType, Stat


def get_engine(environment: SimulationEnvironment):
    match environment.jobtype:
        case JobType.mechanic:
            return mechanic.mechanic_engine(environment)
        case JobType.archmagefb:
            return archmagefb.archmagefb_engine(environment)
        case _:
            raise ValueError(f"Unsupported job type: {environment.jobtype}")
