from simaple.core.base import Stat
from simaple.simulate.base import Event
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.feature import DamageAndHit, PeriodicFeature
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import InvalidatableCooldownTrait
from simaple.simulate.component.view import Running
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
            "periodic_01": Periodic(interval=self.periodic_01.interval, time_left=0),
            "periodic_02": Periodic(interval=self.periodic_02.interval, time_left=0),
            "periodic_03": Periodic(interval=self.periodic_03.interval, time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: TriplePeriodicDamageHexaComponentState):
        damage_events: list[Event] = []

        cooldown = state.cooldown.elapse(time)
        periodic_01, lapse_count_01 = state.periodic_01.elapse(time)
        periodic_02, lapse_count_02 = state.periodic_02.elapse(time)
        periodic_03, lapse_count_03 = state.periodic_03.elapse(time)

        damage_events.extend(
            self.event_provider.dealt(self.periodic_01.damage, self.periodic_01.hit)
            for _ in range(lapse_count_01)
        )
        damage_events.extend(
            self.event_provider.dealt(self.periodic_02.damage, self.periodic_02.hit)
            for _ in range(lapse_count_02)
        )
        damage_events.extend(
            self.event_provider.dealt(self.periodic_03.damage, self.periodic_03.hit)
            for _ in range(lapse_count_03)
        )

        return state.copy(
            {
                "cooldown": cooldown,
                "periodic_01": periodic_01,
                "periodic_02": periodic_02,
                "periodic_03": periodic_03,
            }
        ), [self.event_provider.elapsed(time)] + damage_events

    @reducer_method
    def use(self, _: None, state: TriplePeriodicDamageHexaComponentState):
        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        delay = self._get_delay()

        cooldown = state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        periodic_01 = state.periodic_01.set_time_left(self._get_lasting_duration(state))
        periodic_02 = state.periodic_02.set_time_left(self._get_lasting_duration(state))
        periodic_03 = state.periodic_03.set_time_left(self._get_lasting_duration(state))

        return state.copy(
            {
                "cooldown": cooldown,
                "periodic_01": periodic_01,
                "periodic_02": periodic_02,
                "periodic_03": periodic_03,
            }
        ), [
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
