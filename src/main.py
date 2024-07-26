# -*- coding: utf-8 -*-

import click

from src.utils.version import get_version

from src.commands.run import main as run
from src.commands.config import main as config
from src.commands.check_wallet import main as check_wallet
from src.commands.increase_wallet import main as increase_wallet
from src.commands.decrease_wallet import main as decrease_wallet
from src.commands.change_maintainer import main as change_maintainer
from src.commands.delegate import main as delegate
from src.commands.deposit import main as deposit
from src.commands.set_fallback import main as set_fallback


@click.group()
@click.version_option(version=get_version())
def cli() -> None:
    pass


# geonius
cli.add_command(run, "run")
cli.add_command(config, "config")

# Operator helpers
cli.add_command(change_maintainer, "change-maintainer")
cli.add_command(check_wallet, "check-wallet")
cli.add_command(increase_wallet, "increase-wallet")
cli.add_command(decrease_wallet, "decrease-wallet")

# Pool helpers
cli.add_command(delegate, "delegate")
cli.add_command(deposit, "deposit")
cli.add_command(set_fallback, "set-fallback")

if __name__ == "__main__":
    cli()
