# -*- coding: utf-8 -*-

import os
from argparse import ArgumentParser
from src.exceptions import UnknownFlagError
from src.common import AttributeDict


def collect_flags() -> dict:
    # TODO: update docs
    parser = ArgumentParser()
    parser.add_argument(
        "--main-directory",
        action="store",
        dest="main_directory",
        help="main directory name that will be created, and used to store data",
        default=os.path.join(os.getcwd(), '.geonius'),
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        dest="reset",
        help="reinitializes the databases",
    )
    parser.add_argument(
        "--dont-notify-devs",
        action="store_true",
        dest="dont_notify_devs",
        help="don't send email notifications to geode for any alerts",
    )
    parser.add_argument(
        "--no-log-stream",
        action="store_true",
        dest="no_log_stream",
        help="don't print log messages to stdout",
    )
    parser.add_argument(
        "--no-log-file",
        action="store_true",
        dest="no_log_file",
        help="don't save log messages to files",
    )
    parser.add_argument(
        "--min-proposal-queue",
        action="store",
        dest="min_proposal_queue",
        type=int,
        help="Minimum amount of proposals to wait before creating a tx",
    )
    parser.add_argument(
        "--max-proposal-delay",
        action="store",
        dest="max_proposal_delay",
        type=int,
        help="Max seconds for any proposals to wait",
    )
    parser.add_argument(
        "--network-refresh-rate",
        action="store",
        dest="network_refresh_rate",
        help="Cached data will be refreshed after provided delay (s)",
    )
    parser.add_argument(
        "--network-attempt-rate",
        action="store",
        dest="network_attempt_rate",
        help="Interval between api requests (s)",
    )
    parser.add_argument(
        "--network-max-attempt",
        action="store",
        dest="network_max_attempt",
        help="Api requests will fail after given max calls",
    )
    parser.add_argument(
        "--logger-directory",
        action="store",
        dest="logger_directory",
        help="main directory the log files will be stored",
    )
    parser.add_argument(
        "--logger-level",
        action="store",
        dest="logger_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="set log level to DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )
    parser.add_argument(
        "--logger-when",
        action="store",
        dest="logger_when",
        choices=['S', 'M', 'H', 'D', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'midnight'],
        help="when should logger continue with a new file",
    )
    parser.add_argument(
        "--logger-interval",
        action="store",
        dest="logger_interval",
        type=int,
        help="how many intervals before logger continue with a new file",
    )
    parser.add_argument(
        "--logger-backup",
        action="store",
        dest="logger_backup",
        type=int,
        help="how many logger files will be saved per logger",
    )
    parser.add_argument(
        "--database-directory",
        action="store",
        dest="database_directory",
        help="database directory name",
    )
    parser.add_argument(
        "--chain",
        action="store",
        dest="chain",
        type=str,
        help="Network name, such as 'holesky' or 'ethereum' etc. Required when providing any other chain setting.",
        required=True,
    )
    parser.add_argument(
        "--chain-start",
        action="store",
        dest="chain_start",
        type=int,
        help="The first block to be considered for events within given chain. Requires --chain",
    )
    parser.add_argument(
        "--chain-identifier",
        action="store",
        dest="chain_identifier",
        choices=["latest", "earliest", "pending", "safe", "finalized"],
        help="method to rely when fetching new blocks: latest, earliest, pending, safe, finalized. Requires --chain",
    )
    parser.add_argument(
        "--chain-period",
        action="store",
        dest="chain_period",
        type=int,
        help="the amount of periods before checking for new blocks. Requires --chain",
    )
    parser.add_argument(
        "--chain-interval",
        action="store",
        dest="chain_interval",
        type=int,
        help="avg block time to rely on for given chain. Requires --chain",
    )
    parser.add_argument(
        "--chain-range",
        action="store",
        dest="chain_range",
        type=int,
        help="maximum block to use when grouping a range of blocks. Requires --chain",
    )
    parser.add_argument(
        "--ethdo-wallet",
        action="store",
        dest="ethdo_wallet",
        help="default ethdo wallet name to be created/used",
    )
    parser.add_argument(
        "--ethdo-account",
        action="store",
        dest="ethdo_account",
        help="deafult ethdo account name to be created/used",
    )

    flags, unknown = parser.parse_known_args()

    if unknown:
        print(f"Unknown flags: {unknown}")
        raise UnknownFlagError

    return AttributeDict.convert_recursive(vars(flags))
