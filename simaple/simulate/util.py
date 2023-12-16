from loguru import logger

from simaple.simulate.base import (
    Event,
    PostActionCallback,
    ViewerType,
    message_signature,
)
from simaple.simulate.reserved_names import Tag


class EventDisplayCallback(PostActionCallback):
    def __call__(self, event: Event, viewer: ViewerType, __: list[Event]) -> None:
        if event["tag"] == Tag.ELAPSED:  # Elapsed log is too verbose
            return

        elapsed_second = viewer("clock") * 0.001
        output = f"TIME [{elapsed_second:.3f}] |  {event['tag']:<17}| {message_signature(event).replace('.', ' -> ')}  {event['payload']}"
        if event["tag"] == Tag.REJECT:
            logger.warning(output)
        else:
            logger.info(output)
