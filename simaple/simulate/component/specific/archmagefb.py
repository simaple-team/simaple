from simaple.simulate.base import State
from simaple.simulate.component.base import Component, reducer_method
from simaple.simulate.component.skill import (
    CooldownState,
    IntervalState,
    StackState,
    TickDamageConfiguratedAttackSkillComponent,
)


class PoisonNovaState(State):
    time_left: float
    maximum_time_left: float

    def create_nova(self, remaining_time):
        self.time_left = remaining_time

    def try_trigger_nova(self) -> bool:
        if 0 < self.time_left < self.maximum_time_left:
            self.time_left = 0
            return True

        return False

    def elapse(self, time: float):
        self.time_left -= time


class PoisonNovaComponent(Component):
    name: str
    damage: float
    hit: float
    cooldown: float = 0.0
    delay: float

    nova_remaining_time: float = 4000
    nova_damage: float
    nova_single_hit: int
    nova_hit_count: int

    listening_actions: dict[str, str] = {"미스트 이럽션.use": "trigger"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "nova_state": PoisonNovaState(time_left=0, maximum_time_left=100 * 1000.0),
        }

    @reducer_method
    def elapse(
        self, time: float, cooldown_state: CooldownState, nova_state: PoisonNovaState
    ):
        cooldown_state, nova_state = cooldown_state.copy(), nova_state.copy()
        cooldown_state.elapse(time)
        nova_state.elapse(time)
        return (cooldown_state, nova_state), self.event_provider.elapsed(time)

    @reducer_method
    def use(self, _: None, cooldown_state: CooldownState, nova_state: PoisonNovaState):
        cooldown_state, nova_state = cooldown_state.copy(), nova_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, nova_state), self.event_provider.rejected()

        cooldown_state.set_time_left(self.cooldown)
        nova_state.create_nova(self.nova_remaining_time)

        return (cooldown_state, nova_state), [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @reducer_method
    def trigger(self, _: None, nova_state: PoisonNovaState):
        nova_state = nova_state.copy()
        triggered = nova_state.try_trigger_nova()
        if triggered:
            return nova_state, [
                self.event_provider.dealt(
                    self.nova_damage, self.nova_single_hit * min(self.nova_hit_count, 3)
                ),
                self.event_provider.dealt(
                    self.nova_damage * 0.5,
                    self.nova_single_hit * max(self.nova_hit_count - 3, 0),
                ),
            ]

        return nova_state, None


class PoisonChainComponent(TickDamageConfiguratedAttackSkillComponent):
    tick_damage_increment: float

    def get_default_state(self):
        tick_states = super().get_default_state()
        tick_states.update(
            {
                "stack_state": StackState(maximum_stack=5),
            }
        )
        return tick_states

    def get_tick_damage(self, stack_state: StackState):
        return self.tick_damage + self.tick_damage_increment * stack_state.get_stack()

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        stack_state: StackState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()
        stack_state = stack_state.copy()

        cooldown_state.elapse(time)

        dealing_events = []

        for _ in interval_state.resolving(time):
            dealing_events.append(
                self.event_provider.dealt(
                    self.get_tick_damage(stack_state), self.tick_hit
                )
            )
            stack_state.increase(1)

        return (cooldown_state, interval_state, stack_state), [
            self.event_provider.elapsed(time)
        ] + dealing_events

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        stack_state: StackState,
    ):
        stack_state = stack_state.copy()

        (cooldown_state, interval_state), events = super().use(
            None, cooldown_state, interval_state
        )
        stack_state.reset(1)
        return (cooldown_state, interval_state, stack_state), events
