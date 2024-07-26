# Commands & Flags

## Global flags

The following flags can be provided to all of the commands listed below (except [check-wallet](#check-wallet)). They can also be provided as an environment variable, if that is easier.

### --main-dir

> Corresponds to environment variable: `GEONIUS_DIR`

Relative path for the main directory that will be used to store data. Default is ./.geonius
Required if any folder name other than `.geonius` is being used.

### --chain

> Corresponds to environment variable: `GEONIUS_CHAIN`

Network name, such as 'holesky' or 'ethereum' etc.
**Required for all of the commands. But it will ask if not provided**

### --private-key

> Corresponds to environment variable: `GEONIUS_PRIVATE_KEY`
Private key for the Node Operator maintainer that will run geonius.

Overrides .env file.

### --api-key-execution

> Corresponds to environment variable: `API_KEY_EXECUTION`

Api key for the execution layer end point. Could be the rest api of the execution client.

Overrides .env file.

### --api-key-consensus
  
> Corresponds to environment variable: `API_KEY_CONSENSUS`

Api key for the consensus layer end point. Could be the rest api of the consensus client.

Overrides .env file.

### --api-key-gas

> Corresponds to environment variable: `API_KEY_GAS`

Api key for the end point used fetching gas prices in gwei.

Overrides .env file.

## Main Commands

### config

```bash
geonius config
```

Prints the current config file and its path.

If there is no config file already, **helps creating a new config.json and .env**.
This command should be called **before the first time running geonius**.

- `--reset` : Reset the config file and start over. Suggested if there is anything failing.

### run

```bash
geonius run --chain holesky
```

- `--reset`: Reset the database and start over. Suggested after a new update or unexpected error.
- `--dont-notify-devs`: Don't send email notifications to geodefi for any unexpected errors.
- `--ethdo-account-prefix`: Default ethdo account name to be created/used.
- `--ethdo-wallet`: Default ethdo wallet name to be  created/used.
- `--database-dir`: Directory name that for the database.
- `--logger-backup`: How many logger files will be saved per  logger.
- `--logger-interval`: How many intervals before logger continue with a new file.
- `--logger-when`: When should logger continue with a new file.
- `--logger-level`: Set logging level for both stream and log file.
- `--logger-dir`: Directory name that log files will be stored.
- `--no-log-stream`: Don't print log messages to the terminal.
- `--no-log-file`: Don't store log messages in a file.
- `--max-proposal-delay`: Max seconds for any proposals to wait.
- `--min-proposal-queue`: Minimum amount of proposals to wait before creating a tx.
- `--network-max-attempt`: Api requests will fail after given max calls.
- `--network-attempt-rate`: Interval between api requests (s).
- `--network-refresh-rate`: Cached data will be refreshed after provided delay (s).
- `--chain-consensus-api`: Api endpoint for the consensus layer. Could be the rest api of the consensus client.
- `--chain-execution-api`: Api endpoint for the execution layer. Could be the rest api of the execution client.
- `--chain-range`: Maximum block to use when grouping a range of blocks.
- `--chain-interval`: Average block time to rely on for given chain.
- `--chain-period`: The amount of periods before checking for new blocks.
- `--chain-identifier`:  Identifier fetching new blocks.
- `--chain-start`: The first block to be considered for events within given chain.
- `--operator-id`: geodefi ID for the Node Operator, defaults to configured ID when not provided.

## Operator Commands

Additional commands that make things easier for the maintainers.

### change-maintainer

Changes the maintainer of the Node Operator. Requires the private key of the CONTROLLER.

```bash
geonius change-maintainer
```

- `--operator-id` : geodefi ID for the Node Operator, defaults to configured ID when not provided.

- `--address` :  Maintainer address to set and use in geonius

### check-wallet

```bash
geonius check-wallet
```

> This command does not utilize `--private-key` and `api-key-gas` flags as there is no transaction to create.

- `--operator-id` : geodefi ID for the Node Operator, defaults to configured ID when not provided.

### decrease-wallet

```bash
geonius decrease-wallet
```

- `--operator-id` : geodefi ID for the Node Operator, defaults to configured ID when not provided.
- `--wei` : Amount to withdraw from the internal wallet (wei)
- `--interval` : Will run as a daemon when provided (seconds)

### increase-wallet

```bash
geonius increase-wallet
```

- `--operator-id` : geodefi ID for the Node Operator, defaults to configured ID when not provided.
- `--wei` : Amount to deposit into the internal wallet (wei)
- `--interval` : Will run as a daemon when provided (seconds)

## Pool Commands

Helpful commands when interacting with pools.

### delegate

```bash
geonius delegate
```

- `--pool` : Pool ID to give allowance from.  
- `--operator` : Operator ID that will be allowed to create validators  
- `--allowance` : Number of validators provided Operator can create on behalf of the provided Pool
- `--interval` : Will run as a daemon when provided (seconds)

### deposit

```bash
geonius deposit
```

- `--pool` : Pool ID to deposit ether.  
- `--wei` : Amount to deposit into provided staking pool (wei)  
- `--interval` : Will run as a daemon when provided (seconds)

### set-fallback

```bash
geonius set-fallback
```

- `--pool` : Pool ID that will allow provided operator to create validators when suitable.  
- `--operator` : Operator ID that will be allowed to create validators  
- `--threshold` : Provided Operator can create infinitely many validators after this threshold is filled.
- `--interval` : Will run as a daemon when provided (seconds)
