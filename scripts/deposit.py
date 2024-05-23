# Initilize Geode
from os import getenv
from time import sleep
import random

import sys

sys.path.append(".")

from dotenv import load_dotenv

from geodefi.globals import ID_TYPE

from src.globals import SDK
from src.helpers import get_name

from geodefi import Geode

load_dotenv()

geode = Geode(exec_api=getenv('EXECUTION_API'), cons_api=getenv('CONSENSUS_API'))

portal = geode.portal

pools = list()
pools_type = ID_TYPE.POOL
pools_len = portal.functions.allIdsByTypeLength(pools_type).call()

if pools_len > 0:
    for i in range(12, pools_len):
        pools.append(portal.functions.allIdsByType(pools_type, i).call())

while True:
    try:
        pool_id = random.choice(pools)
        print(f"Depositing 1 wei to pool {get_name(pool_id)}")
        tx_hash: bytes = SDK.portal.contract.functions.deposit(
            int(pool_id),
            0,
            [],
            0,
            1719127731,
            SDK.w3.eth.defaultAccount.address,
        ).transact({"value": 1_000_000_000, "from": SDK.w3.eth.defaultAccount.address})
        print(f"tx:\nhttps://holesky.etherscan.io/tx/{tx_hash.hex()}\n\n")
    except:
        print("Tx failed, trying again.")
    sleep(32)
