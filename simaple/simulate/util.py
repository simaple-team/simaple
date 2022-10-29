from typing import Optional

from loguru import logger

from simaple.simulate.base import Action, Event, EventHandler, Store
from simaple.simulate.reserved_names import Tag
from simaple.simulate.timer import get_current_time


class EventDisplayHandler(EventHandler):
    def __call__(
        self, event: Event, store: Store, __: list[Event]
    ) -> Optional[list[Action]]:
        if event.tag == Tag.ELAPSED:  # Elapsed log is too verbose
            return

        elapsed_second = get_current_time(store) * 0.001
        output = f"TIME [{elapsed_second:.3f}] |  {event.tag:<17}| {event.signature.replace('.', ' -> ')}  {event.payload}"
        if event.tag == Tag.REJECT:
            logger.warning(output)
        else:
            logger.info(output)
