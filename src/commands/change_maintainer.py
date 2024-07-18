# -*- coding: utf-8 -*-

import os
from argparse import ArgumentParser

from src.common import AttributeDict
from src.exceptions import UnknownFlagError
from src.globals import get_sdk, get_config, get_logger, get_flags
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
    parser.add_argument(
        "--address",
        action="store",
        dest="value",
        type=int,
        help="maintainer address to set and use in geonius",
        required=True,
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


def change_maintainer(address: str):
    try:
        operator_id: int = get_config().operator_id
        get_logger().info(f"Setting a new maintainer for {get_name(operator_id)}: {address}")

        params: dict = tx_params()

        tx: dict = (
            get_sdk().portal.functions.changeMaintainer(operator_id, address).transact(params)
        )

        get_logger().etherscan("increaseWalletBalance", tx)

    except Exception as err:
        get_logger().error("Tx failed, try again.")
        get_logger().error(err)


def main():
    setup(flag_collector=collect_local_flags)
    f: dict = get_flags()
    change_maintainer(f.address)


if __name__ == "__main__":
    main()
