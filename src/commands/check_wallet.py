# -*- coding: utf-8 -*-

import click

from geodefi.globals import ETHER_DENOMINATOR
from src.utils.env import (
    load_env,
    set_api_key_execution,
    set_api_key_consensus,
    set_api_key_gas,
)
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
    "--operator-id",
    required=False,
    type=click.INT,
    help="geodefi ID for the Node Operator",
)
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
    "--api-key-execution",
    envvar="API_KEY_EXECUTION",
    required=False,
    type=click.STRING,
    is_eager=True,
    callback=set_api_key_execution,
    help="Api key for the execution layer endpoint."
    " Could be the rest api of the execution client. Overrides .env file.",
)
@click.option(
    "--api-key-consensus",
    envvar="API_KEY_CONSENSUS",
    required=False,
    type=click.STRING,
    is_eager=True,
    callback=set_api_key_consensus,
    help="Api key for the consensus layer endpoint."
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
    help="Api key for the endpoint used fetching gas prices in gwei. Overrides .env file.",
)
@click.option(
    "--main-dir",
    envvar="GEONIUS_DIR",
    required=False,
    is_eager=False,
    callback=load_env,
    type=click.STRING,
    default=".geonius",
    help="Relative path for the directory that will be used to store data."
    " Default is ./.geonius",
)
@click.command(
    help="Prints the balance that can be utilized by Node Operators to propose new validators. "
    "Every new validator requires 1 ETH to be available in the internal wallet. "
    "Ether will be returned back to the internal wallet after the activation of the validator."
)
def main(
    chain: str,
    main_dir: str,
    api_key_execution: str,
    api_key_consensus: str,
    api_key_gas: str,
    operator_id: int,
):
    setup(
        chain=chain,
        main_dir=main_dir,
        api_key_execution=api_key_execution,
        api_key_consensus=api_key_consensus,
        api_key_gas=api_key_gas,
        operator_id=operator_id,
        no_log_file=True,
        test_email=False,
        test_ethdo=False,
        test_operator=True,
    )
    check_wallet()
