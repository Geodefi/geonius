# -*- coding: utf-8 -*-

import os
from time import sleep
import click

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


def deposit(
    pool: int,
    value: int,
):
    try:
        get_logger().critical(f"Depositing {value} wei to pool {get_name(pool)}")

        params: dict = tx_params()
        params.update({"value": value})

        tx: dict = (
            get_sdk()
            .portal.contract.functions.deposit(
                pool,
                0,
                [],
                0,
                32503680061,  # will fail in year 3000
                get_sdk().w3.eth.default_account,
            )
            .transact(params)
        )

        get_logger().etherscan("deposit", tx)

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
    prompt="Please specify the deposit amount (wei)",
    help="Amount to deposit into provided staking pool (wei)",
)
@click.option(
    "--pool",
    required=True,
    type=click.INT,
    prompt="Please specify the Pool ID",
    help="Pool ID to deposit ether.",
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
    help="Deposit ether into a Staking pool."
    "Circuit breakers like 'deadline' or 'min gETH amount' can not be specified at the moment."
)
def main(chain: str, main_dir: str, pool: int, value: int, interval: int):
    setup(chain=chain, main_dir=main_dir, no_log_file=True)

    if interval:
        while True:
            deposit(pool, value)
            get_logger().info(f"Will run again in {interval} seconds")
            sleep(interval)
    else:
        deposit(pool, value)
