# -*- coding: utf-8 -*-

from geodefi.utils.wrappers import http_request
from src.globals import CONFIG
from src.common import AttributeDict
from src.logger import log
from src.utils import send_email

# TODO: take <GAS_API_KEY> if if exist and replace with ENV.GAS_API_KEY


@http_request
def fetch_gas() -> tuple:
    url: str = CONFIG.gas.api
    return (url, True)


def parse_gas(gas) -> tuple[int]:
    priority: list = CONFIG.gas.parser.priority.split('.')
    gas_priority = gas
    for i in priority:
        gas_priority = gas_priority[i]

    base_fee: list = CONFIG.gas.parser.fee.split('.')
    gas_base_fee = gas
    for j in base_fee:
        gas_base_fee = gas_base_fee[j]

    return float(gas_priority), float(gas_base_fee)


def get_gas() -> tuple[int]:
    gas: AttributeDict = CONFIG.gas
    if gas:
        if gas.api and gas.parser and gas.max_priority and gas.max_fee:
            priority_fee, base_fee = parse_gas(fetch_gas())
            if priority_fee < gas.max_priority and base_fee < gas.max_fee:
                return priority_fee, base_fee
            else:
                log.critical(
                    f"Undesired GAS price => priority:{priority_fee}, fee:{base_fee}. Will reconsider next time."
                )
                send_email(
                    "High Gas Alert",
                    f"On Chain gas api reported that \
                    gas prices have surpassed the default max settings. Please fix.",
                    [("<file_path>", "<file_name>.log")],
                )
    return (None, None)
