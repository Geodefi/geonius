# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

from src.common import AttributeDict
from src.globals import get_flags


def load_env():
    flags: dict = get_flags()
    dotenv_path = os.path.join(flags.main_directory, '.env')

    load_dotenv(dotenv_path)
    return AttributeDict.convert_recursive(
        {  # TODO: (now) some of these belong to config:
            "EXECUTION_API": os.getenv("EXECUTION_API"),  # THIS
            "CONSENSUS_API": os.getenv("CONSENSUS_API"),  # THIS
            "PRIVATE_KEY": os.getenv("PRIVATE_KEY"),
            "OPERATOR_ID": int(os.getenv("OPERATOR_ID")),  # THIS
            "ACCOUNT_PASSPHRASE": os.getenv("ACCOUNT_PASSPHRASE"),
            "WALLET_PASSPHRASE": os.getenv("WALLET_PASSPHRASE"),
            "SENDER_EMAIL": os.getenv('SENDER_EMAIL'),  # THIS, RENAME
            "SENDER_PASSWORD": os.getenv('SENDER_PASSWORD'),  # just RENAME
            "RECEIVER_EMAIL": os.getenv('RECEIVER_EMAIL'),  # THIS, RENAME
            "GAS_API_KEY": os.getenv("GAS_API_KEY"),
        }
    )
