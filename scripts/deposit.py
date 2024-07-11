from time import sleep
from argparse import ArgumentParser

from src.exceptions import UnknownFlagError
from src.setup import setup_globals
from src.globals import get_sdk, get_logger, get_flags
from src.helpers import get_name
from src.utils import get_gas


def collect_local_flags() -> dict:
    parser = ArgumentParser()
    parser.add_argument("--value", action="store", dest="value", type=int, required=True)
    parser.add_argument("--pool", action="store", dest="pool", type=int, required=True)
    parser.add_argument(
        "--sleep",
        action="store",
        dest="sleep",
        type=int,
        required=False,
        help="Will run as a daemon when provided, interpreted as seconds.",
    )
    flags, unknown = parser.parse_known_args()
    if unknown:
        get_logger().error(f"Unknown flags:{unknown}")
        raise UnknownFlagError
    return flags


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
        get_logger().info(f"Depositing {value} to pool {get_name(pool)}")

        params: dict = tx_params()
        params.update({'value': value})

        tx: dict = (
            get_sdk()
            .portal.contract.functions.deposit(
                pool,
                0,
                [],
                0,
                1719127731,  # will fail in 2100
                get_sdk().w3.eth.default_account,
            )
            .transact(params)
        )

        get_logger().etherscan(tx)

    except Exception as err:
        get_logger().error("Tx failed, try again.")
        get_logger().error(err)


if __name__ == "__main__":
    setup_globals(flag_collector=collect_local_flags)
    f: dict = get_flags()
    if hasattr(f, 'sleep'):
        while True:
            deposit(f.pool, f.value)
            sleep(f.sleep)
    else:
        deposit(f.pool, f.value)
