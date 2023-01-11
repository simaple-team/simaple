from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.entity import Consumable, Periodic, Stack
from simaple.simulate.component.trait.base import (
    DelayTrait,
    EventProviderTrait,
    LastingTrait,
)
from simaple.simulate.component.trait.impl import ConsumableValidityTrait
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class HowlingGaleState(ReducerState):
    consumable: Consumable
    stack: Stack
    periodic: Periodic
    dynamics: Dynamics


class HowlingGaleComponent(
    SkillComponent,
    ConsumableValidityTrait,
    DelayTrait,
    EventProviderTrait,
    LastingTrait,
):
    name: str
    delay: float
    maximum_stack: int

    cooldown_duration: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: list[float]

    lasting_duration: float

    def get_default_state(self):
        return {
            "consumable": Consumable(
                maximum_stack=self.maximum_stack,
                stack=0,
                cooldown_duration=self.cooldown_duration,
                time_left=0,
            ),
            "stack": Stack(stack=0, maximum_stack=3),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: HowlingGaleState):
        state = state.deepcopy()

        state.consumable.elapse(time)
        lapse_count = state.periodic.elapse(time)

        dealing_events = []
        if lapse_count > 0:
            gale_stack = state.stack.get_stack()
            if gale_stack in (1, 2):
                for _ in range(lapse_count):
                    dealing_events.append(
                        self.event_provider.dealt(
                            self.periodic_damage[gale_stack], self.periodic_hit[gale_stack]
                        )
                    )
            elif gale_stack == 3:
                for _ in range(lapse_count):
                    dealing_events.append(
                        self.event_provider.dealt(
                            self.periodic_damage[0], self.periodic_hit[0]
                        )
                    )
                    dealing_events.append(
                        self.event_provider.dealt(
                            self.periodic_damage[1], self.periodic_hit[1]
                        )
                    )

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: HowlingGaleState):
        state = state.deepcopy()

        if not state.consumable.available:
            return state, [self.event_provider.rejected()]

        delay = self._get_delay()

        gale_stack = min(state.consumable.get_stack(), state.stack.maximum_stack)
        state.stack.reset()
        state.stack.increase(gale_stack)
        state.consumable.stack -= gale_stack

        state.periodic.set_time_left(self._get_lasting_duration(state), self.delay)

        return state, [
            self.event_provider.delayed(delay),
        ]

    @view_method
    def validity(self, state: HowlingGaleState):
        return self.validity_in_consumable_trait(state)

    @view_method
    def running(self, state: HowlingGaleState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: HowlingGaleState) -> float:
        return self.lasting_duration + self.delay
