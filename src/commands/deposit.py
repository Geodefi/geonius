# -*- coding: utf-8 -*-

import os
from time import sleep
from argparse import ArgumentParser

from src.common import AttributeDict
from src.exceptions import UnknownFlagError
from src.globals import get_sdk, get_logger, get_flags
from src.helpers.portal import get_name
from src.utils.gas import get_gas
from src.setup import setup


def collect_local_flags() -> dict:
    parser = ArgumentParser()
    parser.add_argument(
        "--chain",
        action="store",
        dest="chain",
        type=str,
        help="Network name, such as 'holesky' or 'ethereum' etc. Required when providing any other chain setting.",
        required=True,
    )
    parser.add_argument(
        "--main-directory",
        action="store",
        dest="main_directory",
        type=str,
        help="main directory name that will be created, and used to store data",
        default=os.path.join(os.getcwd(), '.geonius'),
    )
    parser.add_argument("--value", action="store", dest="value", type=int, required=True)
    parser.add_argument("--pool", action="store", dest="pool", type=int, required=True)
    parser.add_argument(
        "--interval",
        action="store",
        dest="interval",
        type=int,
        required=False,
        help="Will run as a daemon when provided, interpreted as seconds.",
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


def deposit(
    pool: int,
    value: int,
):
    try:
        get_logger().info(f"Depositing {value} wei to pool {get_name(pool)}")

        params: dict = tx_params()
        params.update({'value': value})

        tx: dict = (
            get_sdk()
            .portal.contract.functions.deposit(
                pool,
                0,
                [],
                0,
                1821194534,  # will fail in 2100
                get_sdk().w3.eth.default_account,
            )
            .transact(params)
        )

        get_logger().etherscan("deposit", tx)

    except Exception as err:
        get_logger().error("Tx failed, try again.")
        get_logger().error(err)


def main():
    setup(flag_collector=collect_local_flags)
    f: dict = get_flags()
    if "interval" in f and f.interval:
        while True:
            deposit(f.pool, f.value)
            sleep(f.interval)
    else:
        deposit(f.pool, f.value)


if __name__ == "__main__":
    main()
