# -*- coding: utf-8 -*-

from os import getenv
from dotenv import load_dotenv
from src.common.attribute_dict import AttributeDict


def load_env():
    # TODO: (now) path can be provided through flags or config json
    load_dotenv()
    return AttributeDict.convert_recursive(
        {
            "EXECUTION_API": getenv("EXECUTION_API"),
            "CONSENSUS_API": getenv("CONSENSUS_API"),
            "PRIVATE_KEY": getenv("PRIVATE_KEY"),
            "OPERATOR_ID": int(getenv("OPERATOR_ID")),
            "ACCOUNT_PASSPHRASE": getenv("ACCOUNT_PASSPHRASE"),
            "WALLET_PASSPHRASE": getenv("WALLET_PASSPHRASE"),
            "SENDER_EMAIL": getenv('SENDER_EMAIL'),
            "SENDER_PASSWORD": getenv('SENDER_PASSWORD'),
            "RECEIVER_EMAIL": getenv('RECEIVER_EMAIL'),
            "GAS_API_KEY": getenv("GAS_API_KEY"),
        }
    )
