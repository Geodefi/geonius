# -*- coding: utf-8 -*-

from geodefi import Geode
from web3.middleware import construct_sign_and_send_raw_middleware
from src.globals.exceptions import CouldNotConnect
from src.globals.env import EXECUTION_API, CONSENSUS_API, PRIVATE_KEY


def __init_sdk(exec_api: str, cons_api: str, priv_key: str = None) -> Geode:
    """
    Initialize an SDK object according to the env vars and return
    """
    try:
        sdk: Geode = Geode(exec_api=exec_api, cons_api=cons_api)

        if priv_key:
            # Create account on Geode's web3py instance
            acct = sdk.w3.eth.account.from_key(priv_key)

            # Allow Geodefi to use your private key
            sdk.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))

            # Set default account if one address is used generally
            sdk.w3.eth.defaultAccount = acct
        else:
            raise CouldNotConnect 
        return sdk

    except Exception as e:
        raise CouldNotConnect from e


# global SDK
SDK: Geode = __init_sdk(
    exec_api=EXECUTION_API, cons_api=CONSENSUS_API, priv_key=PRIVATE_KEY
)
