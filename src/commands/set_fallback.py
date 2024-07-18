# -*- coding: utf-8 -*-

import os
from time import sleep
import click

from geodefi.globals.constants import PERCENTAGE_DENOMINATOR
from src.globals import get_sdk, get_logger
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


def set_fallback_operator(pool: int, operator: int, threshold: int):
    try:
        perc_threshold: int = threshold * PERCENTAGE_DENOMINATOR / 100
        get_logger().critical(
            f"Setting threshold as {perc_threshold} from pool {get_name(pool)} for {get_name(operator)}"
        )

        tx: dict = (
            get_sdk()
            .portal.contract.functions.setFallbackOperator(pool, operator, perc_threshold)
            .transact(tx_params())
        )
        get_logger().etherscan("setFallbackOperator", tx)

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
    "--threshold",
    required=True,
    type=click.IntRange(0, 100),
    prompt="Please specify the threshold (percentage)",
    help="Provided Operator can create infinitely many validators after this threshold is filled.",
)
@click.option(
    "--operator",
    required=True,
    type=click.INT,
    prompt="Please specify the Operator ID",
    help="Operator ID that will be allowed to create validators",
)
@click.option(
    "--pool",
    required=True,
    type=click.INT,
    prompt="Please specify the Pool ID",
    help="Pool ID that will allow provided operator to create validators when suitable.",
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
    help="Sets a new fallback operator for the provided pool id. "
    "Provided Operator can create infinitely many validators after the provided threshold is filled."
)
def main(chain: str, main_dir: str, pool: int, operator: int, threshold: int, interval: int):
    setup(chain=chain, main_dir=main_dir, no_log_file=True)

    if interval:
        while True:
            set_fallback_operator(pool, operator, threshold)
            get_logger().info(f"Will run again in {interval} seconds")
            sleep(interval)
    else:
        set_fallback_operator(pool, operator, threshold)
