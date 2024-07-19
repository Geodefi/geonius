# -*- coding: utf-8 -*-

from time import sleep
import click

from geodefi.globals.constants import PERCENTAGE_DENOMINATOR
from src.globals import get_sdk, get_logger
from src.helpers.portal import get_name
from src.utils.env import (
    load_env,
    set_geonius_private_key,
    set_api_key_execution,
    set_api_key_consensus,
    set_api_key_gas,
)

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
        get_logger().info(
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
    "--private-key",
    envvar="GEONIUS_PRIVATE_KEY",
    required=False,
    type=click.STRING,
    is_eager=True,
    callback=set_geonius_private_key,
    help="Password for the ethdo wallet that will be used to create validators. Overrides .env file.",
)
@click.option(
    "--api-key-execution",
    envvar="API_KEY_EXECUTION",
    required=False,
    type=click.STRING,
    is_eager=True,
    callback=set_api_key_execution,
    help="Api key for the execution layer end point."
    " Could be the rest api of the execution client. Overrides .env file.",
)
@click.option(
    "--api-key-consensus",
    envvar="API_KEY_CONSENSUS",
    required=False,
    type=click.STRING,
    is_eager=True,
    callback=set_api_key_consensus,
    help="Api key for the consensus layer end point."
    " Could be the rest api of the consensus client."
    " Overrides .env file.",
)
@click.option(
    "--api-key-gas",
    envvar="API_KEY_GAS",
    required=False,
    type=click.STRING,
    is_eager=True,
    callback=set_api_key_gas,
    help="Api key for the end point used fetching gas prices in gwei. Overrides .env file.",
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
    is_eager=False,
    callback=load_env,
    type=click.STRING,
    default=".geonius",
    help="Relative path for the main directory that will be used to store data. Default is ./.geonius",
)
@click.command(
    help="Sets a new fallback operator for the provided pool id. "
    "Provided Operator can create infinitely many validators "
    "after the provided threshold is filled."
)
def main(
    chain: str,
    main_dir: str,
    private_key: str,
    api_key_execution: str,
    api_key_consensus: str,
    api_key_gas: str,
    pool: int,
    operator: int,
    threshold: int,
    interval: int,
):
    setup(
        chain=chain,
        main_dir=main_dir,
        private_key=private_key,
        api_key_execution=api_key_execution,
        api_key_consensus=api_key_consensus,
        api_key_gas=api_key_gas,
        no_log_file=True,
        test_email=False,
        test_ethdo=False,
        test_operator=True,
    )

    if interval:
        while True:
            set_fallback_operator(pool, operator, threshold)
            get_logger().info(f"Will run again in {interval} seconds")
            sleep(interval)
    else:
        set_fallback_operator(pool, operator, threshold)
