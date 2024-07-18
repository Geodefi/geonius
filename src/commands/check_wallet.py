# -*- coding: utf-8 -*-

import os
import click

from geodefi.globals import ETHER_DENOMINATOR

from src.globals import get_config, get_logger
from src.helpers.portal import get_wallet_balance
from src.helpers.portal import get_name
from src.setup import setup


def check_wallet():
    try:
        oid = get_config().operator_id
        balance: int = get_wallet_balance(oid)

        get_logger().info(
            f"{get_name(oid)} has {balance/ETHER_DENOMINATOR}ETH ({balance} wei) balance in portal."
            f" Use 'geonius increase-wallet' to deposit more."
        )

    except Exception as e:
        get_logger().error(str(e))
        get_logger().error("Check failed, try again.")


@click.option(
    "--chain",
    envvar="GEONIUS_CHAIN",
    required=True,
    type=click.Choice(["holesky", "ethereum"]),
    prompt="You forgot to specify the chain:",
    default="holesky",
    help="Network name, such as 'holesky' or 'ethereum' etc.",
)
@click.option(
    "--main-dir",
    envvar="GEONIUS_DIR",
    required=False,
    type=click.STRING,
    default=os.path.join(os.getcwd(), ".geonius"),
    help="Main directory PATH that will be used to store data. Default is ./.geonius",
)
@click.command(
    help="Prints the amount of ether that can be utilized by Node Operators to propose new validators. "
    "Every new validator requires 1 ETH to be available in the internal wallet. "
    "Ether will be returned back to the internal wallet after the activation of the validator."
)
def main(chain: str, main_dir: str):
    setup(chain=chain, main_dir=main_dir, no_log_file=True)
    check_wallet()
