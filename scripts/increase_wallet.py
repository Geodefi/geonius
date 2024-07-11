from time import sleep
from argparse import ArgumentParser
from geodefi.globals import ETHER_DENOMINATOR

from src.exceptions import UnknownFlagError
from src.setup import setup_globals
from src.globals import get_sdk, get_env, get_logger, get_flags
from src.helpers import get_name
from src.utils import get_gas


def collect_local_flags() -> dict:
    parser = ArgumentParser()
    parser.add_argument("--value", action="store", dest="value", type=int, required=True)
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


def increase_wallet(value: int):
    try:
        get_logger().info(
            f"Increasing id wallet for {get_name(get_env().OPERATOR_ID)} by {value/ETHER_DENOMINATOR} ether"
        )

        params: dict = tx_params()
        params.update({'value': value})

        tx: dict = (
            get_sdk().portal.functions.increaseWalletBalance(get_env().OPERATOR_ID).transact(params)
        )

        get_logger().etherscan("increaseWalletBalance", tx)

    except Exception as err:
        get_logger().error("Tx failed, try again.")
        get_logger().error(err)


if __name__ == "__main__":
    setup_globals(flag_collector=collect_local_flags)
    f: dict = get_flags()

    if hasattr(f, 'sleep'):
        while True:
            increase_wallet(f.value)
            sleep(f.sleep)
    else:
        increase_wallet(f.value)
