import simaple.simulate.component.common  # noqa: F401
import simaple.simulate.component.specific  # noqa: F401
from simaple.container.simulation import SimulationEnvironment
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
from simaple.core import JobType
from simaple.core.base import ActionStat
from simaple.simulate.component.view import (
    AccessiblityParentView,
    BuffParentView,
    InformationParentView,
    KeydownParentView,
    RunningParentView,
    ValidityParentView,
)
from simaple.simulate.core.store import AddressedStore, ConcreteStore
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.timer import clock_view, timer_delay_dispatcher
from simaple.simulate.usecase import Usecase


def bare_store(action_stat: ActionStat) -> AddressedStore:
    store = AddressedStore(ConcreteStore())
    GlobalProperty(action_stat).install_global_properties(store)
    return store


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
    usecase.add_view(
        "accessiblity", AccessiblityParentView.build(usecase.build_viewset())
    )

    store = bare_store(environment.character.action_stat)
    return usecase.create_engine(store)
