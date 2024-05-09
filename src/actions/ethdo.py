import json
from subprocess import check_output
import geodefi

from src.globals.sdk import SDK
from src.globals.env import ACCOUNT_PASSPHRASE, WALLET_PASSPHRASE
from src.globals.config import CONFIG


def generate_deposit_data(
    withdrawal_address: str,
    deposit_value: str,
) -> dict:
    """Generates the deposit data for a new validator proposal.

    Args:
        withdrawal_address (str): WithdrawalPackage contract address of the desired pool to withdraw the deposit.
        deposit_value (str): The amount of deposit to be made, 1 ETH on proposal, 31 ETH on stake.

    Returns:
        dict: Returns the deposit data in JSON format.
    """

    res: str = check_output(
        [
            "ethdo",
            "validator",
            "depositdata",
            f"--validatoraccount={CONFIG.ethdo.account_name}",
            f"--passphrase={ACCOUNT_PASSPHRASE}",
            f"--withdrawaladdress={withdrawal_address}",
            f"--depositvalue={deposit_value}",
            f"--forkversion={geodefi.globals.GENESIS_FORK_VERSION[SDK.network]}",
            "--launchpad",
        ]
    )

    return json.loads(res)


def create_wallet() -> dict:
    """Creates a new wallet to be used on ethdo

    Returns:
        dict: Returns the wallet data in JSON format.
    """

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


def create_account() -> dict:
    """Creates a new account on given ethdo wallet

    Returns:
        dict: Returns the account data in JSON format.
    """

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


def exit_validator(pubkey: str) -> dict:
    """Triggers a validator exit for given pubkey

    Args:
        pubkey (str): The validator pubkey to exit

    Returns:
        dict: Returns the exit data in JSON format.
    """

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
