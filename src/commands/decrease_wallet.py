# -*- coding: utf-8 -*-

from time import sleep
import click

from geodefi.globals import ETHER_DENOMINATOR

from src.globals import get_sdk, get_config, get_logger
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


def decrease_wallet(value: int):
    try:
        _id = int(get_config().operator_id)
        get_logger().info(
            f"Decreasing internal wallet for {get_name(_id)} by {value/ETHER_DENOMINATOR} ether"
        )

        params: dict = tx_params()

        tx: str = get_sdk().portal.functions.decreaseWalletBalance(_id, value).transact(params)

        get_logger().etherscan("decreaseWalletBalance", tx)

    except Exception as e:
        get_logger().error(str(e))
        get_logger().error("Tx failed, try again.")


@click.option(
    "--operator-id",
    required=False,
    type=click.INT,
    help="geodefi ID for the Node Operator",
)
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
    prompt="Please specify the amount to withdraw (wei)",
    help="Amount to withdraw from the internal wallet (wei)",
)
@click.option(
    "--operator-id",
    required=False,
    type=click.INT,
    help="geodefi ID for the Node Operator",
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
    + "Default is ./.geonius",
)
@click.command(
    help="Withdraws the specified amount of wei from the Node Operator's internal wallet. "
    "Withdrawn amount will be sent to the CONTROLLER of the ID. "
    "Every new validator requires 1 ETH to be available in the internal wallet. "
    "Ether will be returned back to the internal wallet after the activation of the validator."
)
def main(
    chain: str,
    main_dir: str,
    private_key: str,
    api_key_execution: str,
    api_key_consensus: str,
    api_key_gas: str,
    operator_id: int,
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
        operator_id=operator_id,
        no_log_file=True,
        test_email=False,
        test_ethdo=False,
        test_operator=True,
    )

    if interval:
        while True:
            decrease_wallet(wei)
            get_logger().info(f"Will run again in {interval} seconds")
            sleep(interval)
    else:
        decrease_wallet(wei)
