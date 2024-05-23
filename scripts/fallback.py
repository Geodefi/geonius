# Initilize Geode
from os import getenv
from time import sleep
import random

import sys

sys.path.append(".")

from dotenv import load_dotenv

from geodefi import Geode
from geodefi.globals import ID_TYPE

from src.globals import SDK
from src.helpers import get_name
from src.logger import log

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

thresholds = range(5 * 10**8, 10**10 + 1, 5 * 10**8)

while True:
    for operator_id in operators:
        try:
            pool_id = random.choice(pools)
            fallback_threshold = random.choice(thresholds)
            log.info(
                f"Setting fallback operator for pool {get_name(pool_id)} to operator {get_name(operator_id)} with threshold {fallback_threshold}"
            )
            tx_hash: str = SDK.portal.contract.functions.setFallbackOperator(
                pool_id, operator_id, fallback_threshold
            ).transact({"from": SDK.w3.eth.defaultAccount.address})
            log.info(f"tx:\nhttps://holesky.etherscan.io/tx/{tx_hash.hex()}\n\n")
        except:
            log.error("Tx failed, trying again.")
        sleep(61)
