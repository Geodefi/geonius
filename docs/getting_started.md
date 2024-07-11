# Getting Started- [Getting Started](#getting-started)

- [Getting Started- Getting Started](#getting-started--getting-started)
  - [Prerequisites](#prerequisites)
    - [1. Join Operator Marketplace](#1-join-operator-marketplace)
      - [Set a maintainer](#set-a-maintainer)
      - [Deposit ether to internal wallet](#deposit-ether-to-internal-wallet)
    - [2. Execution Client](#2-execution-client)
    - [3. Consensus Client](#3-consensus-client)
    - [4. Ethdo \& Vouch](#4-ethdo--vouch)
  - [Running Geonius](#running-geonius)

## Prerequisites

> ### Do not use MEV clients
>
> Currently Geodefi Staking Library does not support MEV income.
> However, it will be supported on the mainnet launch.

### 1. Join Operator Marketplace

To be able to utilize staking pools as a Node Operator and create validators, you will need to join [geodefi marketplace](https://www.info.geode.fi/operators). Visit [onboarding page](join.geode.fi) to initialize your Node Operator after being onboarded by Geodefi government.

> Here, you will obtain an `OPERATOR_ID` that will define your Node Operator. Note it!

#### Set a maintainer

After joining to the marketplace and initialization, your Node Operator can immediately start creating validators. The address we will use to own and control the Operator is named `CONTROLLER`. The address that handles the daily operations is named `maintainer`. Currently, both points to the address that is used to initialize the Operator.

We should be careful and set a hotwallet address to `maintainer`, while keeping the `CONTROLLER` safe, such as using via assigning to a multisig.

`changeMaintainer` can be called by:

- [etherscan on holesky](https://holesky.etherscan.io/address/0x181C0F3103116Cc02665365c7a5E5574db011D38#writeProxyContract#F5).
<!-- TODO: how to achieve this? -->
- geonius change-maintainer <_new_maintainer_address_>

#### Deposit ether to internal wallet

Every ID has an Internal Wallet, which makes transferring Ether easier for both Geode's Portal, and it's users.

> The Internal Wallet is also the place where your fees will accrue over time.

Because of the bug explained [here](https://medium.com/immunefi/rocketpool-lido-frontrunning-bug-fix-postmortem-e701f26d7971), Operators need **1 Ether per validator proposal** available in your internal wallet.

You will be reimbursed after activating the validator. However, this amount limits how many proposals you can have at the same time.

> If you have 100 Ether in your internal wallet, and if it takes 1 day for proposals to be approved:
> You can propose 100 validators a day.

`increaseWalletBalance` can be called by:

- [etherscan on holesky](https://holesky.etherscan.io/address/0x181C0F3103116Cc02665365c7a5E5574db011D38#writeProxyContract#F12).
<!-- TODO: how to achieve this? -->
- geonius increase_wallet <_eth_amount_>

> Similarly, `decreaseWalletBalance` can be called by:
>
> - etherscan
> - geonius withdraw-portal <_eth_amount_>

### 2. Execution Client

Geonius requires an execution client that is fully synced and running.
While any client that supports [API specification](https://ethereum.github.io/execution-apis/api-documentation/) will be supported, currently supported clients:

- [x] Geth
- [ ] Nethermind
- [ ] Besu
- [ ] Erigon

Checkout [this guide](./docs/guides/execution_clients.md) for more.

### 3. Consensus Client

Geonius requires a consensus client that is fully synced and running.
While any client that supports [API specification v2.3.0](https://ethereum.github.io/beacon-APIs/?urls.primaryName=v2.3.0) will be supported, currently supported clients:

- [x] Nimbus
- [ ] Lighthouse
- [ ] Prysm
- [ ] Teku

Checkout [this guide](./docs/guides/consensus_clients.md) for more.

### 4. Ethdo & Vouch

[Ethdo](https://github.com/wealdtech/ethdo) is a command-line tool for managing common tasks in Ethereum 2, such as validator deposit-data generation, voluntary exit etc.

[Vouch](https://github.com/attestantio/vouch) is a multi-node validator client that will create the bridge between the wallet managers: ethdo, dirk, etc.; and eth2 clients.

Checkout [this guide](./docs/guides/ethdo_vouch.md) for more.

## Running Geonius

<!-- TODO: check -->

```bash
geth  --holesky --authrpc.addr localhost --authrpc.port 8551 --authrpc.vhosts localhost --authrpc.jwtsecret /tmp/jwtsecret --http --http.api eth,net,engine,admin --snapshot=false
```

- Runs on holesky network
- Enable the HTTP-RPC server
- AUTH port : 8551
- HTTP port : 8545

```bash
build/nimbus_beacon_node trustedNodeSync  --network:holesky    --data-dir=build/data/shared_holesky_0    --trusted-node-url="https://checkpoint-sync.holesky.ethpandaops.io"
```

- Sync nimbus with trusted node (faster)

```bash
./run-holesky-beacon-node.sh \
  --el="http://127.0.0.1:8551" \
  --jwt-secret=/tmp/jwtsecret --rest
```

- connects to port 8551

```bash
vouch
```

- run vouch

```bash
geonius
```

- run geonius
