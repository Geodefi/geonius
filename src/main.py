# -*- coding: utf-8 -*-

import click

from src.commands.run import main as run
from src.commands.check_wallet import main as check_wallet
from src.commands.increase_wallet import main as increase_wallet
from src.commands.decrease_wallet import main as decrease_wallet
from src.commands.change_maintainer import main as change_maintainer


@click.version_option(version="0.0.1", prog_name='geonius: geodefi node operator automation')
@click.group()
def cli() -> None:
    pass


cli.add_command(run)
cli.add_command(check_wallet)
cli.add_command(increase_wallet)
cli.add_command(decrease_wallet)
cli.add_command(change_maintainer)
