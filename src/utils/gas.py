# -*- coding: utf-8 -*-
import struct
from geodefi.utils import wrappers

from src.globals import CONFIG
from src.common import AttributeDict
from src.logger import log
from src.utils import send_email


def __float_to_hexstring(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])


@wrappers.http_request
def __fetch_gas() -> tuple:
    _url: str = CONFIG.gas.api
    return (_url, True)


def __parse_gas(gas) -> tuple[float]:
    __priority_fee: list = CONFIG.gas.parser.priority.split('.')
    gas_priority = gas
    for i in __priority_fee:
        gas_priority = gas_priority[i]

    __base_fee: list = CONFIG.gas.parser.base.split('.')
    gas_base_fee = gas
    for j in __base_fee:
        gas_base_fee = gas_base_fee[j]

    return float(gas_priority), float(gas_base_fee)


def get_gas() -> tuple[str]:
    gas: AttributeDict = CONFIG.gas
    if gas:
        if gas.api and gas.parser and gas.max_priority and gas.max_fee:
            priority_fee, base_fee = __parse_gas(__fetch_gas())
            if priority_fee < gas.max_priority and base_fee < gas.max_fee:
                return __float_to_hexstring(priority_fee), __float_to_hexstring(base_fee)
            else:
                log.critical(
                    f"Undesired GAS price => priority:{priority_fee}, fee:{base_fee}. \
                        Tx will not be submitted."
                )
                send_email(
                    "High Gas Alert",
                    f"On Chain gas api reported that \
                    gas prices have surpassed the default max settings. Please fix.",
                    [("<file_path>", "<file_name>.log")],
                )
                # TODO: raise Exception and catch it in daemon so it doesn't create a tx!
    return (None, None)
