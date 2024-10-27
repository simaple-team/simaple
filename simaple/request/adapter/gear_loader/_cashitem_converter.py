from simaple.core import Stat
from simaple.request.adapter.gear_loader._converter import (
    get_stat_from_option_value_and_type,
)
from simaple.request.external.nexon.schema.character.item import CashItemResponse


def get_cash_item_stat(response: CashItemResponse):
    cash_item_stat = Stat()
    for item in response["cash_item_equipment_base"]:
        for option in item["cash_item_option"]:
            cash_item_stat += get_stat_from_option_value_and_type(option)

    return cash_item_stat
