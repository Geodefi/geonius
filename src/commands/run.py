# -*- coding: utf-8 -*-

from src.globals import get_logger
from src.setup import setup, init_dbs, run_daemons


def main():
    """Main function of the program.

    This function is called with `geonius run --chain _xxx_`.

    initializes the databases and sets up the daemons.
    """
    try:
        setup()
        init_dbs()
        run_daemons()

    except Exception as e:
        try:
            get_logger().error(str(e))
            get_logger().error("Could not initiate geonius")
            get_logger().info("Exiting...")
        except Exception:
            print(str(e) + "\nCould not initiate geonius.\nExiting...")
