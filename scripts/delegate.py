# Initilize Geode
from time import sleep
from os import getenv
import random

from dotenv import load_dotenv

from geodefi.globals import ID_TYPE

from geodefi import Geode

import sys

sys.path.append(".")

from src.globals import SDK, PRIVATE_KEY
from src.helpers import get_name
from src.logger import log
from src.utils import get_gas

load_dotenv()

geode = Geode(exec_api=getenv('EXECUTION_API'), cons_api=getenv('CONSENSUS_API'))

portal = geode.portal

pools = list()
pools_type = ID_TYPE.POOL
pools_len = portal.functions.allIdsByTypeLength(pools_type).call()

if pools_len > 0:
    for i in range(pools_len):
        pools.append(portal.functions.allIdsByType(pools_type, i).call())

### UNIQUE PART BELOW

# GET OPERATORS LIST
operators = list()
op_type = ID_TYPE.OPERATOR
op_len = portal.functions.allIdsByTypeLength(op_type).call()

if op_len > 0:
    for i in range(op_len):
        operators.append(portal.functions.allIdsByType(op_type, i).call())

# OUT OPERATORS
crash_op = operators[0]
ice_op = operators[1]

# DELEGATE
while True:

    for op_id in operators:
        try:
            allowance = random.randint(0, 100)
            pool_id = random.choice(pools)
            log.info(
                f"Delegating {allowance} to operator {get_name(op_id)} in pool {get_name(pool_id)}"
            )

            # priority_fee, base_fee = get_gas()

            address = SDK.w3.eth.defaultAccount.address

            tx: dict = SDK.portal.contract.functions.delegate(
                pool_id, [op_id], [allowance]
            ).build_transaction(
                {
                    "nonce": SDK.w3.eth.get_transaction_count(address),
                    "from": address,
                    # "maxPriorityFeePerGas": priority_fee,
                    # "maxFeePerGas": base_fee,
                }
            )

            signed_tx = SDK.w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash: bytes = SDK.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            log.info(f"tx:\nhttps://holesky.etherscan.io/tx/0x{tx_hash.hex()}\n\n")

        except Exception as err:
            log.error("Tx failed, trying again.")
            log.error(err)
        sleep(87)
