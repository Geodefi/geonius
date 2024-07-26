# -*- coding: utf-8 -*-

import click

from src.globals import get_sdk, get_config, get_logger
from src.helpers.portal import get_name
from src.utils.gas import get_gas
from src.utils.env import (
    load_env,
    set_geonius_private_key,
    set_api_key_execution,
    set_api_key_consensus,
    set_api_key_gas,
)
from src.setup import setup


def tx_params() -> dict:
    priority_fee, base_fee = get_gas()
    if priority_fee and base_fee:
        return {
            "maxPriorityFeePerGas": priority_fee,
            "maxFeePerGas": base_fee,
        }
    return {}


def change_maintainer(address: str):
    try:
        operator_id: int = get_config().operator_id
        get_logger().info(f"Setting a new maintainer for {get_name(operator_id)}: {address}")

        params: dict = tx_params()

        tx: dict = (
            get_sdk().portal.functions.changeMaintainer(operator_id, address).transact(params)
        )

        get_logger().etherscan("changeMaintainer", tx)

    except Exception as e:
        get_logger().error(str(e))
        get_logger().error("Tx failed, try again.")


@click.option(
    "--address",
    required=True,
    type=click.STRING,
    prompt="Please specify the maintainer address",
    help="Maintainer address to set and use in geonius",
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
    type=click.STRING,
    is_eager=False,
    callback=load_env,
    default=".geonius",
    help="Relative path for the main directory that will be used to store data."
    " Default is ./.geonius",
)
@click.command(
    help="Set a new maintainer for the Node Operator."
    " Maintainers are allowed to create validators, and should be the ones operating geonius."
)
def main(
    chain: str,
    main_dir: str,
    private_key: str,
    api_key_execution: str,
    api_key_consensus: str,
    api_key_gas: str,
    operator_id: int,
    address: str,
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
    change_maintainer(address)
