# Geonius

- [Geonius](#geonius)
  - [What is geonius?](#what-is-geonius)
    - [How it works?](#how-it-works)
    - [What geonius does not do](#what-geonius-does-not-do)
    - [What geonius does](#what-geonius-does)
  - [Prerequisites](#prerequisites)
    - [Ethdo](#ethdo)
    - [Vouch](#vouch)
      - [Vouch: A Novel Approach on Client Diversity](#vouch-a-novel-approach-on-client-diversity)
    - [Execution node](#execution-node)
    - [Consensus node](#consensus-node)
  - [Installation](#installation)
    - [Using pipx](#using-pipx)
    - [Using a Binary Executable](#using-a-binary-executable)
    - [Build from source](#build-from-source)
  - [Configuration](#configuration)
    - [1. Register as a Permissioned Node Operator](#1-register-as-a-permissioned-node-operator)
    - [2. Create a .geonius folder](#2-create-a-geonius-folder)
      - [config.json](#configjson)
      - [.env](#env)
    - [3. Setting up the gas api](#3-setting-up-the-gas-api)
    - [4. Setting up the notification service](#4-setting-up-the-notification-service)
      - [--dont-notify-devs](#--dont-notify-devs)
  - [Running geonius](#running-geonius)
    - [Preflight checks](#preflight-checks)
      - [Maintainer](#maintainer)
      - [Internal Wallet](#internal-wallet)
    - [with pipx](#with-pipx)
    - [with Binary](#with-binary)
    - [with source files](#with-source-files)
  - [Commands \& Flags](#commands--flags)
  - [Contacts](#contacts)
  - [License](#license)

## What is geonius?

Geonius is a **highly costumisable** multi*daemon*tional cli app that automates [geoDefi](https://www.geode.fi) Node Operators.

### How it works?

Geonius keeps track of all of the staking pools created through geodefi's Portal, and creates multiple daemons for 4 main tasks:

- Proposing new validators when suitable, :
  - When a new **delegation** from a pool's maintainer to the Node Operator's ID is registered, checks if there is enough available ether that is deposited & waiting to be staked.
  - When there is a new deposit on a staking pool that already delegated some allowance to the Node Operator.
  - When a pool maintainer sets the Node Operator as a fallback Operator. Which means, the Operator can create as many validators as possible when all other delegations are filled.
- Finalizing the validator creation when the proposal is approved by the oracle.
- Exiting from the validator when there is a new exit request for a specific validator pubkey.

> There are multiple daemons that are mostly just listening some events on Portal.
>
> Check [this document](docs/daemons.md) to learn more about these daemons.

### What geonius does not do

Simply, it does not interact with anything other than the bare minimum required to run a Node Operator service on geodefi. So, it does not empose any trust assumptions.

- Does not register or initiate a Node Operator service to be available on geodefi, visit [join.geodefi](https://www.join.geode.fi) for that
- Does not maintain the validators, keep the validator keys or secure the withdrawal keys. Delegates to [ethdo](https://github.com/wealdtech/ethdo) for that.
- Does not create a bridge for the communication between ethdo and the validator, that is crucial for block building. Delegates to [vouch](<https://github.com/attestantio/vouch/tree/master>) for that.
- Does not create validator keys, ask for mnemonic, ask for permission to build blocks, or in any way communicate with the validator.
- Does not trust you or your friends.

### What geonius does

- Help you with its configuration.
- Proposes new validators that are created through ethdo.
- Waits for validator proposals to be approved.
- Finalizes the stake when the proposals are approved.
- Intitiates a withdrawal on the validator when asked, via ethdo.
- Checks if the gas is ok, before submitting a transaction.
- Mails to its owners when there is a matter of importance, if the notification service is configured.
- Refuses to eleborate and leaves (sometimes). So, it is crucial to check if it is still alive every now and then.

## Prerequisites

Geonius does not actually need a consensus or execution client! It only needs an api endpoint to start running. But, ethdo and vouch does need the nodes for the validator operations.

![Dependency graphs](./docs/img/dependency.png)

### Ethdo

[Ethdo](https://github.com/wealdtech/ethdo) is a command-line tool for managing common tasks in Ethereum 2, such as validator deposit-data generation, voluntary exit etc.

[Ethdo](https://github.com/wealdtech/ethdo) contains a large number of features that are useful for day-to-day interactions, suitable with the different consensus clients. It helps anything related with the Beacon chain wallets and accounts.

> If you need help while installing or interacting with Ethdo, check out [this document](./docs/ethdo_vouch.md).

### Vouch

[Vouch](https://github.com/attestantio/vouch) is a multi-node validator client that will create the bridge between the wallet managers (ethdo, dirk, etc.) and beacon chain clients.

#### Vouch: A Novel Approach on Client Diversity

Vouch is a powerful tool. Thanks to Vouch, Geonius supports utilizing multiple beacon chain clients at the same time. Thus, it helps solving the client diversity by choosing to delegate the validator operations to Vouch.

> If you need help while installing or interacting with Vouch, check out [this document](./docs/ethdo_vouch.md).
>
### Execution node

Geonius likes to have access to a execution client that is fully synced and running.
Any client that supports [API specification](https://ethereum.github.io/execution-apis/api-documentation/) can be used.

However, since the validator ops is delegated to ethdo and vouch, it only needs the api endpoint to read from ethereum and submit transactions when needed.

### Consensus node

Geonius likes to have access to a consensus client that is fully synced and running.
Any client that supports[API specification v2.3.0](https://ethereum.github.io/beacon-APIs/?urls.primaryName=v2.3.0) can be used.

However, since the validator ops is delegated to ethdo and vouch, it only needs the api endpoint to track the validator on the beacon chain.

> #### Do not use MEV clients
>
> Currently Geodefi Staking Library does not support MEV income.
> However, it will be supported on the mainnet launch.

## Installation

### Using pipx

> **Preferred**
>
> [pipx](https://pipx.pypa.io/stable/) is the go-to choice for executable python applications.
> Running this cli app with pipx will make it easy to update, and less error prone compared to using a binary executable or building from source.

```bash
pipx install https://github.com/Geodefi/geonius/tree/main
```

Pipx installation requires python version between **3.8** to **3.12**.

Check out [this document](./docs/installation_guide.md) if you need help or suggestions on this.

### Using a Binary Executable

Binaries for the latest version of Geonius can be obtained from the [releases page](https://github.com/Geodefi/geonius/releases).

Simply, locate and download the suitable one for your operation system.

### Build from source

Check out [this document](./docs/installation_guide.md).

## Configuration

### 1. Register as a Permissioned Node Operator

Before configuration, visit [join.geodefi](https://www.join.geode.fi/?chain=holesky) to register as a Node Operator. Keep your operator ID to be utilized in geonius.

> Here, you will obtain an `OPERATOR_ID` that will define your Node Operator. **Take a note of it!**

### 2. Create a .geonius folder

> Note that, this is unnecessary and `geonius config` command will create one for you. However, if you want to make sure everything is perfect, or if you already have a configuration file (config.json) or an environment file (.env) that you want to use and skip the `geonius config` step; you can.
>
> Alternatively;
>
> ```bash
> geonius config
> ```

This folder should be placed under the same parent folder where the geonius script will run.

It will be used for the database, store the log files and keep the configuration file for you.

#### config.json

A sample config.json with gas and email services activated can be found [here](./.geonius/config.json).

If you want to understand the meaning of the fields, you can check [Commands \& Flags](#commands--flags).

#### .env

A sample config.json with gas and email services activated can be found [here](./.geonius/.env.sample).

- `GEONIUS_PRIVATE_KEY` : private key for the Node Operator maintainer that will run geonius.
- `ETHDO_WALLET_PASSPHRASE` : wallet password for the ethdo wallet that is specified in config.json
- `ETHDO_ACCOUNT_PASSPHRASE`: password for the created accounts that will act as a validator.
- `API_KEY_EXECUTION` : (optional) api key that will be changed with the "<API_KEY_EXECUTION>" section of the execution layer api string. Not needed if the endpoint does not need a key.
- `API_KEY_CONSENSUS` : (optional) api key that will be changed with the "<API_KEY_CONSENSUS>" section of the consensus layer api string. Not needed if the endpoint does not need a key.
- `API_KEY_GAS` : (optional) api key that will be changed with the "<API_KEY_GAS>" section of the gas api string. Not needed if the endpoint does not need a key.
- `EMAIL_PASSWORD` : (optional) Not needed if the notification service is not configured.

### 3. Setting up the gas api

> Not suggested for holesky deployments.

Simply, you can provide any endpoint that responds as **gwei**, which will be used as a gas price oracle.
Moreover, you can add maximum limits to the base and priority fees when api is provided.

Note that you can also create a custom parser! For example, if the response has a body that looks like this, and you want to choose the "high" option.

```json
{
  "low":..,
  "mid":..,
  "high": {"base":0,"priority":0}
}
```

Then you can provide the parser as :
{
  "base": "high.base",
  "priority": "high.priority"
}

For an easy setup, visit [infura](https://docs.infura.io/api/infura-expansion-apis/gas-api/api-reference/gasprices-type2) and aquire an app key. Then you can use the default parsers on the configuration step.

### 4. Setting up the notification service

You can configure this service easily so geonius send you regular updates or notifications on its current situation. This can be crucial if there is a bug and geonius fully or partially stops.

Sign into gmail and head to: `https://myaccount.google.com/apppasswords`. Then you will acquire a passphrase like "xxx xxx xxx xxx". This password can be provided during the configuration with `geonius config` or as `EMAIL_PASSWORD` directly in .env file.

Then all you need to do is to provide the mail addresses for receiver and sender.

> Note that, you can add many for the receiver field.

#### --dont-notify-devs

When there is an unexpected error, geonius will send emails to the geodefi team as well (<notifications@geode.fi>). To prevent this, provide `dont-notify-devs` flag when running it.

## Running geonius

Up until this point, if you have:

1. Got a execution node is ready or already have one running for the target chain.
2. Similarly, a consensus node is ready.
3. Installed ethdo and created a wallet for geonius.
4. Installed vouch and configured it with a yml/json file.
5. Installed geonius with pipx, or downloaded it as a binary, or built it from source.
6. Configured it with `geonius config`

So, you are ready to start geonius.

### Preflight checks

#### Maintainer

Note that, you can set a new maintainer using the current CONTROLLER (registerer) address.

Check out [Commands \& Flags](#commands--flags) for `change-maintainer` command.

#### Internal Wallet

Because of the bug explained [here](https://medium.com/immunefi/rocketpool-lido-frontrunning-bug-fix-postmortem-e701f26d7971), Operators need **1 Ether per validator proposal** available in your internal wallet.

You will be reimbursed after activating the validator. However, this amount limits how many proposals you can have at the same time.

> If you have 10 Ether in your internal wallet, and since it takes around 24 hours for a proposal to be approved:
> You can propose 10 validators a day.

> The Internal Wallet is also the place where your fees will accrue over time.

Check out [Commands \& Flags](#commands--flags) for `increase-wallet` command.

### with pipx

```bash
geonius run --chain holesky
```

### with Binary

```bash
geonius run --chain holesky
```

### with source files

Check out [this document](./docs/installation_guide.md).

## Commands & Flags

[Check out this document.](./docs/commands.md)

## Contacts

- Ice Bear - <admin@geode.fi>
- Crash Bandicoot - <bandicoot@geode.fi>

## License

`geonius` is licensed under [MIT](./LICENSE).
