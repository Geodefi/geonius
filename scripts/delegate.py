from time import sleep
from argparse import ArgumentParser

from src.exceptions import UnknownFlagError
from src.setup import setup_globals
from src.globals import get_sdk, get_env, get_logger, get_flags
from src.helpers import get_name
from src.utils import get_gas


def collect_local_flags() -> dict:
    parser = ArgumentParser()
    parser.add_argument("--allowance", action="store", dest="allowance", type=int, required=True)
    parser.add_argument("--pool", action="store", dest="pool", type=int, required=True)
    parser.add_argument("--operator", action="store", dest="operator", type=int, required=True)
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


def delegate(allowance: int, pool: int, operator: int):
    try:
        get_logger().info(
            f"Delegating {allowance} to operator {get_name(get_env().OPERATOR_ID)} in pool {get_name(pool)}"
        )

        tx: dict = (
            get_sdk().portal.functions.delegate(pool, [operator], [allowance]).transact(tx_params())
        )

        get_logger().etherscan("delegate", tx)

    except Exception as err:
        get_logger().error("Tx failed, trying again.")
        get_logger().error(err)


if __name__ == "__main__":
    setup_globals(flag_collector=collect_local_flags)
    f: dict = get_flags()

    if hasattr(f, 'sleep'):
        while True:
            delegate(f.allowance, f.pool, f.operator)

            sleep(f.sleep)
    else:
        delegate(f.allowance, f.pool, f.operator)
