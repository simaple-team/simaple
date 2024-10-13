from simaple.core.base import Stat
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.feature import DamageAndHit, PeriodicFeature
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import InvalidatableCooldownTrait
from simaple.simulate.component.view import Running
from simaple.simulate.core.base import Event
from simaple.simulate.global_property import Dynamics


class TriplePeriodicDamageHexaComponentState(ReducerState):
    cooldown: Cooldown

    periodic_01: Periodic
    periodic_02: Periodic
    periodic_03: Periodic

    dynamics: Dynamics


class TriplePeriodicDamageHexaComponent(SkillComponent, InvalidatableCooldownTrait):
    """
    TriplePeriodicDamageConfiguratedHexaSkillComponent
    This describes skill that act like:
    - Initial damage x hit
      + (1) periodic damage x hit
      + (2) periodic damage x hit
      + (3) periodic damage x hit

    ex) Holy Advent
    """

    name: str
    damage_and_hits: list[DamageAndHit]
    cooldown_duration: float
    delay: float

    periodic_01: PeriodicFeature
    periodic_02: PeriodicFeature
    periodic_03: PeriodicFeature

    lasting_duration: float

    synergy: Stat

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic_01": Periodic(
                interval=self.periodic_01.interval,
                initial_counter=self.periodic_01.initial_delay,
                time_left=0,
            ),
            "periodic_02": Periodic(
                interval=self.periodic_02.interval,
                initial_counter=self.periodic_02.initial_delay,
                time_left=0,
            ),
            "periodic_03": Periodic(
                interval=self.periodic_03.interval,
                initial_counter=self.periodic_03.initial_delay,
                time_left=0,
            ),
        }

    @reducer_method
    def elapse(self, time: float, state: TriplePeriodicDamageHexaComponentState):
        state = state.deepcopy()
        state.cooldown.elapse(time)

        damage_events: list[Event] = []

        for periodic, feature in self._get_all_periodics(state):
            lapse_count = periodic.elapse(time)
            damage_events.extend(
                self.event_provider.dealt(feature.damage, feature.hit)
                for _ in range(lapse_count)
            )

        return state, [self.event_provider.elapsed(time)] + damage_events

    @reducer_method
    def use(self, _: None, state: TriplePeriodicDamageHexaComponentState):
        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state = state.deepcopy()

        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )

        for periodic, _feature in self._get_all_periodics(state):
            periodic.set_time_left(self._get_lasting_duration(state))

        return state, [
            self.event_provider.dealt(entry.damage, entry.hit)
            for entry in self.damage_and_hits
        ] + [
            self.event_provider.delayed(delay),
        ]

    @view_method
    def validity(self, state: TriplePeriodicDamageHexaComponentState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    @view_method
    def running(self, state: TriplePeriodicDamageHexaComponentState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.periodic_01.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    @view_method
    def buff(self, _: TriplePeriodicDamageHexaComponentState):
        return self.synergy

    def _get_lasting_duration(
        self, state: TriplePeriodicDamageHexaComponentState
    ) -> float:
        return self.lasting_duration

    def _get_all_periodics(
        self, state: TriplePeriodicDamageHexaComponentState
    ) -> list[tuple[Periodic, PeriodicFeature]]:
        return [
            (state.periodic_01, self.periodic_01),
            (state.periodic_02, self.periodic_02),
            (state.periodic_03, self.periodic_03),
        ]
