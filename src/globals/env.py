# -*- coding: utf-8 -*-

from os import getenv
from dotenv import load_dotenv

load_dotenv()

# catch environment variables
EXECUTION_API = getenv("EXECUTION_API")
CONSENSUS_API = getenv("CONSENSUS_API")
PRIVATE_KEY = getenv("PRIVATE_KEY")
OPERATOR_ID = int(getenv("OPERATOR_ID"))

ACCOUNT_PASSPHRASE = getenv("ACCOUNT_PASSPHRASE")
WALLET_PASSPHRASE = getenv("WALLET_PASSPHRASE")

SENDER_EMAIL = getenv('SENDER_EMAIL')
SENDER_PASSWORD = getenv('SENDER_PASSWORD')
RECEIVER_EMAIL = getenv('RECEIVER_EMAIL')
