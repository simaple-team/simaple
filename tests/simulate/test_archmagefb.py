import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.job.description import GeneralJobArgument
from simaple.job.spec.patch import SkillLevelPatch
from simaple.simulate.base import Actor, AddressedStore, Client, ConcreteStore, Reducer
from simaple.simulate.timer import install_timer
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch
from simaple.spec.repository import DirectorySpecRepository
from tests.simulate.schedule import get_archmagefb_schedule


def test_archmage_fb():
    loader = SpecBasedLoader(
        DirectorySpecRepository("simaple/simulate/spec/components")
    )

    components = loader.load_all(
        query={"group": "archmagefb"},
        patches=[
            SkillLevelPatch(
                job_argument=GeneralJobArgument(
                    combat_orders_level=1,
                    passive_skill_level=0,
                    character_level=260,
                ),
            ),
            EvalPatch(
                injected_values={
                    "character_level": 260,
                }
            ),
        ],
    )

    store = AddressedStore(ConcreteStore())
    reducer = Reducer(store=store)

    for component in components:
        component.add_to_reducer(reducer)

    actor = Actor()
    client = Client(reducer, actor)

    actions = get_archmagefb_schedule()
    install_timer(client)

    for action in actions:
        events = client.play(action)
        print(client.reducer.store.read_state("global.time", None))
        print(events)
