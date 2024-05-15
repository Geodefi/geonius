# -*- coding: utf-8 -*-

import sys
from geodefi import Geode
from web3.middleware import construct_sign_and_send_raw_middleware

from src.globals.env import EXECUTION_API, CONSENSUS_API, PRIVATE_KEY
from src.utils.error import PrivateKeyMissingError


def __set_web3_account(sdk: Geode, private_key: str) -> Geode:
    """Sets the web3 account to the private key provided in the environment variables.

    Args:
        sdk: Initialized Geode SDK instance.

    Returns:
        Geode: Initialized Geode SDK instance.
    """

    # Create account on Geode's web3py instance
    acct = sdk.w3.eth.account.from_key(private_key)

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

    Raises:
        SDKException: If an error occurs while initializing the SDK.
    """
    try:
        sdk: Geode = Geode(exec_api=exec_api, cons_api=cons_api)
        if not priv_key:
            raise PrivateKeyMissingError(
                "Problem occured while connecting to SDK, private key is missing in .env file."
            )
        sdk = __set_web3_account(sdk, priv_key)
        return sdk

    except PrivateKeyMissingError as e:
        # TODO: log the error
        sys.exit(e)
    except Exception as e:
        # TODO: log the error
        sys.exit(e)


# global SDK
SDK: Geode = __init_sdk(exec_api=EXECUTION_API, cons_api=CONSENSUS_API, priv_key=PRIVATE_KEY)
