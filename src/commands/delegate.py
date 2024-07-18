# -*- coding: utf-8 -*-

import os
from time import sleep
import click

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


def delegate(pool: int, operator: int, allowance: int):
    try:
        get_logger().critical(
            f"Delegating {allowance} to operator {get_name(get_config().operator_id)} in pool {get_name(pool)}"
        )

        tx: dict = (
            get_sdk().portal.functions.delegate(pool, [operator], [allowance]).transact(tx_params())
        )

        get_logger().etherscan("delegate", tx)

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
    "--allowance",
    required=True,
    type=click.INT,
    prompt="Please specify the allowance (validators)",
    help="Number of validators provided Operator can create on behalf of the provided Pool",
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
    help="Pool ID to give allowance from.",
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
@click.command(help="Allow an Operator to propose validators on behalf of the staking pool.")
def main(chain: str, main_dir: str, pool: int, operator: int, allowance: int, interval: int):
    setup(chain=chain, main_dir=main_dir, no_log_file=True)

    if interval:
        while True:
            delegate(pool, operator, allowance)
            get_logger().info(f"Will run again in {interval} seconds")
            sleep(interval)
    else:
        delegate(pool, operator, allowance)
