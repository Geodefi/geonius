# Initilize Geode
from time import sleep
from os import getenv
import random

from dotenv import load_dotenv

from geodefi.globals import ID_TYPE

from geodefi import Geode

import sys

sys.path.append(".")

from src.globals import SDK
from src.helpers import get_name


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
            print(
                f"Delegating {allowance} to operator {get_name(op_id)} in pool {get_name(pool_id)}"
            )
            tx_hash: str = SDK.portal.contract.functions.delegate(
                pool_id, [op_id], [allowance]
            ).transact({"from": SDK.w3.eth.defaultAccount.address})
            print(f"tx:\nhttps://holesky.etherscan.io/tx/{tx_hash.hex()}\n\n")
        except:
            print("Tx failed, trying again.")
        sleep(87)


# threshold = 9e9  # 90%
# tx_hash: str = SDK.portal.contract.functions.fallbackThreshold(pool_id, ice_op, threshold).transact(
#     {"from": SDK.w3.eth.defaultAccount.address}
# )
# choose a pool id:
# # random an action:
# # # deposit
# ->>>>>>>>>>>>>> wait.
# # # delegate
# ---------------> random operator
# ->>>>>>>>>>>>>> wait.
# # # fallback
# ---------------> random operator
# ---------------> x% : 1, 30, 90, 100
# ->>>>>>>>>>>>>> wait.
