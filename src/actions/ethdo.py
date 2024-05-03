import json
from subprocess import check_output
import geodefi
from src.globals.sdk import SDK
from src.globals.env import ACCOUNT_PASSPHRASE, WALLET_PASSPHRASE
from src.globals.config import CONFIG


def generate_deposit_data(
    withdrawaladdress: str,
    depositvalue: str,
) -> list:
    """Get a fresh deposit data from ethdo

    Args:
        withdrawaladdress (str): WithdrawalPackage contract address of the desired pool
        depositvalue (str): 1 ETH on proposals & 31 ETH on stake calls.
    """

    res: str = check_output(
        [
            "ethdo",
            "validator",
            "depositdata",
            f"--validatoraccount={CONFIG.ethdo.account_name}",
            f"--passphrase={ACCOUNT_PASSPHRASE}",
            f"--withdrawaladdress={withdrawaladdress}",
            f"--depositvalue={depositvalue}",
            f"--forkversion={geodefi.globals.GENESIS_FORK_VERSION[SDK.network]}",
            "--launchpad",
        ]
    )

    return json.loads(res)


def create_wallet() -> list:
    """Creates a new wallet to be used on ethdo"""

    res: str = check_output(
        [
            "ethdo",
            "wallet",
            "create",
            f"--wallet={CONFIG.ethdo.wallet_name}",
            f"--wallet-passphrase={WALLET_PASSPHRASE}",
            f"-type=hd",
        ]
    )
    return json.loads(res)


def create_account() -> list:
    """Creates a new account on given ethdo wallet"""

    res: str = check_output(
        [
            "ethdo",
            "account",
            "create",
            f"--account={CONFIG.ethdo.account_name}",
            f"--passphrase={ACCOUNT_PASSPHRASE}",
            f"--wallet-passphrase={WALLET_PASSPHRASE}",
        ]
    )

    return json.loads(res)


def exit_validator(pubkey: str) -> list:
    """Triggers a validator exit for given pubkey"""

    res: str = check_output(
        [
            "ethdo",
            "validator",
            "exit",
            f"----validator={pubkey}",
            f"--passphrase={ACCOUNT_PASSPHRASE}",
            f"--wallet-passphrase={WALLET_PASSPHRASE}",
        ]
    )

    return json.loads(res)
