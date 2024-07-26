# -*- coding: utf-8 -*-

from time import sleep
import click

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
    return {}


def deposit(
    pool: int,
    value: int,
):
    try:
        get_logger().info(f"Depositing {value} wei to pool {get_name(pool)}")

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
    "--wei",
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
    "--private-key",
    envvar="GEONIUS_PRIVATE_KEY",
    required=False,
    type=click.STRING,
    is_eager=True,
    callback=set_geonius_private_key,
    help="Private key for the Node Operator maintainer that will run geonius. Overrides .env file.",
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
    help="Relative path for the main directory that will be used to store data."
    " Default is ./.geonius",
)
@click.command(
    help="Deposit ether into a Staking pool."
    "Circuit breakers like 'deadline' or 'min gETH amount' can not be specified at the moment."
)
def main(
    chain: str,
    main_dir: str,
    private_key: str,
    api_key_execution: str,
    api_key_consensus: str,
    api_key_gas: str,
    pool: int,
    wei: int,
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
            deposit(pool, wei)
            get_logger().info(f"Will run again in {interval} seconds")
            sleep(interval)
    else:
        deposit(pool, wei)
