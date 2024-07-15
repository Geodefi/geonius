# -*- coding: utf-8 -*-
import struct
from geodefi.utils import wrappers

from src.common import AttributeDict
from src.exceptions import HighGasException
from src.globals import get_logger, get_config
from src.utils.notify import send_email


def __float_to_hexstring(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])


@wrappers.http_request
def __fetch_gas() -> tuple:
    _url: str = get_config().gas.api
    return (_url, True)


def __parse_gas(gas) -> tuple[float]:
    __priority_fee: list = get_config().gas.parser.priority.split('.')
    gas_priority = gas
    for i in __priority_fee:
        gas_priority = gas_priority[i]

    __base_fee: list = get_config().gas.parser.base.split('.')
    gas_base_fee = gas
    for j in __base_fee:
        gas_base_fee = gas_base_fee[j]

    return float(gas_priority), float(gas_base_fee)


def get_gas() -> tuple[str]:
    gas: AttributeDict = get_config().gas
    if gas:
        if gas.api and gas.parser and gas.max_priority and gas.max_fee:
            priority_fee, base_fee = __parse_gas(__fetch_gas())
            if priority_fee < gas.max_priority and base_fee < gas.max_fee:
                return __float_to_hexstring(priority_fee), __float_to_hexstring(base_fee)
            else:
                get_logger().critical(
                    f"Undesired GAS price => priority:{priority_fee}, fee:{base_fee}. Tx will not be submitted."
                )
                send_email(
                    "High Gas Alert",
                    f"On Chain gas api reported that gas prices have surpassed the default max settings. Please fix.",
                    dont_notify_devs=True,
                )
                raise HighGasException("Gas prices are too high!")
    return (None, None)
