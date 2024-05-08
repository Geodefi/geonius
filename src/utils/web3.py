# -*- coding: utf-8 -*-

from web3.middleware import construct_sign_and_send_raw_middleware
from src.globals import SDK, PRIVATE_KEY


def set_web3_account():
    """Sets the web3 account to the private key provided in the environment variables."""

    # Create account on Geode's web3py instance
    acct = SDK.w3.eth.account.from_key(PRIVATE_KEY)

    # Allow Geodefi to use your private key on transact
    SDK.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))

    # Set default account if one address is used generally
    SDK.w3.eth.defaultAccount = acct
