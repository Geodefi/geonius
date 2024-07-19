# -*- coding: utf-8 -*-

import click

from src.globals import get_sdk, get_config, get_logger
from src.helpers.portal import get_name
from src.utils.gas import get_gas
from src.utils.env import load_env
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
    is_eager=True,
    callback=load_env,
    default=".geonius",
    help="Relative path for the main directory that will be used to store data. Default is ./.geonius",
)
@click.command(
    help="Set a new maintainer for the Node Operator. Maintainers are allowed to create validators, and should be the ones operating geonius."
)
def main(chain: str, main_dir: str, address: str):
    setup(chain=chain, main_dir=main_dir, no_log_file=True, send_test_email=False)
    change_maintainer(address)
