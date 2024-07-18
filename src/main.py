# -*- coding: utf-8 -*-

import click

from src import __version__

from src.commands.start import main as start
from src.commands.check_wallet import main as check_wallet
from src.commands.increase_wallet import main as increase_wallet
from src.commands.decrease_wallet import main as decrease_wallet
from src.commands.change_maintainer import main as change_maintainer
from src.commands.delegate import main as delegate
from src.commands.deposit import main as deposit
from src.commands.set_fallback import main as set_fallback


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    pass


# geonius
cli.add_command(start, "start")

# Operator helpers
cli.add_command(check_wallet, "check-wallet")
cli.add_command(increase_wallet, "increase-wallet")
cli.add_command(decrease_wallet, "decrease-wallet")
cli.add_command(change_maintainer, "change-maintainer")

# Pool helpers
cli.add_command(delegate, "delegate")
cli.add_command(deposit, "deposit")
cli.add_command(set_fallback, "set-fallback")

if __name__ == "__main__":
    cli()
