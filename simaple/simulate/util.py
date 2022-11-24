from loguru import logger

from simaple.simulate.base import Environment, Event, EventHandler
from simaple.simulate.reserved_names import Tag


class EventDisplayHandler(EventHandler):
    def __call__(self, event: Event, environment: Environment, __: list[Event]) -> None:
        if event.tag == Tag.ELAPSED:  # Elapsed log is too verbose
            return

        elapsed_second = environment.show("clock") * 0.001
        output = f"TIME [{elapsed_second:.3f}] |  {event.tag:<17}| {event.signature.replace('.', ' -> ')}  {event.payload}"
        if event.tag == Tag.REJECT:
            logger.warning(output)
        else:
            logger.info(output)
