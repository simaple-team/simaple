from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.base import Usecase
from simaple.container.usecase.builtin import (
    adele,
    archmagefb,
    archmagetc,
    bishop,
    dualblade,
    mechanic,
    soulmaster,
    windbreaker,
)
from simaple.core import ActionStat, ExtendedStat, JobType, Stat
from simaple.simulate.component.view import (
    BuffParentView,
    InformationParentView,
    KeydownParentView,
    RunningParentView,
    ValidityParentView,
)
from simaple.simulate.kms import bare_store, get_builder
from simaple.simulate.timer import clock_view, timer_delay_dispatcher


def get_usecase(environment: SimulationEnvironment) -> Usecase:
    match environment.jobtype:
        case JobType.mechanic:
            return mechanic.mechanic_usecase(environment)
        case JobType.archmagefb:
            return archmagefb.archmagefb_usecase(environment)
        case JobType.archmagetc:
            return archmagetc.archmagetc_usecase(environment)
        case JobType.bishop:
            return bishop.bishop_usecase(environment)
        case JobType.adele:
            return adele.adele_usecase(environment)
        case JobType.windbreaker:
            return windbreaker.windbreaker_usecase(environment)
        case JobType.soulmaster:
            return soulmaster.soulmaster_usecase(environment)
        case JobType.dualblade:
            return dualblade.dualblade_usecase(environment)
        case _:
            raise ValueError(f"Unsupported job type: {environment.jobtype}")


def get_engine(environment: SimulationEnvironment):
    usecase = get_usecase(environment)

    usecase.listen(("*", "elapse"), timer_delay_dispatcher)
    usecase.add_view("clock", clock_view)

    usecase.add_view("info", InformationParentView.build(usecase.build_viewset()))
    usecase.add_view("validity", ValidityParentView.build(usecase.build_viewset()))
    usecase.add_view("buff", BuffParentView.build(usecase.build_viewset()))
    usecase.add_view("running", RunningParentView.build(usecase.build_viewset()))
    usecase.add_view("keydown", KeydownParentView.build(usecase.build_viewset()))

    store = bare_store(environment.character.action_stat)
    return usecase.create_engine(store)
