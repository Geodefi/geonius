# -*- coding: utf-8 -*-

import os
from argparse import ArgumentParser

from geodefi.globals import ETHER_DENOMINATOR

from src.common import AttributeDict
from src.exceptions import UnknownFlagError
from src.globals import get_config, get_logger
from src.helpers.portal import get_wallet_balance
from src.helpers.portal import get_name
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
    flags, unknown = parser.parse_known_args()
    if unknown:
        print(f"Unknown flags:{unknown}")
        raise UnknownFlagError
    flags_dict = vars(flags)
    flags_dict["no_log_file"] = True
    return AttributeDict.convert_recursive(flags_dict)


def check_wallet():
    try:
        oid = get_config().operator_id
        balance: int = get_wallet_balance(oid)

        get_logger().info(
            f"{get_name(oid)} has {balance/ETHER_DENOMINATOR} ETH ({balance} wei) in the internal wallet. Use 'geonius increase-wallet --value X --chain X' to deposit more."
        )

    except Exception as e:
        get_logger().error(str(e))
        get_logger().error("Check failed, try again.")


def main():
    setup()
    check_wallet()
