# -*- coding: utf-8 -*-

import json
from subprocess import check_output

import geodefi

from src.exceptions import EthdoError
from src.globals import get_sdk, get_env, get_config, get_logger


def generate_deposit_data(withdrawal_address: str, deposit_value: str, index: int) -> dict:
    """Generates the deposit data for a new validator proposal.

    Args:
        withdrawal_address (str): WithdrawalPackage contract address of the desired pool to withdraw the deposit.
        deposit_value (str): The amount of deposit to be made, 1 ETH on proposal, 31 ETH on stake.

    Returns:
        dict: Returns the deposit data in JSON format.

    Raises:
        EthdoError: Raised if the deposit data generation fails.
        JSONDecodeError: Raised if the response cannot be decoded to JSON.
        TypeError: Raised if the response is not type of str, bytes or bytearray.
    """
    get_logger().info(f"Generating deposit data{f'index: {index}'if index else '' }")

    account: str = get_config().ethdo.account
    wallet: str = get_config().ethdo.wallet

    if index is not None:
        account += str(index)

    fork_version = geodefi.globals.GENESIS_FORK_VERSION[get_sdk().network].hex()

    try:
        if not ping_account(wallet=wallet, account=account):
            create_account(index=index)

        res: str = check_output(
            [
                "ethdo",
                "validator",
                "depositdata",
                f"--validatoraccount='{wallet}/{account}'",
                f"--passphrase={get_env().ACCOUNT_PASSPHRASE}",
                f"--withdrawaladdress={withdrawal_address}",
                f"--depositvalue={deposit_value}",
                f"--forkversion={fork_version}",
                "--launchpad",
            ]
        )

    except Exception as e:
        raise EthdoError(
            f"Failed to generate deposit data from account {account} \
                with withdrawal address {withdrawal_address}, deposit value {deposit_value} \
                and fork version {fork_version}. Will try again later.",
        ) from e

    try:
        return json.loads(res)
    except (json.JSONDecodeError, TypeError) as e:
        raise EthdoError(f"Failed to interpret the response from ethdo: {res}") from e


def ping_account(wallet: str, account: str) -> bool:
    """Checks if an account exist on ethdo.

    Args:
        wallet (str): Provided ethdo wallet
        account (str): Provided ethdo account

    Returns:
        bool: True if exists, False if not.
    """
    try:
        check_output(["ethdo", "account", "info", f"--validatoraccount={wallet}/{account}"])
        return True
    # pylint: disable-next=broad-exception-caught
    except Exception:
        return False


def create_account(index: int = None) -> dict:
    """Creates a new account on given ethdo wallet

    Returns:
        dict: Returns the account data in JSON format.

    Raises:
        EthdoError: Raised if the account creation fails.
        JSONDecodeError: Raised if the response cannot be decoded to JSON.
        TypeError: Raised if the response is not type of str, bytes or bytearray.
    """

    account = get_config().ethdo.account

    if index is not None:
        account += f"{index}"

    get_logger().info(f"Creating a new account: {account} on wallet: {get_config().ethdo.wallet}")

    try:
        res: str = check_output(
            [
                "ethdo",
                "account",
                "create",
                f"--account={get_config().ethdo.wallet}/{account}",
                f"--passphrase={get_env().ACCOUNT_PASSPHRASE}",
                f"--wallet-passphrase={get_env().WALLET_PASSPHRASE}",
            ]
        )

    except Exception as e:
        raise EthdoError(f"Failed to create account {account}") from e

    try:
        return json.loads(res)
    except (json.JSONDecodeError, TypeError) as e:
        get_logger().error(f"Failed to interpret the response from ethdo: {res}")
        raise e
    except Exception as e:
        raise e


def exit_validator(pubkey: str) -> dict:
    """Triggers a validator exit for given pubkey

    Args:
        pubkey (str): The validator pubkey to exit

    Returns:
        dict: Returns the exit data in JSON format.

    Raises:
        EthdoError: Raised if the validator exit fails.
        JSONDecodeError: Raised if the response cannot be decoded to JSON.
        TypeError: Raised if the response is not type of str, bytes or bytearray.
    """
    get_logger().info(f"Exiting from a validator: {pubkey}")

    try:
        res: str = check_output(
            [
                "ethdo",
                "validator",
                "exit",
                f"----validator={pubkey}",
                f"--passphrase={get_env().ACCOUNT_PASSPHRASE}",
                f"--wallet-passphrase={get_env().WALLET_PASSPHRASE}",
            ]
        )

    except Exception as e:
        raise EthdoError(f"Failed to exit validator {pubkey}") from e

    try:
        return json.loads(res)
    except (json.JSONDecodeError, TypeError) as e:
        get_logger().error(f"Failed to interpret the response from ethdo")
        raise e
    except Exception as e:
        raise e
