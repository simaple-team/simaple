from typing import Optional

from loguru import logger

from simaple.simulate.base import Action, Environment, Event, EventHandler
from simaple.simulate.reserved_names import Tag


class EventDisplayHandler(EventHandler):
    def __call__(
        self, event: Event, environment: Environment, __: list[Event]
    ) -> Optional[list[Action]]:
        if event.tag == Tag.ELAPSED:  # Elapsed log is too verbose
            return None

        elapsed_second = environment.show("clock") * 0.001
        output = f"TIME [{elapsed_second:.3f}] |  {event.tag:<17}| {event.signature.replace('.', ' -> ')}  {event.payload}"
        if event.tag == Tag.REJECT:
            logger.warning(output)
        else:
            logger.info(output)

        return None
