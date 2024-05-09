# -*- coding: utf-8 -*-

from geodefi import Geode
from web3.middleware import construct_sign_and_send_raw_middleware
from src.globals.exceptions import CouldNotConnect
from src.globals.env import EXECUTION_API, CONSENSUS_API, PRIVATE_KEY


def __set_web3_account(sdk: Geode) -> Geode:
    """Sets the web3 account to the private key provided in the environment variables.

    Args:
        sdk: Initialized Geode SDK instance.

    Returns:
        Geode: Initialized Geode SDK instance.
    """

    # Create account on Geode's web3py instance
    acct = sdk.w3.eth.account.from_key(PRIVATE_KEY)

    # Allow Geodefi to use your private key on transact
    sdk.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))

    # Set default account if one address is used generally
    sdk.w3.eth.defaultAccount = acct

    return sdk


def __init_sdk(exec_api: str, cons_api: str, priv_key: str = None) -> Geode:
    """Initializes the SDK with the provided APIs and private key. If private key is provided, sets the web3 account.

    Args:
        exec_api (str): Execution API URL.
        cons_api (str): Consensus API URL.
        priv_key (str, optional): Private key to be used. Default is None.

    Returns:
        Geode: Initialized Geode SDK instance.
    """
    try:
        sdk: Geode = Geode(exec_api=exec_api, cons_api=cons_api)
        if priv_key:
            sdk = __set_web3_account(sdk)
        else:
            raise CouldNotConnect
        return sdk

    except Exception as e:
        raise CouldNotConnect from e


# global SDK
SDK: Geode = __init_sdk(exec_api=EXECUTION_API, cons_api=CONSENSUS_API, priv_key=PRIVATE_KEY)
