# -*- coding: utf-8 -*-

import json
from subprocess import check_output
import geodefi

from src.globals import SDK, ACCOUNT_PASSPHRASE, WALLET_PASSPHRASE, CONFIG

from src.logger import log
from src.exceptions import EthdoError


def generate_deposit_data(withdrawal_address: str, deposit_value: str, index: int = None) -> dict:
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
    log.info(f"Generating deposit data{f'index: {index}'if index else '' }")

    account: str = CONFIG.ethdo.account
    wallet: str = CONFIG.ethdo.wallet
    # if index is not None:
    #     account += str(index)

    try:
        res: str = check_output(
            [
                "ethdo",
                "validators",
                "depositdata",
                f"--validatoraccount{wallet}/{account}",
                f"--passphrase={ACCOUNT_PASSPHRASE}",
                f"--withdrawaladdress={withdrawal_address}",
                f"--depositvalue={deposit_value}",
                f"--forkversion={geodefi.globals.GENESIS_FORK_VERSION[SDK.network].hex()}",
                "--launchpad",
            ]
        )

        print("ETHDO RESPONSE", res)

    except Exception as e:
        print("ETHDO ERROR", e)
        raise EthdoError(
            f"Failed to generate deposit data from account {account} \
                with withdrawal address {withdrawal_address}, deposit value {deposit_value} \
                and fork version {geodefi.globals.GENESIS_FORK_VERSION[SDK.network]}",
        ) from e

    try:
        return json.loads(res)
    except (json.JSONDecodeError, TypeError) as e:
        log.error(f"Failed to interpret the response from ethdo: {res}")
        raise e
    except Exception as e:
        raise e


def create_wallet() -> dict:
    """Creates a new wallet to be used on ethdo

    Returns:
        dict: Returns the wallet data in JSON format.

    Raises:
        EthdoError: Raised if the wallet creation fails.
        JSONDecodeError: Raised if the response cannot be decoded to JSON.
        TypeError: Raised if the response is not type of str, bytes or bytearray.
    """
    log.info(f"Creating a new wallet: {CONFIG.ethdo.wallet}")

    try:
        res: str = check_output(
            [
                "ethdo",
                "wallet",
                "create",
                f"--wallet={CONFIG.ethdo.wallet}",
                f"--wallet-passphrase={WALLET_PASSPHRASE}",
                f"-type=hd",
            ]
        )

    except Exception as e:
        raise EthdoError(f"Failed to create wallet {CONFIG.ethdo.wallet}") from e

    try:
        return json.loads(res)
    except (json.JSONDecodeError, TypeError) as e:
        log.error(f"Failed to interpret the response from ethdo: {res}")
        raise e
    except Exception as e:
        raise e


def create_account(index: int = None) -> dict:
    """Creates a new account on given ethdo wallet

    Returns:
        dict: Returns the account data in JSON format.

    Raises:
        EthdoError: Raised if the account creation fails.
        JSONDecodeError: Raised if the response cannot be decoded to JSON.
        TypeError: Raised if the response is not type of str, bytes or bytearray.
    """

    account = CONFIG.ethdo.account
    if index:
        account += f"_{index}_"

    log.info(f"Creating a new account: {account} on wallet: {CONFIG.ethdo.wallet}")

    try:
        res: str = check_output(
            [
                "ethdo",
                "account",
                "create",
                f"--account={CONFIG.ethdo.wallet}/{account}",
                f"--passphrase={ACCOUNT_PASSPHRASE}",
                f"--wallet-passphrase={WALLET_PASSPHRASE}",
            ]
        )

    except Exception as e:
        raise EthdoError(f"Failed to create account {account}") from e

    try:
        return json.loads(res)
    except (json.JSONDecodeError, TypeError) as e:
        log.error(f"Failed to interpret the response from ethdo: {res}")
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
    log.info(f"Exiting from a validator: {pubkey}")

    try:
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

    except Exception as e:
        raise EthdoError(f"Failed to exit validator {pubkey}") from e

    try:
        return json.loads(res)
    except (json.JSONDecodeError, TypeError) as e:
        log.error(f"Failed to interpret the response from ethdo")
        raise e
    except Exception as e:
        raise e
