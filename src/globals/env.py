# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

from src.common import AttributeDict


def load_env(main_dir: str):
    dotenv_path = os.path.join(main_dir, '.env')

    load_dotenv(dotenv_path)
    return AttributeDict.convert_recursive(
        {
            "PRIVATE_KEY": os.getenv("PRIVATE_KEY"),
            "ACCOUNT_PASSPHRASE": os.getenv("ACCOUNT_PASSPHRASE"),
            "WALLET_PASSPHRASE": os.getenv("WALLET_PASSPHRASE"),
            "EXECUTION_API_KEY": os.getenv("EXECUTION_API_KEY"),
            "CONSENSUS_API_KEY": os.getenv("CONSENSUS_API_KEY"),
            "GAS_API_KEY": os.getenv("GAS_API_KEY"),
            "EMAIL_PASSWORD": os.getenv('EMAIL_PASSWORD'),
        }
    )
