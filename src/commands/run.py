# -*- coding: utf-8 -*-

import os
import click

from src.globals import get_logger
from src.setup import setup, init_dbs, run_daemons


def config_reset(ctx, option, value):
    if not value or ctx.resilient_parsing:
        return

    click.confirm("Are you sure you want to drop the db?", abort=True)
    return value


@click.option(
    "--min-proposal-queue",
    required=False,
    type=click.IntRange(0, 50),
    help="Minimum amount of proposals to wait before creating a tx",
)
@click.option(
    "--max-proposal-delay",
    required=False,
    type=click.IntRange(0, 604800),
    help="Max seconds for any proposals to wait",
)
@click.option(
    "--network-refresh-rate",
    required=False,
    type=click.IntRange(0, 360),
    help="Cached data will be refreshed after provided delay (s)",
)
@click.option(
    "--network-attempt-rate",
    required=False,
    type=click.IntRange(0, 10),
    help="Interval between api requests (s)",
)
@click.option(
    "--network-max-attempt",
    required=False,
    type=click.IntRange(0, 100),
    help="Api requests will fail after given max calls",
)
@click.option(
    "--logger-dir",
    required=False,
    type=click.STRING,
    help="Directory name that log files will be stored",
)
@click.option(
    "--logger-level",
    required=False,
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Set logging level",
)
@click.option(
    "--logger-when",
    required=False,
    type=click.Choice(
        ["S", "M", "H", "D", "W0", "W1", "W2", "W3", "W4", "W5", "W6", "midnight"],
    ),
    help="When should logger continue with a new file",
)
@click.option(
    "--logger-interval",
    required=False,
    type=click.INT,
    help="how many intervals before logger continue with a new file",
)
@click.option(
    "--logger-backup",
    required=False,
    type=click.INT,
    help="how many logger files will be saved per logger",
)
@click.option(
    "--database-dir",
    required=False,
    type=click.STRING,
    help="Directory name that for the database",
)
@click.option(
    "--chain-start",
    required=False,
    type=click.INT,
    help="The first block to be considered for events within given chain.",
)
@click.option(
    "--chain-identifier",
    required=False,
    type=click.Choice(["latest", "earliest", "pending", "safe", "finalized"]),
    help="method to rely when fetching new blocks: latest, earliest, pending, safe, finalized.",
)
@click.option(
    "--chain-period",
    required=False,
    type=click.INT,
    help="the amount of periods before checking for new blocks.",
)
@click.option(
    "--chain-interval",
    required=False,
    type=click.INT,
    help="avg block time to rely on for given chain.",
)
@click.option(
    "--chain-range",
    required=False,
    type=click.INT,
    help="maximum block to use when grouping a range of blocks.",
)
@click.option(
    "--ethdo-wallet",
    required=False,
    type=click.STRING,
    help="default ethdo wallet name to be created/used",
)
@click.option(
    "--ethdo-account",
    required=False,
    type=click.STRING,
    help="deafult ethdo account name to be created/used",
)
@click.option(
    "--no-log-file",
    is_flag=True,
    help="Don't store log messages in a file",
)
@click.option(
    "--no-log-stream",
    is_flag=True,
    help="don't print log messages to the terminal",
)
@click.option(
    "--dont-notify-devs",
    required=False,
    is_flag=True,
    help="Don't send email notifications to geodefi for any unexpected errors.",
)
@click.option(
    "--reset",
    required=False,
    is_eager=True,
    is_flag=True,
    callback=config_reset,
    help="Reset the database and start over. Suggested after a new update or unexpected error.",
)
@click.option(
    "--chain",
    envvar="GEONIUS_CHAIN",
    required=True,
    type=click.Choice(["holesky", "ethereum"]),
    prompt="You forgot to specify the chain:",
    default="holesky",
    help="Network name, such as 'holesky' or 'ethereum' etc.",
)
@click.option(
    "--main-dir",
    envvar="GEONIUS_DIR",
    required=False,
    type=click.STRING,
    default=os.path.join(os.getcwd(), ".geonius"),
    help="Main directory PATH that will be used to store data. Default is ./.geonius",
)
@click.command(help="Start geonius.")
def main(**kwargs):
    """Main function of the program.
    This function is called with `geonius run`.
    Initializes the databases and starts the daemons.
    """
    try:
        setup(**kwargs)
        init_dbs(reset=kwargs["reset"])
        run_daemons()

    except Exception as e:
        try:
            get_logger().error(str(e))
            get_logger().error("Could not initiate geonius")
            get_logger().info("Exiting...")
        except Exception:
            print(str(e) + "\nCould not initiate geonius.\nExiting...")
