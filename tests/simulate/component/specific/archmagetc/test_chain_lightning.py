from simaple.simulate.component.entity import Periodic
from simaple.simulate.component.specific.archmagetc import CurrentField


def test_current_field_entity():
    start_current_field = CurrentField(
        field_interval=1000,
        field_duration=4000,
        max_count=4,
        force_trigger_interval=7000,
    )

    assert not start_current_field.stack_rng(0.5)
    assert start_current_field.stack_rng(0.5)
    assert not start_current_field.stack_rng(0.5)
    assert start_current_field.stack_rng(0.6)


def test_current_field_entity_elapse():
    start_current_field = CurrentField(
        field_interval=1000,
        field_duration=4000,
        max_count=4,
        force_trigger_interval=7000,
    )

    assert not start_current_field.stack_rng(0.5)
    start_current_field.elapse(1000)

    assert start_current_field.stack_rng(0.5)
    start_current_field.elapse(1000)

    assert start_current_field.field_periodics == [
        Periodic(interval=1000, time_left=3000, count=2, interval_counter=1000)
    ]

    assert not start_current_field.stack_rng(0.5)
    assert start_current_field.stack_rng(0.5)
    start_current_field.elapse(1200)

    assert start_current_field.field_periodics == [
        Periodic(interval_counter=800.0, interval=1000.0, time_left=1800.0, count=3),
        Periodic(interval_counter=800.0, interval=1000.0, time_left=2800.0, count=2),
    ]

    start_current_field.elapse(4000)
    assert start_current_field.field_periodics == []


def test_current_field_entity_max_count():
    start_current_field = CurrentField(
        field_interval=1000,
        field_duration=4000,
        max_count=4,
        force_trigger_interval=7000,
    )

    assert start_current_field.stack_rng(1.0)
    assert start_current_field.stack_rng(1.0)
    assert start_current_field.stack_rng(1.0)
    assert start_current_field.stack_rng(1.0)
    assert start_current_field.stack_rng(1.0)

    assert len(start_current_field.field_periodics) == 4
