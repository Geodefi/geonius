# -*- coding: utf-8 -*-

import os
from time import sleep
from argparse import ArgumentParser

from src.common import AttributeDict
from src.exceptions import UnknownFlagError
from src.setup import setup
from src.globals import get_sdk, get_logger, get_flags
from src.helpers import get_name
from src.utils import get_gas


def collect_local_flags() -> dict:
    parser = ArgumentParser()
    parser.add_argument(
        "--main-directory",
        action="store",
        dest="main_directory",
        help="main directory name that will be created, and used to store data",
        default=os.path.join(os.getcwd(), '.geonius'),
    )
    parser.add_argument("--pool", action="store", dest="pool", type=int, required=True)
    parser.add_argument("--operator", action="store", dest="operator", type=int, required=True)
    parser.add_argument("--threshold", action="store", dest="threshold", type=int, required=True)
    parser.add_argument(
        "--interval",
        action="store",
        type=int,
        dest="interval",
        required=False,
        help="Will run as a daemon when provided, interpreted in seconds.",
    )
    flags, unknown = parser.parse_known_args()
    if unknown:
        print(f"Unknown flags:{unknown}")
        raise UnknownFlagError
    flags_dict = vars(flags)
    flags_dict["no_log_file"] = True
    return AttributeDict.convert_recursive(flags_dict)


def tx_params() -> dict:
    priority_fee, base_fee = get_gas()
    if priority_fee and base_fee:
        return {
            "maxPriorityFeePerGas": priority_fee,
            "maxFeePerGas": base_fee,
        }
    else:
        return {}


def set_fallback_operator(pool: int, operator: int, threshold: int):
    try:
        get_logger().info(
            f"Setting threshold as {threshold} from pool {get_name(pool)} for {get_name(operator)}"
        )

        tx: dict = (
            get_sdk()
            .portal.contract.functions.setFallbackOperator(pool, operator, threshold)
            .transact(tx_params())
        )
        get_logger().etherscan("setFallbackOperator", tx)

    except Exception as err:
        get_logger().error("Tx failed, try again.")
        get_logger().error(err)


if __name__ == "__main__":
    setup(flag_collector=collect_local_flags)
    f: dict = get_flags()

    if "interval" in f and f.interval:
        while True:
            set_fallback_operator(f.pool, f.operator, f.threshold)
            sleep(f.interval)
    else:
        set_fallback_operator(f.pool, f.operator, f.threshold)
