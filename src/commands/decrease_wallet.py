# -*- coding: utf-8 -*-

import os
from time import sleep
import click

from geodefi.globals import ETHER_DENOMINATOR

from src.globals import get_sdk, get_config, get_logger
from src.helpers.portal import get_name
from src.utils.gas import get_gas
from src.setup import setup


def tx_params() -> dict:
    priority_fee, base_fee = get_gas()
    if priority_fee and base_fee:
        return {
            "maxPriorityFeePerGas": priority_fee,
            "maxFeePerGas": base_fee,
        }
    else:
        return {}


def decrease_wallet(value: int):
    try:
        _id = int(get_config().operator_id)
        get_logger().critical(
            f"Decreasing internal wallet for {get_name(_id)} by {value/ETHER_DENOMINATOR} ether"
        )

        params: dict = tx_params()

        tx: str = get_sdk().portal.functions.decreaseWalletBalance(_id, value).transact(params)

        get_logger().etherscan("decreaseWalletBalance", tx)

    except Exception as e:
        get_logger().error(str(e))
        get_logger().error("Tx failed, try again.")


@click.option(
    "--interval",
    required=False,
    type=click.INT,
    help="Will run as a daemon when provided (seconds)",
)
@click.option(
    "--value",
    required=True,
    type=click.INT,
    prompt="Please specify the amount to withdraw (wei)",
    help="Amount to withdraw from the internal wallet (wei)",
)
@click.option(
    "--chain",
    envvar="GEONIUS_CHAIN",
    required=True,
    type=click.Choice(["holesky", "ethereum"]),
    prompt="You forgot to specify the chain",
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
    help="Withdraws the specified amount of wei from the Node Operator's internal wallet. "
    "Withdrawn amount will be sent to the CONTROLLER of the ID. "
    "Every new validator requires 1 ETH to be available in the internal wallet. "
    "Ether will be returned back to the internal wallet after the activation of the validator."
)
def main(chain: str, main_dir: str, value: int, interval: int):
    setup(chain=chain, main_dir=main_dir, no_log_file=True)

    if interval:
        while True:
            decrease_wallet(value)
            get_logger().info(f"Will run again in {interval} seconds")
            sleep(interval)
    else:
        decrease_wallet(value)
