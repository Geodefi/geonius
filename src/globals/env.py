# -*- coding: utf-8 -*-

from os import getenv

# catch environment variables
EXECUTION_API = getenv("EXECUTION_API")
CONSENSUS_API = getenv("CONSENSUS_API")
PRIVATE_KEY = getenv("PRIVATE_KEY")
OPERATOR_ID = int(getenv("OPERATOR_ID"))

ACCOUNT_PASSPHRASE = getenv("ACCOUNT_PASSPHRASE")
WALLET_PASSPHRASE = getenv("WALLET_PASSPHRASE")
