# Geonius

Geonius is a multi**daemon**tional daemonic python script that allows Node Operators to automate their operations on geodefi Operator Marketplace

- [Geonius](#geonius)
  - [Validator Creation Explained](#validator-creation-explained)
  - [Getting Started](#getting-started)
  - [Installation](#installation)
    - [Binaries](#binaries)
    - [Docker](#docker)
    - [Build from source](#build-from-source)
  - [Usage](#usage)
    - [Flags](#flags)
    - [Scripts](#scripts)
  - [Contacts](#contacts)
  - [License](#license)

## Validator Creation Explained
<!-- TODO -->
1. Delegation
2. Proposal
3. Approval
4. Activation

## Getting Started

[Here](./docs/getting_started.md) is the detailed documentation explaining how to install and configure dependencies before installing and running a `geonius` instance.

## Installation

### Binaries

Binaries for the latest version of Geonius can be obtained from the [releases page](https://github.com/Geodefi/geonius/releases).

### Docker

You can obtain the latest version of geonius using docker with:

```bash
docker pull Geodefi/geonius
```

### Build from source
<!-- TODO: needs to check -->

## Usage
<!-- TODO: add more information on usage -->
Run:

 ```bash
 export PYTHONFAULTHANDLER=1
 PYTHONPATH=.  python3 src/main.py --flags 
 ```

 Put & to run it on background

### Flags

| Parameter  | Description |
| --- | --- |
| --background          |      Runs All daemons in the background, does not block the terminal with outputs                                             |
| --no-log-stream       |      Don't print log messages to stdout                                                                                       |
| --no-log-file         |      Don't save log messages to files                                                                                         |
| --min-proposal-queue  |      Minimum amount of proposals to wait before creating a tx                                                                 |
| --max-proposal-delay  |      Max seconds for any proposals to wait                                                                                    |
| --main-directory      |      Main directory name that will be created, and used to store data                                                         |
| --logger-directory    |      Main directory the log files will be stored                                                                              |
| --logger-level        |      Set log level to DEBUG, INFO, WARNING, ERROR, CRITICAL                                                                   |
| --logger-when         |      When should logger continue with a new file: 'S', 'M', 'H', 'D', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'midnight'    |
| --logger-interval     |      How many intervals before logger continue with a new file                                                                |
| --logger-backup       |      How many logger files will be saved per logger                                                                           |
| --database-directory  |      Database directory name                                                                                                  |
| --chain-start         |      The first block to be considered for events within given chain                                                           |
| --chain-identifier    |      Method to rely when fetching new blocks: latest, earliest, pending, safe, finalized                                      |
| --chain-period        |      The amount of periods before checking for new blocks                                                                     |
| --chain-interval      |      Avg block time to rely on for given chain                                                                                |
| --chain-range         |      Maximum block to use when grouping a range of blocks                                                                     |
| --ethdo-wallet        |      Default ethdo wallet name to be created/used                                                                             |
| --ethdo-account       |      Deafult ethdo account name to be created/used                                                                            |

### Scripts
<!-- TODO: add more information on additional scripts when coded -->

## Contacts

- Ice Bear - <admin@geode.fi>
- Crash Bandicoot - <bandicoot@geode.fi>

## License

`geonius` is licensed under [MIT](./LICENSE).
